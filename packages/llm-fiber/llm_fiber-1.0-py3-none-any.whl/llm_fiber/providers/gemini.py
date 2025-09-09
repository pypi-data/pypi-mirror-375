"""Google Gemini provider adapter for llm-fiber."""

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


class GeminiAdapter(BaseProvider):
    """Google Gemini API adapter."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_seconds: float = 30.0,
    ):
        if base_url is None:
            base_url = "https://generativelanguage.googleapis.com"

        super().__init__(api_key, base_url, timeout_seconds)
        self.name = "gemini"

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
        """Prepare Gemini API request payload."""

        # Convert messages to Gemini format
        contents = []
        system_instruction = None

        for msg in messages:
            if msg.role == "system":
                # Gemini uses systemInstruction instead of system messages in contents
                system_instruction = {"parts": [{"text": msg.content}]}
                continue

            # Map roles
            role = "user" if msg.role in ["user", "human"] else "model"
            if msg.role == "assistant":
                role = "model"

            # Handle different content types
            parts = []

            if msg.content:
                parts.append({"text": msg.content})

            # Handle tool calls
            if msg.tool_calls:
                for tool_call in msg.tool_calls:
                    function_call = tool_call.get("function", {})
                    parts.append(
                        {
                            "functionCall": {
                                "name": function_call.get("name", ""),
                                "args": json.loads(function_call.get("arguments", "{}")),
                            }
                        }
                    )

            # Handle tool responses
            if msg.tool_call_id and msg.role == "tool":
                # In Gemini, tool responses are part of the model's response
                parts.append(
                    {
                        "functionResponse": {
                            "name": msg.name or "unknown_function",
                            "response": {"content": msg.content},
                        }
                    }
                )
                role = "model"  # Tool responses are considered model messages

            if parts:
                contents.append({"role": role, "parts": parts})

        # Build payload
        payload = {"contents": contents}

        # Add system instruction if present
        if system_instruction:
            payload["systemInstruction"] = system_instruction

        # Add generation config
        generation_config = {}
        if temperature is not None:
            generation_config["temperature"] = temperature
        if max_tokens is not None:
            generation_config["maxOutputTokens"] = max_tokens
        if top_p is not None:
            generation_config["topP"] = top_p
        if stop is not None:
            generation_config["stopSequences"] = stop

        if generation_config:
            payload["generationConfig"] = generation_config

        # Add tools if present
        if tools is not None:
            gemini_tools = []
            function_declarations = []

            for tool in tools:
                function_info = tool.get("function", {})
                function_declaration = {
                    "name": function_info.get("name", ""),
                    "description": function_info.get("description", ""),
                    "parameters": function_info.get("parameters", {}),
                }
                function_declarations.append(function_declaration)

            if function_declarations:
                gemini_tools.append({"functionDeclarations": function_declarations})
                payload["tools"] = gemini_tools

        # Add any additional kwargs
        payload.update(kwargs)

        return payload

    def parse_response(self, response: Dict[str, Any]) -> ChatResult:
        """Parse Gemini API response."""

        candidates = response.get("candidates", [])
        if not candidates:
            raise FiberProviderError("No candidates in response", provider=self.name)

        candidate = candidates[0]
        content = candidate.get("content", {})
        parts = content.get("parts", [])

        # Extract text and tool calls
        text_parts = []
        tool_calls = []

        for part in parts:
            if "text" in part:
                text_parts.append(part["text"])
            elif "functionCall" in part:
                # Convert to OpenAI-compatible format
                function_call = part["functionCall"]
                tool_call = {
                    "id": f"call_{len(tool_calls)}",  # Gemini doesn't provide IDs
                    "type": "function",
                    "function": {
                        "name": function_call.get("name", ""),
                        "arguments": json.dumps(function_call.get("args", {})),
                    },
                }
                tool_calls.append(tool_call)

        text = "".join(text_parts)
        finish_reason = candidate.get("finishReason", "").lower()

        # Parse usage information
        usage_metadata = response.get("usageMetadata", {})
        usage = Usage(
            prompt=usage_metadata.get("promptTokenCount", 0),
            completion=usage_metadata.get("candidatesTokenCount", 0),
            total=usage_metadata.get("totalTokenCount", 0),
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
        """Execute Gemini chat completion request."""

        # Clean up model name (remove provider prefix if present)
        clean_model = model.replace("gemini/", "").replace("google/", "")
        url = f"{self.base_url}/v1beta/models/{clean_model}:generateContent"

        # Add API key to URL for Gemini
        if self.api_key:
            url += f"?key={self.api_key}"

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
        """Execute Gemini streaming chat completion request."""

        # Clean up model name
        clean_model = model.replace("gemini/", "").replace("google/", "")
        url = f"{self.base_url}/v1beta/models/{clean_model}:streamGenerateContent"

        # Add API key to URL
        if self.api_key:
            url += f"?key={self.api_key}"

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
            # Parse response chunks (Gemini streams JSON objects, not SSE)
            chunk_text = chunk.decode("utf-8", errors="ignore").strip()
            if not chunk_text:
                continue

            # Handle potential multiple JSON objects in one chunk
            for line in chunk_text.split("\n"):
                line = line.strip()
                if not line:
                    continue

                try:
                    chunk_data = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Process candidates
                candidates = chunk_data.get("candidates", [])
                if not candidates:
                    continue

                candidate = candidates[0]
                content = candidate.get("content", {})
                parts = content.get("parts", [])

                # Process each part
                for part in parts:
                    if "text" in part:
                        text = part["text"]
                        if text:
                            accumulated_content += text
                            yield StreamEvent.chunk(text)

                    elif "functionCall" in part:
                        # Handle function calls
                        function_call = part["functionCall"]
                        tool_call = {
                            "id": f"call_{len(accumulated_tool_calls)}",
                            "type": "function",
                            "function": {
                                "name": function_call.get("name", ""),
                                "arguments": json.dumps(function_call.get("args", {})),
                            },
                        }
                        accumulated_tool_calls[len(accumulated_tool_calls)] = tool_call
                        # Normalize and emit tool call event
                        if validate_tool_call_format(tool_call, "openai"):
                            try:
                                normalized = normalize_tool_call(tool_call, "openai")
                                yield StreamEvent.create_tool_call(normalized.to_openai_format())
                            except Exception:
                                # Fallback to original format
                                yield StreamEvent.create_tool_call(tool_call)
                        else:
                            # Emit original format for invalid tool calls
                            yield StreamEvent.create_tool_call(tool_call)

                # Handle usage information
                usage_metadata = chunk_data.get("usageMetadata", {})
                if usage_metadata:
                    final_usage = Usage(
                        prompt=usage_metadata.get("promptTokenCount", 0),
                        completion=usage_metadata.get("candidatesTokenCount", 0),
                        total=usage_metadata.get("totalTokenCount", 0),
                    )

                # Check if streaming is complete
                finish_reason = candidate.get("finishReason")
                if finish_reason:
                    if final_usage:
                        yield StreamEvent.create_usage(final_usage)
                    return

    def supports_feature(self, feature: str) -> bool:
        """Check Gemini feature support."""
        supported_features = {
            "streaming": True,
            "tools": True,  # Function calling supported
            "vision": True,  # Gemini Pro Vision supports images
            "json_mode": True,  # Via response_mime_type
            "system_messages": True,  # Via systemInstruction
            "seed": False,  # Not supported by Gemini
            "logprobs": False,  # Not supported
        }
        return supported_features.get(feature, False)

    def validate_model(self, model: str) -> bool:
        """Validate Gemini model name."""
        # Clean up model name for validation
        clean_model = model.replace("gemini/", "").replace("google/", "")

        # Gemini models typically start with 'gemini-'
        valid_prefixes = ["gemini-", "models/gemini-"]
        valid_models = [
            "gemini-pro",
            "gemini-pro-vision",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.0-pro",
        ]

        return (
            any(clean_model.startswith(prefix) for prefix in valid_prefixes)
            or clean_model in valid_models
        )

    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens using Gemini's rough approximation."""
        # Similar to other providers, ~4 characters per token
        return max(1, len(text) // 4)

    def get_headers(self, idempotency_key: Optional[str] = None) -> Dict[str, str]:
        """Get HTTP headers for Gemini requests."""
        headers = {"Content-Type": "application/json", "User-Agent": "llm-fiber/0.2.0"}

        # Gemini doesn't use Authorization header, API key is in URL
        # But we can add idempotency headers if needed
        if idempotency_key:
            headers.update(self._get_idempotency_headers(idempotency_key))

        return headers

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get Gemini authentication headers."""
        # Gemini uses API key in URL parameter, not headers
        return {}

    def _get_idempotency_headers(self, key: str) -> Dict[str, str]:
        """Get Gemini idempotency headers."""
        # Gemini doesn't have standard idempotency headers, but we can add custom ones
        return {"X-Request-Id": key}
