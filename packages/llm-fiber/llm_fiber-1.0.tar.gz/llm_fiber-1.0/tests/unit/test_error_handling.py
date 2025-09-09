"""Comprehensive error handling tests for llm-fiber."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from llm_fiber import (
    ChatMessage,
    Fiber,
    FiberAuthError,
    FiberConnectionError,
    FiberError,
    FiberParsingError,
    FiberProviderError,
    FiberQuotaError,
    FiberRateLimitError,
    FiberTimeoutError,
    FiberValidationError,
    RetryPolicy,
    StreamEvent,
)


@pytest.fixture
def fiber_client():
    """Create a basic Fiber client for testing."""
    return Fiber(api_keys={"openai": "test-key"}, default_model="gpt-4o-mini")


@pytest.fixture
def fiber_with_retries():
    """Create Fiber client with retry configuration."""
    return Fiber(
        api_keys={"openai": "test-key"},
        default_model="gpt-4o-mini",
        retry_policy=RetryPolicy(max_attempts=3),
    )


class TestErrorHierarchy:
    """Test error class hierarchy and inheritance."""

    def test_base_fiber_error(self):
        """Test base FiberError functionality."""
        error = FiberError("Base error message")

        assert str(error) == "Base error message"
        assert isinstance(error, Exception)

    def test_error_inheritance(self):
        """Test that all specific errors inherit from FiberError."""
        error_types = [
            FiberAuthError,
            FiberConnectionError,
            FiberParsingError,
            FiberProviderError,
            FiberQuotaError,
            FiberRateLimitError,
            FiberTimeoutError,
            FiberValidationError,
        ]

        for error_type in error_types:
            error = error_type("Test message")
            assert isinstance(error, FiberError)
            assert isinstance(error, Exception)

    def test_auth_error_specifics(self):
        """Test FiberAuthError specific functionality."""
        error = FiberAuthError("Invalid API key", provider="openai")

        assert str(error) == "Invalid API key"
        assert error.provider == "openai"

    def test_rate_limit_error_with_retry_after(self):
        """Test FiberRateLimitError with retry_after information."""
        error = FiberRateLimitError("Rate limit exceeded", provider="openai", retry_after=60)

        assert error.retry_after == 60
        assert "Rate limit exceeded" in str(error)

    def test_connection_error_with_details(self):
        """Test FiberConnectionError with connection details."""
        error = FiberConnectionError("Connection failed", provider="openai", host="api.openai.com")

        assert error.host == "api.openai.com"
        assert error.provider == "openai"

    def test_parsing_error_with_raw_response(self):
        """Test FiberParsingError with raw response data."""
        error = FiberParsingError("Invalid response format", provider="openai")

        assert error.provider == "openai"

    def test_quota_error_with_limits(self):
        """Test FiberQuotaError with quota limits."""
        error = FiberQuotaError("Quota exceeded", provider="openai", limit=1000000, usage=1000000)

        assert error.limit == 1000000
        assert error.usage == 1000000


class TestHttpErrorHandling:
    """Test HTTP error status code mapping."""

    @pytest.mark.asyncio
    async def test_401_maps_to_auth_error(self, fiber_client):
        """Test that 401 status codes map to FiberAuthError."""
        mock_response = AsyncMock()
        mock_response.status_code = 401
        mock_response.aread = AsyncMock(return_value=b'{"error": {"message": "Invalid API key"}}')

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            with pytest.raises(FiberAuthError) as exc_info:
                await fiber_client.chat([ChatMessage.user("Test")])

            assert "Authentication failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_403_maps_to_auth_error(self, fiber_client):
        """Test that 403 status codes map to FiberAuthError."""
        mock_response = AsyncMock()
        mock_response.status_code = 403
        mock_response.aread = AsyncMock(return_value=b'{"error": {"message": "Access forbidden"}}')

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            with pytest.raises(FiberAuthError) as exc_info:
                await fiber_client.chat([ChatMessage.user("Test")])

            assert "Access forbidden" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_429_maps_to_rate_limit_error(self, fiber_client):
        """Test that 429 status codes map to FiberRateLimitError."""
        mock_response = AsyncMock()
        mock_response.status_code = 429
        mock_response.aread = AsyncMock(
            return_value=b'{"error": {"message": "Rate limit exceeded"}}'
        )

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            with pytest.raises(FiberRateLimitError) as exc_info:
                await fiber_client.chat([ChatMessage.user("Test")])

            assert "Rate limit exceeded" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_500_maps_to_provider_error(self, fiber_client):
        """Test that 500 status codes map to FiberProviderError."""
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.aread = AsyncMock(
            return_value=b'{"error": {"message": "Internal server error"}}'
        )

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            with pytest.raises(FiberProviderError) as exc_info:
                await fiber_client.chat([ChatMessage.user("Test")])

            assert "Server error (500)" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_timeout_maps_to_timeout_error(self, fiber_client):
        """Test that timeout exceptions map to FiberTimeoutError."""
        with patch("httpx.AsyncClient.post", side_effect=asyncio.TimeoutError("Request timed out")):
            with pytest.raises(FiberTimeoutError) as exc_info:
                await fiber_client.chat([ChatMessage.user("Test")])

            assert "Request timed out" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_connection_error_mapping(self, fiber_client):
        """Test that connection errors map to FiberConnectionError."""
        with patch("httpx.AsyncClient.post", side_effect=ConnectionError("Connection failed")):
            with pytest.raises(FiberConnectionError) as exc_info:
                await fiber_client.chat([ChatMessage.user("Test")])

            assert "Connection failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_malformed_json_response(self, fiber_client):
        """Test handling of malformed JSON responses."""
        # Mock a response that returns valid status but invalid JSON
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(side_effect=json.JSONDecodeError("Expecting value", "", 0))
        mock_response.aread = AsyncMock(return_value=b"invalid json")

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            with pytest.raises(FiberProviderError) as exc_info:
                await fiber_client.chat([ChatMessage.user("Test")])

            assert "Request failed" in str(exc_info.value)


class TestRetryErrorHandling:
    """Test retry behavior for different error types."""

    @pytest.mark.asyncio
    async def test_retryable_error_retry_behavior(self, fiber_with_retries):
        """Test that retryable errors trigger retry attempts."""
        call_count = 0

        def mock_post_with_retries(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                # First two calls fail with retryable error
                mock_response = AsyncMock()
                mock_response.status_code = 429
                mock_response.aread = AsyncMock(
                    return_value=b'{"error": {"message": "Rate limit"}}'
                )
                return mock_response
            else:
                # Third call succeeds
                mock_response = AsyncMock()
                mock_response.status_code = 200
                mock_response.json = MagicMock(
                    return_value={
                        "choices": [
                            {
                                "message": {"role": "assistant", "content": "Success"},
                                "finish_reason": "stop",
                            }
                        ],
                        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
                    }
                )
                return mock_response

        with patch("httpx.AsyncClient.post", side_effect=mock_post_with_retries):
            result = await fiber_with_retries.chat([ChatMessage.user("Test retry")])

            assert result.text == "Success"
            assert call_count == 3  # Should retry until success

    @pytest.mark.asyncio
    async def test_non_retryable_error_no_retry(self, fiber_with_retries):
        """Test that non-retryable errors don't trigger retries."""
        call_count = 0

        def mock_post_no_retry(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            # Always return auth error (non-retryable)
            mock_response = AsyncMock()
            mock_response.status_code = 401
            mock_response.aread = AsyncMock(
                return_value=b'{"error": {"message": "Invalid API key"}}'
            )
            return mock_response

        with patch("httpx.AsyncClient.post", side_effect=mock_post_no_retry):
            with pytest.raises(FiberAuthError):
                await fiber_with_retries.chat([ChatMessage.user("Test no retry")])

            assert call_count == 1  # Should not retry auth errors

    @pytest.mark.asyncio
    async def test_max_retries_exhausted(self, fiber_with_retries):
        """Test behavior when max retries are exhausted."""
        call_count = 0

        def mock_post_always_fail(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            mock_response = AsyncMock()
            mock_response.status_code = 500
            mock_response.aread = AsyncMock(return_value=b'{"error": {"message": "Server error"}}')
            return mock_response

        with patch("httpx.AsyncClient.post", side_effect=mock_post_always_fail):
            with pytest.raises(FiberProviderError):
                await fiber_with_retries.chat([ChatMessage.user("Test max retries")])

            assert call_count == 3  # Initial attempt + 2 retries


class TestStreamingErrorHandling:
    """Test streaming error handling."""

    @pytest.mark.asyncio
    async def test_streaming_connection_error(self, fiber_client):
        """Test handling of connection errors during streaming."""

        async def failing_stream(*args, **kwargs):
            yield StreamEvent.create_chunk("Starting")
            raise FiberConnectionError("Connection lost", provider="openai")

        from llm_fiber.providers.openai import OpenAIAdapter

        with patch.object(OpenAIAdapter, "chat_stream", side_effect=failing_stream):
            with pytest.raises(FiberConnectionError):
                async for event in fiber_client.chat_stream([ChatMessage.user("Test")]):
                    pass

    @pytest.mark.asyncio
    async def test_streaming_partial_response_error(self, fiber_client):
        """Test handling of partial response errors during streaming."""

        async def partial_stream(*args, **kwargs):
            yield StreamEvent.create_chunk("This is a partial")
            raise FiberProviderError("Stream interrupted", provider="openai")

        from llm_fiber.providers.openai import OpenAIAdapter

        with patch.object(OpenAIAdapter, "chat_stream", side_effect=partial_stream):
            with pytest.raises(FiberProviderError):
                events = []
                async for event in fiber_client.chat_stream([ChatMessage.user("Test")]):
                    events.append(event)

    @pytest.mark.asyncio
    async def test_streaming_timeout_error(self, fiber_client):
        """Test handling of timeout errors during streaming."""

        async def slow_stream(*args, **kwargs):
            yield StreamEvent.create_chunk("Starting")
            await asyncio.sleep(2)  # Simulate slow response
            raise FiberTimeoutError("Request timed out", provider="openai")

        from llm_fiber.providers.openai import OpenAIAdapter

        with patch.object(OpenAIAdapter, "chat_stream", side_effect=slow_stream):
            with pytest.raises(FiberTimeoutError):
                async for event in fiber_client.chat_stream([ChatMessage.user("Test")]):
                    pass


class TestProviderSpecificErrorHandling:
    """Test provider-specific error handling."""

    @pytest.mark.asyncio
    async def test_openai_specific_errors(self, fiber_client):
        """Test OpenAI-specific error handling."""
        # Mock content policy violation
        mock_response = AsyncMock()
        mock_response.status_code = 400
        mock_response.aread = AsyncMock(
            return_value=b'{"error": {"message": "Content policy violation", '
            b'"code": "content_policy_violation"}}'
        )

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            with pytest.raises(FiberValidationError) as exc_info:
                await fiber_client.chat([ChatMessage.user("Generate something inappropriate")])

            assert "Invalid request" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_anthropic_specific_errors(self):
        """Test Anthropic-specific error handling."""
        fiber = Fiber(api_keys={"anthropic": "test-key"}, default_model="claude-3-sonnet-20240229")

        # Mock context length error
        mock_response = AsyncMock()
        mock_response.status_code = 400
        mock_response.aread = AsyncMock(
            return_value=b'{"error": {"message": "Context length exceeded", '
            b'"type": "invalid_request"}}'
        )

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            with pytest.raises(FiberValidationError) as exc_info:
                await fiber.chat([ChatMessage.user("Very long message" * 10000)])

            assert "Invalid request" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_gemini_specific_errors(self):
        """Test Gemini-specific error handling."""
        fiber = Fiber(api_keys={"gemini": "test-key"}, default_model="gemini-pro")

        # Mock safety filter error
        mock_response = AsyncMock()
        mock_response.status_code = 400
        mock_response.aread = AsyncMock(
            return_value=b'{"error": {"message": "Safety filter triggered", "code": "SAFETY"}}'
        )

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            with pytest.raises(FiberValidationError) as exc_info:
                await fiber.chat([ChatMessage.user("Test safety filter")])

            assert "Invalid request" in str(exc_info.value)


class TestErrorRecovery:
    """Test error recovery and graceful degradation."""

    def test_graceful_degradation_on_error(self):
        """Test graceful degradation when errors occur."""
        # Test that the system can continue operating after non-fatal errors
        fiber = Fiber(api_keys={"openai": "test-key"}, default_model="gpt-4o-mini")

        # Verify fiber client is still functional after initialization
        assert fiber.default_model == "gpt-4o-mini"
        assert hasattr(fiber, "_providers")

    @pytest.mark.asyncio
    async def test_error_context_preservation(self, fiber_client):
        """Test that error context is preserved through the call stack."""
        mock_response = AsyncMock()
        mock_response.status_code = 401
        mock_response.aread = AsyncMock(
            return_value=b'{"error": {"message": "Invalid API key", '
            b'"details": {"key_id": "sk-123"}}}'
        )

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            with pytest.raises(FiberAuthError) as exc_info:
                await fiber_client.chat([ChatMessage.user("Test context")])

            # Verify error context is preserved
            error = exc_info.value
            assert error.provider is not None
            assert hasattr(error, "message")


class TestErrorEdgeCases:
    """Test edge cases in error handling."""

    def test_empty_error_response(self):
        """Test handling of empty error responses."""
        error = FiberProviderError("", provider="test")
        assert str(error) == ""
        assert error.provider == "test"

    @pytest.mark.asyncio
    async def test_unicode_error_messages(self, fiber_client):
        """Test handling of Unicode error messages."""
        mock_response = AsyncMock()
        mock_response.status_code = 400
        mock_response.aread = AsyncMock(
            return_value='{"error": {"message": "Error: 测试错误消息"}}'.encode("utf-8")
        )

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            with pytest.raises(FiberValidationError) as exc_info:
                await fiber_client.chat([ChatMessage.user("Test unicode")])

            assert "测试错误消息" in str(exc_info.value) or "Invalid request" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_very_long_error_messages(self, fiber_client):
        """Test handling of very long error messages."""
        long_message = "Error: " + "x" * 10000
        mock_response = AsyncMock()
        mock_response.status_code = 400
        mock_response.aread = AsyncMock(
            return_value=f'{{"error": {{"message": "{long_message}"}}}}'.encode("utf-8")
        )

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            with pytest.raises(FiberValidationError) as exc_info:
                await fiber_client.chat([ChatMessage.user("Test long error")])

            # Should handle long messages without issues
            error_str = str(exc_info.value)
            assert len(error_str) > 0

    @pytest.mark.asyncio
    async def test_nested_error_structures(self, fiber_client):
        """Test handling of complex nested error structures."""
        complex_error = {
            "error": {
                "message": "Complex error",
                "details": {"nested": {"deep": {"error": "Deep nested error"}}},
            }
        }

        mock_response = AsyncMock()
        mock_response.status_code = 400
        mock_response.aread = AsyncMock(return_value=json.dumps(complex_error).encode("utf-8"))

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            with pytest.raises(FiberValidationError):
                await fiber_client.chat([ChatMessage.user("Test complex error")])

    @pytest.mark.asyncio
    async def test_concurrent_errors(self, fiber_client):
        """Test handling of concurrent errors."""
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.aread = AsyncMock(return_value=b'{"error": {"message": "Server error"}}')

        async def failing_task():
            return await fiber_client.chat([ChatMessage.user("Concurrent test")])

        # Apply patch to all concurrent requests
        with patch("httpx.AsyncClient.post", return_value=mock_response):
            # Run multiple failing tasks concurrently
            tasks = [failing_task() for _ in range(5)]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should result in errors
        for result in results:
            assert isinstance(result, FiberProviderError)


class TestErrorLogging:
    """Test error logging and metrics collection."""

    @pytest.mark.asyncio
    async def test_error_metrics_collection(self, fiber_client):
        """Test that errors are properly collected for metrics."""
        mock_response = AsyncMock()
        mock_response.status_code = 429
        mock_response.aread = AsyncMock(return_value=b'{"error": {"message": "Rate limit"}}')

        # Verify that error metrics were recorded properly
        if hasattr(fiber_client, "metrics") and fiber_client.metrics:
            # Get initial metrics state
            initial_metrics = fiber_client.metrics.get_metrics()
            initial_counters = initial_metrics.get_counters()
            initial_error_count = 0

            from llm_fiber.observability.metrics import FiberMetrics

            if FiberMetrics.ERROR_COUNT in initial_counters:
                for counter_value in initial_counters[FiberMetrics.ERROR_COUNT].values():
                    initial_error_count += counter_value.value

            # Trigger the error
            with patch("httpx.AsyncClient.post", return_value=mock_response):
                with pytest.raises(FiberRateLimitError):
                    await fiber_client.chat([ChatMessage.user("Test metrics")])

            # Get metrics after error
            final_metrics = fiber_client.metrics.get_metrics()
            final_counters = final_metrics.get_counters()
            final_error_count = 0

            if FiberMetrics.ERROR_COUNT in final_counters:
                for counter_value in final_counters[FiberMetrics.ERROR_COUNT].values():
                    final_error_count += counter_value.value

            # Verify error count increased
            assert final_error_count > initial_error_count, (
                f"Error count should have increased from {initial_error_count} "
                f"to {final_error_count}"
            )

            # Verify specific error type was recorded
            rate_limit_error_recorded = False
            for labels_key in final_counters.get(FiberMetrics.ERROR_COUNT, {}).keys():
                if "FiberRateLimitError" in labels_key or "RateLimitError" in labels_key:
                    rate_limit_error_recorded = True
                    break

            assert rate_limit_error_recorded, (
                "Rate limit error should be recorded with proper error type in metrics labels"
            )

        else:
            # Create temporary metrics collector to test behavior
            from llm_fiber.observability.metrics import FiberMetrics

            test_metrics = FiberMetrics()
            fiber_client.metrics = test_metrics

            # Trigger the error with temporary metrics
            with patch("httpx.AsyncClient.post", return_value=mock_response):
                with pytest.raises(FiberRateLimitError):
                    await fiber_client.chat([ChatMessage.user("Test with temp metrics")])

            # Verify metrics were collected
            metrics = test_metrics.get_metrics()
            counters = metrics.get_counters()

            assert FiberMetrics.ERROR_COUNT in counters, (
                "Error metrics should be collected during rate limit errors"
            )

            total_errors = sum(
                counter.value for counter in counters[FiberMetrics.ERROR_COUNT].values()
            )
            assert total_errors > 0, "At least one error should be recorded in metrics"

    @pytest.mark.asyncio
    async def test_error_structured_logging(self, fiber_client):
        """Test that errors generate structured log entries."""
        mock_response = AsyncMock()
        mock_response.status_code = 401
        mock_response.aread = AsyncMock(return_value=b'{"error": {"message": "Auth error"}}')

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            with pytest.raises(FiberAuthError):
                await fiber_client.chat([ChatMessage.user("Test logging")])

        # Verify structured logging occurred by capturing log calls
        if hasattr(fiber_client, "logger") and fiber_client.logger:
            # Capture the actual log calls made during the error
            with patch.object(fiber_client.logger, "error") as mock_error, patch.object(
                fiber_client.logger, "log_request_error"
            ) as mock_log_request_error:
                # Re-trigger the error to capture logging
                mock_response = AsyncMock()
                mock_response.status_code = 401
                mock_response.aread = AsyncMock(
                    return_value=b'{"error": {"message": "Auth error"}}'
                )

                with patch("httpx.AsyncClient.post", return_value=mock_response):
                    with pytest.raises(FiberAuthError):
                        await fiber_client.chat([ChatMessage.user("Test logging again")])

                # Verify structured log calls were made
                assert mock_error.called or mock_log_request_error.called, (
                    "Either error() or log_request_error() should have been called"
                )

                # Check that error logging included relevant context
                if mock_log_request_error.called:
                    call_args = mock_log_request_error.call_args
                    assert call_args is not None, (
                        "log_request_error should have been called with arguments"
                    )
                    # Verify the call included provider and error information

                    assert "provider" in str(call_args) or "openai" in str(call_args), (
                        "Log call should include provider information"
                    )

                elif mock_error.called:
                    call_args = mock_error.call_args
                    assert call_args is not None, "error() should have been called with arguments"
                    # Verify error message and context
                    message = call_args[0][0] if call_args[0] else ""

                    assert "failed" in message.lower() or "error" in message.lower(), (
                        "Error log message should indicate failure"
                    )
        else:
            # If no logger available, create a temporary one to test logging behavior
            from llm_fiber.observability.logging import FiberLogger

            test_logger = FiberLogger()
            fiber_client.logger = test_logger

            with patch.object(test_logger, "error") as mock_error:
                mock_response = AsyncMock()
                mock_response.status_code = 401
                mock_response.aread = AsyncMock(
                    return_value=b'{"error": {"message": "Auth error"}}'
                )

                with patch("httpx.AsyncClient.post", return_value=mock_response):
                    with pytest.raises(FiberAuthError):
                        await fiber_client.chat([ChatMessage.user("Test with temp logger")])

                # At minimum, verify some logging occurred
                assert mock_error.called, (
                    "Error logging should occur during authentication failures"
                )
