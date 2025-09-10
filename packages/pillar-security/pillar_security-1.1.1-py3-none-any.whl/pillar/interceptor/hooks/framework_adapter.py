from abc import ABC, abstractmethod
from collections.abc import AsyncIterable, Iterable
from enum import Enum
from typing import TYPE_CHECKING, Any, NamedTuple, TypeAlias

from pillar.callbacks import OnFlaggedResultType
from pillar.logging import Logger as PillarLogger
from pillar.types import PillarMessage

if TYPE_CHECKING:
    from pillar.client import Pillar

StreamChunk: TypeAlias = Any  # Base type for any stream chunk


class ExtractedInput(NamedTuple):
    """Standardized structure for input extracted from framework calls."""

    input_data: Any  # Framework-specific input (e.g., messages list, prompt string)
    input_arg_name: str  # The keyword arg name for the input_data (e.g., 'messages', 'prompt')
    model: str | None
    stream: bool
    api_type: Enum
    is_async: bool
    original_kwargs: dict  # Keep original kwargs for fallback/reconstruction
    tools: list[dict[str, Any]] | None = None


class FrameworkAdapter(ABC):
    """
    Abstract Base Class defining the interface for framework-specific hook logic.
    """

    _is_async: bool  # Internal flag set during instantiation

    def __init__(self, is_async: bool, logger: PillarLogger):
        self._is_async = is_async
        self.logger = logger

    @property
    def is_async(self) -> bool:
        """Returns True if the adapter is configured for asynchronous operations."""
        return self._is_async

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name (e.g., 'openai', 'anthropic')."""
        pass

    @abstractmethod
    def extract_input(self, args: tuple, kwargs: dict) -> ExtractedInput:
        """
        Extract relevant information (model, input, stream flag, etc.)
        from the framework's specific function arguments.
        Should populate all fields of ExtractedInput, including is_async based on self._is_async.
        Logs warnings for unexpected positional args.
        Raises ValueError if essential arguments (input, model) are missing.
        """
        pass

    @abstractmethod
    def format_input_for_pillar(
        self, pillar: "Pillar", extracted_input: ExtractedInput
    ) -> tuple[list[PillarMessage], Any]:
        """
        Convert the framework-specific input data into a list of PillarMessages.
        Returns tuple of:
        - list of messages
        - original_formatting_metadata with provider-specific information,
          in order to correctly re-format the output.
          e.g. had_role_prefix for OpenAI's legacy completion API.
          however for OpenAI's chat completion API, this will be None.
        """
        pass

    @abstractmethod
    def format_output_from_pillar(
        self,
        pillar: "Pillar",
        processed_input: OnFlaggedResultType,
        original_formatting_metadata: Any,
        extracted_input: ExtractedInput,  # Pass the whole tuple for context
    ) -> Any:
        """
        Convert Pillar's processed input messages back into the format expected
        by the framework's API call (e.g., potentially modified list or string).

        'original_formatting_metadata' is the second element returned by `format_input_for_pillar`.
        It carries provider-specific information needed to correctly re-format the output.
        For example, for OpenAI's legacy completion API, this might be a boolean
        `had_role_prefix` indicating if the original prompt used role prefixes.
        'extracted_input' provides original context like input_arg_name, model, tools, etc.
        """
        pass

    @abstractmethod
    def handle_sync_stream(
        self,
        pillar: "Pillar",
        extracted_input: ExtractedInput,  # Pass extracted input for context
        original_stream: Iterable[StreamChunk],
    ) -> Iterable[StreamChunk]:
        """
        Handles a synchronous stream result.
        Uses context from extracted_input (model, tools, api_type).

        Returns an Iterable[StreamChunk] which is a wrapper around the original stream result.
        """
        pass

    @abstractmethod
    def handle_async_stream(
        self,
        pillar: "Pillar",
        extracted_input: ExtractedInput,  # Pass extracted input for context
        original_stream: AsyncIterable[StreamChunk],
    ) -> AsyncIterable[StreamChunk]:
        """
        Handles an asynchronous stream result by returning an async iterable.
        The returned iterable yields chunks and performs analysis upon completion.
        Uses context from extracted_input (model, tools, api_type).

        Returns an AsyncIterable[StreamChunk] which is a wrapper around the original stream result.
        """
        pass

    @abstractmethod
    def extract_output_for_pillar(
        self, pillar: "Pillar", result: Any, extracted_input: ExtractedInput  # Pass context
    ) -> list[PillarMessage] | None:
        """
        Extract the LLM response from the framework's non-stream result object
        and convert it into a list of PillarMessages for analysis.
        Uses context from extracted_input (api_type).
        Returns None if no valid output messages can be extracted.
        """
        pass
