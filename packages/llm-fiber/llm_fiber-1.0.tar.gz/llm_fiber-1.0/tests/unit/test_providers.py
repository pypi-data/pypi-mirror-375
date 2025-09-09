"""Unit tests for provider adapters."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from llm_fiber.providers import AnthropicAdapter, BaseProvider, GeminiAdapter, OpenAIAdapter
from llm_fiber.types import (
    ChatMessage,
    ChatResult,
    FiberAuthError,
    FiberConnectionError,
    FiberProviderError,
    FiberQuotaError,
    FiberRateLimitError,
    FiberTimeoutError,
    StreamEvent,
    StreamEventType,
    Usage,
)


class MockResponse:
    """Mock HTTP response for testing."""

    def __init__(self, data, status_code=200):
        self.data = data
        self.status_code = status_code

    def json(self):
        return self.data

    async def aread(self):
        return json.dumps(self.data).encode("utf-8")


@pytest.fixture
def openai_adapter():
    """Create OpenAI adapter for testing."""
    return OpenAIAdapter(api_key="test-openai-key", base_url="https://api.openai.com/v1")


@pytest.fixture
def anthropic_adapter():
    """Create Anthropic adapter for testing."""
    return AnthropicAdapter(api_key="test-anthropic-key", base_url="https://api.anthropic.com/v1")


@pytest.fixture
def gemini_adapter():
    """Create Gemini adapter for testing."""
    return GeminiAdapter(
        api_key="test-gemini-key", base_url="https://generativelanguage.googleapis.com/v1"
    )


class TestBaseProvider:
    """Tests for BaseProvider abstract class."""

    def test_base_provider_abstract(self):
        """Test that BaseProvider cannot be instantiated directly."""
        with pytest.raises(TypeError, match="abstract"):
            BaseProvider()

    def test_base_provider_timeouts_default(self):
        """Test base provider uses default timeouts."""

        class TestProvider(BaseProvider):
            def prepare_request(self, model, messages, **kwargs):
                return {"model": model, "messages": [msg.to_dict() for msg in messages]}

            def parse_response(self, response):
                return ChatResult("test", [], "stop", Usage(10, 20), {})

            async def chat(self, model, messages, **kwargs):
                return ChatResult("test", [], "stop", Usage(10, 20), {})

            async def chat_stream(self, model, messages, **kwargs):
                yield StreamEvent.create_chunk("test")

        provider = TestProvider(api_key="test-key")
        assert provider.timeout_seconds == 30.0
        assert provider.api_key == "test-key"

    def test_base_provider_timeouts_custom(self):
        """Test base provider with custom timeouts."""

        class TestProvider(BaseProvider):
            def prepare_request(self, model, messages, **kwargs):
                return {"model": model, "messages": [msg.to_dict() for msg in messages]}

            def parse_response(self, response):
                return ChatResult("test", [], "stop", Usage(10, 20), {})

            async def chat(self, model, messages, **kwargs):
                return ChatResult("test", [], "stop", Usage(10, 20), {})

            async def chat_stream(self, model, messages, **kwargs):
                yield StreamEvent.create_chunk("test")

        provider = TestProvider(api_key="test-key", timeout_seconds=60.0)
        assert provider.timeout_seconds == 60.0

    def test_base_provider_headers(self):
        """Test base provider header generation."""

        class TestProvider(BaseProvider):
            def prepare_request(self, model, messages, **kwargs):
                return {"model": model, "messages": [msg.to_dict() for msg in messages]}

            def parse_response(self, response):
                return ChatResult("test", [], "stop", Usage(10, 20), {})

            async def chat(self, model, messages, **kwargs):
                return ChatResult("test", [], "stop", Usage(10, 20), {})

            async def chat_stream(self, model, messages, **kwargs):
                yield StreamEvent.create_chunk("test")

        provider = TestProvider(api_key="test-key")
        headers = provider.get_headers()

        assert headers["Content-Type"] == "application/json"
        assert headers["User-Agent"] == "llm-fiber/0.1.0"
        assert headers["Authorization"] == "Bearer test-key"


class TestOpenAIAdapter:
    """Tests for OpenAI adapter."""

    def test_openai_adapter_init(self, openai_adapter):
        """Test OpenAI adapter initialization."""
        assert openai_adapter.api_key == "test-openai-key"
        assert openai_adapter.base_url == "https://api.openai.com/v1"
        assert openai_adapter.name == "openai"

    def test_openai_adapter_init_default_base_url(self):
        """Test OpenAI adapter with default base URL."""
        adapter = OpenAIAdapter(api_key="test-key")
        assert adapter.base_url == "https://api.openai.com/v1"

    def test_openai_prepare_request(self, openai_adapter):
        """Test OpenAI request preparation."""
        messages = [
            ChatMessage.system("You are helpful."),
            ChatMessage.user("Hello!"),
            ChatMessage.assistant("Hi there!"),
            ChatMessage.tool("Result: 42", tool_call_id="call_123"),
        ]

        request = openai_adapter.prepare_request(
            model="gpt-4o-mini", messages=messages, temperature=0.7, max_tokens=100
        )

        assert request["model"] == "gpt-4o-mini"
        assert request["temperature"] == 0.7
        assert request["max_tokens"] == 100
        assert len(request["messages"]) == 4

        # Check message formatting
        assert request["messages"][0]["role"] == "system"
        assert request["messages"][0]["content"] == "You are helpful."
        assert request["messages"][3]["tool_call_id"] == "call_123"

    def test_openai_parse_response(self, openai_adapter):
        """Test OpenAI response parsing."""
        response_data = {
            "choices": [
                {
                    "message": {"role": "assistant", "content": "Hello! How can I help you today?"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 25, "completion_tokens": 15, "total_tokens": 40},
        }

        result = openai_adapter.parse_response(response_data)

        assert isinstance(result, ChatResult)
        assert result.text == "Hello! How can I help you today?"
        assert result.finish_reason == "stop"
        assert result.usage.prompt == 25
        assert result.usage.completion == 15
        assert result.usage.total == 40

    def test_openai_parse_response_with_tool_calls(self, openai_adapter):
        """Test OpenAI response parsing with tool calls."""
        response_data = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_abc123",
                                "type": "function",
                                "function": {
                                    "name": "get_weather",
                                    "arguments": '{"location": "San Francisco"}',
                                },
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 100, "completion_tokens": 25, "total_tokens": 125},
        }

        result = openai_adapter.parse_response(response_data)

        assert result.text == ""
        assert result.finish_reason == "tool_calls"
        assert len(result.tool_calls) == 1
        assert result.tool_calls[0]["id"] == "call_abc123"

    @pytest.mark.asyncio
    async def test_openai_chat_success(self, openai_adapter):
        """Test successful OpenAI chat completion."""
        mock_response_data = {
            "choices": [
                {
                    "message": {"role": "assistant", "content": "Hello! How can I help you today?"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 25, "completion_tokens": 15, "total_tokens": 40},
        }

        mock_response = MockResponse(mock_response_data)

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            messages = [ChatMessage.user("Hello")]
            result = await openai_adapter.chat("gpt-4o-mini", messages)

            assert isinstance(result, ChatResult)
            assert result.text == "Hello! How can I help you today?"
            assert result.usage.prompt == 25

    @pytest.mark.asyncio
    async def test_openai_chat_with_tool_calls(self, openai_adapter):
        """Test OpenAI chat completion with tool calls."""
        mock_response_data = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_abc123",
                                "type": "function",
                                "function": {
                                    "name": "get_weather",
                                    "arguments": '{"location": "San Francisco"}',
                                },
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 100, "completion_tokens": 25, "total_tokens": 125},
        }

        mock_response = MockResponse(mock_response_data)

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            messages = [ChatMessage.user("What's the weather?")]
            tools = [{"type": "function", "function": {"name": "get_weather"}}]
            result = await openai_adapter.chat("gpt-4o", messages, tools=tools)

            assert result.finish_reason == "tool_calls"
            assert len(result.tool_calls) == 1

    @pytest.mark.asyncio
    async def test_openai_chat_stream_success(self, openai_adapter):
        """Test OpenAI streaming chat completion."""
        # Mock streaming response
        stream_data = [
            b'data: {"choices": [{"delta": {"content": "Hello"}}]}\n\n',
            b'data: {"choices": [{"delta": {"content": " there"}}]}\n\n',
            b'data: {"choices": [{"delta": {}}], "usage": {"prompt_tokens": 10, '
            b'"completion_tokens": 5, "total_tokens": 15}}\n\n',
            b"data: [DONE]\n\n",
        ]

        async def mock_stream(*args, **kwargs):
            for chunk in stream_data:
                yield chunk

        with patch.object(openai_adapter, "_make_streaming_request", side_effect=mock_stream):
            messages = [ChatMessage.user("Hello")]
            events = []
            async for event in openai_adapter.chat_stream("gpt-4o-mini", messages):
                events.append(event)

            # Should have chunk events and usage event
            chunk_events = [e for e in events if e.type == StreamEventType.CHUNK]
            usage_events = [e for e in events if e.type == StreamEventType.USAGE]

            assert len(chunk_events) == 2
            assert chunk_events[0].delta == "Hello"
            assert chunk_events[1].delta == " there"
            assert len(usage_events) == 1

    def test_openai_validate_model(self, openai_adapter):
        """Test OpenAI model validation."""
        assert openai_adapter.validate_model("gpt-4o")
        assert openai_adapter.validate_model("gpt-3.5-turbo")
        assert openai_adapter.validate_model("text-davinci-003")
        assert openai_adapter.validate_model("o1-preview")
        assert not openai_adapter.validate_model("claude-3")
        assert not openai_adapter.validate_model("random-model")

    def test_openai_supports_feature(self, openai_adapter):
        """Test OpenAI feature support."""
        assert openai_adapter.supports_feature("streaming")
        assert openai_adapter.supports_feature("tools")
        assert openai_adapter.supports_feature("vision")
        assert openai_adapter.supports_feature("json_mode")
        assert openai_adapter.supports_feature("system_messages")
        assert not openai_adapter.supports_feature("unknown_feature")

    @pytest.mark.asyncio
    async def test_openai_error_handling_auth(self, openai_adapter):
        """Test OpenAI authentication error handling."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.aread = AsyncMock(return_value=b'{"error": {"message": "Invalid API key"}}')

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            with pytest.raises(FiberAuthError, match="Authentication failed"):
                await openai_adapter.chat("gpt-4o", [ChatMessage.user("Hello")])

    @pytest.mark.asyncio
    async def test_openai_error_handling_rate_limit(self, openai_adapter):
        """Test OpenAI rate limit error handling."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.aread = AsyncMock(
            return_value=b'{"error": {"message": "Rate limit exceeded"}}'
        )

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            with pytest.raises(FiberRateLimitError, match="Rate limit exceeded"):
                await openai_adapter.chat("gpt-4o", [ChatMessage.user("Hello")])

    @pytest.mark.asyncio
    async def test_openai_error_handling_quota(self, openai_adapter):
        """Test OpenAI quota error handling."""
        mock_response = MagicMock()
        mock_response.status_code = 402
        mock_response.aread = AsyncMock(return_value=b'{"error": {"message": "Quota exceeded"}}')

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            with pytest.raises(FiberQuotaError, match="Quota exceeded"):
                await openai_adapter.chat("gpt-4o", [ChatMessage.user("Hello")])


class TestAnthropicAdapter:
    """Tests for Anthropic adapter."""

    def test_anthropic_adapter_init(self, anthropic_adapter):
        """Test Anthropic adapter initialization."""
        assert anthropic_adapter.api_key == "test-anthropic-key"
        assert anthropic_adapter.base_url == "https://api.anthropic.com/v1"
        assert anthropic_adapter.name == "anthropic"

    def test_anthropic_prepare_request(self, anthropic_adapter):
        """Test Anthropic request preparation."""
        messages = [
            ChatMessage.system("You are helpful."),
            ChatMessage.user("Hello!"),
            ChatMessage.assistant("Hi there!"),
        ]

        request = anthropic_adapter.prepare_request(
            model="claude-3-sonnet-20240229", messages=messages, temperature=0.7, max_tokens=100
        )

        assert request["model"] == "claude-3-sonnet-20240229"
        assert request["temperature"] == 0.7
        assert request["max_tokens"] == 100
        assert "system" in request
        assert len(request["messages"]) == 2  # System message extracted

    def test_anthropic_parse_response(self, anthropic_adapter):
        """Test Anthropic response parsing."""
        response_data = {
            "content": [{"type": "text", "text": "Hello! How can I help you today?"}],
            "stop_reason": "end_turn",
            "usage": {"input_tokens": 25, "output_tokens": 15},
        }

        result = anthropic_adapter.parse_response(response_data)

        assert isinstance(result, ChatResult)
        assert result.text == "Hello! How can I help you today?"
        assert result.finish_reason == "end_turn"
        assert result.usage.prompt == 25
        assert result.usage.completion == 15

    @pytest.mark.asyncio
    async def test_anthropic_chat_success(self, anthropic_adapter):
        """Test successful Anthropic chat completion."""
        mock_response_data = {
            "content": [{"type": "text", "text": "Hello! How can I help you today?"}],
            "stop_reason": "end_turn",
            "usage": {"input_tokens": 25, "output_tokens": 15},
        }

        mock_response = MockResponse(mock_response_data)

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            messages = [ChatMessage.user("Hello")]
            result = await anthropic_adapter.chat("claude-3-sonnet-20240229", messages)

            assert isinstance(result, ChatResult)
            assert result.text == "Hello! How can I help you today?"
            assert result.usage.prompt == 25


class TestGeminiAdapter:
    """Tests for Gemini adapter."""

    def test_gemini_adapter_init(self, gemini_adapter):
        """Test Gemini adapter initialization."""
        assert gemini_adapter.api_key == "test-gemini-key"
        assert gemini_adapter.base_url == "https://generativelanguage.googleapis.com/v1"
        assert gemini_adapter.name == "gemini"

    def test_gemini_prepare_request(self, gemini_adapter):
        """Test Gemini request preparation."""
        messages = [ChatMessage.system("You are helpful."), ChatMessage.user("Hello!")]

        request = gemini_adapter.prepare_request(
            model="gemini-pro", messages=messages, temperature=0.7, max_tokens=100
        )

        assert "contents" in request
        assert "generationConfig" in request
        assert request["generationConfig"]["temperature"] == 0.7
        assert request["generationConfig"]["maxOutputTokens"] == 100

    def test_gemini_parse_response(self, gemini_adapter):
        """Test Gemini response parsing."""
        response_data = {
            "candidates": [
                {
                    "content": {"parts": [{"text": "Hello! How can I help you today?"}]},
                    "finishReason": "STOP",
                }
            ],
            "usageMetadata": {
                "promptTokenCount": 25,
                "candidatesTokenCount": 15,
                "totalTokenCount": 40,
            },
        }

        result = gemini_adapter.parse_response(response_data)

        assert isinstance(result, ChatResult)
        assert result.text == "Hello! How can I help you today?"
        assert result.finish_reason == "stop"  # Gemini normalizes to lowercase
        assert result.usage.prompt == 25
        assert result.usage.completion == 15

    @pytest.mark.asyncio
    async def test_gemini_chat_success(self, gemini_adapter):
        """Test successful Gemini chat completion."""
        mock_response_data = {
            "candidates": [
                {
                    "content": {"parts": [{"text": "Hello! How can I help you today?"}]},
                    "finishReason": "STOP",
                }
            ],
            "usageMetadata": {
                "promptTokenCount": 25,
                "candidatesTokenCount": 15,
                "totalTokenCount": 40,
            },
        }

        mock_response = MockResponse(mock_response_data)

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            messages = [ChatMessage.user("Hello")]
            result = await gemini_adapter.chat("gemini-pro", messages)

            assert isinstance(result, ChatResult)
            assert result.text == "Hello! How can I help you today?"
            assert result.usage.prompt == 25


class TestProviderErrorHandling:
    """Tests for provider error handling."""

    @pytest.mark.asyncio
    async def test_connection_error_handling(self, openai_adapter):
        """Test connection error handling."""
        with patch("httpx.AsyncClient.post", side_effect=ConnectionError("Connection failed")):
            with pytest.raises(FiberConnectionError, match="Connection failed"):
                await openai_adapter.chat("gpt-4o", [ChatMessage.user("Hello")])

    @pytest.mark.asyncio
    async def test_timeout_error_handling(self, openai_adapter):
        """Test timeout error handling."""
        with patch("httpx.AsyncClient.post", side_effect=asyncio.TimeoutError("Request timed out")):
            with pytest.raises(FiberTimeoutError, match="Request timed out"):
                await openai_adapter.chat("gpt-4o", [ChatMessage.user("Hello")])

    @pytest.mark.asyncio
    async def test_generic_provider_error_handling(self, openai_adapter):
        """Test generic provider error handling."""
        with patch("httpx.AsyncClient.post", side_effect=RuntimeError("Unexpected error")):
            with pytest.raises(FiberProviderError, match="Request failed"):
                await openai_adapter.chat("gpt-4o", [ChatMessage.user("Hello")])

    @pytest.mark.asyncio
    async def test_malformed_response_error(self, openai_adapter):
        """Test handling of malformed responses."""
        mock_response_data = {"invalid": "response"}  # Missing required fields

        mock_response = MockResponse(mock_response_data)

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            with pytest.raises(FiberProviderError, match="No choices in response"):
                await openai_adapter.chat("gpt-4o", [ChatMessage.user("Hello")])


class TestProviderIntegration:
    """Integration tests for provider consistency."""

    def test_provider_message_consistency(self, openai_adapter, anthropic_adapter, gemini_adapter):
        """Test that all providers handle messages consistently."""
        messages = [
            ChatMessage.system("You are helpful."),
            ChatMessage.user("Hello!"),
            ChatMessage.assistant("Hi there!"),
        ]

        # All providers should be able to prepare requests
        openai_request = openai_adapter.prepare_request("gpt-4o", messages)
        anthropic_request = anthropic_adapter.prepare_request("claude-3-sonnet-20240229", messages)
        gemini_request = gemini_adapter.prepare_request("gemini-pro", messages)

        # Basic structure checks
        assert "model" in openai_request or "model" in str(openai_request)
        assert "model" in anthropic_request or "messages" in anthropic_request
        assert "contents" in gemini_request or "generationConfig" in gemini_request

    def test_provider_feature_support(self, openai_adapter, anthropic_adapter, gemini_adapter):
        """Test that providers correctly report feature support."""
        # All providers should support basic features
        for provider in [openai_adapter, anthropic_adapter, gemini_adapter]:
            assert provider.supports_feature("streaming")
            assert provider.supports_feature("system_messages")

    def test_provider_headers(self, openai_adapter, anthropic_adapter, gemini_adapter):
        """Test that all providers generate appropriate headers."""
        # OpenAI uses Authorization header
        openai_headers = openai_adapter.get_headers()
        assert "Content-Type" in openai_headers
        assert "Authorization" in openai_headers

        # Anthropic uses x-api-key header
        anthropic_headers = anthropic_adapter.get_headers()
        assert "Content-Type" in anthropic_headers
        # Anthropic may have different auth header format

        # Gemini uses query parameter auth, not headers
        gemini_headers = gemini_adapter.get_headers()
        assert "Content-Type" in gemini_headers

    def test_provider_model_validation(self, openai_adapter, anthropic_adapter, gemini_adapter):
        """Test provider model validation."""
        # OpenAI models
        assert openai_adapter.validate_model("gpt-4o")
        assert not anthropic_adapter.validate_model("gpt-4o")
        assert not gemini_adapter.validate_model("gpt-4o")

        # Anthropic models
        assert anthropic_adapter.validate_model("claude-3-sonnet-20240229")
        assert not openai_adapter.validate_model("claude-3-sonnet-20240229")
        assert not gemini_adapter.validate_model("claude-3-sonnet-20240229")

        # Gemini models
        assert gemini_adapter.validate_model("gemini-pro")
        assert not openai_adapter.validate_model("gemini-pro")
        assert not anthropic_adapter.validate_model("gemini-pro")
