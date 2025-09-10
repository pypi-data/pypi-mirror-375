"""
Core types for the Pillar SDK.

This module contains the core types used across the Pillar SDK,
independent of any specific integration.
"""

import json
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class Role(Enum):
    """Possible roles for a message."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"
    TOOL = "tool"


# === Message Types ===


class FunctionCall(BaseModel):
    name: str
    arguments: str

    @model_validator(mode="before")
    @classmethod
    def normalize_arguments_to_str(cls, values):
        """
        Normalize the arguments to a string.
        The OpenAI chat completions endpoint returns a list of tool calls,
        where each argument of the tool call is a string.
        Example:
            [
                {
                    "id": "call_12345xyz",
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "arguments": "{\"location\":\"Paris, France\"}"
                    }
                },
            ]
        The arguments field is a string, so we need to normalize it to a dict.
        """
        # get the raw tool calls from the message
        arguments = values.get("arguments")
        # if the arguments are a string, return the original values
        if isinstance(arguments, str):
            return values
        # if the arguments are a dict, make it a string
        elif isinstance(arguments, dict):
            values["arguments"] = json.dumps(arguments, sort_keys=True)
            return values
        # if the arguments field exists and is not a string or a dict, raise an error
        else:
            raise ValueError(f"Invalid tool call arguments: {arguments}")


class ToolCall(BaseModel):
    """
    This is the tool call from the user message.
    https://platform.openai.com/docs/guides/function-calling?api-mode=chat
    """

    id: str
    type: Literal["function"]
    function: FunctionCall


class PillarMessage(BaseModel):
    """A message in the Pillar system."""

    role: str
    content: str | None = Field(default=None, description="Content of the message, None for tool messages")
    tool_calls: list[ToolCall] | None = Field(default=None, description="Only used by assistant messages")
    tool_call_id: str | None = Field(default=None, description="Only used for tool results")

    @model_validator(mode="before")
    @classmethod
    def validate_message(cls, values):
        """
        Validate that the message has at least 2 fields.
        """
        if values is None or len(values) < 2:
            raise ValueError("Message must have at least 2 fields.")
        return values


# === Pillar Response Types ===


class FindingMetadata(BaseModel):
    """Metadata for a finding from Pillar analysis."""

    start_idx: int | None = Field(default=None, description="Start index of the evidence in the text")
    end_idx: int | None = Field(default=None, description="End index of the evidence in the text")


class Finding(BaseModel):
    """Detailed finding from Pillar analysis."""

    category: str = Field(description="Category of the finding (e.g., 'pii', 'prompt_injection')")
    type: str = Field(description="Type of the finding within the category")
    metadata: FindingMetadata | None = Field(default=None, description="Metadata for the finding")


class PillarApiResponse(BaseModel):
    """Response from the Pillar API content analysis endpoint (synchronous mode)."""

    flagged: bool = Field(description="Whether the content was flagged")
    session_id: str = Field(description="Session identifier")
    scanners: dict[str, bool] | None = Field(default=None, description="Scanners that were triggered and their results")
    evidence: list[Finding] | None = Field(default=None, description="Detailed findings from analysis")
    masked_messages: list[str] | None = Field(default=None, description="All messages without sensitive content")


class PillarMetadata(BaseModel):
    """Metadata for the Pillar API request."""

    source: str
    version: str


class PillarApiRequest(BaseModel):
    """Request for the Pillar API."""

    messages: list[PillarMessage]
    metadata: PillarMetadata
    tools: list[dict[str, Any]] | None = None
    session_id: str | None = None
    user_id: str | None = None
    service: str | None = Field(default=None, description="Service provider")
    model: str | None = Field(default=None, description="Model identifier")
