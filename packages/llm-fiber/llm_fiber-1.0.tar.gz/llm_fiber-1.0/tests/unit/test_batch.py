"""Unit tests for batch operations functionality."""

import asyncio
import time

import pytest

from llm_fiber.batch import (
    BatchConfig,
    BatchError,
    BatchProcessor,
    BatchRequest,
    BatchResult,
    BatchStrategy,
    BatchSummary,
    create_batch_from_conversations,
    create_batch_from_prompts,
    create_batch_request,
)
from llm_fiber.types import ChatMessage, ChatResult, FiberError, Usage


class TestBatchStrategy:
    """Test BatchStrategy enum functionality."""

    def test_batch_strategy_values(self):
        """Test batch strategy enum values."""
        assert BatchStrategy.CONCURRENT.value == "concurrent"
        assert BatchStrategy.SEQUENTIAL.value == "sequential"
        assert BatchStrategy.ADAPTIVE.value == "adaptive"

    def test_batch_strategy_from_string(self):
        """Test creating batch strategy from string."""
        assert BatchStrategy("concurrent") == BatchStrategy.CONCURRENT
        assert BatchStrategy("sequential") == BatchStrategy.SEQUENTIAL
        assert BatchStrategy("adaptive") == BatchStrategy.ADAPTIVE


class TestBatchConfig:
    """Test BatchConfig functionality."""

    def test_batch_config_defaults(self):
        """Test batch config default values."""
        config = BatchConfig()
        assert config.max_concurrent == 10
        assert config.strategy == BatchStrategy.CONCURRENT
        assert config.return_exceptions is True
        assert config.timeout_per_request == 60.0
        assert config.fail_fast is False

    def test_batch_config_custom_values(self):
        """Test batch config with custom values."""
        config = BatchConfig(
            max_concurrent=5,
            strategy=BatchStrategy.SEQUENTIAL,
            return_exceptions=False,
            timeout_per_request=30.0,
            fail_fast=True,
        )
        assert config.max_concurrent == 5
        assert config.strategy == BatchStrategy.SEQUENTIAL
        assert config.return_exceptions is False
        assert config.timeout_per_request == 30.0
        assert config.fail_fast is True

    def test_batch_config_validation(self):
        """Test batch config validation."""
        # Invalid max_concurrent
        with pytest.raises(ValueError):
            BatchConfig(max_concurrent=0)

        with pytest.raises(ValueError):
            BatchConfig(max_concurrent=-1)

        # Invalid timeout
        with pytest.raises(ValueError):
            BatchConfig(timeout_per_request=0.0)

        with pytest.raises(ValueError):
            BatchConfig(timeout_per_request=-1.0)


class TestBatchRequest:
    """Test BatchRequest functionality."""

    def test_batch_request_creation(self):
        """Test creating a batch request."""
        messages = [ChatMessage.user("Hello")]
        request = BatchRequest(
            id="req_001", messages=messages, model="gpt-4o-mini", temperature=0.7, max_tokens=100
        )

        assert request.id == "req_001"
        assert request.messages == messages
        assert request.model == "gpt-4o-mini"
        assert request.temperature == 0.7
        assert request.max_tokens == 100

    def test_batch_request_with_kwargs(self):
        """Test batch request with additional kwargs."""
        messages = [ChatMessage.user("Hello")]
        request = BatchRequest(
            id="req_002",
            messages=messages,
            model="claude-3-haiku",
            custom_param="value",
            another_param=42,
        )

        assert request.custom_param == "value"
        assert request.another_param == 42

    def test_batch_request_to_dict(self):
        """Test converting batch request to dict."""
        messages = [ChatMessage.user("Hello")]
        request = BatchRequest(
            id="req_003", messages=messages, model="gpt-4o-mini", temperature=0.5
        )

        request_dict = request.to_dict()
        assert request_dict["messages"] == messages
        assert request_dict["model"] == "gpt-4o-mini"
        assert request_dict["temperature"] == 0.5
        assert "id" not in request_dict  # ID should not be in the request dict


class TestBatchResult:
    """Test BatchResult functionality."""

    def test_batch_result_success(self):
        """Test successful batch result."""
        usage = Usage(prompt=10, completion=20)
        chat_result = ChatResult(
            text="Hello world", tool_calls=[], finish_reason="stop", usage=usage, raw={"id": "test"}
        )

        result = BatchResult(id="req_001", result=chat_result, error=None, duration_ms=150.5)

        assert result.id == "req_001"
        assert result.result == chat_result
        assert result.error is None
        assert result.duration_ms == 150.5
        assert result.is_success is True

    def test_batch_result_error(self):
        """Test error batch result."""
        error = FiberError("Something went wrong")
        result = BatchResult(id="req_002", result=None, error=error, duration_ms=50.0)

        assert result.id == "req_002"
        assert result.result is None
        assert result.error == error
        assert result.duration_ms == 50.0
        assert result.is_success is False


class TestBatchSummary:
    """Test BatchSummary functionality."""

    def test_batch_summary_all_success(self):
        """Test batch summary with all successful requests."""
        usage1 = Usage(prompt=10, completion=20, cost_estimate=0.001)
        usage2 = Usage(prompt=15, completion=25, cost_estimate=0.002)

        result1 = BatchResult(
            "req_001", ChatResult("Response 1", [], "stop", usage1, {}), None, 100.0
        )
        result2 = BatchResult(
            "req_002", ChatResult("Response 2", [], "stop", usage2, {}), None, 150.0
        )

        summary = BatchSummary([result1, result2])

        assert summary.total_requests == 2
        assert summary.successful_requests == 2
        assert summary.failed_requests == 0
        assert summary.total_duration_ms == 250.0
        assert summary.average_duration_ms == 125.0
        assert summary.total_usage.prompt == 25
        assert summary.total_usage.completion == 45
        assert summary.total_usage.total == 70
        assert summary.total_usage.cost_estimate == 0.003

    def test_batch_summary_mixed_results(self):
        """Test batch summary with mixed success/failure results."""
        usage1 = Usage(prompt=10, completion=20, cost_estimate=0.001)
        error = FiberError("Request failed")

        result1 = BatchResult(
            "req_001", ChatResult("Response 1", [], "stop", usage1, {}), None, 100.0
        )
        result2 = BatchResult("req_002", None, error, 50.0)

        summary = BatchSummary([result1, result2])

        assert summary.total_requests == 2
        assert summary.successful_requests == 1
        assert summary.failed_requests == 1
        assert summary.total_duration_ms == 150.0
        assert summary.average_duration_ms == 75.0
        assert summary.total_usage.prompt == 10
        assert summary.total_usage.completion == 20
        assert summary.total_usage.total == 30
        assert summary.total_usage.cost_estimate == 0.001

    def test_batch_summary_all_failures(self):
        """Test batch summary with all failed requests."""
        error1 = FiberError("Error 1")
        error2 = FiberError("Error 2")

        result1 = BatchResult("req_001", None, error1, 25.0)
        result2 = BatchResult("req_002", None, error2, 30.0)

        summary = BatchSummary([result1, result2])

        assert summary.total_requests == 2
        assert summary.successful_requests == 0
        assert summary.failed_requests == 2
        assert summary.total_duration_ms == 55.0
        assert summary.average_duration_ms == 27.5
        assert summary.total_usage.prompt == 0
        assert summary.total_usage.completion == 0
        assert summary.total_usage.total == 0
        assert summary.total_usage.cost_estimate == 0.0

    def test_batch_summary_empty(self):
        """Test batch summary with empty results."""
        summary = BatchSummary([])

        assert summary.total_requests == 0
        assert summary.successful_requests == 0
        assert summary.failed_requests == 0
        assert summary.total_duration_ms == 0.0
        assert summary.average_duration_ms == 0.0


class TestBatchProcessor:
    """Test BatchProcessor functionality."""

    @pytest.fixture
    def mock_chat_function(self):
        """Create a mock chat function."""

        async def mock_chat(**kwargs):
            # Simulate processing time
            await asyncio.sleep(0.01)

            messages = kwargs.get("messages", [])
            content = messages[0].content if messages else "default"

            usage = Usage(prompt=10, completion=20, cost_estimate=0.001)
            return ChatResult(
                text=f"Response to: {content}",
                tool_calls=[],
                finish_reason="stop",
                usage=usage,
                raw={"id": f"test-{content}"},
            )

        return mock_chat

    @pytest.fixture
    def failing_chat_function(self):
        """Create a mock chat function that always fails."""

        async def failing_chat(**kwargs):
            await asyncio.sleep(0.01)
            raise FiberError("Mock error")

        return failing_chat

    @pytest.fixture
    def selective_failing_chat_function(self):
        """Create a mock chat function that fails for specific inputs."""

        async def selective_failing_chat(**kwargs):
            messages = kwargs.get("messages", [])
            content = messages[0].content if messages else ""

            await asyncio.sleep(0.01)

            if "fail" in content.lower():
                raise FiberError(f"Intentional failure for: {content}")

            usage = Usage(prompt=10, completion=20, cost_estimate=0.001)
            return ChatResult(
                text=f"Response to: {content}",
                tool_calls=[],
                finish_reason="stop",
                usage=usage,
                raw={"id": f"test-{content}"},
            )

        return selective_failing_chat

    @pytest.mark.asyncio
    async def test_batch_processor_concurrent_success(self, mock_chat_function):
        """Test batch processor with concurrent strategy - all success."""
        requests = [
            BatchRequest("req_001", [ChatMessage.user("Hello")], "gpt-4o-mini"),
            BatchRequest("req_002", [ChatMessage.user("Hi")], "gpt-4o-mini"),
            BatchRequest("req_003", [ChatMessage.user("Hey")], "gpt-4o-mini"),
        ]

        config = BatchConfig(max_concurrent=2, strategy=BatchStrategy.CONCURRENT)
        processor = BatchProcessor(config)

        results = await processor.process_batch(requests, mock_chat_function)

        assert len(results) == 3
        assert all(result.is_success for result in results)

        # Check that responses correspond to requests
        result_map = {result.id: result for result in results}
        assert "Response to: Hello" in result_map["req_001"].result.text
        assert "Response to: Hi" in result_map["req_002"].result.text
        assert "Response to: Hey" in result_map["req_003"].result.text

    @pytest.mark.asyncio
    async def test_batch_processor_sequential_success(self, mock_chat_function):
        """Test batch processor with sequential strategy."""
        requests = [
            BatchRequest("req_001", [ChatMessage.user("First")], "gpt-4o-mini"),
            BatchRequest("req_002", [ChatMessage.user("Second")], "gpt-4o-mini"),
        ]

        config = BatchConfig(strategy=BatchStrategy.SEQUENTIAL)
        processor = BatchProcessor(config)

        start_time = time.time()
        results = await processor.process_batch(requests, mock_chat_function)
        end_time = time.time()

        assert len(results) == 2
        assert all(result.is_success for result in results)

        # Sequential should take longer than concurrent for the same requests
        # (though this is a rough check due to mock timing)
        assert end_time - start_time >= 0.02  # At least 2 * 0.01s mock delay

    @pytest.mark.asyncio
    async def test_batch_processor_concurrency_limit(self, mock_chat_function):
        """Test that concurrency limit is respected."""
        # Create many requests
        requests = [
            BatchRequest(f"req_{i:03d}", [ChatMessage.user(f"Message {i}")], "gpt-4o-mini")
            for i in range(10)
        ]

        # Set low concurrency limit
        config = BatchConfig(max_concurrent=2, strategy=BatchStrategy.CONCURRENT)
        processor = BatchProcessor(config)

        # Mock to track concurrent executions
        active_count = 0
        max_concurrent = 0

        async def tracking_chat(**kwargs):
            nonlocal active_count, max_concurrent
            active_count += 1
            max_concurrent = max(max_concurrent, active_count)

            await asyncio.sleep(0.05)  # Longer delay to ensure overlap

            active_count -= 1

            messages = kwargs.get("messages", [])
            content = messages[0].content if messages else "default"
            usage = Usage(prompt=10, completion=20)
            return ChatResult(f"Response to: {content}", [], "stop", usage, {})

        results = await processor.process_batch(requests, tracking_chat)

        assert len(results) == 10
        assert all(result.is_success for result in results)
        assert max_concurrent <= 2  # Should respect concurrency limit

    @pytest.mark.asyncio
    async def test_batch_processor_error_handling(self, selective_failing_chat_function):
        """Test batch processor error handling."""
        requests = [
            BatchRequest("req_001", [ChatMessage.user("Success message")], "gpt-4o-mini"),
            BatchRequest("req_002", [ChatMessage.user("This should fail")], "gpt-4o-mini"),
            BatchRequest("req_003", [ChatMessage.user("Another success")], "gpt-4o-mini"),
        ]

        config = BatchConfig(return_exceptions=True)
        processor = BatchProcessor(config)

        results = await processor.process_batch(requests, selective_failing_chat_function)

        assert len(results) == 3

        # Check results
        result_map = {result.id: result for result in results}
        assert result_map["req_001"].is_success
        assert not result_map["req_002"].is_success
        assert result_map["req_003"].is_success

        # Check error details
        assert result_map["req_002"].error is not None
        assert "Intentional failure" in str(result_map["req_002"].error)

    @pytest.mark.asyncio
    async def test_batch_processor_fail_fast(self, selective_failing_chat_function):
        """Test batch processor fail-fast behavior."""
        requests = [
            BatchRequest("req_001", [ChatMessage.user("Success message")], "gpt-4o-mini"),
            BatchRequest("req_002", [ChatMessage.user("This should fail")], "gpt-4o-mini"),
            BatchRequest("req_003", [ChatMessage.user("Another success")], "gpt-4o-mini"),
        ]

        config = BatchConfig(fail_fast=True, return_exceptions=False)
        processor = BatchProcessor(config)

        with pytest.raises(BatchError):
            await processor.process_batch(requests, selective_failing_chat_function)

    @pytest.mark.asyncio
    async def test_batch_processor_timeout_handling(self):
        """Test batch processor timeout handling."""

        async def slow_chat(**kwargs):
            await asyncio.sleep(0.2)  # Longer than timeout
            return ChatResult("Slow response", [], "stop", Usage(10, 20), {})

        requests = [
            BatchRequest("req_001", [ChatMessage.user("Fast")], "gpt-4o-mini"),
        ]

        config = BatchConfig(timeout_per_request=0.1)  # Short timeout
        processor = BatchProcessor(config)

        results = await processor.process_batch(requests, slow_chat)

        assert len(results) == 1
        assert not results[0].is_success
        assert (
            "timeout" in str(results[0].error).lower()
            or "timed out" in str(results[0].error).lower()
        )

    @pytest.mark.asyncio
    async def test_batch_processor_adaptive_strategy(self, selective_failing_chat_function):
        """Test batch processor adaptive strategy."""
        # Create requests with mixed success/failure patterns
        requests = [
            BatchRequest("req_001", [ChatMessage.user("Success 1")], "gpt-4o-mini"),
            BatchRequest("req_002", [ChatMessage.user("Success 2")], "gpt-4o-mini"),
            BatchRequest("req_003", [ChatMessage.user("This should fail")], "gpt-4o-mini"),
            BatchRequest("req_004", [ChatMessage.user("Success 3")], "gpt-4o-mini"),
            BatchRequest("req_005", [ChatMessage.user("Another fail")], "gpt-4o-mini"),
        ]

        config = BatchConfig(strategy=BatchStrategy.ADAPTIVE, max_concurrent=3)
        processor = BatchProcessor(config)

        results = await processor.process_batch(requests, selective_failing_chat_function)

        assert len(results) == 5

        # Should have some successes and some failures
        successful = [r for r in results if r.is_success]
        failed = [r for r in results if not r.is_success]

        assert len(successful) == 3
        assert len(failed) == 2

    @pytest.mark.asyncio
    async def test_batch_processor_empty_batch(self, mock_chat_function):
        """Test batch processor with empty batch."""
        config = BatchConfig()
        processor = BatchProcessor(config)

        results = await processor.process_batch([], mock_chat_function)

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_batch_processor_single_request(self, mock_chat_function):
        """Test batch processor with single request."""
        requests = [BatchRequest("req_001", [ChatMessage.user("Single message")], "gpt-4o-mini")]

        config = BatchConfig()
        processor = BatchProcessor(config)

        results = await processor.process_batch(requests, mock_chat_function)

        assert len(results) == 1
        assert results[0].is_success
        assert results[0].id == "req_001"


class TestBatchHelperFunctions:
    """Test batch helper functions."""

    def test_create_batch_request(self):
        """Test creating individual batch request."""
        messages = [ChatMessage.user("Hello")]
        request = create_batch_request(
            messages=messages,
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=100,
            request_id="custom_id",
        )

        assert request.id == "custom_id"
        assert request.messages == messages
        assert request.model == "gpt-4o-mini"
        assert request.temperature == 0.7
        assert request.max_tokens == 100

    def test_create_batch_request_auto_id(self):
        """Test creating batch request with auto-generated ID."""
        messages = [ChatMessage.user("Hello")]
        request = create_batch_request(messages=messages, model="gpt-4o-mini")

        assert request.id is not None
        assert request.id.startswith("batch_req_")
        assert len(request.id) > 10  # Should have timestamp or unique part

    def test_create_batch_from_prompts(self):
        """Test creating batch from list of prompts."""
        prompts = ["What is Python?", "What is JavaScript?", "What is Go?"]

        requests = create_batch_from_prompts(
            prompts, model="claude-3-haiku", temperature=0.5, max_tokens=200
        )

        assert len(requests) == 3

        for i, request in enumerate(requests):
            assert len(request.messages) == 1
            assert request.messages[0].role == "user"
            assert request.messages[0].content == prompts[i]
            assert request.model == "claude-3-haiku"
            assert request.temperature == 0.5
            assert request.max_tokens == 200

    def test_create_batch_from_prompts_with_system(self):
        """Test creating batch from prompts with system message."""
        prompts = ["Question 1", "Question 2"]
        system_message = "You are a helpful assistant."

        requests = create_batch_from_prompts(prompts, model="gpt-4o", system_message=system_message)

        assert len(requests) == 2

        for request in requests:
            assert len(request.messages) == 2
            assert request.messages[0].role == "system"
            assert request.messages[0].content == system_message
            assert request.messages[1].role == "user"

    def test_create_batch_from_conversations(self):
        """Test creating batch from list of conversations."""
        conversations = [
            [
                ChatMessage.user("What is 2+2?"),
                ChatMessage.assistant("2+2 equals 4."),
                ChatMessage.user("What about 3+3?"),
            ],
            [
                ChatMessage.user("Hello!"),
                ChatMessage.assistant("Hi there!"),
                ChatMessage.user("How are you?"),
            ],
        ]

        requests = create_batch_from_conversations(
            conversations, model="gpt-4o-mini", temperature=0.8
        )

        assert len(requests) == 2

        for i, request in enumerate(requests):
            assert request.messages == conversations[i]
            assert request.model == "gpt-4o-mini"
            assert request.temperature == 0.8

    def test_create_batch_from_conversations_with_system(self):
        """Test creating batch from conversations with system message."""
        conversations = [[ChatMessage.user("Question 1")], [ChatMessage.user("Question 2")]]
        system_message = "You are an expert."

        requests = create_batch_from_conversations(
            conversations, model="claude-3-sonnet", system_message=system_message
        )

        assert len(requests) == 2

        for request in requests:
            assert request.messages[0].role == "system"
            assert request.messages[0].content == system_message
            assert len(request.messages) == 2  # system + original user message


class TestBatchIntegration:
    """Test batch operation integration scenarios."""

    @pytest.mark.asyncio
    async def test_batch_with_summary_statistics(self):
        """Test complete batch processing with summary statistics."""

        async def mock_chat(**kwargs):
            messages = kwargs.get("messages", [])
            content = messages[0].content if messages else "default"

            # Simulate variable response times
            if "slow" in content.lower():
                await asyncio.sleep(0.05)
            else:
                await asyncio.sleep(0.01)

            # Simulate variable token usage
            base_tokens = 50 if "long" in content.lower() else 20
            usage = Usage(
                prompt=base_tokens, completion=base_tokens // 2, cost_estimate=base_tokens * 0.0001
            )

            return ChatResult(
                text=f"Response to: {content}",
                tool_calls=[],
                finish_reason="stop",
                usage=usage,
                raw={"id": f"test-{hash(content)}"},
            )

        requests = [
            BatchRequest("req_001", [ChatMessage.user("Quick question")], "gpt-4o-mini"),
            BatchRequest("req_002", [ChatMessage.user("Long detailed question")], "gpt-4o-mini"),
            BatchRequest("req_003", [ChatMessage.user("Slow processing question")], "gpt-4o-mini"),
        ]

        config = BatchConfig(max_concurrent=2)
        processor = BatchProcessor(config)

        results = await processor.process_batch(requests, mock_chat)
        summary = BatchSummary(results)

        # Verify summary statistics
        assert summary.total_requests == 3
        assert summary.successful_requests == 3
        assert summary.failed_requests == 0
        assert summary.total_duration_ms > 0
        assert summary.average_duration_ms > 0
        assert summary.total_usage.prompt > 0
        assert summary.total_usage.completion > 0
        assert summary.total_usage.cost_estimate > 0

    @pytest.mark.asyncio
    async def test_batch_error_recovery_patterns(self):
        """Test batch processing with various error recovery patterns."""
        call_count = 0

        async def unreliable_chat(**kwargs):
            nonlocal call_count
            call_count += 1

            # Fail the first few calls, then succeed
            if call_count <= 2:
                raise FiberError(f"Temporary failure #{call_count}")

            messages = kwargs.get("messages", [])
            content = messages[0].content if messages else f"call_{call_count}"

            usage = Usage(prompt=10, completion=15, cost_estimate=0.001)
            return ChatResult(
                text=f"Success response to: {content}",
                tool_calls=[],
                finish_reason="stop",
                usage=usage,
                raw={"id": f"success-{call_count}"},
            )

        requests = [
            BatchRequest("req_001", [ChatMessage.user("Message 1")], "gpt-4o-mini"),
            BatchRequest("req_002", [ChatMessage.user("Message 2")], "gpt-4o-mini"),
            BatchRequest("req_003", [ChatMessage.user("Message 3")], "gpt-4o-mini"),
            BatchRequest("req_004", [ChatMessage.user("Message 4")], "gpt-4o-mini"),
        ]

        config = BatchConfig(return_exceptions=True, strategy=BatchStrategy.SEQUENTIAL)
        processor = BatchProcessor(config)

        results = await processor.process_batch(requests, unreliable_chat)

        # First two should fail, last two should succeed
        assert len(results) == 4
        assert not results[0].is_success
        assert not results[1].is_success
        assert results[2].is_success
        assert results[3].is_success

    @pytest.mark.asyncio
    async def test_batch_performance_characteristics(self):
        """Test batch processing performance characteristics."""

        async def timed_chat(**kwargs):
            # Consistent small delay to measure timing
            await asyncio.sleep(0.02)

            messages = kwargs.get("messages", [])
            content = messages[0].content if messages else "default"
            usage = Usage(prompt=25, completion=15, cost_estimate=0.002)

            return ChatResult(
                text=f"Timed response: {content}",
                tool_calls=[],
                finish_reason="stop",
                usage=usage,
                raw={"timing_test": True},
            )

        # Create requests for timing test
        requests = [
            BatchRequest(f"timing_{i}", [ChatMessage.user(f"Message {i}")], "gpt-4o-mini")
            for i in range(6)
        ]

        # Test concurrent vs sequential timing
        concurrent_config = BatchConfig(strategy=BatchStrategy.CONCURRENT, max_concurrent=3)
        sequential_config = BatchConfig(strategy=BatchStrategy.SEQUENTIAL)

        concurrent_processor = BatchProcessor(concurrent_config)
        sequential_processor = BatchProcessor(sequential_config)

        # Measure concurrent execution
        start = time.time()
        concurrent_results = await concurrent_processor.process_batch(requests, timed_chat)
        concurrent_time = time.time() - start

        # Reset for sequential test
        start = time.time()
        sequential_results = await sequential_processor.process_batch(requests, timed_chat)
        sequential_time = time.time() - start

        # Verify both succeed
        assert len(concurrent_results) == 6
        assert len(sequential_results) == 6
        assert all(r.is_success for r in concurrent_results)
        assert all(r.is_success for r in sequential_results)

        # Concurrent should be significantly faster for this workload
        assert concurrent_time < sequential_time * 0.8  # At least 20% faster

    def test_batch_request_id_generation(self):
        """Test that batch request IDs are unique."""
        requests = []
        for i in range(100):
            request = create_batch_request(
                messages=[ChatMessage.user(f"Message {i}")], model="gpt-4o-mini"
            )
            requests.append(request)

        # All IDs should be unique
        ids = [req.id for req in requests]
        assert len(ids) == len(set(ids))

        # IDs should follow expected pattern
        for request_id in ids:
            assert isinstance(request_id, str)
            assert len(request_id) > 0
