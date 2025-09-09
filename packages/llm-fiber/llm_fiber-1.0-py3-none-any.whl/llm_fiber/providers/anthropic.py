"""Anthropic provider adapter for llm-fiber."""

from __future__ import annotations

import json
from typing import Any, AsyncIterator, Dict, List, Optional

from ..types import (
    ChatMessage,
    ChatResult,
    FiberProviderError,
    StreamEvent,
    Usage,
    normalize_tool_call,
    validate_tool_call_format,
)
from .base import BaseProvider


class AnthropicAdapter(BaseProvider):
    """Anthropic API adapter for Claude models."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_seconds: float = 30.0,
    ):
        if base_url is None:
            base_url = "https://api.anthropic.com"

        super().__init__(api_key, base_url, timeout_seconds)
        self.name = "anthropic"

    def prepare_request(
        self,
        model: str,
        messages: List[ChatMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        seed: Optional[int] = None,
        stop: Optional[List[str]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Prepare Anthropic API request payload."""

        # Separate system messages from conversation messages
        system_messages = []
        conversation_messages = []

        for msg in messages:
            if msg.role == "system":
                system_messages.append(msg.content)
            else:
                # Convert to Anthropic format
                api_msg = {"role": msg.role, "content": msg.content}

                # Handle tool calls and responses
                if msg.tool_calls:
                    # Convert tool calls to Anthropic format
                    content_blocks = []
                    if msg.content:
                        content_blocks.append({"type": "text", "text": msg.content})

                    for tool_call in msg.tool_calls:
                        content_blocks.append(
                            {
                                "type": "tool_use",
                                "id": tool_call.get("id", ""),
                                "name": tool_call.get("function", {}).get("name", ""),
                                "input": json.loads(
                                    tool_call.get("function", {}).get("arguments", "{}")
                                ),
                            }
                        )

                    api_msg["content"] = content_blocks

                elif msg.tool_call_id:
                    # Tool result message
                    api_msg["content"] = [
                        {
                            "type": "tool_result",
                            "tool_use_id": msg.tool_call_id,
                            "content": msg.content,
                        }
                    ]

                conversation_messages.append(api_msg)

        # Build payload
        payload = {
            "model": model,
            "messages": conversation_messages,
            "max_tokens": max_tokens or 4096,  # Required by Anthropic
        }

        # Add system message if present
        if system_messages:
            payload["system"] = "\n\n".join(system_messages)

        # Add optional parameters
        if temperature is not None:
            payload["temperature"] = temperature
        if top_p is not None:
            payload["top_p"] = top_p
        if stop is not None:
            payload["stop_sequences"] = stop
        if tools is not None:
            # Convert tools to Anthropic format
            anthropic_tools = []
            for tool in tools:
                anthropic_tool = {
                    "name": tool.get("function", {}).get("name", ""),
                    "description": tool.get("function", {}).get("description", ""),
                    "input_schema": tool.get("function", {}).get("parameters", {}),
                }
                anthropic_tools.append(anthropic_tool)
            payload["tools"] = anthropic_tools

        if tool_choice is not None:
            if tool_choice == "none":
                # Don't include tool_choice, Anthropic will not use tools
                pass
            elif tool_choice == "auto":
                payload["tool_choice"] = {"type": "auto"}
            else:
                # Specific tool
                payload["tool_choice"] = {"type": "tool", "name": tool_choice}

        # Add any additional kwargs
        payload.update(kwargs)

        return payload

    def parse_response(self, response: Dict[str, Any]) -> ChatResult:
        """Parse Anthropic API response."""

        content_blocks = response.get("content", [])
        if not content_blocks:
            raise FiberProviderError("No content in response", provider=self.name)

        # Extract text and tool calls
        text_parts = []
        tool_calls = []

        for block in content_blocks:
            if block.get("type") == "text":
                text_parts.append(block.get("text", ""))
            elif block.get("type") == "tool_use":
                # Convert to OpenAI-compatible format
                tool_call = {
                    "id": block.get("id", ""),
                    "type": "function",
                    "function": {
                        "name": block.get("name", ""),
                        "arguments": json.dumps(block.get("input", {})),
                    },
                }
                tool_calls.append(tool_call)

        text = "".join(text_parts)
        finish_reason = response.get("stop_reason")

        # Parse usage information
        usage_data = response.get("usage", {})
        usage = Usage(
            prompt=usage_data.get("input_tokens", 0),
            completion=usage_data.get("output_tokens", 0),
            total=usage_data.get("input_tokens", 0) + usage_data.get("output_tokens", 0),
        )

        return ChatResult(
            text=text, tool_calls=tool_calls, finish_reason=finish_reason, usage=usage, raw=response
        )

    async def chat(
        self,
        model: str,
        messages: List[ChatMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        seed: Optional[int] = None,
        stop: Optional[List[str]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        idempotency_key: Optional[str] = None,
        **kwargs,
    ) -> ChatResult:
        """Execute Anthropic chat completion request."""

        url = f"{self.base_url}/v1/messages"
        headers = self.get_headers(idempotency_key)

        payload = self.prepare_request(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            seed=seed,
            stop=stop,
            tools=tools,
            tool_choice=tool_choice,
            **kwargs,
        )

        response_data = await self._make_request(
            method="POST",
            url=url,
            headers=headers,
            json_data=payload,
            timeout_override=timeout_seconds,
        )

        return self.parse_response(response_data)

    async def chat_stream(
        self,
        model: str,
        messages: List[ChatMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        seed: Optional[int] = None,
        stop: Optional[List[str]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        idempotency_key: Optional[str] = None,
        **kwargs,
    ) -> AsyncIterator[StreamEvent]:
        """Execute Anthropic streaming chat completion request."""

        url = f"{self.base_url}/v1/messages"
        headers = self.get_headers(idempotency_key)

        payload = self.prepare_request(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            seed=seed,
            stop=stop,
            tools=tools,
            tool_choice=tool_choice,
            stream=True,  # Enable streaming
            **kwargs,
        )

        # Track streaming state
        accumulated_content = ""
        current_tool_call = None
        final_usage = None

        async for chunk in self._make_streaming_request(
            method="POST",
            url=url,
            headers=headers,
            json_data=payload,
            timeout_override=timeout_seconds,
        ):
            # Parse Server-Sent Events format
            for line in chunk.decode("utf-8", errors="ignore").strip().split("\n"):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith(":"):
                    continue

                # Parse event lines
                if line.startswith("event: "):
                    event_type = line[7:].strip()
                    continue

                # Parse data lines
                if line.startswith("data: "):
                    data_str = line[6:].strip()

                    try:
                        event_data = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    # Handle different event types
                    event_type = event_data.get("type", "")

                    if event_type == "message_start":
                        # Extract initial usage if available
                        message = event_data.get("message", {})
                        usage_data = message.get("usage", {})
                        if usage_data:
                            final_usage = Usage(
                                prompt=usage_data.get("input_tokens", 0),
                                completion=usage_data.get("output_tokens", 0),
                                total=usage_data.get("input_tokens", 0)
                                + usage_data.get("output_tokens", 0),
                            )

                    elif event_type == "content_block_start":
                        # Start of a new content block
                        content_block = event_data.get("content_block", {})
                        if content_block.get("type") == "tool_use":
                            current_tool_call = {
                                "id": content_block.get("id", ""),
                                "type": "function",
                                "function": {
                                    "name": content_block.get("name", ""),
                                    "arguments": "",
                                },
                            }

                    elif event_type == "content_block_delta":
                        # Content delta
                        delta = event_data.get("delta", {})

                        if delta.get("type") == "text_delta":
                            # Text content
                            text = delta.get("text", "")
                            if text:
                                accumulated_content += text
                                yield StreamEvent.chunk(text)

                        elif delta.get("type") == "input_json_delta":
                            # Tool call argument delta
                            if current_tool_call:
                                partial_json = delta.get("partial_json", "")
                                current_tool_call["function"]["arguments"] += partial_json

                    elif event_type == "content_block_stop":
                        # End of content block
                        if current_tool_call:
                            # Normalize and emit tool call event
                            if validate_tool_call_format(current_tool_call, "openai"):
                                try:
                                    normalized = normalize_tool_call(current_tool_call, "openai")
                                    yield StreamEvent.create_tool_call(
                                        normalized.to_openai_format()
                                    )
                                except Exception:
                                    # Fallback to original format
                                    yield StreamEvent.create_tool_call(current_tool_call)
                            else:
                                # Emit original format for invalid tool calls
                                yield StreamEvent.create_tool_call(current_tool_call)
                            current_tool_call = None

                    elif event_type == "message_delta":
                        # Message-level delta, may contain final usage
                        delta = event_data.get("delta", {})
                        usage_data = delta.get("usage", {})
                        if usage_data:
                            # Update final usage with completion tokens
                            if final_usage:
                                final_usage = Usage(
                                    prompt=final_usage.prompt,
                                    completion=usage_data.get(
                                        "output_tokens", final_usage.completion
                                    ),
                                    total=final_usage.prompt
                                    + usage_data.get("output_tokens", final_usage.completion),
                                )

                    elif event_type == "message_stop":
                        # End of message
                        if final_usage:
                            yield StreamEvent.create_usage(final_usage)
                        return

    def supports_feature(self, feature: str) -> bool:
        """Check Anthropic feature support."""
        supported_features = {
            "streaming": True,
            "tools": True,
            "vision": True,  # Claude 3 supports vision
            "json_mode": False,  # Not directly supported
            "system_messages": True,
            "seed": False,  # Not supported by Anthropic
            "logprobs": False,  # Not supported
        }
        return supported_features.get(feature, False)

    def validate_model(self, model: str) -> bool:
        """Validate Anthropic model name."""
        # Anthropic models typically start with 'claude-'
        valid_prefixes = ["claude-", "claude"]
        return any(model.startswith(prefix) for prefix in valid_prefixes)

    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens using Anthropic's rough approximation."""
        # Anthropic's approximation: similar to OpenAI, ~4 characters per token
        return max(1, len(text) // 4)

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get Anthropic authentication headers."""
        return {"x-api-key": self.api_key, "anthropic-version": "2023-06-01"}

    def _get_idempotency_headers(self, key: str) -> Dict[str, str]:
        """Get Anthropic idempotency headers."""
        return {"anthropic-beta": f"idempotency-{key}"}
