"""Integration tests for Fiber client functionality."""

import asyncio
import json
import time
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest

from llm_fiber import (
    BatchConfig,
    BatchRequest,
    BatchStrategy,
    BoundFiber,
    BudgetExceededError,
    BudgetManager,
    BudgetPeriod,
    ChatMessage,
    ChatResult,
    Fiber,
    FiberAuthError,
    MemoryCacheAdapter,
    RetryPolicy,
    StreamEventType,
    Timeouts,
    create_cost_budget,
    create_token_budget,
)


class TestFiberClientIntegration:
    """Test Fiber client integration scenarios."""

    @pytest.fixture
    def mock_successful_response(self):
        """Mock successful provider response."""
        return {
            "id": "chatcmpl-integration123",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "gpt-4o-mini",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "I'm a helpful AI assistant. I can help you with various tasks.",
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 50, "completion_tokens": 25, "total_tokens": 75},
        }

    @pytest.fixture
    def mock_streaming_chunks(self):
        """Mock streaming response chunks."""
        return [
            'data: {{"id":"chatcmpl-stream123","object":"chat.completion.chunk",'
            '"created":1234567890,"model":"gpt-4o-mini",'
            '"choices":[{{"index":0,"delta":{{"role":"assistant","content":""}},"finish_reason":null}}]}}',
            'data: {{"id":"chatcmpl-stream123","object":"chat.completion.chunk",'
            '"created":1234567890,"model":"gpt-4o-mini",'
            '"choices":[{{"index":0,"delta":{{"content":"Hello"}},"finish_reason":null}}]}}',
            'data: {{"id":"chatcmpl-stream123","object":"chat.completion.chunk",'
            '"created":1234567890,"model":"gpt-4o-mini",'
            '"choices":[{{"index":0,"delta":{{"content":" there"}},"finish_reason":null}}]}}',
            'data: {{"id":"chatcmpl-stream123","object":"chat.completion.chunk",'
            '"created":1234567890,"model":"gpt-4o-mini",'
            '"choices":[{{"index":0,"delta":{{"content":"! How"}},"finish_reason":null}}]}}',
            'data: {{"id":"chatcmpl-stream123","object":"chat.completion.chunk",'
            '"created":1234567890,"model":"gpt-4o-mini",'
            '"choices":[{{"index":0,"delta":{{"content":" can I"}},"finish_reason":null}}]}}',
            'data: {{"id":"chatcmpl-stream123","object":"chat.completion.chunk",'
            '"created":1234567890,"model":"gpt-4o-mini",'
            '"choices":[{{"index":0,"delta":{{"content":" help?"}},"finish_reason":null}}]}}',
            'data: {{"id":"chatcmpl-stream123","object":"chat.completion.chunk",'
            '"created":1234567890,"model":"gpt-4o-mini",'
            '"choices":[{{"index":0,"delta":{{}},"finish_reason":"stop"}},'
            '"usage":{{"prompt_tokens":30,"completion_tokens":20,"total_tokens":50}}}}',
            "data: [DONE]",
        ]

    @pytest.mark.asyncio
    async def test_fiber_basic_chat_integration(self, mock_successful_response):
        """Test basic chat functionality end-to-end."""
        fiber = Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=False
        )

        with patch("httpx.AsyncClient.request") as mock_request:
            mock_response = AsyncMock()
            mock_response.json.return_value = mock_successful_response
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_request.return_value = mock_response

            messages = [
                ChatMessage.system("You are a helpful assistant."),
                ChatMessage.user("Hello, how are you?"),
            ]

            result = await fiber.chat(messages)

            # Verify result structure
            assert isinstance(result, ChatResult)
            assert result.text == "I'm a helpful AI assistant. I can help you with various tasks."
            assert result.finish_reason == "stop"
            assert result.usage.prompt == 50
            assert result.usage.completion == 25
            assert result.usage.total == 75

            # Verify API call was made correctly
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            request_data = call_args[1]["json"]
            assert request_data["model"] == "gpt-4o-mini"
            assert len(request_data["messages"]) == 2

    @pytest.mark.asyncio
    async def test_fiber_streaming_integration(self):
        """Test streaming functionality end-to-end."""
        fiber = Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=False
        )

        # Mock streaming chunks - hardcoded to avoid fixture issues
        mock_streaming_chunks = [
            'data: {"id":"chatcmpl-test456","object":"chat.completion.chunk",'
            '"created":1234567890,"model":"gpt-4o-mini",'
            '"choices":[{"index":0,"delta":{"role":"assistant"},"finish_reason":null}]}\n',
            'data: {"id":"chatcmpl-test456","object":"chat.completion.chunk",'
            '"created":1234567890,"model":"gpt-4o-mini",'
            '"choices":[{"index":0,"delta":{"content":"Hello"},"finish_reason":null}]}\n',
            'data: {"id":"chatcmpl-test456","object":"chat.completion.chunk",'
            '"created":1234567890,"model":"gpt-4o-mini",'
            '"choices":[{"index":0,"delta":{"content":" there!"},"finish_reason":null}]}\n',
            'data: {"id":"chatcmpl-test456","object":"chat.completion.chunk",'
            '"created":1234567890,"model":"gpt-4o-mini",'
            '"choices":[{"index":0,"delta":{"content":" How"},"finish_reason":null}]}\n',
            'data: {"id":"chatcmpl-test456","object":"chat.completion.chunk",'
            '"created":1234567890,"model":"gpt-4o-mini",'
            '"choices":[{"index":0,"delta":{"content":" can"},"finish_reason":null}]}\n',
            'data: {"id":"chatcmpl-test456","object":"chat.completion.chunk",'
            '"created":1234567890,"model":"gpt-4o-mini",'
            '"choices":[{"index":0,"delta":{"content":" I"},"finish_reason":null}]}\n',
            'data: {"id":"chatcmpl-test456","object":"chat.completion.chunk",'
            '"created":1234567890,"model":"gpt-4o-mini",'
            '"choices":[{"index":0,"delta":{"content":" help?"},"finish_reason":null}]}\n',
            'data: {"id":"chatcmpl-test456","object":"chat.completion.chunk",'
            '"created":1234567890,"model":"gpt-4o-mini",'
            '"choices":[{"index":0,"delta":{},"finish_reason":"stop"}],'
            '"usage":{"prompt_tokens":20,"completion_tokens":30,"total_tokens":50}}\n',
            "data: [DONE]\n",
        ]

        # Mock streaming response
        async def mock_aiter_bytes(chunk_size=1024):
            for chunk_str in mock_streaming_chunks:
                yield chunk_str.encode("utf-8")

        mock_stream_response = MagicMock()
        mock_stream_response.aiter_bytes.return_value = mock_aiter_bytes()
        mock_stream_response.status_code = 200
        mock_stream_response.raise_for_status.return_value = None

        with patch("httpx.AsyncClient.stream") as mock_stream:
            mock_stream.return_value.__aenter__.return_value = mock_stream_response

            messages = [ChatMessage.user("Hello")]
            events = []

            async for event in fiber.chat_stream(messages):
                events.append(event)

            # Verify events
            chunk_events = [e for e in events if e.type == StreamEventType.CHUNK]
            usage_events = [e for e in events if e.type == StreamEventType.USAGE]

            assert len(chunk_events) > 0
            assert len(usage_events) == 1

            # Reconstruct full text
            full_text = "".join(e.delta for e in chunk_events)
            assert full_text == "Hello there! How can I help?"

            # Verify final usage
            assert usage_events[0].usage.total == 50

    @pytest.mark.asyncio
    async def test_fiber_with_caching_integration(self, mock_successful_response):
        """Test Fiber with caching integration."""
        cache = MemoryCacheAdapter(max_size=100, default_ttl_seconds=3600)
        fiber = Fiber(
            default_model="gpt-4o-mini",
            api_keys={"openai": "test-key"},
            cache_adapter=cache,
            enable_observability=False,
        )

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value.json.return_value = mock_successful_response
            mock_post.return_value.status_code = 200
            mock_post.return_value.raise_for_status.return_value = None

            messages = [ChatMessage.user("What is Python?")]

            # First call should hit the API and cache the result
            result1 = await fiber.chat(messages, model="gpt-4o-mini", temperature=0.7)
            assert mock_post.call_count == 1

            # Second identical call should hit the cache
            result2 = await fiber.chat(messages, model="gpt-4o-mini", temperature=0.7)
            assert mock_post.call_count == 1  # No additional API call

            # Results should be identical
            assert result1.text == result2.text
            assert result1.usage.total == result2.usage.total

            # Cache should have one entry
            cache_stats = fiber.get_cache_stats()
            assert cache_stats["writes"] >= 1
            assert cache_stats["hits"] >= 1

    @pytest.mark.asyncio
    async def test_fiber_with_budgets_integration(self, mock_successful_response):
        """Test Fiber with budget management integration."""
        budgets = [
            create_cost_budget("daily_cost", 5.0, BudgetPeriod.DAILY, hard_limit=True),
            create_token_budget("hourly_tokens", 1000, BudgetPeriod.HOURLY, hard_limit=False),
        ]
        budget_manager = BudgetManager(budgets)

        fiber = Fiber(
            default_model="gpt-4o-mini",
            api_keys={"openai": "test-key"},
            budget_manager=budget_manager,
            enable_observability=False,
        )

        with patch("httpx.AsyncClient.post") as mock_post:
            # Mock response with cost estimate
            response_with_cost = mock_successful_response.copy()
            mock_post.return_value.json.return_value = response_with_cost
            mock_post.return_value.status_code = 200
            mock_post.return_value.raise_for_status.return_value = None

            messages = [ChatMessage.user("Hello")]

            # First request should succeed
            result = await fiber.chat(messages)
            assert result.text == "I'm a helpful AI assistant. I can help you with various tasks."

            # Verify budget consumption
            budget_status = budget_manager.get_budget_status()
            assert budget_status["daily_cost"]["consumed"] > 0
            assert budget_status["hourly_tokens"]["consumed"] == 75  # From usage

            # Consume most of the cost budget
            cost_budget = budget_manager.get_budget("daily_cost")
            cost_budget.consumed = 4.8  # Just under the $5 limit

            # This should still work
            await fiber.chat([ChatMessage.user("Another small request")])

            # But consuming too much should fail
            cost_budget.consumed = (
                4.999999  # Very close to $5 limit so even tiny request cost will exceed it
            )
            # BudgetExceededError already imported at top of file

            with pytest.raises(BudgetExceededError):
                await fiber.chat([ChatMessage.user("Expensive request")] * 10)

    @pytest.mark.asyncio
    async def test_fiber_batch_processing_integration(self, mock_successful_response):
        """Test Fiber batch processing integration."""
        batch_config = BatchConfig(
            max_concurrent=3, strategy=BatchStrategy.CONCURRENT, return_exceptions=True
        )

        fiber = Fiber(
            default_model="gpt-4o-mini",
            api_keys={"openai": "test-key"},
            batch_config=batch_config,
            enable_observability=False,
        )

        # Create multiple batch requests
        batch_requests = [
            BatchRequest("req_1", [ChatMessage.user("What is Python?")], "gpt-4o-mini"),
            BatchRequest("req_2", [ChatMessage.user("What is JavaScript?")], "gpt-4o-mini"),
            BatchRequest("req_3", [ChatMessage.user("What is Go?")], "gpt-4o-mini"),
            BatchRequest("req_4", [ChatMessage.user("What is Rust?")], "gpt-4o-mini"),
        ]

        with patch("httpx.AsyncClient.post") as mock_post:
            # Mock different responses for variety
            responses = [
                {
                    "choices": [
                        {
                            "message": {"role": "assistant", "content": f"Response {i}"},
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30},
                    "id": f"resp_{i}",
                    "model": "gpt-4o-mini",
                    "object": "chat.completion",
                    "created": int(time.time()),
                }
                for i in range(1, 5)
            ]

            mock_post.return_value.json.side_effect = responses
            mock_post.return_value.status_code = 200
            mock_post.return_value.raise_for_status.return_value = None

            results = await fiber.batch_chat(batch_requests)

            # Verify all requests succeeded
            assert len(results) == 4
            assert all(result.is_success for result in results)

            # Verify responses
            result_map = {result.id: result for result in results}
            assert "Response 1" in result_map["req_1"].result.text
            assert "Response 2" in result_map["req_2"].result.text

            # Verify concurrent execution (should have made 4 API calls)
            assert mock_post.call_count == 4

    @pytest.mark.asyncio
    async def test_fiber_context_binding_integration(self, mock_successful_response):
        """Test Fiber context binding integration."""
        fiber = Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=False
        )

        # Create bound fiber with specific context
        bound_fiber = fiber.bind(temperature=0.3, max_tokens=50, custom_param="test_value")

        assert isinstance(bound_fiber, BoundFiber)

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value.json.return_value = mock_successful_response
            mock_post.return_value.status_code = 200
            mock_post.return_value.raise_for_status.return_value = None

            messages = [ChatMessage.user("Hello")]
            result = await bound_fiber.chat(messages=messages)

            # Verify result
            assert result.text == "I'm a helpful AI assistant. I can help you with various tasks."

            # Verify context was applied
            call_args = mock_post.call_args
            request_data = call_args[1]["json"]
            assert request_data["temperature"] == 0.3
            assert request_data["max_tokens"] == 50
            assert request_data["custom_param"] == "test_value"

        # Test chained binding
        double_bound = bound_fiber.bind(top_p=0.9, temperature=0.7)  # Override temperature

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value.json.return_value = mock_successful_response
            mock_post.return_value.status_code = 200
            mock_post.return_value.raise_for_status.return_value = None

            await double_bound.chat(messages=messages)

            # Verify merged context
            call_args = mock_post.call_args
            request_data = call_args[1]["json"]
            assert request_data["temperature"] == 0.7  # Overridden
            assert request_data["max_tokens"] == 50  # From first bind
            assert request_data["custom_param"] == "test_value"  # From first bind
            assert request_data["top_p"] == 0.9  # From second bind

    @pytest.mark.asyncio
    async def test_fiber_provider_routing_integration(self):
        """Test Fiber provider routing integration."""
        fiber = Fiber(
            api_keys={
                "openai": "test-openai-key",
                "anthropic": "test-anthropic-key",
                "gemini": "test-gemini-key",
            },
            enable_observability=False,
        )

        # Test OpenAI routing
        openai_response = {
            "id": "chatcmpl-openai",
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
            "usage": {"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30},
        }

        # Test Anthropic routing
        anthropic_response = {
            "id": "msg_anthropic",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": "Anthropic response"}],
            "model": "claude-3-haiku",
            "stop_reason": "end_turn",
            "usage": {"input_tokens": 20, "output_tokens": 10},
        }

        # Test Gemini routing
        gemini_response = {
            "candidates": [
                {
                    "content": {"parts": [{"text": "Gemini response"}], "role": "model"},
                    "finishReason": "STOP",
                }
            ],
            "usageMetadata": {
                "promptTokenCount": 20,
                "candidatesTokenCount": 10,
                "totalTokenCount": 30,
            },
        }

        test_cases = [
            ("gpt-4o", openai_response, "OpenAI response"),
            ("claude-3-haiku", anthropic_response, "Anthropic response"),
            ("gemini-1.5-pro", gemini_response, "Gemini response"),
        ]

        for model, response, expected_text in test_cases:
            with patch("httpx.AsyncClient.post") as mock_post:
                mock_post.return_value.json.return_value = response
                mock_post.return_value.status_code = 200
                mock_post.return_value.raise_for_status.return_value = None

                messages = [ChatMessage.user("Hello")]
                result = await fiber.chat(messages, model=model)

                assert result.text == expected_text

                # Verify correct base URL was used for each provider
                call_args = mock_post.call_args
                if "gpt-" in model:
                    assert "openai.com" in str(call_args)
                elif "claude-" in model:
                    assert "anthropic.com" in str(call_args)
                elif "gemini-" in model:
                    assert "googleapis.com" in str(call_args)

    @pytest.mark.asyncio
    async def test_fiber_error_handling_and_retries(self):
        """Test Fiber error handling and retry logic integration."""
        retry_policy = RetryPolicy(max_attempts=3, base_delay=0.01, max_delay=0.1)

        fiber = Fiber(
            default_model="gpt-4o-mini",
            api_keys={"openai": "test-key"},
            retry_policy=retry_policy,
            enable_observability=False,
        )

        # Test retry on transient error
        error_count = 0
        success_response = {
            "id": "chatcmpl-retry",
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

        def mock_post_with_retry(*args, **kwargs):
            nonlocal error_count
            error_count += 1

            mock_response = AsyncMock()
            if error_count < 3:  # Fail first two times
                mock_response.status_code = 500
                mock_response.aread.return_value = (
                    b'{"error": {"message": "Internal server error"}}'
                )
                mock_response.json.return_value = {"error": {"message": "Internal server error"}}
            else:  # Succeed on third try
                mock_response.status_code = 200
                mock_response.aread.return_value = json.dumps(success_response).encode("utf-8")
                mock_response.json.return_value = success_response

            return mock_response

        with patch("httpx.AsyncClient.post", side_effect=mock_post_with_retry):
            messages = [ChatMessage.user("Test retry")]
            result = await fiber.chat(messages)

            # Should succeed after retries
            assert result.text == "Success after retry"
            assert error_count == 3  # Failed twice, succeeded on third try

        # Test non-retryable error (auth error)
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = AsyncMock()
            mock_response.status_code = 401
            mock_response.aread.return_value = (
                b'{"error": {"message": "Invalid API key", "type": "invalid_request_error"}}'
            )
            mock_response.json.return_value = {
                "error": {"message": "Invalid API key", "type": "invalid_request_error"}
            }
            mock_post.return_value = mock_response

            # FiberAuthError already imported at top of file
            with pytest.raises(FiberAuthError):
                await fiber.chat([ChatMessage.user("Test auth error")])

            # Should not retry auth errors
            assert mock_post.call_count == 1

    def test_fiber_sync_wrapper_integration(self, mock_successful_response):
        """Test Fiber synchronous wrapper integration."""
        fiber = Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=False
        )

        sync_fiber = fiber.sync

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value.json.return_value = mock_successful_response
            mock_post.return_value.status_code = 200
            mock_post.return_value.raise_for_status.return_value = None

            messages = [ChatMessage.user("Test sync")]

            # Test synchronous chat
            result = sync_fiber.chat(messages)

            assert isinstance(result, ChatResult)
            assert result.text == "I'm a helpful AI assistant. I can help you with various tasks."

        # Test synchronous streaming
        with patch("httpx.AsyncClient.stream") as mock_stream:
            # Create async iterator for streaming lines
            async def mock_aiter_bytes():
                lines = [
                    b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n',
                    b'data: {"choices":[{"delta":{"content":" sync"}}]}\n',
                    b'data: {"choices":[{"delta":{},"finish_reason":"stop"}],'
                    b'"usage":{"total_tokens":20}}\n',
                    b"data: [DONE]\n",
                ]
                for line in lines:
                    yield line

            mock_stream_response = MagicMock()
            mock_stream_response.aiter_bytes.return_value = mock_aiter_bytes()
            # Ensure status_code is an actual integer, not a Mock
            type(mock_stream_response).status_code = PropertyMock(return_value=200)
            mock_stream_response.raise_for_status.return_value = None

            # Properly mock the async context manager
            mock_context_manager = MagicMock()
            mock_context_manager.__aenter__.return_value = mock_stream_response
            mock_context_manager.__aexit__.return_value = None
            mock_stream.return_value = mock_context_manager

            events = list(sync_fiber.chat_stream(messages))

            chunk_events = [e for e in events if e.type == StreamEventType.CHUNK]
            assert len(chunk_events) >= 2

            full_text = "".join(e.delta for e in chunk_events)
            assert "Hello sync" in full_text

    @pytest.mark.asyncio
    async def test_fiber_comprehensive_feature_integration(self, mock_successful_response):
        """Test comprehensive integration with all features enabled."""
        # Setup all features
        cache = MemoryCacheAdapter(max_size=50, default_ttl_seconds=1800)

        budgets = [
            create_cost_budget("integration_cost", 20.0, BudgetPeriod.DAILY, hard_limit=True),
            create_token_budget("integration_tokens", 10000, BudgetPeriod.HOURLY, hard_limit=False),
        ]
        budget_manager = BudgetManager(budgets)

        batch_config = BatchConfig(
            max_concurrent=2, strategy=BatchStrategy.ADAPTIVE, return_exceptions=True
        )

        timeout = Timeouts(connect=5.0, read=30.0, total=60.0)
        retry_policy = RetryPolicy(max_attempts=2, base_delay=0.1)

        # Create fully-featured Fiber client
        fiber = Fiber(
            default_model="gpt-4o-mini",
            api_keys={"openai": "test-key", "anthropic": "test-anthropic"},
            cache_adapter=cache,
            budget_manager=budget_manager,
            batch_config=batch_config,
            timeout=timeout,
            retry_policy=retry_policy,
            enable_observability=True,
        )

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value.json.return_value = mock_successful_response
            mock_post.return_value.status_code = 200
            mock_post.return_value.raise_for_status.return_value = None

            # Test individual chat with caching and budgets
            messages = [ChatMessage.user("Comprehensive test")]

            # First call - should hit API, cache result, track budget
            result1 = await fiber.chat(messages, temperature=0.5)
            assert result1.text == "I'm a helpful AI assistant. I can help you with various tasks."
            assert mock_post.call_count == 1

            # Second identical call - should hit cache
            result2 = await fiber.chat(messages, temperature=0.5)
            assert result1.text == result2.text
            assert mock_post.call_count == 1  # No additional API call

            # Verify budget tracking
            budget_status = budget_manager.get_budget_status()
            assert budget_status["integration_cost"]["consumed"] > 0
            assert budget_status["integration_tokens"]["consumed"] == 75  # From usage

            # Verify cache stats
            cache_stats = fiber.get_cache_stats()
            assert cache_stats["writes"] >= 1
            assert cache_stats["hits"] >= 1

            # Test batch processing with all features
            batch_requests = [
                BatchRequest("comp_1", [ChatMessage.user("Batch test 1")], "gpt-4o-mini"),
                BatchRequest("comp_2", [ChatMessage.user("Batch test 2")], "claude-3-haiku"),
            ]

            # Mock responses for both providers
            mock_post.return_value.json.side_effect = [
                mock_successful_response,  # OpenAI response
                {
                    "id": "msg_anthropic",
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "text", "text": "Anthropic batch response"}],
                    "model": "claude-3-haiku",
                    "stop_reason": "end_turn",
                    "usage": {"input_tokens": 25, "output_tokens": 15},
                },
            ]

            batch_results = await fiber.batch_chat(batch_requests)

            assert len(batch_results) == 2
            assert all(result.is_success for result in batch_results)

            # Verify provider routing worked in batch
            result_map = {result.id: result for result in batch_results}
            assert (
                result_map["comp_1"].result.text
                == "I'm a helpful AI assistant. I can help you with various tasks."
            )
            assert result_map["comp_2"].result.text == "Anthropic batch response"

            # Test context binding with all features
            bound_fiber = fiber.bind(temperature=0.8, custom_header="test")

            # Reset side_effect to None so return_value is used again
            mock_post.return_value.json.side_effect = None
            mock_post.return_value.json.return_value = mock_successful_response
            bound_result = await bound_fiber.chat(messages=[ChatMessage.user("Bound test")])

            assert (
                bound_result.text
                == "I'm a helpful AI assistant. I can help you with various tasks."
            )

            # Verify context was applied
            last_call = mock_post.call_args
            request_data = last_call[1]["json"]
            assert request_data["temperature"] == 0.8
            assert request_data["custom_header"] == "test"

    @pytest.mark.asyncio
    async def test_fiber_observability_integration(self, mock_successful_response):
        """Test Fiber observability features integration."""
        fiber = Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=True
        )

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value.json.return_value = mock_successful_response
            mock_post.return_value.status_code = 200
            mock_post.return_value.raise_for_status.return_value = None

            messages = [ChatMessage.user("Observability test")]
            result = await fiber.chat(messages)

            # Test that metrics are accessible
            metrics = fiber.metrics
            assert metrics is not None

            # Basic metrics should be recorded
            # Note: Specific metric names depend on implementation
            assert hasattr(metrics, "record_request_success")

            # Test that we can get some observability data
            # This is a basic test since exact metrics depend on implementation
            assert result is not None

    @pytest.mark.asyncio
    async def test_fiber_ask_helper_integration(self, mock_successful_response):
        """Test Fiber ask helper method integration."""
        fiber = Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=False
        )

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value.json.return_value = mock_successful_response
            mock_post.return_value.status_code = 200
            mock_post.return_value.raise_for_status.return_value = None

            # Test ask with string input
            result = await fiber.ask("What is the meaning of life?")
            assert isinstance(result, str)
            assert result == "I'm a helpful AI assistant. I can help you with various tasks."

            # Test ask with additional parameters
            result2 = await fiber.ask(
                "Explain quantum computing", model="gpt-4o", temperature=0.3, max_tokens=200
            )
            assert isinstance(result2, str)

            # Verify parameters were passed correctly
            last_call = mock_post.call_args
            request_data = last_call[1]["json"]
            assert request_data["model"] == "gpt-4o"
            assert request_data["temperature"] == 0.3
            assert request_data["max_tokens"] == 200

    @pytest.mark.asyncio
    async def test_fiber_from_env_integration(self):
        """Test Fiber.from_env initialization integration."""
        with patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test-openai-from-env",
                "ANTHROPIC_API_KEY": "test-anthropic-from-env",
                "GEMINI_API_KEY": "test-gemini-from-env",
            },
        ):
            fiber = Fiber.from_env(enable_observability=False)

            # Should have detected all API keys
            assert "openai" in fiber._api_keys
            assert "anthropic" in fiber._api_keys
            assert "gemini" in fiber._api_keys

            # Should have selected a default model
            assert fiber.default_model is not None

            # Test with preference
            fiber_with_pref = Fiber.from_env(
                prefer=["anthropic", "openai"], enable_observability=False
            )

            # Should respect preference for default model selection
            # (exact model depends on implementation, but should be from preferred provider)
            assert fiber_with_pref.default_model is not None

    @pytest.mark.asyncio
    async def test_fiber_tool_calling_integration(self):
        """Test Fiber tool calling integration across providers."""
        fiber = Fiber(
            api_keys={"openai": "test-openai-key", "anthropic": "test-anthropic-key"},
            enable_observability=False,
        )

        # Test OpenAI tool calling
        openai_tool_response = {
            "id": "chatcmpl-tool",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "gpt-4o",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_123",
                                "type": "function",
                                "function": {
                                    "name": "get_weather",
                                    "arguments": '{"location": "Paris"}',
                                },
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 30, "completion_tokens": 20, "total_tokens": 50},
        }

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value.json.return_value = openai_tool_response
            mock_post.return_value.status_code = 200
            mock_post.return_value.raise_for_status.return_value = None

            messages = [ChatMessage.user("What's the weather in Paris?")]
            result = await fiber.chat(messages, model="gpt-4o")

            # Verify tool call normalization
            assert len(result.tool_calls) == 1
            tool_call = result.tool_calls[0]
            assert tool_call["id"] == "call_123"
            assert tool_call["function"]["name"] == "get_weather"
            assert "Paris" in tool_call["function"]["arguments"]

        # Test Anthropic tool calling
        anthropic_tool_response = {
            "id": "msg_tool",
            "type": "message",
            "role": "assistant",
            "content": [
                {
                    "type": "tool_use",
                    "id": "toolu_456",
                    "name": "get_weather",
                    "input": {"location": "Paris"},
                }
            ],
            "model": "claude-3-sonnet",
            "stop_reason": "tool_use",
            "usage": {"input_tokens": 30, "output_tokens": 20},
        }

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value.json.return_value = anthropic_tool_response
            mock_post.return_value.status_code = 200
            mock_post.return_value.raise_for_status.return_value = None

            result = await fiber.chat(messages, model="claude-3-sonnet")

            # Tool calls should be normalized to same format
            assert len(result.tool_calls) == 1
            tool_call = result.tool_calls[0]
            assert "id" in tool_call
            assert tool_call["function"]["name"] == "get_weather"

    @pytest.mark.asyncio
    async def test_fiber_performance_characteristics(self, mock_successful_response):
        """Test Fiber performance characteristics integration."""
        fiber = Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=True
        )

        # Test concurrent request handling
        num_requests = 5
        delay_per_request = 0.05

        async def mock_post_with_delay(*args, **kwargs):
            await asyncio.sleep(delay_per_request)
            mock_response = MagicMock()
            mock_response.json.return_value = mock_successful_response
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            return mock_response

        with patch("httpx.AsyncClient.post", side_effect=mock_post_with_delay):
            messages = [ChatMessage.user(f"Request {i}") for i in range(num_requests)]

            # Test concurrent execution
            start_time = time.time()
            tasks = [fiber.chat([msg]) for msg in messages]
            results = await asyncio.gather(*tasks)
            concurrent_time = time.time() - start_time

            # Verify all requests succeeded
            assert len(results) == num_requests
            assert all(isinstance(r, ChatResult) for r in results)

            # Concurrent execution should be much faster than sequential
            # With 5 requests at 0.05s each, concurrent should be ~0.05s, sequential would be ~0.25s
            assert concurrent_time < (num_requests * delay_per_request * 0.8)

    @pytest.mark.asyncio
    async def test_fiber_edge_cases_integration(self):
        """Test Fiber edge cases and boundary conditions."""
        fiber = Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=False
        )

        # Test empty message handling
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = {
                "id": "empty-test",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "gpt-4o-mini",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "I need more context."},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 5, "completion_tokens": 8, "total_tokens": 13},
            }
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.status_code = 200
            mock_post.return_value.raise_for_status.return_value = None

            # Test with minimal input
            result = await fiber.chat([ChatMessage.user("")])
            assert isinstance(result, ChatResult)

        # Test very long message handling
        long_message = "This is a very long message. " * 1000
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = {
                "id": "long-test",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "gpt-4o-mini",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "I understand your long message.",
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 5000, "completion_tokens": 10, "total_tokens": 5010},
            }
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.status_code = 200
            mock_post.return_value.raise_for_status.return_value = None

            result = await fiber.chat([ChatMessage.user(long_message)])
            assert isinstance(result, ChatResult)
            assert result.usage.prompt == 5000

        # Test special characters and unicode
        special_message = (
            "Hello 🌍! Test with emojis and special characters: Chinese, Arabic, Russian"
        )
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = {
                "id": "unicode-test",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "gpt-4o-mini",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "I can handle unicode! 🎉"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 20, "completion_tokens": 8, "total_tokens": 28},
            }
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.status_code = 200
            mock_post.return_value.raise_for_status.return_value = None

            result = await fiber.chat([ChatMessage.user(special_message)])
            assert isinstance(result, ChatResult)
            assert "🎉" in result.text

    @pytest.mark.asyncio
    async def test_fiber_cleanup_and_resource_management(self, mock_successful_response):
        """Test Fiber resource cleanup and management."""
        fiber = Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=False
        )

        # Test that fiber can handle multiple sequential operations
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value.json.return_value = mock_successful_response
            mock_post.return_value.status_code = 200
            mock_post.return_value.raise_for_status.return_value = None

            # Perform multiple operations in sequence
            for i in range(10):
                messages = [ChatMessage.user(f"Sequential test {i}")]
                result = await fiber.chat(messages)
                assert isinstance(result, ChatResult)

            # Should have made 10 API calls
            assert mock_post.call_count == 10

        # Test context manager behavior (if implemented)
        try:
            async with fiber:
                result = await fiber.chat([ChatMessage.user("Context manager test")])
                assert isinstance(result, ChatResult)
        except TypeError:
            # Context manager not implemented, which is fine
            pass

        # Test that fiber remains functional after many operations
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value.json.return_value = mock_successful_response
            mock_post.return_value.status_code = 200
            mock_post.return_value.raise_for_status.return_value = None

            result = await fiber.chat([ChatMessage.user("Final test")])
            assert isinstance(result, ChatResult)

    @pytest.mark.asyncio
    async def test_fiber_configuration_validation_integration(self):
        """Test Fiber configuration validation integration."""
        # Test invalid timeouts
        with pytest.raises(ValueError):
            Fiber(api_keys={"openai": "test"}, timeout=Timeouts(connect=-1.0))

        # Test valid configuration works
        fiber = Fiber(
            default_model="gpt-4o-mini",
            api_keys={"openai": "valid-key"},
            timeout=Timeouts(connect=5.0, read=30.0, total=60.0),
            enable_observability=False,
        )
        assert fiber.default_model == "gpt-4o-mini"
