"""Unit tests for Fiber core client functionality."""

import os
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from llm_fiber import (
    BoundFiber,
    ChatMessage,
    ChatResult,
    Fiber,
    FiberAuthError,
    FiberConnectionError,
    FiberProviderError,
    FiberRateLimitError,
    FiberTimeoutError,
    ModelRegistry,
    RetryPolicy,
    StreamEvent,
    StreamEventType,
    Timeouts,
    Usage,
)


class TestFiberInitialization:
    """Test Fiber client initialization."""

    def test_fiber_init_with_default_model(self):
        """Test Fiber initialization with default model."""
        fiber = Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=False
        )

        assert fiber.default_model == "gpt-4o-mini"
        assert fiber._api_keys["openai"] == "test-key"
        assert fiber.enable_observability is False

    def test_fiber_init_minimal(self):
        """Test Fiber initialization with minimal parameters."""
        fiber = Fiber(api_keys={"openai": "test-key"})

        assert fiber._api_keys["openai"] == "test-key"
        assert fiber.default_model is not None  # Should auto-select
        assert fiber.enable_observability is True  # Default

    def test_fiber_init_with_all_options(self):
        """Test Fiber initialization with all options."""
        timeouts = Timeouts(connect=10.0, read=60.0, total=120.0)
        retry_policy = RetryPolicy(max_attempts=5, base_delay=2.0)

        fiber = Fiber(
            default_model="claude-3-haiku",
            api_keys={"anthropic": "test-anthropic", "openai": "test-openai"},
            timeouts=timeouts,
            retry_policy=retry_policy,
            enable_observability=True,
        )

        assert fiber.default_model == "claude-3-haiku"
        assert len(fiber._api_keys) == 2
        assert fiber.timeouts == timeouts
        assert fiber.retry_policy == retry_policy

    def test_fiber_init_invalid_api_keys(self):
        """Test Fiber initialization with invalid API keys."""
        with pytest.raises(ValueError, match="At least one API key must be provided"):
            Fiber(api_keys={})

        with pytest.raises(ValueError):
            Fiber(api_keys={"invalid_provider": "test-key"})

    def test_fiber_init_invalid_timeouts(self):
        """Test Fiber initialization with invalid timeouts."""
        with pytest.raises(ValueError):
            Fiber(api_keys={"openai": "test-key"}, timeouts=Timeouts(connect=-1.0))

    @patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "env-openai-key",
            "ANTHROPIC_API_KEY": "env-anthropic-key",
            "GEMINI_API_KEY": "env-gemini-key",
        },
    )
    def test_fiber_from_env(self):
        """Test Fiber.from_env initialization."""
        fiber = Fiber.from_env(enable_observability=False)

        assert "openai" in fiber._api_keys
        assert "anthropic" in fiber._api_keys
        assert "gemini" in fiber._api_keys
        assert fiber._api_keys["openai"] == "env-openai-key"

    @patch.dict(os.environ, {"OPENAI_API_KEY": "env-openai-key"})
    def test_fiber_from_env_partial(self):
        """Test Fiber.from_env with partial environment."""
        fiber = Fiber.from_env(enable_observability=False)

        assert "openai" in fiber._api_keys
        assert "anthropic" not in fiber._api_keys
        assert fiber.default_model is not None

    @patch.dict(
        os.environ, {"OPENAI_API_KEY": "env-openai-key", "ANTHROPIC_API_KEY": "env-anthropic-key"}
    )
    def test_fiber_from_env_with_preference(self):
        """Test Fiber.from_env with provider preference."""
        fiber = Fiber.from_env(prefer=["anthropic", "openai"], enable_observability=False)

        # Should have both keys
        assert "openai" in fiber._api_keys
        assert "anthropic" in fiber._api_keys

        # Default model should reflect preference (anthropic preferred)
        # This is implementation-dependent, but should be from preferred provider
        assert fiber.default_model is not None

    @patch.dict(os.environ, {}, clear=True)
    def test_fiber_from_env_no_keys(self):
        """Test Fiber.from_env with no environment keys."""
        with pytest.raises(ValueError, match="No API keys found"):
            Fiber.from_env()


class TestFiberBasicChat:
    """Test Fiber basic chat functionality."""

    @pytest.fixture
    def fiber(self):
        """Create basic Fiber instance."""
        return Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=False
        )

    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI API response."""
        return {
            "id": "chatcmpl-test123",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "gpt-4o-mini",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Hello! I'm here to help you with any questions or tasks.",
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 25, "completion_tokens": 15, "total_tokens": 40},
        }

    @pytest.mark.asyncio
    async def test_chat_basic_success(self, fiber, mock_openai_response):
        """Test basic successful chat completion."""
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value.json.return_value = mock_openai_response
            mock_post.return_value.status_code = 200
            mock_post.return_value.raise_for_status.return_value = None

            messages = [ChatMessage.user("Hello, how are you?")]
            result = await fiber.chat(messages)

            assert isinstance(result, ChatResult)
            assert result.text == "Hello! I'm here to help you with any questions or tasks."
            assert result.finish_reason == "stop"
            assert result.usage.prompt == 25
            assert result.usage.completion == 15
            assert result.usage.total == 40
            assert result.raw["id"] == "chatcmpl-test123"

            # Verify API call
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[1]["url"].endswith("/chat/completions")
            request_data = call_args[1]["json"]
            assert request_data["model"] == "gpt-4o-mini"
            assert len(request_data["messages"]) == 1
            assert request_data["messages"][0]["role"] == "user"

    @pytest.mark.asyncio
    async def test_chat_with_model_override(self, fiber, mock_openai_response):
        """Test chat with model override."""
        mock_openai_response["model"] = "gpt-4o"

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value.json.return_value = mock_openai_response
            mock_post.return_value.status_code = 200
            mock_post.return_value.raise_for_status.return_value = None

            messages = [ChatMessage.user("Test")]
            await fiber.chat(messages, model="gpt-4o")

            call_args = mock_post.call_args
            request_data = call_args[1]["json"]
            assert request_data["model"] == "gpt-4o"

    @pytest.mark.asyncio
    async def test_chat_with_parameters(self, fiber, mock_openai_response):
        """Test chat with additional parameters."""
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value.json.return_value = mock_openai_response
            mock_post.return_value.status_code = 200
            mock_post.return_value.raise_for_status.return_value = None

            messages = [ChatMessage.user("Test")]
            await fiber.chat(messages, temperature=0.7, max_tokens=150, top_p=0.9)

            call_args = mock_post.call_args
            request_data = call_args[1]["json"]
            assert request_data["temperature"] == 0.7
            assert request_data["max_tokens"] == 150
            assert request_data["top_p"] == 0.9

    @pytest.mark.asyncio
    async def test_chat_message_normalization(self, fiber, mock_openai_response):
        """Test chat with various message input formats."""
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value.json.return_value = mock_openai_response
            mock_post.return_value.status_code = 200
            mock_post.return_value.raise_for_status.return_value = None

            # Test string input
            await fiber.chat("Hello there!")

            call_args = mock_post.call_args
            request_data = call_args[1]["json"]
            assert len(request_data["messages"]) == 1
            assert request_data["messages"][0]["role"] == "user"
            assert request_data["messages"][0]["content"] == "Hello there!"

            # Test tuple input
            mock_post.reset_mock()
            await fiber.chat([("system", "You are helpful"), ("user", "Hi")])

            call_args = mock_post.call_args
            request_data = call_args[1]["json"]
            assert len(request_data["messages"]) == 2
            assert request_data["messages"][0]["role"] == "system"
            assert request_data["messages"][1]["role"] == "user"

    @pytest.mark.asyncio
    async def test_ask_helper_method(self, fiber, mock_openai_response):
        """Test the ask helper method."""
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value.json.return_value = mock_openai_response
            mock_post.return_value.status_code = 200
            mock_post.return_value.raise_for_status.return_value = None

            result = await fiber.ask("What is Python?", temperature=0.5)

            assert isinstance(result, str)

            call_args = mock_post.call_args
            request_data = call_args[1]["json"]
            assert len(request_data["messages"]) == 1
            assert request_data["messages"][0]["content"] == "What is Python?"
            assert request_data["temperature"] == 0.5


class TestFiberStreaming:
    """Test Fiber streaming functionality."""

    @pytest.fixture
    def fiber(self):
        """Create basic Fiber instance."""
        return Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=False
        )

    @pytest.fixture
    def mock_stream_chunks(self):
        """Mock streaming response chunks."""
        return [
            'data: {"id":"chatcmpl-stream","object":"chat.completion.chunk",'
            '"created":1234567890,"model":"gpt-4o-mini",'
            '"choices":[{"index":0,"delta":{"role":"assistant","content":""},"finish_reason":null}]}',
            'data: {"id":"chatcmpl-stream","object":"chat.completion.chunk",'
            '"created":1234567890,"model":"gpt-4o-mini",'
            '"choices":[{"index":0,"delta":{"content":"Hello"},"finish_reason":null}]}',
            'data: {"id":"chatcmpl-stream","object":"chat.completion.chunk",'
            '"created":1234567890,"model":"gpt-4o-mini",'
            '"choices":[{"index":0,"delta":{"content":" there"},"finish_reason":null}]}',
            'data: {"id":"chatcmpl-stream","object":"chat.completion.chunk",'
            '"created":1234567890,"model":"gpt-4o-mini",'
            '"choices":[{"index":0,"delta":{"content":"!"},"finish_reason":null}]}',
            'data: {"id":"chatcmpl-stream","object":"chat.completion.chunk",'
            '"created":1234567890,"model":"gpt-4o-mini",'
            '"choices":[{"index":0,"delta":{},"finish_reason":"stop"}],'
            '"usage":{"prompt_tokens":20,"completion_tokens":10,"total_tokens":30}}',
            "data: [DONE]",
        ]

    @pytest.mark.asyncio
    async def test_chat_stream_basic(self, fiber, mock_stream_chunks):
        """Test basic streaming functionality."""

        async def mock_stream_generator(*args, **kwargs):
            # Yield the expected events directly
            yield StreamEvent.create_chunk("Hello")
            yield StreamEvent.create_chunk(" there")
            yield StreamEvent.create_chunk("!")
            yield StreamEvent.create_usage(Usage(prompt=20, completion=10, total=30))

        # Mock at the provider level instead of HTTP level
        from llm_fiber.providers.openai import OpenAIAdapter

        with patch.object(OpenAIAdapter, "chat_stream", side_effect=mock_stream_generator):
            messages = [ChatMessage.user("Hello")]
            events = []

            async for event in fiber.chat_stream(messages):
                events.append(event)

            # Verify events
            chunk_events = [e for e in events if e.type == StreamEventType.CHUNK]
            usage_events = [e for e in events if e.type == StreamEventType.USAGE]

            assert len(chunk_events) == 3  # "Hello", " there", "!"
            assert len(usage_events) == 1

            # Verify chunk content
            full_text = "".join(e.delta for e in chunk_events)
            assert full_text == "Hello there!"

            # Verify usage
            assert usage_events[0].usage.prompt == 20
            assert usage_events[0].usage.completion == 10
            assert usage_events[0].usage.total == 30

    @pytest.mark.asyncio
    async def test_chat_stream_with_parameters(self, fiber, mock_stream_chunks):
        """Test streaming with additional parameters."""
        mock_stream_response = MagicMock()
        mock_stream_response.aiter_lines.return_value = mock_stream_chunks
        mock_stream_response.status_code = 200
        mock_stream_response.raise_for_status.return_value = None

        with patch("httpx.AsyncClient.stream") as mock_stream:
            mock_stream.return_value.__aenter__.return_value = mock_stream_response

            messages = [ChatMessage.user("Stream test")]
            events = []

            async for event in fiber.chat_stream(
                messages, model="gpt-4o", temperature=0.8, max_tokens=200
            ):
                events.append(event)

            # Verify API call parameters
            call_args = mock_stream.call_args
            assert call_args[1]["url"].endswith("/chat/completions")
            request_data = call_args[1]["json"]
            assert request_data["model"] == "gpt-4o"
            assert request_data["temperature"] == 0.8
            assert request_data["max_tokens"] == 200
            assert request_data["stream"] is True

    @pytest.mark.asyncio
    async def test_chat_stream_error_handling(self, fiber):
        """Test streaming error handling."""
        mock_stream_response = MagicMock()
        mock_stream_response.status_code = 500
        mock_stream_response.raise_for_status.side_effect = Exception("Server error")

        with patch("httpx.AsyncClient.stream") as mock_stream:
            mock_stream.return_value.__aenter__.return_value = mock_stream_response

            with pytest.raises(FiberProviderError):
                messages = [ChatMessage.user("Error test")]
                async for event in fiber.chat_stream(messages):
                    pass


class TestFiberContextBinding:
    """Test Fiber context binding functionality."""

    @pytest.fixture
    def fiber(self):
        """Create basic Fiber instance."""
        return Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=False
        )

    def test_bind_creates_bound_fiber(self, fiber):
        """Test that bind creates a BoundFiber instance."""
        bound = fiber.bind(temperature=0.7, max_tokens=100)

        assert isinstance(bound, BoundFiber)
        assert bound._context["temperature"] == 0.7
        assert bound._context["max_tokens"] == 100

    def test_bind_preserves_original_fiber(self, fiber):
        """Test that binding doesn't modify original fiber."""
        original_model = fiber.default_model
        bound = fiber.bind(model="gpt-4o", temperature=0.5)

        assert fiber.default_model == original_model
        assert bound._context["model"] == "gpt-4o"

    def test_chained_binding(self, fiber):
        """Test chained context binding."""
        bound1 = fiber.bind(temperature=0.7)
        bound2 = bound1.bind(max_tokens=150, temperature=0.8)  # Override temperature

        assert bound1._context["temperature"] == 0.7
        assert "max_tokens" not in bound1._context

        assert bound2._context["temperature"] == 0.8  # Overridden
        assert bound2._context["max_tokens"] == 150

    @pytest.mark.asyncio
    async def test_bound_fiber_chat(self, fiber):
        """Test chat functionality of bound fiber."""
        mock_response = {
            "id": "bound-test",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "gpt-4o-mini",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "Bound response"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        }

        bound = fiber.bind(temperature=0.3, max_tokens=50)

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.status_code = 200
            mock_post.return_value.raise_for_status.return_value = None

            messages = [ChatMessage.user("Test bound")]
            result = await bound.chat(messages)

            assert result.text == "Bound response"

            # Verify context was applied
            call_args = mock_post.call_args
            request_data = call_args[1]["json"]
            assert request_data["temperature"] == 0.3
            assert request_data["max_tokens"] == 50

    @pytest.mark.asyncio
    async def test_bound_fiber_with_override(self, fiber):
        """Test bound fiber with parameter override."""
        mock_response = {
            "id": "override-test",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "gpt-4o-mini",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "Override response"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        }

        bound = fiber.bind(temperature=0.5, max_tokens=100)

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.status_code = 200
            mock_post.return_value.raise_for_status.return_value = None

            # Override temperature in call
            await bound.chat([ChatMessage.user("Test")], temperature=0.9)

            call_args = mock_post.call_args
            request_data = call_args[1]["json"]
            assert request_data["temperature"] == 0.9  # Overridden
            assert request_data["max_tokens"] == 100  # From context

    def test_bound_fiber_sync_property(self, fiber):
        """Test that bound fiber has sync property."""
        bound = fiber.bind(temperature=0.7)
        sync_bound = bound.sync

        assert sync_bound is not None
        # Verify it's a sync wrapper (exact type depends on implementation)


class TestFiberProviderRouting:
    """Test Fiber provider routing functionality."""

    @pytest.fixture
    def multi_provider_fiber(self):
        """Create Fiber with multiple providers."""
        return Fiber(
            api_keys={
                "openai": "test-openai-key",
                "anthropic": "test-anthropic-key",
                "gemini": "test-gemini-key",
            },
            enable_observability=False,
        )

    @pytest.mark.asyncio
    async def test_openai_routing(self, multi_provider_fiber):
        """Test routing to OpenAI provider."""
        mock_response = {
            "id": "openai-test",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "gpt-4o",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "OpenAI response"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        }

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.status_code = 200
            mock_post.return_value.raise_for_status.return_value = None

            result = await multi_provider_fiber.chat(
                [ChatMessage.user("Test OpenAI")], model="gpt-4o"
            )

            assert result.text == "OpenAI response"

            # Verify OpenAI endpoint was called
            call_args = mock_post.call_args
            assert "openai.com" in call_args[1]["url"]

    @pytest.mark.asyncio
    async def test_anthropic_routing(self, multi_provider_fiber):
        """Test routing to Anthropic provider."""
        mock_response = {
            "id": "anthropic-test",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": "Anthropic response"}],
            "model": "claude-3-haiku",
            "stop_reason": "end_turn",
            "usage": {"input_tokens": 10, "output_tokens": 5},
        }

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.status_code = 200
            mock_post.return_value.raise_for_status.return_value = None

            result = await multi_provider_fiber.chat(
                [ChatMessage.user("Test Anthropic")], model="claude-3-haiku"
            )

            assert result.text == "Anthropic response"

            # Verify Anthropic endpoint was called
            call_args = mock_post.call_args
            assert "anthropic.com" in call_args[1]["url"]

    @pytest.mark.asyncio
    async def test_gemini_routing(self, multi_provider_fiber):
        """Test routing to Gemini provider."""
        mock_response = {
            "candidates": [
                {
                    "content": {"parts": [{"text": "Gemini response"}], "role": "model"},
                    "finishReason": "STOP",
                }
            ],
            "usageMetadata": {
                "promptTokenCount": 10,
                "candidatesTokenCount": 5,
                "totalTokenCount": 15,
            },
        }

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.status_code = 200
            mock_post.return_value.raise_for_status.return_value = None

            result = await multi_provider_fiber.chat(
                [ChatMessage.user("Test Gemini")], model="gemini-1.5-pro"
            )

            assert result.text == "Gemini response"

            # Verify Gemini endpoint was called
            call_args = mock_post.call_args
            assert "googleapis.com" in call_args[1]["url"]

    def test_model_registry_integration(self, multi_provider_fiber):
        """Test model registry integration."""
        # Access the model registry
        registry = multi_provider_fiber.model_registry

        assert isinstance(registry, ModelRegistry)

        # Test provider resolution
        assert registry.resolve_provider("gpt-4o") == "openai"
        assert registry.resolve_provider("claude-3-sonnet") == "anthropic"
        assert registry.resolve_provider("gemini-1.5-pro") == "gemini"

    def test_unknown_model_handling(self, multi_provider_fiber):
        """Test handling of unknown models."""
        registry = multi_provider_fiber.model_registry

        # Unknown model should still resolve to a provider (fallback behavior)
        provider = registry.resolve_provider("unknown-model-12345")
        assert provider in ["openai", "anthropic", "gemini"]


class TestFiberErrorHandling:
    """Test Fiber error handling."""

    @pytest.fixture
    def fiber(self):
        """Create basic Fiber instance."""
        return Fiber(
            default_model="gpt-4o-mini",
            api_keys={"openai": "test-key"},
            retry_policy=RetryPolicy(max_attempts=2, base_delay=0.01),
            enable_observability=False,
        )

    @pytest.mark.asyncio
    async def test_auth_error_handling(self, fiber):
        """Test authentication error handling."""
        mock_response = AsyncMock()
        mock_response.status_code = 401
        mock_response.aread = AsyncMock(
            return_value=b'{"error": {"message": "Invalid API key", '
            b'"type": "invalid_request_error"}}'
        )

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            with pytest.raises(FiberAuthError) as exc_info:
                await fiber.chat([ChatMessage.user("Test auth error")])

            assert "Invalid API key" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_rate_limit_error_handling(self, fiber):
        """Test rate limit error handling."""
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value.status_code = 429
            mock_post.return_value.json.return_value = {
                "error": {"message": "Rate limit exceeded", "type": "rate_limit_error"}
            }
            mock_post.return_value.headers = {"retry-after": "60"}
            mock_post.return_value.raise_for_status.side_effect = Exception("Rate limit")

            with pytest.raises(FiberRateLimitError) as exc_info:
                await fiber.chat([ChatMessage.user("Test rate limit")])

            assert hasattr(exc_info.value, "retry_after")

    @pytest.mark.asyncio
    async def test_connection_error_handling(self, fiber):
        """Test connection error handling."""
        import httpx

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.side_effect = httpx.ConnectError("Connection failed")

            with pytest.raises(FiberConnectionError):
                await fiber.chat([ChatMessage.user("Test connection error")])

    @pytest.mark.asyncio
    async def test_timeout_error_handling(self, fiber):
        """Test timeout error handling."""
        import httpx

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.side_effect = httpx.TimeoutException("Request timed out")

            with pytest.raises(FiberTimeoutError):
                await fiber.chat([ChatMessage.user("Test timeout")])

    @pytest.mark.asyncio
    async def test_retry_on_transient_error(self, fiber):
        """Test retry logic on transient errors."""
        call_count = 0
        success_response = {
            "id": "retry-success",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "gpt-4o-mini",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "Success after retry"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        }

        async def mock_post(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            mock_response = MagicMock()
            if call_count == 1:  # First call fails
                mock_response.status_code = 500
                mock_response.json.return_value = {"error": {"message": "Server error"}}

                async def mock_aread():
                    return b'{"error": {"message": "Server error"}}'

                mock_response.aread = mock_aread
                mock_response.raise_for_status.side_effect = Exception("Server error")
            else:  # Second call succeeds
                mock_response.status_code = 200
                mock_response.json.return_value = success_response

                async def mock_aread_success():
                    return b'{"success": true}'

                mock_response.aread = mock_aread_success
                mock_response.raise_for_status.return_value = None

            return mock_response

        with patch("httpx.AsyncClient.post", side_effect=mock_post):
            result = await fiber.chat([ChatMessage.user("Test retry")])

            assert result.text == "Success after retry"
            assert call_count == 2  # Should have retried once

    @pytest.mark.asyncio
    async def test_no_retry_on_auth_error(self, fiber):
        """Test that auth errors are not retried."""
        call_count = 0

        async def mock_post(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.json.return_value = {
                "error": {"message": "Invalid API key", "type": "invalid_request_error"}
            }

            async def mock_aread_auth():
                return b'{"error": {"message": "Invalid API key"}}'

            mock_response.aread = mock_aread_auth
            mock_response.raise_for_status.side_effect = Exception("Auth error")
            return mock_response

        with patch("httpx.AsyncClient.post", side_effect=mock_post):
            with pytest.raises(FiberAuthError):
                await fiber.chat([ChatMessage.user("Test no retry on auth error")])

            # Should have been called only once (no retries for auth errors)
            assert call_count == 1


class TestFiberCapabilities:
    """Test Fiber capabilities API functionality."""

    @pytest.fixture
    def fiber(self):
        """Create basic Fiber instance."""
        return Fiber(
            default_model="gpt-4o-mini",
            api_keys={"openai": "test-key", "anthropic": "test-anthropic"},
            enable_observability=False,
        )

    def test_capabilities_registered_model(self, fiber):
        """Test capabilities for a registered model with full info."""
        caps = fiber.capabilities("gpt-4o")

        assert caps["model"] == "gpt-4o"
        assert caps["provider"] == "openai"
        assert caps["registered"] is True
        assert caps["supports_tools"] is True
        assert caps["supports_vision"] is True
        assert caps["supports_streaming"] is True
        assert caps["context_length"] == 128000

        # Check pricing structure
        assert "pricing" in caps
        pricing = caps["pricing"]
        assert "input_cost_per_token" in pricing
        assert "output_cost_per_token" in pricing
        assert "input_cost_per_1k_tokens" in pricing
        assert "output_cost_per_1k_tokens" in pricing
        assert pricing["currency"] == "USD"

    def test_capabilities_unregistered_model(self, fiber):
        """Test capabilities for an unregistered model."""
        caps = fiber.capabilities("unknown-model-123")

        assert caps["model"] == "unknown-model-123"
        assert caps["registered"] is False
        assert caps["pricing"] == {}
        # Should fall back to reasonable defaults
        assert caps["supports_streaming"] is True

    def test_capabilities_anthropic_model(self, fiber):
        """Test capabilities for an Anthropic model."""
        caps = fiber.capabilities("claude-3-haiku-20240307")

        assert caps["model"] == "claude-3-haiku-20240307"
        assert caps["provider"] == "anthropic"
        assert caps["registered"] is True
        assert caps["supports_tools"] is True
        assert caps["supports_vision"] is True
        assert caps["context_length"] == 200000

        # Verify pricing is present for registered model
        assert caps["pricing"]["input_cost_per_1k_tokens"] == 0.00025
        assert caps["pricing"]["output_cost_per_1k_tokens"] == 0.00125

    def test_capabilities_pricing_calculation(self, fiber):
        """Test that pricing calculations are correct."""
        caps = fiber.capabilities("gpt-4o-mini")
        pricing = caps["pricing"]

        # Verify the math: per-token * 1000 = per-1k-tokens
        expected_input_1k = pricing["input_cost_per_token"] * 1000
        expected_output_1k = pricing["output_cost_per_token"] * 1000

        assert abs(pricing["input_cost_per_1k_tokens"] - expected_input_1k) < 0.001
        assert abs(pricing["output_cost_per_1k_tokens"] - expected_output_1k) < 0.001

    def test_capabilities_model_with_no_pricing(self, fiber):
        """Test capabilities for a model without pricing info."""
        # Create a temporary model registry with a model that has no pricing
        registry = ModelRegistry()
        from llm_fiber.routing import ModelInfo

        registry.register_model(
            ModelInfo(
                name="test-no-pricing",
                provider="openai",
                supports_tools=False,
                supports_vision=False,
            )
        )
        fiber.model_registry = registry

        caps = fiber.capabilities("test-no-pricing")

        assert caps["model"] == "test-no-pricing"
        assert caps["supports_tools"] is False
        assert caps["supports_vision"] is False
        assert caps["pricing"] == {}  # No pricing info
