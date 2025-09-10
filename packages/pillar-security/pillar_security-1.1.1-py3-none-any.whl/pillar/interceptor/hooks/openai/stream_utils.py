from typing import Any, TypeAlias

from openai.types import Completion
from openai.types.chat import ChatCompletionChunk

from pillar.types import PillarMessage, Role

# Type alias for Completion-style stream chunks (dict-like)
# CompletionChunk = dict[str, Any] | Completion
CompletionChunk: TypeAlias = dict[str, Any] | Completion


def chat_completion_stream_collector(
    chunks: list[ChatCompletionChunk],
) -> list[PillarMessage]:
    """
    Reconstructs one or more PillarMessages from a stream of OpenAI ChatCompletion chunks.
    Handles tool calls and multi-part assistant messages.
    """
    results: list[PillarMessage] = []
    current_message: dict[str, Any] | None = None
    tool_calls_by_index: dict[int, dict[str, Any]] = {}

    for chunk in chunks:
        if not chunk.choices:
            continue  # Skip malformed or empty chunks

        choice = chunk.choices[0]
        delta = choice.delta

        # Initialize message if needed
        if current_message is None:
            current_message = {
                "role": delta.role or Role.ASSISTANT.value,
                "content": "",
                "tool_calls": [],
            }

        # If tool_calls come in after text, flush text message first
        if delta.tool_calls and current_message.get("content"):
            results.append(
                PillarMessage(
                    role=current_message["role"],
                    content=current_message["content"],
                    tool_calls=[],
                )
            )
            current_message = {
                "role": Role.ASSISTANT.value,
                "content": "",
                "tool_calls": [],
            }

        # Accumulate content
        if delta.content:
            current_message["content"] += delta.content

        # Accumulate tool calls
        if delta.tool_calls:
            for tool_call in delta.tool_calls:
                idx = tool_call.index
                existing = tool_calls_by_index.get(
                    idx,
                    {"id": "", "type": "", "function": {"name": "", "arguments": ""}},
                )

                if tool_call.id:
                    existing["id"] = tool_call.id
                if tool_call.type:
                    existing["type"] = tool_call.type
                if tool_call.function:
                    if tool_call.function.name:
                        existing["function"]["name"] = tool_call.function.name
                    if tool_call.function.arguments:
                        prev_args = existing["function"].get("arguments", "")
                        existing["function"]["arguments"] = prev_args + tool_call.function.arguments

                tool_calls_by_index[idx] = existing

        # Finish the message when completion is done
        if choice.finish_reason:
            if tool_calls_by_index:
                current_message["tool_calls"] = [tool_calls_by_index[i] for i in sorted(tool_calls_by_index)]
            results.append(PillarMessage(**current_message))
            current_message = None
            tool_calls_by_index = {}

    # Fallback if last chunk had no finish_reason
    if current_message:
        if tool_calls_by_index:
            current_message["tool_calls"] = [tool_calls_by_index[i] for i in sorted(tool_calls_by_index)]
        results.append(PillarMessage(**current_message))

    return results


def completion_stream_collector(
    chunks: list[CompletionChunk],
) -> list[PillarMessage]:
    """
    Reconstructs a single PillarMessage from a stream of Completion (non-chat) chunks.
    Assumes all content is one assistant message. Handles both dict and object chunks.
    """
    full_text = ""
    role = Role.ASSISTANT.value  # Completions always imply assistant role

    for chunk in chunks:
        if not chunk:
            continue

        choices = None
        # Use attribute access for Completion objects, fallback to .get for dicts
        if isinstance(chunk, Completion):
            choices = getattr(chunk, "choices", None)
        elif isinstance(chunk, dict):
            choices = chunk.get("choices")

        if not choices or not isinstance(choices, list) or len(choices) == 0:
            continue  # skip invalid/malformed chunk or chunk with empty choices list

        choice = choices[0]
        delta_text = None
        if isinstance(choice, dict):
            delta_text = choice.get("text")
        elif hasattr(choice, "text"):  # Check if it's likely a CompletionChoice object
            delta_text = getattr(choice, "text", None)

        if delta_text is not None:  # Check explicitly for None
            full_text += delta_text

    if full_text:
        return [PillarMessage(role=role, content=full_text)]
    return []
