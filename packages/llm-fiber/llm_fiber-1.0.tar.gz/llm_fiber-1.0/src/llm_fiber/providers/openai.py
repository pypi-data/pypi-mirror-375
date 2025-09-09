"""OpenAI provider adapter for llm-fiber."""

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


class OpenAIAdapter(BaseProvider):
    """OpenAI API adapter."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_seconds: float = 30.0,
    ):
        if base_url is None:
            base_url = "https://api.openai.com/v1"

        super().__init__(api_key, base_url, timeout_seconds)
        self.name = "openai"

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
        """Prepare OpenAI API request payload."""

        # Convert messages to OpenAI format
        api_messages = []
        for msg in messages:
            api_msg = {"role": msg.role, "content": msg.content}

            if msg.name:
                api_msg["name"] = msg.name

            if msg.tool_calls:
                api_msg["tool_calls"] = msg.tool_calls

            if msg.tool_call_id:
                api_msg["tool_call_id"] = msg.tool_call_id

            api_messages.append(api_msg)

        payload = {"model": model, "messages": api_messages}

        # Add optional parameters
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if top_p is not None:
            payload["top_p"] = top_p
        if seed is not None:
            payload["seed"] = seed
        if stop is not None:
            payload["stop"] = stop
        if tools is not None:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice

        # Add any additional kwargs
        payload.update(kwargs)

        return payload

    def parse_response(self, response: Dict[str, Any]) -> ChatResult:
        """Parse OpenAI API response."""

        choices = response.get("choices", [])
        if not choices:
            raise FiberProviderError("No choices in response", provider=self.name)

        choice = choices[0]
        message = choice.get("message", {})

        text = message.get("content", "") or ""
        tool_calls = message.get("tool_calls", [])
        finish_reason = choice.get("finish_reason")

        # Parse usage information
        usage_data = response.get("usage", {})
        usage = Usage(
            prompt=usage_data.get("prompt_tokens", 0),
            completion=usage_data.get("completion_tokens", 0),
            total=usage_data.get("total_tokens", 0),
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
        """Execute OpenAI chat completion request."""

        url = f"{self.base_url}/chat/completions"
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
        """Execute OpenAI streaming chat completion request."""

        url = f"{self.base_url}/chat/completions"
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
        accumulated_tool_calls = {}
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

                # Parse data lines
                if line.startswith("data: "):
                    data_str = line[6:].strip()

                    # Check for end of stream
                    if data_str == "[DONE]":
                        # Emit final usage if available
                        if final_usage:
                            yield StreamEvent.create_usage(final_usage)
                        return

                    try:
                        chunk_data = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    # Process chunk
                    choices = chunk_data.get("choices", [])
                    if not choices:
                        continue

                    choice = choices[0]
                    delta = choice.get("delta", {})

                    # Handle content delta
                    if "content" in delta and delta["content"]:
                        content = delta["content"]
                        accumulated_content += content
                        yield StreamEvent.create_chunk(content)

                    # Handle tool call deltas
                    if "tool_calls" in delta:
                        for tool_call_delta in delta["tool_calls"]:
                            index = tool_call_delta.get("index", 0)

                            # Initialize tool call if not exists
                            if index not in accumulated_tool_calls:
                                accumulated_tool_calls[index] = {
                                    "id": tool_call_delta.get("id", ""),
                                    "type": tool_call_delta.get("type", "function"),
                                    "function": {"name": "", "arguments": ""},
                                }

                            # Update tool call
                            if "id" in tool_call_delta:
                                accumulated_tool_calls[index]["id"] = tool_call_delta["id"]

                            if "function" in tool_call_delta:
                                func_delta = tool_call_delta["function"]
                                if "name" in func_delta:
                                    accumulated_tool_calls[index]["function"]["name"] += func_delta[
                                        "name"
                                    ]
                                if "arguments" in func_delta:
                                    accumulated_tool_calls[index]["function"]["arguments"] += (
                                        func_delta["arguments"]
                                    )

                            # Normalize and emit tool call event with current state
                            current_tool_call = accumulated_tool_calls[index]
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

                    # Handle usage information (usually comes at the end)
                    if "usage" in chunk_data:
                        usage_data = chunk_data["usage"]
                        final_usage = Usage(
                            prompt=usage_data.get("prompt_tokens", 0),
                            completion=usage_data.get("completion_tokens", 0),
                            total=usage_data.get("total_tokens", 0),
                        )

    def supports_feature(self, feature: str) -> bool:
        """Check OpenAI feature support."""
        supported_features = {
            "streaming": True,
            "tools": True,
            "vision": True,
            "json_mode": True,
            "system_messages": True,
            "seed": True,
            "logprobs": True,
        }
        return supported_features.get(feature, False)

    def validate_model(self, model: str) -> bool:
        """Validate OpenAI model name."""
        # OpenAI models typically start with 'gpt-', 'text-', 'code-', or 'o1-'
        valid_prefixes = ["gpt-", "text-", "code-", "o1-", "davinci", "curie", "babbage", "ada"]
        return any(model.startswith(prefix) for prefix in valid_prefixes)

    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens using OpenAI's rough approximation."""
        # OpenAI's approximation: ~4 characters per token for English text
        return max(1, len(text) // 4)

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get OpenAI authentication headers."""
        return {"Authorization": f"Bearer {self.api_key}"}

    def _get_idempotency_headers(self, key: str) -> Dict[str, str]:
        """Get OpenAI idempotency headers."""
        return {"Idempotency-Key": key}
