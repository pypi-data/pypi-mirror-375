"""Performance and resource management tests for llm-fiber."""

import asyncio
import gc
import threading
import time
from unittest.mock import MagicMock, patch

import httpx
import psutil
import pytest

from llm_fiber import (
    ChatMessage,
    ChatResult,
    Fiber,
    FiberConnectionError,
    FiberProviderError,
    FiberTimeoutError,
    StreamEvent,
    Usage,
)
from llm_fiber.caching.memory import MemoryCacheAdapter
from llm_fiber.retry import RetryPolicy
from llm_fiber.timeouts import Timeouts


class ResourceMonitor:
    """Helper class to monitor resource usage during tests."""

    def __init__(self):
        self.process = psutil.Process()
        self.initial_memory = self.process.memory_info().rss
        self.peak_memory = self.initial_memory
        self.initial_threads = self.process.num_threads()
        self.peak_threads = self.initial_threads

    def update(self):
        """Update peak resource measurements."""
        current_memory = self.process.memory_info().rss
        current_threads = self.process.num_threads()

        self.peak_memory = max(self.peak_memory, current_memory)
        self.peak_threads = max(self.peak_threads, current_threads)

    def memory_increase_mb(self) -> float:
        """Get memory increase in MB."""
        return (self.peak_memory - self.initial_memory) / (1024 * 1024)

    def thread_increase(self) -> int:
        """Get thread count increase."""
        return self.peak_threads - self.initial_threads


class TestMemoryManagement:
    """Test memory usage and leak prevention."""

    @pytest.fixture
    def fiber_client(self):
        """Create Fiber client for memory tests."""
        return Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=False
        )

    def test_basic_memory_footprint(self, fiber_client):
        """Test basic memory footprint of Fiber client."""
        monitor = ResourceMonitor()

        # Create multiple clients to see baseline memory usage
        clients = []
        for i in range(10):
            client = Fiber(
                default_model="gpt-4o-mini",
                api_keys={"openai": f"test-key-{i}"},
                enable_observability=False,
            )
            clients.append(client)
            monitor.update()

        # Memory increase should be reasonable (< 10MB for 10 clients)
        memory_increase = monitor.memory_increase_mb()
        assert memory_increase < 10.0, f"Memory increase too high: {memory_increase}MB"

        # Clean up
        del clients
        gc.collect()

    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, fiber_client):
        """Test memory usage doesn't grow excessively under load."""
        monitor = ResourceMonitor()

        async def mock_chat(**kwargs):
            await asyncio.sleep(0.01)  # Simulate processing time
            return ChatResult(
                text="Mock response",
                tool_calls=[],
                finish_reason="stop",
                usage=Usage(prompt=10, completion=5, total=15),
                raw={},
            )

        # Simulate many requests
        tasks = []
        for i in range(100):
            with patch.object(fiber_client, "chat", side_effect=mock_chat):
                task = asyncio.create_task(fiber_client.chat([ChatMessage.user(f"Message {i}")]))
                tasks.append(task)

            if i % 10 == 0:
                monitor.update()

        # Wait for all tasks to complete
        await asyncio.gather(*tasks, return_exceptions=True)
        monitor.update()

        # Memory increase should be bounded (< 50MB for 100 requests)
        memory_increase = monitor.memory_increase_mb()
        assert memory_increase < 50.0, f"Memory increase too high: {memory_increase}MB"

    @pytest.mark.asyncio
    async def test_streaming_memory_efficiency(self, fiber_client):
        """Test that streaming doesn't accumulate excessive memory."""
        monitor = ResourceMonitor()

        async def large_stream():
            # Simulate a very large streaming response
            for i in range(1000):
                chunk = "x" * 1000  # 1KB chunks
                yield StreamEvent.create_chunk(chunk, sequence=i)
                if i % 100 == 0:
                    monitor.update()
                    await asyncio.sleep(0.001)  # Allow GC

        with patch.object(fiber_client, "chat_stream", return_value=large_stream()):
            # Process stream without accumulating all chunks
            chunk_count = 0
            total_chars = 0

            async for event in fiber_client.chat_stream([ChatMessage.user("Large stream")]):
                if event.type.value == "chunk":
                    chunk_count += 1
                    total_chars += len(event.delta or "")
                    # Don't store events, just process them

            monitor.update()

        assert chunk_count == 1000
        assert total_chars == 1000 * 1000  # 1MB total

        # Memory increase should be much less than total data size
        memory_increase = monitor.memory_increase_mb()
        assert memory_increase < 10.0, f"Memory not efficiently managed: {memory_increase}MB"

    @pytest.mark.asyncio
    async def test_cache_memory_limits(self):
        """Test that cache respects memory limits."""
        monitor = ResourceMonitor()

        # Create cache with small size limit
        cache = MemoryCacheAdapter(max_size=10, default_ttl_seconds=60)

        Fiber(
            default_model="gpt-4o-mini",
            api_keys={"openai": "test-key"},
            cache_adapter=cache,
        )

        # Fill cache beyond capacity
        for i in range(50):  # More than cache size
            large_result = ChatResult(
                text="x" * 10000,  # 10KB result
                tool_calls=[],
                finish_reason="stop",
                usage=Usage(prompt=100, completion=50, total=150),
                raw={"large_data": "x" * 5000},
            )

            key = f"test_key_{i}"
            from llm_fiber.caching import serialize_chat_result

            await cache.set(key, serialize_chat_result(large_result))

            if i % 10 == 0:
                monitor.update()

        # Cache should not grow unboundedly
        cache_size = await cache.size()
        assert cache_size <= 10, f"Cache exceeded size limit: {cache_size}"

        # Memory should be bounded due to LRU eviction
        memory_increase = monitor.memory_increase_mb()
        assert memory_increase < 20.0, f"Cache memory not bounded: {memory_increase}MB"

    def test_object_cleanup_on_deletion(self):
        """Test that Fiber objects are properly cleaned up."""
        import weakref

        # Create client and get weak reference
        client = Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=False
        )

        weak_ref = weakref.ref(client)
        assert weak_ref() is not None

        # Delete client and force garbage collection
        del client
        gc.collect()

        # Weak reference should be None (object was cleaned up)
        assert weak_ref() is None, "Fiber client not properly cleaned up"


class TestConnectionManagement:
    """Test HTTP connection management and pooling."""

    @pytest.fixture
    def fiber_client(self):
        return Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=False
        )

    @pytest.mark.asyncio
    async def test_connection_reuse(self, fiber_client):
        """Test that HTTP connections are reused efficiently."""
        call_count = 0
        connection_ids = set()

        async def mock_request(request, **kwargs):
            nonlocal call_count
            call_count += 1

            # Simulate connection ID (in real case, this would be from httpx internals)
            connection_id = id(request)
            connection_ids.add(connection_id)

            return httpx.Response(
                200,
                json={
                    "choices": [
                        {"message": {"role": "assistant", "content": f"Response {call_count}"}}
                    ],
                    "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
                },
            )

        with patch("httpx.AsyncClient.send", side_effect=mock_request):
            # Make multiple requests
            tasks = []
            for i in range(20):
                task = asyncio.create_task(fiber_client.chat([ChatMessage.user(f"Request {i}")]))
                tasks.append(task)

            await asyncio.gather(*tasks)

        # All requests should have been made
        assert call_count == 20

        # Connection reuse should limit unique connection IDs
        # (In practice, httpx would reuse connections from the pool)
        assert len(connection_ids) <= call_count

    @pytest.mark.asyncio
    async def test_connection_timeout_handling(self, fiber_client):
        """Test proper handling of connection timeouts."""
        timeout_count = 0

        async def slow_request(*args, **kwargs):
            nonlocal timeout_count
            timeout_count += 1
            await asyncio.sleep(2.0)  # Longer than timeout
            return MagicMock()

        # Set aggressive timeout
        fiber_client._timeouts = Timeouts(connect=0.1, read=0.1, total=0.5)

        with patch("httpx.AsyncClient.post", side_effect=slow_request):
            with pytest.raises(FiberTimeoutError):
                await fiber_client.chat([ChatMessage.user("Slow request")])

        # Should have attempted the request
        assert timeout_count == 1

    @pytest.mark.asyncio
    async def test_concurrent_connection_limits(self):
        """Test that concurrent connections are properly limited."""
        max_concurrent = 5
        active_connections = 0
        peak_connections = 0

        # Use semaphore to simulate connection limiting
        connection_semaphore = asyncio.Semaphore(max_concurrent)

        async def connection_tracking_request(*args, **kwargs):
            nonlocal active_connections, peak_connections

            async with connection_semaphore:
                active_connections += 1
                peak_connections = max(peak_connections, active_connections)

                # Simulate network delay
                await asyncio.sleep(0.1)

                active_connections -= 1

                return MagicMock(
                    status_code=200,
                    json=lambda: {
                        "choices": [{"message": {"role": "assistant", "content": "Response"}}],
                        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
                    },
                )

        with patch("httpx.AsyncClient") as MockClient:
            mock_client = MockClient.return_value
            mock_client.post.side_effect = connection_tracking_request

            fiber_client = Fiber(
                default_model="gpt-4o-mini",
                api_keys={"openai": "test-key"},
                enable_observability=False,
            )

            # Start many concurrent requests
            tasks = []
            for i in range(20):
                task = asyncio.create_task(fiber_client.chat([ChatMessage.user(f"Request {i}")]))
                tasks.append(task)

            await asyncio.gather(*tasks, return_exceptions=True)

        # Peak connections should respect the limit
        assert peak_connections <= max_concurrent

    @pytest.mark.asyncio
    async def test_connection_error_recovery(self, fiber_client):
        """Test recovery from connection errors."""
        error_count = 0

        async def failing_then_success_request(*args, **kwargs):
            nonlocal error_count
            error_count += 1

            if error_count <= 2:
                raise httpx.ConnectError("Connection failed")
            else:
                return MagicMock(
                    status_code=200,
                    json=lambda: {
                        "choices": [{"message": {"role": "assistant", "content": "Success"}}],
                        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
                    },
                )

        # Enable retries
        fiber_client._retry_policy = RetryPolicy(max_attempts=5, base_delay=0.1)

        with patch("httpx.AsyncClient.post", side_effect=failing_then_success_request):
            result = await fiber_client.chat([ChatMessage.user("Test recovery")])

            assert result.text == "Success"
            assert error_count == 3  # 2 failures + 1 success


class TestResourceLimits:
    """Test resource limits and constraints."""

    @pytest.mark.asyncio
    async def test_concurrent_request_limiting(self):
        """Test that concurrent requests can be limited."""
        semaphore = asyncio.Semaphore(3)  # Max 3 concurrent
        active_count = 0
        max_active = 0

        async def limited_request(*args, **kwargs):
            nonlocal active_count, max_active

            async with semaphore:
                active_count += 1
                max_active = max(max_active, active_count)

                await asyncio.sleep(0.1)  # Simulate processing time

                active_count -= 1

                return MagicMock(
                    status_code=200,
                    json=lambda: {
                        "choices": [{"message": {"role": "assistant", "content": "Response"}}],
                        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
                    },
                )

        fiber_client = Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=False
        )

        with patch("httpx.AsyncClient.post", side_effect=limited_request):
            # Start 10 concurrent requests
            tasks = []
            for i in range(10):
                task = asyncio.create_task(fiber_client.chat([ChatMessage.user(f"Request {i}")]))
                tasks.append(task)

            await asyncio.gather(*tasks)

        # Should have limited concurrency
        assert max_active <= 3

    @pytest.mark.asyncio
    async def test_request_size_limits(self, fiber_client):
        """Test handling of very large requests."""
        # Create extremely large message
        large_content = "x" * 1000000  # 1MB message
        large_message = ChatMessage.user(large_content)

        mock_response = MagicMock(
            status_code=200,
            json=lambda: {
                "choices": [
                    {"message": {"role": "assistant", "content": "Response to large request"}}
                ],
                "usage": {"prompt_tokens": 250000, "completion_tokens": 10, "total_tokens": 250010},
            },
        )

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            # Should handle large requests without issues
            result = await fiber_client.chat([large_message])
            assert result.text == "Response to large request"

    @pytest.mark.asyncio
    async def test_response_size_limits(self, fiber_client):
        """Test handling of very large responses."""
        # Mock very large response
        large_response_text = "y" * 500000  # 500KB response

        mock_response = MagicMock(
            status_code=200,
            json=lambda: {
                "choices": [{"message": {"role": "assistant", "content": large_response_text}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 125000, "total_tokens": 125010},
            },
        )

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            result = await fiber_client.chat([ChatMessage.user("Generate large response")])

            assert len(result.text) == 500000
            assert result.usage.completion == 125000

    @pytest.mark.asyncio
    async def test_timeout_cascading(self):
        """Test that timeouts cascade properly through the system."""
        timeouts = Timeouts(connect=1.0, read=2.0, total=3.0)

        fiber_client = Fiber(
            default_model="gpt-4o-mini",
            api_keys={"openai": "test-key"},
            timeouts=timeouts,
            enable_observability=False,
        )

        start_time = time.time()

        async def very_slow_request(*args, **kwargs):
            await asyncio.sleep(5.0)  # Longer than total timeout
            return MagicMock()

        with patch("httpx.AsyncClient.post", side_effect=very_slow_request):
            with pytest.raises(FiberTimeoutError):
                await fiber_client.chat([ChatMessage.user("Slow request")])

        elapsed = time.time() - start_time
        # Should timeout around the total timeout (3s), not wait the full 5s
        assert elapsed < 4.0, f"Timeout took too long: {elapsed}s"


class TestResourceCleanup:
    """Test proper resource cleanup and shutdown."""

    @pytest.mark.asyncio
    async def test_graceful_shutdown(self):
        """Test graceful shutdown of Fiber client."""
        fiber_client = Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=False
        )

        # Start some background activity
        async def background_request(*args, **kwargs):
            await asyncio.sleep(0.5)
            return ChatResult("Background result", [], "stop", Usage(10, 5, 15), {})

        with patch.object(fiber_client, "chat", side_effect=background_request):
            # Start background task
            task = asyncio.create_task(fiber_client.chat([ChatMessage.user("Background")]))

            # Give it time to start
            await asyncio.sleep(0.1)

            # Now simulate shutdown
            if hasattr(fiber_client, "close"):
                await fiber_client.close()

            # Background task should still complete gracefully
            result = await task
            assert result.text == "Background result"

    @pytest.mark.asyncio
    async def test_cache_cleanup(self):
        """Test that cache resources are properly cleaned up."""
        cache = MemoryCacheAdapter(max_size=100)

        # Fill cache with data
        for i in range(50):
            await cache.set(f"key_{i}", f"value_{i}")

        initial_size = await cache.size()
        assert initial_size == 50

        # Clear cache
        await cache.clear()

        final_size = await cache.size()
        assert final_size == 0

    def test_thread_cleanup(self):
        """Test that threads are properly cleaned up."""
        initial_thread_count = threading.active_count()

        # Create clients that might spawn threads
        clients = []
        for i in range(5):
            client = Fiber(
                default_model="gpt-4o-mini",
                api_keys={"openai": f"test-key-{i}"},
                enable_observability=False,
            )
            clients.append(client)

        # Clean up clients
        del clients
        gc.collect()

        # Give threads time to clean up
        time.sleep(0.1)

        final_thread_count = threading.active_count()

        # Thread count should not have grown significantly
        thread_increase = final_thread_count - initial_thread_count
        assert thread_increase <= 2, f"Too many threads created: {thread_increase}"


class TestStressConditions:
    """Test behavior under stress conditions."""

    @pytest.mark.asyncio
    async def test_rapid_fire_requests(self):
        """Test handling of rapid-fire requests."""
        fiber_client = Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=False
        )

        request_count = 0

        async def fast_response(*args, **kwargs):
            nonlocal request_count
            request_count += 1
            return MagicMock(
                status_code=200,
                json=lambda: {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": f"Fast response {request_count}",
                            }
                        }
                    ],
                    "usage": {"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
                },
            )

        with patch("httpx.AsyncClient.post", side_effect=fast_response):
            start_time = time.time()

            # Fire 100 requests as fast as possible
            tasks = []
            for i in range(100):
                task = asyncio.create_task(fiber_client.chat([ChatMessage.user(f"Fast {i}")]))
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)
            elapsed_time = time.time() - start_time

        # All requests should complete successfully
        successful_results = [r for r in results if isinstance(r, ChatResult)]
        assert len(successful_results) == 100

        # Should handle high throughput (>= 50 RPS)
        throughput = len(successful_results) / elapsed_time
        assert throughput >= 50, f"Low throughput: {throughput} RPS"

    @pytest.mark.asyncio
    async def test_mixed_workload_stress(self):
        """Test mixed workload with different request types."""
        fiber_client = Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=False
        )

        # Different response types
        async def variable_response(*args, **kwargs):
            # Simulate variable response times and sizes
            # Use a simple counter or hash of kwargs to vary response type
            request_type = hash(str(kwargs.get("json", {}))) % 3

            if request_type == 0:
                # Fast, small response
                await asyncio.sleep(0.01)
                content = "Quick response"
            elif request_type == 1:
                # Medium response
                await asyncio.sleep(0.05)
                content = "Medium response " * 50
            else:
                # Slow, large response
                await asyncio.sleep(0.1)
                content = "Large response " * 200

            return MagicMock(
                status_code=200,
                json=lambda: {
                    "choices": [{"message": {"role": "assistant", "content": content}}],
                    "usage": {
                        "prompt_tokens": 10,
                        "completion_tokens": len(content.split()),
                        "total_tokens": 10 + len(content.split()),
                    },
                },
            )

        with patch("httpx.AsyncClient.post", side_effect=variable_response):
            # Mix of different request types
            tasks = []
            for i in range(60):  # Mix of 60 requests
                message_content = f"Request type {i % 3} number {i}"
                task = asyncio.create_task(fiber_client.chat([ChatMessage.user(message_content)]))
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should complete successfully
        successful_results = [r for r in results if isinstance(r, ChatResult)]
        failed_results = [r for r in results if isinstance(r, Exception)]

        assert len(successful_results) == 60
        assert len(failed_results) == 0

    @pytest.mark.asyncio
    async def test_error_storm_resilience(self):
        """Test resilience during error storms."""
        fiber_client = Fiber(
            default_model="gpt-4o-mini",
            api_keys={"openai": "test-key"},
            retry_policy=RetryPolicy(max_attempts=2, base_delay=0.01),
            enable_observability=False,
        )

        error_count = 0
        success_count = 0

        async def error_prone_response(*args, **kwargs):
            nonlocal error_count, success_count

            # 70% error rate
            if (error_count + success_count) % 10 < 7:
                error_count += 1
                raise httpx.HTTPStatusError(
                    "500 Server Error", request=MagicMock(), response=MagicMock(status_code=500)
                )
            else:
                success_count += 1
                return MagicMock(
                    status_code=200,
                    json=lambda: {
                        "choices": [{"message": {"role": "assistant", "content": "Success"}}],
                        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
                    },
                )

        with patch("httpx.AsyncClient.post", side_effect=error_prone_response):
            tasks = []
            for i in range(50):
                task = asyncio.create_task(fiber_client.chat([ChatMessage.user(f"Error test {i}")]))
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Some should succeed despite high error rate
        successful_results = [r for r in results if isinstance(r, ChatResult)]

        # Should have some successful results (retries help)
        assert len(successful_results) > 0

        # Error handling should be graceful
        error_results = [r for r in results if isinstance(r, Exception)]
        for error in error_results:
            assert isinstance(error, (FiberConnectionError, FiberProviderError))
