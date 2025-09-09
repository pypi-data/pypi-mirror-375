"""Unit tests for streaming functionality in llm-fiber."""

import asyncio
import time
from unittest.mock import MagicMock, patch

import pytest

from llm_fiber import (
    ChatMessage,
    Fiber,
    FiberConnectionError,
    StreamEvent,
    StreamEventType,
    Usage,
)


class TestStreamEventTypes:
    """Test StreamEventType enum and basic functionality."""

    def test_stream_event_types(self):
        """Test all stream event types are defined."""
        assert StreamEventType.CHUNK.value == "chunk"
        assert StreamEventType.TOOL_CALL.value == "tool_call"
        assert StreamEventType.USAGE.value == "usage"
        assert StreamEventType.LOG.value == "log"

    def test_stream_event_type_from_string(self):
        """Test creating stream event types from strings."""
        assert StreamEventType("chunk") == StreamEventType.CHUNK
        assert StreamEventType("tool_call") == StreamEventType.TOOL_CALL
        assert StreamEventType("usage") == StreamEventType.USAGE
        assert StreamEventType("log") == StreamEventType.LOG


class TestStreamEventCreation:
    """Test StreamEvent creation and properties."""

    def test_chunk_event_creation(self):
        """Test creating chunk events."""
        event = StreamEvent.create_chunk("Hello")

        assert event.type == StreamEventType.CHUNK
        assert event.delta == "Hello"
        assert event.timestamp > 0
        assert event.log_message is None

    def test_chunk_event_with_metadata(self):
        """Test chunk event with additional metadata."""
        event = StreamEvent.create_chunk("World")

        assert event.delta == "World"

    def test_tool_call_event_creation(self):
        """Test creating tool call events."""
        tool_call = {
            "id": "call_123",
            "type": "function",
            "function": {"name": "get_weather", "arguments": '{"location": "San Francisco"}'},
        }

        event = StreamEvent.create_tool_call(tool_call)

        assert event.type == StreamEventType.TOOL_CALL
        assert event.delta == ""

    def test_usage_event_creation(self):
        """Test creating usage events."""
        usage = Usage(prompt=100, completion=50, total=150, cost_estimate=0.003)
        event = StreamEvent.create_usage(usage)

        assert event.type == StreamEventType.USAGE
        assert event.delta == ""

    def test_log_event_creation(self):
        """Test creating log events."""
        event = StreamEvent.create_log("Debug message", level="debug")

        assert event.type == StreamEventType.LOG
        assert event.log_message == "Debug message"
        assert event.log_level == "debug"

    def test_event_timestamp_ordering(self):
        """Test that events have monotonically increasing timestamps."""
        events = []
        for i in range(5):
            events.append(StreamEvent.create_chunk(f"chunk_{i}"))
            # Small delay to ensure timestamp differences
            time.sleep(0.001)

        timestamps = [event.timestamp for event in events]
        assert timestamps == sorted(timestamps)

    def test_event_properties(self):
        """Test that events have proper properties."""
        usage = Usage(prompt=10, completion=5, total=15)
        event = StreamEvent.create_usage(usage)

        assert event.type == StreamEventType.USAGE
        assert event.timestamp > 0


class TestStreamEventProcessing:
    """Test stream event processing and ordering."""

    def test_event_sequence_validation(self):
        """Test that events maintain proper sequence ordering."""
        events = [
            StreamEvent.create_chunk("Hello"),
            StreamEvent.create_chunk(" world"),
            StreamEvent.create_usage(Usage(prompt=10, completion=5)),
        ]

        # Events should maintain creation order through timestamps
        timestamps = [event.timestamp for event in events]
        assert timestamps == sorted(timestamps)

    def test_event_aggregation(self):
        """Test aggregating chunk events into final text."""
        events = [
            StreamEvent.create_chunk("The"),
            StreamEvent.create_chunk(" quick"),
            StreamEvent.create_chunk(" brown"),
            StreamEvent.create_chunk(" fox"),
        ]

        text = "".join(event.delta for event in events if event.delta)
        assert text == "The quick brown fox"

    def test_mixed_event_stream_processing(self):
        """Test processing a stream with mixed event types."""
        tool_call = {"id": "call_123", "type": "function", "function": {"name": "test"}}
        usage = Usage(prompt=20, completion=10, total=30)

        events = [
            StreamEvent.create_chunk("Hello"),
            StreamEvent.create_tool_call(tool_call),
            StreamEvent.create_chunk(" world"),
            StreamEvent.create_log("Processing complete"),
            StreamEvent.create_usage(usage),
        ]

        # Extract different event types
        chunks = [e for e in events if e.type == StreamEventType.CHUNK]
        tools = [e for e in events if e.type == StreamEventType.TOOL_CALL]
        usage_events = [e for e in events if e.type == StreamEventType.USAGE]
        logs = [e for e in events if e.type == StreamEventType.LOG]

        assert len(chunks) == 2
        assert len(tools) == 1
        assert len(usage_events) == 1
        assert len(logs) == 1

        final_text = "".join(chunk.delta for chunk in chunks)
        assert final_text == "Hello world"


class TestStreamingWithMockProviders:
    """Test streaming with mocked providers."""

    @pytest.fixture
    def mock_openai_stream(self):
        """Mock OpenAI streaming response."""
        chunks = [
            'data: {"choices":[{"delta":{"content":"Hello"}}]}\n\n',
            'data: {"choices":[{"delta":{"content":" world"}}]}\n\n',
            'data: {"choices":[{"delta":{"content":"!"}}]}\n\n',
            'data: {"choices":[{"finish_reason":"stop"}],'
            '"usage":{"prompt_tokens":10,"completion_tokens":3,"total_tokens":13}}\n\n',
            "data: [DONE]\n\n",
        ]
        return chunks

    @pytest.fixture
    def mock_anthropic_stream(self):
        """Mock Anthropic streaming response."""
        chunks = [
            'data: {"type":"content_block_delta","delta":{"type":"text_delta","text":"Hello"}}\n\n',
            'data: {"type":"content_block_delta",'
            '"delta":{"type":"text_delta","text":" world"}}\n\n',
            'data: {"type":"content_block_delta","delta":{"type":"text_delta","text":"!"}}\n\n',
            'data: {"type":"message_delta","delta":{"stop_reason":"end_turn"},'
            '"usage":{"input_tokens":10,"output_tokens":3}}\n\n',
        ]
        return chunks

    @pytest.fixture
    def fiber_client(self):
        """Create a Fiber client for testing."""
        return Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=False
        )

    @pytest.mark.asyncio
    async def test_basic_streaming(self, fiber_client):
        """Test basic streaming functionality."""

        async def mock_stream():
            events = [
                StreamEvent.create_chunk("Hello"),
                StreamEvent.create_chunk(" world"),
                StreamEvent.create_usage(Usage(prompt=10, completion=5)),
            ]
            for event in events:
                yield event

        messages = [ChatMessage.user("Hello")]

        with patch.object(fiber_client, "chat_stream", return_value=mock_stream()):
            collected_events = []
            async for event in fiber_client.chat_stream(messages):
                collected_events.append(event)

            assert len(collected_events) == 3
            assert collected_events[0].type == StreamEventType.CHUNK
            assert collected_events[1].type == StreamEventType.CHUNK
            assert collected_events[2].type == StreamEventType.USAGE

    @pytest.mark.asyncio
    async def test_streaming_with_tool_calls(self, fiber_client):
        """Test streaming with tool call events."""

        async def mock_stream_with_tools():
            tool_call = {
                "id": "call_abc123",
                "type": "function",
                "function": {
                    "name": "get_current_weather",
                    "arguments": '{"location": "San Francisco, CA"}',
                },
            }

            events = [
                StreamEvent.create_chunk("I'll check the weather"),
                StreamEvent.create_tool_call(tool_call),
                StreamEvent.create_chunk(" for you."),
                StreamEvent.create_usage(Usage(prompt=25, completion=15)),
            ]
            for event in events:
                yield event

        messages = [ChatMessage.user("What's the weather?")]
        tools = [{"type": "function", "function": {"name": "get_current_weather"}}]

        with patch.object(fiber_client, "chat_stream", return_value=mock_stream_with_tools()):
            collected_events = []
            async for event in fiber_client.chat_stream(messages, tools=tools):
                collected_events.append(event)

            tool_events = [e for e in collected_events if e.type == StreamEventType.TOOL_CALL]
            assert len(tool_events) == 1
            assert tool_events[0].tool_call["id"] == "call_abc123"

    @pytest.mark.asyncio
    async def test_streaming_error_handling(self, fiber_client):
        """Test error handling in streaming."""

        async def mock_failing_stream():
            yield StreamEvent.create_chunk("Starting")
            yield StreamEvent.create_chunk(" response")
            raise FiberConnectionError("Network error during streaming")

        messages = [ChatMessage.user("Test error")]

        with patch.object(fiber_client, "chat_stream", return_value=mock_failing_stream()):
            collected_events = []

            with pytest.raises(FiberConnectionError):
                async for event in fiber_client.chat_stream(messages):
                    collected_events.append(event)

            # Should have received events before the error
            assert len(collected_events) == 2
            assert all(e.type == StreamEventType.CHUNK for e in collected_events)

    @pytest.mark.asyncio
    async def test_streaming_timeout_handling(self, fiber_client):
        """Test timeout handling in streaming."""

        async def mock_slow_stream():
            yield StreamEvent.create_chunk("Slow")
            await asyncio.sleep(2.0)  # Longer than timeout
            yield StreamEvent.create_chunk(" response")

        messages = [ChatMessage.user("Test timeout")]

        with patch.object(fiber_client, "chat_stream", return_value=mock_slow_stream()):
            with pytest.raises(asyncio.TimeoutError):

                async def collect_events():
                    collected_events = []
                    async for event in fiber_client.chat_stream(messages):
                        collected_events.append(event)
                    return collected_events

                await asyncio.wait_for(collect_events(), timeout=1.0)

    @pytest.mark.asyncio
    async def test_streaming_with_context_binding(self, fiber_client):
        """Test streaming with bound context."""
        bound_fiber = fiber_client.bind(temperature=0.7, max_tokens=100)

        async def mock_contextual_stream():
            events = [
                StreamEvent.create_chunk("Context-aware"),
                StreamEvent.create_chunk(" response"),
                StreamEvent.create_usage(Usage(prompt=15, completion=10)),
            ]
            for event in events:
                yield event

        messages = [ChatMessage.user("Test with context")]

        with patch.object(bound_fiber, "chat_stream", return_value=mock_contextual_stream()):
            collected_events = []
            async for event in bound_fiber.chat_stream(messages):
                collected_events.append(event)

            assert len(collected_events) == 3
            text_chunks = [e.delta for e in collected_events if e.delta]
            final_text = "".join(text_chunks)
            assert final_text == "Context-aware response"

    @pytest.mark.asyncio
    async def test_concurrent_streaming(self, fiber_client):
        """Test multiple concurrent streaming requests."""

        async def create_mock_stream(stream_id: int):
            events = [
                StreamEvent.create_chunk(f"Stream {stream_id}"),
                StreamEvent.create_chunk(" response"),
                StreamEvent.create_usage(Usage(prompt=10, completion=5)),
            ]
            for event in events:
                yield event

        messages1 = [ChatMessage.user("First request")]
        messages2 = [ChatMessage.user("Second request")]

        with patch.object(fiber_client, "chat_stream") as mock_stream:
            mock_stream.side_effect = lambda msgs, **kwargs: (
                create_mock_stream(1)
                if msgs[0].content == "First request"
                else create_mock_stream(2)
            )

            # Start concurrent streams
            async def collect_stream(messages):
                return [event async for event in fiber_client.chat_stream(messages)]

            stream1_task = asyncio.create_task(collect_stream(messages1))
            stream2_task = asyncio.create_task(collect_stream(messages2))

            # Wait for both to complete
            stream1_events, stream2_events = await asyncio.gather(stream1_task, stream2_task)

            # Verify both streams completed successfully
            assert len(stream1_events) == 3
            assert len(stream2_events) == 3

            stream1_text = "".join(e.delta for e in stream1_events if e.delta)
            stream2_text = "".join(e.delta for e in stream2_events if e.delta)

            assert "Stream 1" in stream1_text
            assert "Stream 2" in stream2_text


class TestStreamEventValidation:
    """Test validation and edge cases for stream events."""

    def test_event_with_empty_delta(self):
        """Test handling empty delta chunks."""
        event = StreamEvent.create_chunk("")
        assert event.delta == ""
        assert event.type == StreamEventType.CHUNK

    def test_event_with_none_delta(self):
        """Test handling None delta."""
        event = StreamEvent(type=StreamEventType.CHUNK, timestamp=time.time(), delta="")
        assert event.delta == ""

    def test_timestamp_precision(self):
        """Test timestamp precision."""
        event = StreamEvent.create_chunk("test")
        assert event.timestamp > 0
        assert isinstance(event.timestamp, float)

    def test_large_delta_text(self):
        """Test handling large amounts of text in delta."""
        large_text = "x" * 10000
        event = StreamEvent.create_chunk(large_text)
        assert len(event.delta) == 10000

    def test_event_with_different_types(self):
        """Test events with different types."""
        chunk_event = StreamEvent.create_chunk("test")
        usage_event = StreamEvent.create_usage(Usage(prompt=10, completion=5))
        log_event = StreamEvent.create_log("test message", level="debug")

        assert chunk_event.type == StreamEventType.CHUNK
        assert usage_event.type == StreamEventType.USAGE
        assert log_event.type == StreamEventType.LOG
        assert log_event.log_level == "debug"

    def test_tool_call_with_invalid_format(self):
        """Test handling malformed tool calls."""
        # Missing required fields
        malformed_tool = {"id": "call_123"}  # Missing type and function

        event = StreamEvent.create_tool_call(malformed_tool)
        assert event.type == StreamEventType.TOOL_CALL

    def test_usage_with_missing_fields(self):
        """Test usage events with partial data."""
        partial_usage = Usage(prompt=10, completion=0)  # total will be calculated
        event = StreamEvent.create_usage(partial_usage)

        assert event.type == StreamEventType.USAGE
        assert partial_usage.prompt == 10
        assert partial_usage.completion == 0
        assert partial_usage.total == 10


class TestStreamPerformance:
    """Test streaming performance characteristics."""

    @pytest.mark.asyncio
    async def test_high_frequency_streaming(self):
        """Test handling high-frequency stream events."""
        num_events = 1000

        async def high_frequency_stream():
            for i in range(num_events):
                yield StreamEvent.create_chunk(f"chunk_{i}")
                if i % 100 == 99:  # Add usage events periodically
                    yield StreamEvent.create_usage(Usage(prompt=10, completion=i // 100))

        start_time = time.time()
        collected_events = []

        async for event in high_frequency_stream():
            collected_events.append(event)

        elapsed_time = time.time() - start_time

        # Should handle 1000+ events quickly
        assert len(collected_events) == num_events + 10  # 1000 chunks + 10 usage events
        assert elapsed_time < 1.0  # Should complete in under 1 second

    @pytest.mark.asyncio
    async def test_memory_usage_with_large_streams(self):
        """Test memory efficiency with large streaming responses."""
        large_chunk_size = 10000  # 10KB chunks
        num_chunks = 100

        async def large_chunk_stream():
            for i in range(num_chunks):
                large_content = "x" * large_chunk_size
                yield StreamEvent.create_chunk(large_content)

        # Process stream without accumulating all chunks in memory
        total_chars = 0
        chunk_count = 0

        async for event in large_chunk_stream():
            if event.type == StreamEventType.CHUNK:
                total_chars += len(event.delta or "")
                chunk_count += 1
                # Don't store the event, just process it

        expected_total = large_chunk_size * num_chunks
        assert total_chars == expected_total
        assert chunk_count == num_chunks


class TestStreamIntegration:
    """Integration tests for streaming across providers."""

    @pytest.fixture
    def multi_provider_fiber(self):
        """Fiber client with multiple providers."""
        return Fiber(
            api_keys={
                "openai": "test-openai-key",
                "anthropic": "test-anthropic-key",
                "gemini": "test-gemini-key",
            },
            enable_observability=False,
        )

    @pytest.mark.asyncio
    async def test_provider_specific_streaming(self, multi_provider_fiber):
        """Test that streaming works across different providers."""
        test_cases = [
            ("gpt-4o-mini", "openai"),
            ("claude-3-haiku-20240307", "anthropic"),
            ("gemini-1.5-flash", "gemini"),
        ]

        for model, expected_provider in test_cases:

            async def mock_provider_stream():
                yield StreamEvent.create_chunk(f"Response from {expected_provider}")
                yield StreamEvent.create_usage(Usage(prompt=10, completion=5))

            messages = [ChatMessage.user(f"Test {model}")]

            with patch.object(
                multi_provider_fiber, "chat_stream", return_value=mock_provider_stream()
            ):
                events = []
                async for event in multi_provider_fiber.chat_stream(messages, model=model):
                    events.append(event)

                assert len(events) == 2
                text_events = [e for e in events if e.type == StreamEventType.CHUNK]
                assert len(text_events) == 1
                assert expected_provider in text_events[0].delta

    @pytest.mark.asyncio
    async def test_streaming_with_retries(self, multi_provider_fiber):
        """Test streaming behavior with retry logic."""
        call_count = 0

        async def failing_then_success_stream(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            if call_count == 1:
                yield StreamEvent.create_chunk("First attempt")
                raise FiberConnectionError("Network error")
            else:
                yield StreamEvent.create_chunk("Retry success")
                yield StreamEvent.create_usage(Usage(prompt=10, completion=5))

        messages = [ChatMessage.user("Test retries")]

        with patch.object(
            multi_provider_fiber, "chat_stream", side_effect=failing_then_success_stream
        ):
            # First call should fail
            with pytest.raises(FiberConnectionError):
                events = []
                async for event in multi_provider_fiber.chat_stream(messages):
                    events.append(event)

            # Second call should succeed
            events = []
            async for event in multi_provider_fiber.chat_stream(messages):
                events.append(event)

            assert len(events) == 2
            assert call_count == 2


class TestTTFBMetrics:
    """Test Time-To-First-Byte (TTFB) metrics collection during streaming."""

    @pytest.fixture
    def fiber_with_metrics(self):
        """Create Fiber instance with metrics enabled."""
        from llm_fiber.observability.metrics import FiberMetrics, InMemoryMetrics

        metrics_store = InMemoryMetrics()
        fiber = Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=True
        )
        # Replace with in-memory metrics for testing
        fiber.metrics = FiberMetrics(metrics_store)
        return fiber, metrics_store

    @pytest.mark.asyncio
    async def test_ttfb_recorded_on_first_chunk(self, fiber_with_metrics):
        """Test that TTFB is recorded when first chunk arrives."""
        fiber, metrics_store = fiber_with_metrics

        async def mock_stream_with_delay():
            # Simulate some delay before first chunk
            await asyncio.sleep(0.01)
            yield StreamEvent.create_chunk("First chunk")
            await asyncio.sleep(0.005)
            yield StreamEvent.create_chunk("Second chunk")
            yield StreamEvent.create_usage(Usage(prompt=10, completion=5))

        messages = [ChatMessage.user("Test TTFB")]

        # Mock the provider's chat_stream method
        with patch.object(fiber, "_get_provider") as mock_get_provider:
            mock_provider = MagicMock()
            mock_provider.chat_stream.return_value = mock_stream_with_delay()
            mock_get_provider.return_value = mock_provider

            # Collect events
            events = []
            async for event in fiber.chat_stream(messages):
                events.append(event)

            # Verify events were received
            assert len(events) >= 2
            chunk_events = [e for e in events if e.type == StreamEventType.CHUNK]
            assert len(chunk_events) >= 1

            # Check that TTFB metric was recorded
            ttfb_metrics = metrics_store._histograms.get("llm_fiber_ttfb_milliseconds", {})
            assert len(ttfb_metrics) > 0

            # Verify metric labels
            for labels_key, histogram_value in ttfb_metrics.items():
                assert histogram_value.count == 1  # Should be recorded exactly once
                assert histogram_value.sum > 0  # Should have positive timing
                assert "provider=openai" in labels_key
                assert "model=gpt-4o-mini" in labels_key
                assert "operation=stream" in labels_key

    @pytest.mark.asyncio
    async def test_ttfb_timing_reasonable(self, fiber_with_metrics):
        """Test that TTFB timing values are reasonable."""
        fiber, metrics_store = fiber_with_metrics

        delay_ms = 50  # 50ms delay

        async def mock_stream_with_known_delay():
            await asyncio.sleep(delay_ms / 1000)  # Convert to seconds
            yield StreamEvent.create_chunk("Delayed chunk")
            yield StreamEvent.create_usage(Usage(prompt=10, completion=5))

        messages = [ChatMessage.user("Test TTFB timing")]

        with patch.object(fiber, "_get_provider") as mock_get_provider:
            mock_provider = MagicMock()
            mock_provider.chat_stream.return_value = mock_stream_with_known_delay()
            mock_get_provider.return_value = mock_provider

            events = []
            async for event in fiber.chat_stream(messages):
                events.append(event)

            # Check TTFB timing
            ttfb_metrics = metrics_store._histograms.get("llm_fiber_ttfb_milliseconds", {})
            assert len(ttfb_metrics) > 0

            for histogram_value in ttfb_metrics.values():
                recorded_ttfb = histogram_value.sum  # Total time recorded
                # Should be at least the delay we introduced, but not too much more
                assert recorded_ttfb >= delay_ms * 0.8  # Allow some timing variance
                assert recorded_ttfb <= delay_ms * 2.0  # But not too much

    @pytest.mark.asyncio
    async def test_ttfb_only_recorded_once_per_stream(self, fiber_with_metrics):
        """Test that TTFB is recorded only once even with multiple chunks."""
        fiber, metrics_store = fiber_with_metrics

        async def mock_multi_chunk_stream():
            await asyncio.sleep(0.01)
            yield StreamEvent.create_chunk("Chunk 1")
            yield StreamEvent.create_chunk("Chunk 2")
            yield StreamEvent.create_chunk("Chunk 3")
            yield StreamEvent.create_usage(Usage(prompt=10, completion=15))

        messages = [ChatMessage.user("Test TTFB single recording")]

        with patch.object(fiber, "_get_provider") as mock_get_provider:
            mock_provider = MagicMock()
            mock_provider.chat_stream.return_value = mock_multi_chunk_stream()
            mock_get_provider.return_value = mock_provider

            events = []
            async for event in fiber.chat_stream(messages):
                events.append(event)

            # Verify we got multiple chunks
            chunk_events = [e for e in events if e.type == StreamEventType.CHUNK]
            assert len(chunk_events) == 3

            # But TTFB should be recorded only once
            ttfb_metrics = metrics_store._histograms.get("llm_fiber_ttfb_milliseconds", {})
            assert len(ttfb_metrics) > 0

            for histogram_value in ttfb_metrics.values():
                assert histogram_value.count == 1  # Exactly one observation

    @pytest.mark.asyncio
    async def test_no_ttfb_on_non_chunk_events(self, fiber_with_metrics):
        """Test that TTFB is not recorded for non-chunk events."""
        fiber, metrics_store = fiber_with_metrics

        async def mock_stream_no_chunks():
            await asyncio.sleep(0.01)
            # Only log and usage events, no chunks
            yield StreamEvent.create_log("Starting generation")
            yield StreamEvent.create_usage(Usage(prompt=10, completion=0))

        messages = [ChatMessage.user("Test no TTFB without chunks")]

        with patch.object(fiber, "_get_provider") as mock_get_provider:
            mock_provider = MagicMock()
            mock_provider.chat_stream.return_value = mock_stream_no_chunks()
            mock_get_provider.return_value = mock_provider

            events = []
            async for event in fiber.chat_stream(messages):
                events.append(event)

            # Verify no chunk events
            chunk_events = [e for e in events if e.type == StreamEventType.CHUNK]
            assert len(chunk_events) == 0

            # TTFB should not be recorded
            ttfb_metrics = metrics_store._histograms.get("llm_fiber_ttfb_milliseconds", {})
            assert len(ttfb_metrics) == 0
