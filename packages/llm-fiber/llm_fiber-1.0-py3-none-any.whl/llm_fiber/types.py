"""Core types and data structures for llm-fiber."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class FiberError(Exception):
    """Base exception for all llm-fiber errors."""

    def __init__(self, message: str, provider: Optional[str] = None, model: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.model = model


class FiberConnectionError(FiberError):
    """Network connection failed."""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        host: Optional[str] = None,
    ):
        super().__init__(message, provider, model)
        self.host = host


class FiberTimeoutError(FiberError):
    """Request timed out."""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        timeout_duration: Optional[float] = None,
    ):
        super().__init__(message, provider, model)
        self.timeout_duration = timeout_duration


class FiberAuthError(FiberError):
    """Authentication failed."""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        status_code: Optional[int] = None,
    ):
        super().__init__(message, provider, model)
        self.status_code = status_code


class FiberRateLimitError(FiberError):
    """Rate limit exceeded."""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        retry_after: Optional[int] = None,
        limit: Optional[int] = None,
    ):
        super().__init__(message, provider, model)
        self.retry_after = retry_after
        self.limit = limit


class FiberQuotaError(FiberError):
    """Quota or budget exceeded."""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        limit: Optional[int] = None,
        usage: Optional[int] = None,
    ):
        super().__init__(message, provider, model)
        self.limit = limit
        self.usage = usage


class FiberValidationError(FiberError):
    """Invalid request parameters."""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        parameter: Optional[str] = None,
    ):
        super().__init__(message, provider, model)
        self.parameter = parameter


class FiberProviderError(FiberError):
    """Provider-specific error."""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        status_code: Optional[int] = None,
        provider_code: Optional[str] = None,
        raw_response: Optional[str] = None,
    ):
        super().__init__(message, provider, model)
        self.status_code = status_code
        self.provider_code = provider_code
        self.raw_response = raw_response


class FiberParsingError(FiberError):
    """Failed to parse structured output."""

    pass


@dataclass
class Usage:
    """Token usage and cost information."""

    prompt: int = 0
    completion: int = 0
    total: int = 0
    cost_estimate: Optional[float] = None  # USD

    def __post_init__(self):
        if self.total == 0 and (self.prompt > 0 or self.completion > 0):
            self.total = self.prompt + self.completion


class ChatMessage:
    """Represents a chat message with role-specific factory methods."""

    def __init__(
        self,
        role: str,
        content: str,
        name: Optional[str] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        tool_call_id: Optional[str] = None,
    ):
        self.role = role
        self.content = content
        self.name = name
        self.tool_calls = tool_calls or []
        self.tool_call_id = tool_call_id

    @classmethod
    def system(cls, content: str) -> ChatMessage:
        """Create a system message."""
        return cls("system", content)

    @classmethod
    def user(cls, content: str, name: Optional[str] = None) -> ChatMessage:
        """Create a user message."""
        return cls("user", content, name=name)

    @classmethod
    def assistant(
        cls,
        content: str,
        name: Optional[str] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
    ) -> ChatMessage:
        """Create an assistant message."""
        return cls("assistant", content, name=name, tool_calls=tool_calls)

    @classmethod
    def tool(cls, content: str, tool_call_id: str) -> ChatMessage:
        """Create a tool response message."""
        return cls("tool", content, tool_call_id=tool_call_id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls."""
        result = {"role": self.role, "content": self.content}

        if self.name:
            result["name"] = self.name
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id

        return result

    def __repr__(self) -> str:
        return f"ChatMessage(role='{self.role}', content='{self.content[:50]}...')"


@dataclass
class ChatResult:
    """Result from a chat completion request."""

    text: str
    tool_calls: List[Dict[str, Any]]
    finish_reason: Optional[str]
    usage: Optional[Usage]
    raw: Dict[str, Any]  # Raw provider response


class StreamEventType(Enum):
    """Types of streaming events."""

    CHUNK = "chunk"
    TOOL_CALL = "tool_call"
    USAGE = "usage"
    LOG = "log"


@dataclass
class StreamEvent:
    """A single event in a streaming response."""

    type: StreamEventType
    timestamp: float
    delta: str = ""  # Text delta for chunk events
    tool_call: Optional[Dict[str, Any]] = None
    usage: Optional[Usage] = None
    log_message: Optional[str] = None
    log_level: str = "info"

    def __post_init__(self):
        if self.timestamp == 0:
            self.timestamp = time.time()

    @classmethod
    def create_chunk(
        cls, delta: str, timestamp: Optional[float] = None, sequence: Optional[int] = None
    ) -> StreamEvent:
        """Create a text chunk event."""
        return cls(type=StreamEventType.CHUNK, timestamp=timestamp or time.time(), delta=delta)

    @classmethod
    def create_tool_call(
        cls, tool_call: Dict[str, Any], timestamp: Optional[float] = None
    ) -> StreamEvent:
        """Create a tool call event."""
        return cls(
            type=StreamEventType.TOOL_CALL, timestamp=timestamp or time.time(), tool_call=tool_call
        )

    @classmethod
    def create_usage(cls, usage: Usage, timestamp: Optional[float] = None) -> StreamEvent:
        """Create a usage event."""
        return cls(type=StreamEventType.USAGE, timestamp=timestamp or time.time(), usage=usage)

    @classmethod
    def create_log(
        cls, message: str, level: str = "info", timestamp: Optional[float] = None
    ) -> StreamEvent:
        """Create a log event."""
        return cls(
            type=StreamEventType.LOG,
            timestamp=timestamp or time.time(),
            log_message=message,
            log_level=level,
        )


# Tool Call Normalization Utilities
# Addresses the "post-MVP" tool calling normalization mentioned in docs


@dataclass
class NormalizedToolCall:
    """Normalized tool call structure across providers."""

    id: str
    name: str
    arguments: Dict[str, Any]
    type: str = "function"

    def to_openai_format(self) -> Dict[str, Any]:
        """Convert to OpenAI-compatible format."""
        return {
            "id": self.id,
            "type": self.type,
            "function": {
                "name": self.name,
                "arguments": json.dumps(self.arguments),
            },
        }

    def to_anthropic_format(self) -> Dict[str, Any]:
        """Convert to Anthropic-compatible format."""
        return {
            "type": "tool_use",
            "id": self.id,
            "name": self.name,
            "input": self.arguments,
        }

    def to_gemini_format(self) -> Dict[str, Any]:
        """Convert to Gemini-compatible format."""
        return {
            "functionCall": {
                "name": self.name,
                "args": self.arguments,
            }
        }


def normalize_tool_call(tool_call: Dict[str, Any], provider: str = "openai") -> NormalizedToolCall:
    """Normalize tool call from provider-specific format to standard format.

    Args:
        tool_call: Provider-specific tool call dictionary
        provider: Provider name ("openai", "anthropic", "gemini")

    Returns:
        NormalizedToolCall instance

    Raises:
        FiberValidationError: If tool call format is invalid
    """
    try:
        if provider.lower() == "openai":
            return _normalize_openai_tool_call(tool_call)
        elif provider.lower() == "anthropic":
            return _normalize_anthropic_tool_call(tool_call)
        elif provider.lower() == "gemini":
            return _normalize_gemini_tool_call(tool_call)
        else:
            # Fallback: assume OpenAI format
            return _normalize_openai_tool_call(tool_call)
    except (KeyError, TypeError, ValueError) as e:
        raise FiberValidationError(
            f"Invalid tool call format from {provider}: {str(e)}",
            provider=provider,
        )


def _normalize_openai_tool_call(tool_call: Dict[str, Any]) -> NormalizedToolCall:
    """Normalize OpenAI tool call format."""
    import json

    function = tool_call["function"]
    arguments = function.get("arguments", "{}")

    # Parse arguments if they're a JSON string
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError:
            arguments = {}

    return NormalizedToolCall(
        id=tool_call["id"],
        name=function["name"],
        arguments=arguments,
        type=tool_call.get("type", "function"),
    )


def _normalize_anthropic_tool_call(tool_call: Dict[str, Any]) -> NormalizedToolCall:
    """Normalize Anthropic tool call format."""
    return NormalizedToolCall(
        id=tool_call["id"],
        name=tool_call["name"],
        arguments=tool_call.get("input", {}),
        type="function",  # Anthropic uses "tool_use" but normalize to "function"
    )


def _normalize_gemini_tool_call(tool_call: Dict[str, Any]) -> NormalizedToolCall:
    """Normalize Gemini tool call format."""
    function_call = tool_call["functionCall"]

    return NormalizedToolCall(
        id=tool_call.get(
            "id", f"call_{hash(str(function_call))}"
        ),  # Gemini doesn't always provide IDs
        name=function_call["name"],
        arguments=function_call.get("args", {}),
        type="function",
    )


def validate_tool_call_format(tool_call: Dict[str, Any], provider: str = "openai") -> bool:
    """Validate tool call format for a specific provider.

    Args:
        tool_call: Tool call dictionary to validate
        provider: Provider name

    Returns:
        True if valid, False otherwise
    """
    try:
        normalize_tool_call(tool_call, provider)
        return True
    except (FiberValidationError, KeyError, TypeError):
        return False


def create_tool_response_message(
    tool_call_id: str, content: str, name: Optional[str] = None
) -> ChatMessage:
    """Create a tool response message.

    Args:
        tool_call_id: ID of the tool call being responded to
        content: Response content
        name: Optional tool name

    Returns:
        ChatMessage with role="tool"
    """
    return ChatMessage(
        role="tool",
        content=content,
        tool_call_id=tool_call_id,
        name=name,
    )


def extract_tool_calls_from_stream_events(events: List[StreamEvent]) -> List[NormalizedToolCall]:
    """Extract and normalize tool calls from stream events.

    Args:
        events: List of stream events

    Returns:
        List of normalized tool calls
    """
    tool_calls = []

    for event in events:
        if event.type == StreamEventType.TOOL_CALL and event.tool_call:
            try:
                normalized = normalize_tool_call(event.tool_call)
                tool_calls.append(normalized)
            except FiberValidationError:
                # Skip invalid tool calls rather than failing completely
                continue

    return tool_calls


# Type aliases for flexibility
MessageInput = Union[str, ChatMessage, tuple, Dict[str, Any]]
MessagesInput = Union[List[MessageInput], str]


def normalize_message(msg: MessageInput) -> ChatMessage:
    """Normalize various message input formats to ChatMessage."""
    if isinstance(msg, ChatMessage):
        return msg
    elif isinstance(msg, str):
        return ChatMessage.user(msg)
    elif isinstance(msg, tuple):
        if len(msg) == 2:
            role, content = msg
            return ChatMessage(role, content)
        else:
            raise FiberValidationError(
                f"Tuple messages must have exactly 2 elements (role, content), got {len(msg)}"
            )
    elif isinstance(msg, dict):
        role = msg.get("role")
        content = msg.get("content", "")
        if not role:
            raise FiberValidationError("Dict messages must have a 'role' field")

        return ChatMessage(
            role=role,
            content=content,
            name=msg.get("name"),
            tool_calls=msg.get("tool_calls"),
            tool_call_id=msg.get("tool_call_id"),
        )
    else:
        raise FiberValidationError(f"Unsupported message type: {type(msg)}")


def normalize_messages(messages: MessagesInput) -> List[ChatMessage]:
    """Normalize various message input formats to list of ChatMessage."""
    if isinstance(messages, str):
        return [ChatMessage.user(messages)]
    elif isinstance(messages, list):
        return [normalize_message(msg) for msg in messages]
    else:
        raise FiberValidationError(f"Messages must be string or list, got {type(messages)}")
