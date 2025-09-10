from collections.abc import AsyncIterable, Callable, Iterable
from enum import Enum
from typing import TYPE_CHECKING, Any

import pillar.context_vars as cv
from pillar.callbacks import OnFlaggedResultType
from pillar.interceptor.hooks.framework_adapter import ExtractedInput, FrameworkAdapter
from pillar.interceptor.hooks.hook_factory import create_generic_hook
from pillar.interceptor.hooks.openai.format_utils import (
    KNOWN_ROLE_PREFIXES,
    parse_completion_to_pillar_messages,
    pillar_messages_to_completion,
)
from pillar.interceptor.hooks.openai.stream_utils import (
    ChatCompletionChunk,
    CompletionChunk,
    chat_completion_stream_collector,
    completion_stream_collector,
)
from pillar.interceptor.hooks.stream_wrapper import AsyncStreamAnalyzer, SyncStreamAnalyzer
from pillar.types import PillarMessage, Role

if TYPE_CHECKING:
    from pillar.client import Pillar

OPENAI = "openai"


class OpenAIAPIType(Enum):
    CHAT = "chat"
    COMPLETION = "completion"


def extract_open_ai_input(
    args: tuple, kwargs: dict, input_arg_name: str, api_type: OpenAIAPIType, is_async: bool
) -> ExtractedInput:
    """Helper to extract common arguments."""
    input_data = kwargs.get(input_arg_name)
    model = kwargs.get("model")
    stream = kwargs.get("stream", False)
    tools = kwargs.get("tools") if api_type == OpenAIAPIType.CHAT else None  # Tools only for chat

    return ExtractedInput(
        input_data=input_data,
        input_arg_name=input_arg_name,
        model=model,
        stream=stream,
        tools=tools,
        api_type=api_type,
        is_async=is_async,
        original_kwargs=kwargs.copy(),  # Store a copy
    )


class OpenAIChatAdapter(FrameworkAdapter):
    """Adapter for OpenAI Chat Completion API."""

    @property
    def provider_name(self) -> str:
        return OPENAI

    def extract_input(self, args: tuple, kwargs: dict) -> ExtractedInput:
        return extract_open_ai_input(
            args,
            kwargs,
            input_arg_name="messages",
            api_type=OpenAIAPIType.CHAT,
            is_async=self.is_async,
        )

    def format_input_for_pillar(
        self, pillar: "Pillar", extracted_input: ExtractedInput
    ) -> tuple[list[PillarMessage], Any]:
        """
        Format the input for the Pillar framework.

        Chat messages are already in a compatible list format
        No special formatting context needed
        """
        # in the chat completion case, the input_data is already a list of dicts
        is_list = isinstance(extracted_input.input_data, list)
        dict_list = is_list and all(isinstance(item, dict) for item in extracted_input.input_data)
        if dict_list:
            messages = [PillarMessage(**msg) for msg in extracted_input.input_data]
        else:
            # fallback
            messages = []
        return messages, None

    def format_output_from_pillar(
        self,
        pillar: "Pillar",
        processed_input: OnFlaggedResultType,
        original_formatting_metadata: Any,
        extracted_input: ExtractedInput,
    ) -> Any:
        """
        Format the output from the Pillar framework.

        Assume processed_input is the potentially modified list of messages
        """
        fallback = extracted_input.input_data
        if isinstance(processed_input, list):
            if all(isinstance(msg, PillarMessage) for msg in processed_input):
                return [msg.model_dump() for msg in processed_input]
            elif all(isinstance(msg, dict) for msg in processed_input):
                return processed_input
            return fallback
        elif isinstance(processed_input, dict):  # Single message dict
            return [processed_input]
        else:
            self.logger.warning(f"Unexpected type: {type(processed_input)}. Using original.")
            return extracted_input.input_data  # Fallback

    def handle_sync_stream(
        self,
        pillar: "Pillar",
        extracted_input: ExtractedInput,
        original_stream: Iterable[ChatCompletionChunk],
    ) -> Iterable[ChatCompletionChunk]:
        """Handle sync stream for Chat Completion using SyncStreamWrapper."""
        return SyncStreamAnalyzer(
            pillar=pillar,
            extracted_input=extracted_input,
            original_stream=original_stream,
            collector_func=chat_completion_stream_collector,
            provider_name=self.provider_name,
            previous_context=cv.get_context_object(),
        )

    def handle_async_stream(
        self,
        pillar: "Pillar",
        extracted_input: ExtractedInput,
        original_stream: AsyncIterable[ChatCompletionChunk],
    ) -> AsyncIterable[ChatCompletionChunk]:
        """Handle async stream for Chat Completion using AsyncStreamWrapper."""

        return AsyncStreamAnalyzer(
            pillar=pillar,
            extracted_input=extracted_input,
            original_stream=original_stream,
            provider_name=self.provider_name,
            collector_func=chat_completion_stream_collector,
            previous_context=cv.get_context_object(),
        )

    def extract_output_for_pillar(
        self, pillar: "Pillar", result: Any, extracted_input: ExtractedInput
    ) -> list[PillarMessage] | None:
        """Extract the output from the OpenAI API.

        If the result is a ChatCompletion object, extract the messages.
        """
        if hasattr(result, "choices") and result.choices:
            # Ensure messages are dicts for analysis
            try:
                output_dicts = [choice.message.to_dict() for choice in result.choices]
                messages = [PillarMessage(**msg_dict) for msg_dict in output_dicts]
                return messages
            except Exception as e:
                self.logger.error(f"Failed to convert OpenAI chat choices to dicts: {e}")
                return None
        else:
            self.logger.warning(f"No choices found in OpenAI chat response object: {type(result)}")
            return None


class OpenAICompletionAdapter(FrameworkAdapter):
    """Adapter for OpenAI Completion API (Legacy)."""

    @property
    def provider_name(self) -> str:
        return OPENAI

    def extract_input(self, args: tuple, kwargs: dict) -> ExtractedInput:
        return extract_open_ai_input(
            args,
            kwargs,
            input_arg_name="prompt",
            api_type=OpenAIAPIType.COMPLETION,
            is_async=self.is_async,
        )

    def format_input_for_pillar(
        self, pillar: "Pillar", extracted_input: ExtractedInput
    ) -> tuple[list[PillarMessage], Any]:
        # Need to parse the prompt string/list into PillarMessages
        # Also need to track if role prefixes were used.
        prompt = extracted_input.input_data
        had_role_prefix = isinstance(prompt, str) and any(prompt.strip().startswith(p) for p in KNOWN_ROLE_PREFIXES)
        messages = parse_completion_to_pillar_messages(prompt)
        return messages, had_role_prefix  # Pass had_role_prefix as context

    def format_output_from_pillar(
        self,
        pillar: "Pillar",
        processed_input: OnFlaggedResultType,
        original_formatting_metadata: Any,  # This is had_role_prefix
        extracted_input: ExtractedInput,
    ) -> Any:
        """
        Format the output from the Pillar framework.

        Convert pillar messages back to a flat string, respecting original prefix usage
        """
        had_role_prefix = original_formatting_metadata
        final_prompt = pillar_messages_to_completion(processed_input, had_role_prefix)
        return final_prompt

    def handle_sync_stream(
        self,
        pillar: "Pillar",
        extracted_input: ExtractedInput,
        original_stream: Iterable[CompletionChunk],
    ) -> Iterable[CompletionChunk]:
        """Handle sync stream for Completion using SyncStreamWrapper."""
        return SyncStreamAnalyzer(
            pillar=pillar,
            extracted_input=extracted_input,
            original_stream=original_stream,
            collector_func=completion_stream_collector,
            provider_name=self.provider_name,
            previous_context=cv.get_context_object(),
        )

    def handle_async_stream(
        self,
        pillar: "Pillar",
        extracted_input: ExtractedInput,
        original_stream: AsyncIterable[CompletionChunk],
    ) -> AsyncIterable[CompletionChunk]:
        """Handle async stream for Completion using AsyncStreamWrapper."""
        return AsyncStreamAnalyzer(
            pillar=pillar,
            extracted_input=extracted_input,
            original_stream=original_stream,
            collector_func=completion_stream_collector,
            provider_name=self.provider_name,
            previous_context=cv.get_context_object(),
        )

    def extract_output_for_pillar(
        self, pillar: "Pillar", result: Any, extracted_input: ExtractedInput
    ) -> list[PillarMessage] | None:
        """Extract the output from the OpenAI API.

        If the result is a Completion object, extract the text.
        """
        # If for some reason the results is already a list of PillarMessages, return it
        if isinstance(result, list):
            if all(isinstance(msg, PillarMessage) for msg in result):
                return result
        if hasattr(result, "choices") and result.choices:
            try:
                completion_text = result.choices[0].text
                # Convert completion text to a single PillarMessage
                output_messages = [PillarMessage(role=Role.ASSISTANT.value, content=completion_text)]
                return output_messages
            except (AttributeError, IndexError) as e:
                self.logger.error(f"Failed to extract text from OpenAI completion choice: {e}")
                return None
        else:
            self.logger.warning(f"No choices found in OpenAI completion response object: {type(result)}")
            return None


# --- Factory Function ---


def create_openai_hook_factory(
    pillar: "Pillar",
    is_async: bool,
    api_type: Enum,
) -> Callable:
    """
    Factory to create OpenAI hook functions using the generic hook and specific adapters.
    """
    adapter: FrameworkAdapter
    if api_type == OpenAIAPIType.CHAT:
        adapter = OpenAIChatAdapter(is_async=is_async, logger=pillar.logger)
    elif api_type == OpenAIAPIType.COMPLETION:
        adapter = OpenAICompletionAdapter(is_async=is_async, logger=pillar.logger)
    else:
        raise ValueError(f"Unsupported OpenAI API type: {api_type.value}")

    # Create and return the hook using the generic creator and the chosen adapter
    return create_generic_hook(pillar, adapter)
