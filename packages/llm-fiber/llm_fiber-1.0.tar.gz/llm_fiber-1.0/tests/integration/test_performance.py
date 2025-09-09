"""Performance and stress tests for llm-fiber functionality."""

import asyncio
import gc
import os
import statistics
import time
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import psutil
import pytest

from llm_fiber import (
    BatchConfig,
    BatchRequest,
    BatchStrategy,
    BudgetManager,
    CachePolicy,
    ChatMessage,
    ChatResult,
    Fiber,
    MemoryCacheAdapter,
    RetryPolicy,
    create_cost_budget,
    create_token_budget,
)


class PerformanceMetrics:
    """Helper class to collect and analyze performance metrics."""

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.response_times = []
        self.memory_usage = []
        self.success_count = 0
        self.error_count = 0

    def start(self):
        """Start performance measurement."""
        self.start_time = time.time()

    def stop(self):
        """Stop performance measurement."""
        self.end_time = time.time()

    def record_response_time(self, duration: float):
        """Record a response time."""
        self.response_times.append(duration)

    def record_success(self):
        """Record a successful operation."""
        self.success_count += 1

    def record_error(self):
        """Record a failed operation."""
        self.error_count += 1

    def record_memory_usage(self):
        """Record current memory usage."""
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        self.memory_usage.append(memory_mb)

    @property
    def total_duration(self) -> float:
        """Total test duration in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0

    @property
    def throughput(self) -> float:
        """Requests per second."""
        if self.total_duration > 0:
            return len(self.response_times) / self.total_duration
        return 0.0

    @property
    def success_rate(self) -> float:
        """Success rate as percentage."""
        total = self.success_count + self.error_count
        if total > 0:
            return (self.success_count / total) * 100
        return 0.0

    @property
    def avg_response_time(self) -> float:
        """Average response time in seconds."""
        if self.response_times:
            return statistics.mean(self.response_times)
        return 0.0

    @property
    def p95_response_time(self) -> float:
        """95th percentile response time."""
        if self.response_times:
            sorted_times = sorted(self.response_times)
            index = int(0.95 * len(sorted_times))
            return sorted_times[index]
        return 0.0

    @property
    def p99_response_time(self) -> float:
        """99th percentile response time."""
        if self.response_times:
            sorted_times = sorted(self.response_times)
            index = int(0.99 * len(sorted_times))
            return sorted_times[index]
        return 0.0

    @property
    def peak_memory_mb(self) -> float:
        """Peak memory usage in MB."""
        if self.memory_usage:
            return max(self.memory_usage)
        return 0.0

    def summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        return {
            "total_duration": self.total_duration,
            "total_requests": len(self.response_times),
            "throughput_rps": self.throughput,
            "success_rate_pct": self.success_rate,
            "avg_response_time": self.avg_response_time,
            "p95_response_time": self.p95_response_time,
            "p99_response_time": self.p99_response_time,
            "peak_memory_mb": self.peak_memory_mb,
            "memory_growth_mb": self.peak_memory_mb - min(self.memory_usage)
            if self.memory_usage
            else 0,
        }


class TestConcurrentPerformance:
    """Test concurrent request handling performance."""

    @pytest.fixture
    def mock_variable_latency_response(self):
        """Mock response with variable latency to simulate real conditions."""
        call_count = 0

        async def mock_post(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            # Extract request ID from the message content
            request_id = call_count  # default fallback
            json_data = kwargs.get("json", {})
            messages = json_data.get("messages", [])
            if messages and messages[0].get("content"):
                content = messages[0]["content"]
                # Extract number from "Concurrent request X"
                import re

                match = re.search(r"Concurrent request (\d+)", content)
                if match:
                    request_id = int(match.group(1))

            # Variable latency: 10-50ms
            base_delay = 0.01
            variable_delay = (call_count % 5) * 0.01
            await asyncio.sleep(base_delay + variable_delay)

            mock_response = MagicMock()
            mock_response.json.return_value = {
                "id": f"perf-{request_id}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "gpt-4o-mini",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": f"Response {request_id}"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30},
            }
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            return mock_response

        return mock_post

    @pytest.mark.asyncio
    async def test_concurrent_request_throughput(self, mock_variable_latency_response):
        """Test throughput under concurrent load."""
        fiber = Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=False
        )

        metrics = PerformanceMetrics()

        async def make_request(request_id: int):
            start = time.time()
            try:
                messages = [ChatMessage.user(f"Concurrent request {request_id}")]
                result = await fiber.chat(messages)

                duration = time.time() - start
                metrics.record_response_time(duration)
                metrics.record_success()

                assert isinstance(result, ChatResult)
                assert f"Response {request_id}" in result.text

            except Exception as e:
                metrics.record_error()
                print(f"Request {request_id} failed: {e}")

        with patch("httpx.AsyncClient.post", side_effect=mock_variable_latency_response):
            # Test with increasing concurrency levels
            for concurrency in [10, 25, 50]:
                print(f"\nTesting concurrency level: {concurrency}")

                metrics = PerformanceMetrics()
                metrics.start()

                # Create concurrent tasks
                tasks = [make_request(i) for i in range(concurrency)]
                await asyncio.gather(*tasks, return_exceptions=True)

                metrics.stop()
                summary = metrics.summary()

                print(f"Results for {concurrency} concurrent requests:")
                print(f"  Throughput: {summary['throughput_rps']:.2f} requests/sec")
                print(f"  Avg Response Time: {summary['avg_response_time']:.3f}s")
                print(f"  P95 Response Time: {summary['p95_response_time']:.3f}s")
                print(f"  Success Rate: {summary['success_rate_pct']:.1f}%")

                # Performance assertions
                assert summary["success_rate_pct"] >= 95.0, (
                    f"Success rate too low: {summary['success_rate_pct']}%"
                )
                assert summary["throughput_rps"] > 10, (
                    f"Throughput too low: {summary['throughput_rps']} rps"
                )
                assert summary["p95_response_time"] < 1.0, (
                    f"P95 latency too high: {summary['p95_response_time']}s"
                )

    @pytest.mark.asyncio
    async def test_streaming_performance_under_load(self):
        """Test streaming performance under concurrent load."""
        fiber = Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=False
        )

        # Simplified streaming test - no need for per-request customization

        call_count = 0

        async def mock_stream(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            # Simple generic streaming response
            chunks = [
                'data: {"choices":[{"delta":{"role":"assistant","content":""}}]}\n',
                'data: {"choices":[{"delta":{"content":"Streaming"}}]}\n',
                'data: {"choices":[{"delta":{"content":" response"}}]}\n',
                'data: {"choices":[{"delta":{"content":" complete"}}]}\n',
                'data: {"choices":[{"delta":{},"finish_reason":"stop"}],'
                '"usage":{"total_tokens":25}}\n',
                "data: [DONE]\n",
            ]

            # Variable delay for each chunk
            async def delayed_chunks():
                for i, chunk in enumerate(chunks):
                    await asyncio.sleep(0.005 + (i * 0.002))  # 5-15ms per chunk
                    yield chunk.encode("utf-8")

            mock_response = MagicMock()
            mock_response.aiter_bytes.return_value = delayed_chunks()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            return mock_response

        metrics = PerformanceMetrics()

        async def stream_request(request_id: int):
            start = time.time()
            try:
                messages = [ChatMessage.user(f"Stream request {request_id}")]

                events = []
                async for event in fiber.chat_stream(messages):
                    events.append(event)

                duration = time.time() - start
                metrics.record_response_time(duration)
                metrics.record_success()

                # Verify streaming worked
                chunk_events = [e for e in events if e.type.value == "chunk"]
                assert len(chunk_events) >= 3

                full_text = "".join(e.delta for e in chunk_events)
                assert "Streaming response complete" in full_text

            except Exception as e:
                metrics.record_error()
                print(f"Stream request {request_id} failed: {e}")

        with patch("httpx.AsyncClient.stream") as mock_stream_patch:
            # Properly mock the async context manager
            mock_context_manager = MagicMock()
            mock_context_manager.__aenter__ = mock_stream
            mock_context_manager.__aexit__ = AsyncMock(return_value=None)
            mock_stream_patch.return_value = mock_context_manager

            num_concurrent_streams = 20

            metrics.start()

            tasks = [stream_request(i) for i in range(num_concurrent_streams)]
            await asyncio.gather(*tasks, return_exceptions=True)

            metrics.stop()
            summary = metrics.summary()

            print(f"\nStreaming Performance Results ({num_concurrent_streams} concurrent):")
            print(f"  Throughput: {summary['throughput_rps']:.2f} streams/sec")
            print(f"  Avg Response Time: {summary['avg_response_time']:.3f}s")
            print(f"  Success Rate: {summary['success_rate_pct']:.1f}%")

            # Streaming should maintain good performance
            assert summary["success_rate_pct"] >= 95.0
            assert summary["avg_response_time"] < 2.0  # Streaming can be slower
            assert summary["throughput_rps"] > 5


class TestCachingPerformance:
    """Test caching system performance."""

    @pytest.mark.asyncio
    async def test_cache_hit_performance(self):
        """Test cache hit performance vs. API calls."""
        cache = MemoryCacheAdapter(
            max_size=1000, default_ttl_seconds=3600, policy=CachePolicy.WRITE_THROUGH
        )

        fiber = Fiber(
            default_model="gpt-4o-mini",
            api_keys={"openai": "test-key"},
            cache_adapter=cache,
            enable_observability=False,
        )

        mock_response = {
            "id": "cache-perf",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "gpt-4o-mini",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "Cached response"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 15, "completion_tokens": 8, "total_tokens": 23},
        }

        # Add artificial delay to simulate API latency
        async def mock_post_with_delay(*args, **kwargs):
            await asyncio.sleep(0.1)  # 100ms API latency
            mock_resp = MagicMock()
            mock_resp.json.return_value = mock_response
            mock_resp.status_code = 200
            mock_resp.raise_for_status.return_value = None
            return mock_resp

        with patch("httpx.AsyncClient.post", side_effect=mock_post_with_delay):
            messages = [ChatMessage.user("Cache performance test")]

            # First call - should hit API (cache miss)
            miss_start = time.time()
            result1 = await fiber.chat(messages, temperature=0.5)
            miss_duration = time.time() - miss_start

            # Second call - should hit cache
            hit_start = time.time()
            result2 = await fiber.chat(messages, temperature=0.5)
            hit_duration = time.time() - hit_start

            # Verify cache performance
            assert result1.text == result2.text
            assert hit_duration < miss_duration * 0.1  # Cache should be 10x+ faster
            assert hit_duration < 0.01  # Cache hit should be < 10ms

            print(f"API call duration: {miss_duration:.3f}s")
            print(f"Cache hit duration: {hit_duration:.3f}s")
            print(f"Cache speedup: {miss_duration / hit_duration:.1f}x")

            # Test cache hit rate under load
            num_requests = 100

            start_time = time.time()
            tasks = [fiber.chat(messages, temperature=0.5) for _ in range(num_requests)]
            results = await asyncio.gather(*tasks)
            total_time = time.time() - start_time

            # All should be cache hits (after the first)
            assert len(results) == num_requests
            assert all(r.text == "Cached response" for r in results)

            # Average time per request should be very low (all cache hits)
            avg_time_per_request = total_time / num_requests
            assert avg_time_per_request < 0.005  # < 5ms per cached request

            cache_stats = cache.get_stats()
            print(f"Cache stats: hits={cache_stats.hits}, misses={cache_stats.misses}")
            # Calculate hit rate manually
            total_requests = cache_stats.hits + cache_stats.misses
            hit_rate = cache_stats.hits / total_requests if total_requests > 0 else 0.0
            assert hit_rate > 0.95  # >95% hit rate

    @pytest.mark.asyncio
    async def test_cache_memory_efficiency(self):
        """Test cache memory usage and efficiency."""
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024

        cache = MemoryCacheAdapter(max_size=1000, default_ttl_seconds=3600)

        # Fill cache with test data
        for i in range(500):  # Half capacity
            key = f"test_key_{i}"
            value = f"test_value_{i}" * 100  # ~1.2KB per value
            await cache.set(key, value)

        mid_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_per_item = (mid_memory - initial_memory) / 500

        # Fill to capacity
        for i in range(500, 1000):
            key = f"test_key_{i}"
            value = f"test_value_{i}" * 100
            await cache.set(key, value)

        full_memory = psutil.Process().memory_info().rss / 1024 / 1024

        # Test LRU eviction doesn't cause memory leak
        for i in range(1000, 1500):  # Trigger evictions
            key = f"test_key_{i}"
            value = f"test_value_{i}" * 100
            await cache.set(key, value)

        eviction_memory = psutil.Process().memory_info().rss / 1024 / 1024

        print(
            f"Memory usage: Initial={initial_memory:.1f}MB, Mid={mid_memory:.1f}MB, "
            f"Full={full_memory:.1f}MB, After Evictions={eviction_memory:.1f}MB"
        )
        print(f"Memory per cache item: ~{memory_per_item:.3f}MB")

        # Memory should be stable after evictions (not growing unbounded)
        assert eviction_memory <= full_memory * 1.1  # Allow 10% variance
        assert memory_per_item < 0.01  # Less than 10KB overhead per item

        # Cache should maintain its size limit
        current_size = await cache.size()
        assert current_size <= 1000


class TestBatchPerformance:
    """Test batch processing performance."""

    @pytest.mark.asyncio
    async def test_batch_vs_sequential_performance(self):
        """Compare batch vs sequential processing performance."""
        fiber = Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=False
        )

        # Mock with realistic delay
        call_count = 0

        async def mock_post(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.05)  # 50ms per request

            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "id": f"batch-{call_count}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "gpt-4o-mini",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": f"Batch response {call_count}"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            }
            mock_resp.status_code = 200
            mock_resp.raise_for_status.return_value = None
            return mock_resp

        # Create batch requests
        batch_requests = [
            BatchRequest(f"req_{i}", [ChatMessage.user(f"Batch test {i}")], "gpt-4o-mini")
            for i in range(20)
        ]

        with patch("httpx.AsyncClient.post", side_effect=mock_post):
            # Test sequential processing
            call_count = 0
            sequential_start = time.time()

            sequential_results = []
            for request in batch_requests:
                result = await fiber.chat(request.messages, model=request.model)
                sequential_results.append(result)

            sequential_time = time.time() - sequential_start

            # Test batch processing
            call_count = 0
            batch_config = BatchConfig(max_concurrent=5, strategy=BatchStrategy.CONCURRENT)

            fiber_with_batch = Fiber(
                default_model="gpt-4o-mini",
                api_keys={"openai": "test-key"},
                batch_config=batch_config,
                enable_observability=False,
            )

            batch_start = time.time()
            batch_results = await fiber_with_batch.batch_chat(batch_requests)
            batch_time = time.time() - batch_start

            # Verify results
            assert len(sequential_results) == 20
            assert len(batch_results) == 20
            assert all(r.is_success for r in batch_results)

            # Batch should be significantly faster
            speedup = sequential_time / batch_time

            print(f"Sequential time: {sequential_time:.2f}s")
            print(f"Batch time: {batch_time:.2f}s")
            print(f"Batch speedup: {speedup:.1f}x")

            assert speedup >= 3.0, f"Batch processing not efficient enough: {speedup:.1f}x speedup"

            # Test different concurrency levels
            for max_concurrent in [2, 5, 10]:
                config = BatchConfig(
                    max_concurrent=max_concurrent, strategy=BatchStrategy.CONCURRENT
                )
                test_fiber = Fiber(
                    default_model="gpt-4o-mini",
                    api_keys={"openai": "test-key"},
                    batch_config=config,
                    enable_observability=False,
                )

                call_count = 0
                start_time = time.time()
                results = await test_fiber.batch_chat(
                    batch_requests[:10]
                )  # Smaller batch for testing
                duration = time.time() - start_time

                expected_duration = (10 * 0.05) / max_concurrent  # Rough estimate

                print(
                    f"Concurrency {max_concurrent}: {duration:.2f}s "
                    f"(expected ~{expected_duration:.2f}s)"
                )

                assert len(results) == 10
                assert all(r.is_success for r in results)

    @pytest.mark.asyncio
    async def test_batch_error_handling_performance(self):
        """Test batch error handling doesn't significantly impact performance."""
        fiber = Fiber(
            default_model="gpt-4o-mini",
            api_keys={"openai": "test-key"},
            retry_policy=RetryPolicy.none(),
            batch_config=BatchConfig(max_concurrent=5, return_exceptions=True),
            enable_observability=False,
        )

        call_count = 0

        async def mixed_response_mock(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            await asyncio.sleep(0.02)  # Base delay

            mock_resp = MagicMock()

            # Determine request index from payload to make failures deterministic
            req_idx = None
            try:
                payload = kwargs.get("json") or {}
                for m in payload.get("messages", []):
                    if m.get("role") == "user":
                        content = m.get("content", "")
                        if content.startswith("Mixed test "):
                            req_idx = int(content.split("Mixed test ")[1])
                            break
            except Exception:
                req_idx = None

            # Fail every 3rd request deterministically by index (i % 3 == 2)
            should_fail = req_idx is not None and (req_idx % 3 == 2)
            if should_fail:
                mock_resp.status_code = 500
                mock_resp.json.return_value = {"error": {"message": "Server error"}}
                mock_resp.raise_for_status.side_effect = Exception("Server error")
                # Provide bytes for aread() since HTTP handler awaits it on errors
                try:
                    mock_resp.aread = AsyncMock(
                        return_value=b'{"error":{"message":"Server error"}}'
                    )
                except NameError:
                    pass
            else:
                mock_resp.status_code = 200
                mock_resp.json.return_value = {
                    "id": f"mixed-{req_idx if req_idx is not None else call_count}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": "gpt-4o-mini",
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": (
                                    f"Success {req_idx if req_idx is not None else call_count}"
                                ),
                            },
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
                }
                mock_resp.raise_for_status.return_value = None

            return mock_resp

        # Create batch with expected mix of success/failure
        batch_requests = [
            BatchRequest(f"mixed_{i}", [ChatMessage.user(f"Mixed test {i}")], "gpt-4o-mini")
            for i in range(15)  # 5 will fail, 10 will succeed
        ]

        with patch("httpx.AsyncClient.post", side_effect=mixed_response_mock):
            start_time = time.time()
            results = await fiber.batch_chat(batch_requests)
            duration = time.time() - start_time

            # Verify mixed results
            assert len(results) == 15

            successful = [r for r in results if r.is_success]
            failed = [r for r in results if not r.is_success]

            assert len(successful) == 10  # 2/3 should succeed
            assert len(failed) == 5  # 1/3 should fail

            # Performance shouldn't be significantly impacted by errors
            expected_duration = 15 * 0.02 / 5  # ~0.06s with concurrency 5
            assert duration < expected_duration * 2, f"Error handling too slow: {duration}s"

            print(f"Mixed batch duration: {duration:.3f}s")
            print(
                f"Success rate: {len(successful)}/{len(results)} = "
                f"{len(successful) / len(results) * 100:.1f}%"
            )


class TestMemoryAndResourceUsage:
    """Test memory usage and resource management."""

    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self):
        """Test memory usage remains stable under load."""
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024

        fiber = Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=False
        )

        async def mock_post(*args, **kwargs):
            await asyncio.sleep(0.001)  # Minimal delay
            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "id": "memory-test",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "gpt-4o-mini",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "Memory test response"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            }
            mock_resp.status_code = 200
            mock_resp.raise_for_status.return_value = None
            return mock_resp

        with patch("httpx.AsyncClient.post", side_effect=mock_post):
            memory_samples = []

            # Process many requests in batches
            for batch_num in range(10):
                # Create batch of requests
                tasks = []
                for i in range(50):
                    messages = [ChatMessage.user(f"Memory test batch {batch_num} request {i}")]
                    tasks.append(fiber.chat(messages))

                # Execute batch
                results = await asyncio.gather(*tasks)

                # Record memory usage
                current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                memory_samples.append(current_memory)

                # Verify results
                assert len(results) == 50
                assert all(isinstance(r, ChatResult) for r in results)

                # Force garbage collection
                gc.collect()

            final_memory = psutil.Process().memory_info().rss / 1024 / 1024

            print(f"Memory usage: Initial={initial_memory:.1f}MB, Final={final_memory:.1f}MB")
            print(f"Peak memory: {max(memory_samples):.1f}MB")
            print(f"Memory samples: {[f'{m:.1f}' for m in memory_samples]}")

            # Memory growth should be reasonable
            memory_growth = final_memory - initial_memory
            assert memory_growth < 50, f"Excessive memory growth: {memory_growth:.1f}MB"

            # Memory usage should stabilize (not grow unbounded)
            if len(memory_samples) >= 5:
                last_half = memory_samples[-5:]
                first_half = memory_samples[:5]
                avg_recent = statistics.mean(last_half)
                avg_early = statistics.mean(first_half)

                # Recent memory usage shouldn't be much higher than early usage
                growth_ratio = avg_recent / avg_early
                assert growth_ratio < 1.5, f"Memory usage growing over time: {growth_ratio:.2f}x"

    @pytest.mark.asyncio
    async def test_connection_pool_efficiency(self):
        """Test HTTP connection pool efficiency."""
        fiber = Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=False
        )

        connection_count = 0

        async def mock_post(*args, **kwargs):
            nonlocal connection_count
            connection_count += 1
            await asyncio.sleep(0.01)

            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "id": f"conn-{connection_count}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "gpt-4o-mini",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": f"Connection test {connection_count}",
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            }
            mock_resp.status_code = 200
            mock_resp.raise_for_status.return_value = None
            return mock_resp

        with patch("httpx.AsyncClient.post", side_effect=mock_post):
            # Make many concurrent requests
            num_requests = 100

            start_time = time.time()
            tasks = [
                fiber.chat([ChatMessage.user(f"Connection test {i}")]) for i in range(num_requests)
            ]

            results = await asyncio.gather(*tasks)
            duration = time.time() - start_time

            # Verify all requests succeeded
            assert len(results) == num_requests
            assert all(isinstance(r, ChatResult) for r in results)

            # Should maintain good throughput with connection pooling
            throughput = num_requests / duration
            print(
                f"Connection pool test: {num_requests} requests in {duration:.2f}s "
                f"({throughput:.1f} rps)"
            )

            assert throughput > 50, f"Connection pool efficiency too low: {throughput:.1f} rps"


class TestScalabilityLimits:
    """Test system behavior at scale limits."""

    @pytest.mark.asyncio
    async def test_high_concurrency_limits(self):
        """Test system behavior at high concurrency levels."""
        fiber = Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=False
        )

        async def mock_post(*args, **kwargs):
            await asyncio.sleep(0.01)  # Minimal realistic delay
            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "id": "scale-test",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "gpt-4o-mini",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "Scale test response"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            }
            mock_resp.status_code = 200
            mock_resp.raise_for_status.return_value = None
            return mock_resp

        with patch("httpx.AsyncClient.post", side_effect=mock_post):
            # Test increasing levels of concurrency
            for concurrency_level in [100, 200, 500]:
                print(f"\nTesting concurrency level: {concurrency_level}")

                metrics = PerformanceMetrics()
                metrics.start()

                tasks = [
                    fiber.chat([ChatMessage.user(f"Scale test {i}")])
                    for i in range(concurrency_level)
                ]

                try:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    metrics.stop()

                    # Count successful vs failed requests
                    successful = [r for r in results if isinstance(r, ChatResult)]

                    success_rate = len(successful) / len(results) * 100

                    print(f"  Success rate: {success_rate:.1f}% ({len(successful)}/{len(results)})")
                    print(f"  Duration: {metrics.total_duration:.2f}s")
                    print(f"  Throughput: {len(successful) / metrics.total_duration:.1f} rps")

                    # At high concurrency, we expect some degradation but not complete failure
                    if concurrency_level <= 200:
                        assert success_rate >= 90, (
                            f"Success rate too low at {concurrency_level}: {success_rate}%"
                        )
                    else:
                        assert success_rate >= 70, (
                            f"Success rate too low at {concurrency_level}: {success_rate}%"
                        )

                except Exception as e:
                    print(f"  Failed at concurrency {concurrency_level}: {e}")
                    if concurrency_level <= 200:
                        pytest.fail(f"System should handle {concurrency_level} concurrent requests")

    @pytest.mark.asyncio
    async def test_large_batch_processing(self):
        """Test processing very large batches."""
        batch_config = BatchConfig(
            max_concurrent=20, strategy=BatchStrategy.ADAPTIVE, return_exceptions=True
        )

        fiber = Fiber(
            default_model="gpt-4o-mini",
            api_keys={"openai": "test-key"},
            batch_config=batch_config,
            enable_observability=False,
        )

        async def mock_post(*args, **kwargs):
            await asyncio.sleep(0.005)  # Fast response
            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "id": "large-batch",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "gpt-4o-mini",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "Large batch response"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 8, "completion_tokens": 4, "total_tokens": 12},
            }
            mock_resp.status_code = 200
            mock_resp.raise_for_status.return_value = None
            return mock_resp

        # Test increasingly large batches
        for batch_size in [100, 500, 1000]:
            print(f"\nTesting batch size: {batch_size}")

            batch_requests = [
                BatchRequest(
                    f"large_{i}", [ChatMessage.user(f"Large batch test {i}")], "gpt-4o-mini"
                )
                for i in range(batch_size)
            ]

            with patch("httpx.AsyncClient.post", side_effect=mock_post):
                start_time = time.time()
                results = await fiber.batch_chat(batch_requests)
                duration = time.time() - start_time

                successful = [r for r in results if r.is_success]

                success_rate = len(successful) / len(results) * 100
                throughput = len(successful) / duration

                print(f"  Success rate: {success_rate:.1f}%")
                print(f"  Duration: {duration:.2f}s")
                print(f"  Throughput: {throughput:.1f} requests/sec")

                assert len(results) == batch_size
                assert success_rate >= 95, f"Large batch success rate too low: {success_rate}%"
                assert throughput > 50, f"Large batch throughput too low: {throughput} rps"

    @pytest.mark.asyncio
    async def test_memory_pressure_handling(self):
        """Test system behavior under memory pressure."""
        # Create cache with limited memory
        small_cache = MemoryCacheAdapter(
            max_size=10, default_ttl_seconds=60, policy=CachePolicy.WRITE_THROUGH
        )

        fiber = Fiber(
            default_model="gpt-4o-mini",
            api_keys={"openai": "test-key"},
            cache_adapter=small_cache,
            enable_observability=False,
        )

        async def mock_post(*args, **kwargs):
            await asyncio.sleep(0.001)
            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "id": "memory-pressure",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "gpt-4o-mini",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "Memory pressure response"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            }
            mock_resp.status_code = 200
            mock_resp.raise_for_status.return_value = None
            return mock_resp

        with patch("httpx.AsyncClient.post", side_effect=mock_post):
            # Fill cache beyond capacity to trigger evictions
            for i in range(200):  # 4x cache capacity
                messages = [ChatMessage.user(f"Memory pressure test {i}")]
                result = await fiber.chat(messages, temperature=i * 0.001)  # Unique cache keys

                assert isinstance(result, ChatResult)

            # Verify cache handled pressure gracefully
            cache_stats = small_cache.get_stats()
            cache_size = await small_cache.size()
            print(f"Cache under pressure - Size: {cache_size}, Evictions: {cache_stats.evictions}")

            assert cache_size <= 10  # Should maintain size limit (updated to match max_size)
            assert cache_stats.evictions > 100  # Should have evicted many items
            assert cache_stats.errors == 0  # No cache errors despite pressure

    @pytest.mark.asyncio
    async def test_sustained_load_stability(self):
        """Test system stability under sustained load."""
        fiber = Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=False
        )

        request_count = 0

        async def mock_post(*args, **kwargs):
            nonlocal request_count
            request_count += 1

            # Slight delay variation to simulate real conditions
            await asyncio.sleep(0.01 + (request_count % 3) * 0.002)

            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "id": f"sustained-{request_count}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "gpt-4o-mini",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": f"Sustained response {request_count}",
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 12, "completion_tokens": 6, "total_tokens": 18},
            }
            mock_resp.status_code = 200
            mock_resp.raise_for_status.return_value = None
            return mock_resp

        with patch("httpx.AsyncClient.post", side_effect=mock_post):
            # Run sustained load for multiple rounds
            rounds = 5
            requests_per_round = 50
            total_results = []

            for round_num in range(rounds):
                print(f"Sustained load round {round_num + 1}/{rounds}")

                round_start = time.time()

                # Process requests in this round
                tasks = [
                    fiber.chat([ChatMessage.user(f"Sustained test round {round_num} request {i}")])
                    for i in range(requests_per_round)
                ]

                results = await asyncio.gather(*tasks, return_exceptions=True)
                round_duration = time.time() - round_start

                # Analyze round results
                successful = [r for r in results if isinstance(r, ChatResult)]

                success_rate = len(successful) / len(results) * 100
                throughput = len(successful) / round_duration

                print(f"  Round {round_num + 1}: {success_rate:.1f}% success, {throughput:.1f} rps")

                total_results.extend(results)

                # Each round should maintain high performance
                assert success_rate >= 95, (
                    f"Round {round_num + 1} success rate too low: {success_rate}%"
                )
                assert throughput > 20, (
                    f"Round {round_num + 1} throughput too low: {throughput} rps"
                )

                # Brief pause between rounds
                await asyncio.sleep(0.1)

            # Verify overall stability
            total_successful = len([r for r in total_results if isinstance(r, ChatResult)])
            overall_success_rate = total_successful / len(total_results) * 100

            print(f"Overall sustained load: {overall_success_rate:.1f}% success rate")
            assert overall_success_rate >= 95, (
                f"Overall success rate too low: {overall_success_rate}%"
            )


class TestRealWorldScenarios:
    """Test performance in realistic usage scenarios."""

    @pytest.mark.asyncio
    async def test_mixed_workload_performance(self):
        """Test performance with mixed chat, streaming, and batch workloads."""
        # Setup comprehensive fiber client
        cache = MemoryCacheAdapter(max_size=200, default_ttl_seconds=1800)
        budget_manager = BudgetManager(
            [
                create_cost_budget("perf_cost", 100.0, "daily", hard_limit=False),
                create_token_budget("perf_tokens", 50000, "hourly", hard_limit=False),
            ]
        )
        batch_config = BatchConfig(max_concurrent=10, strategy=BatchStrategy.ADAPTIVE)

        fiber = Fiber(
            default_model="gpt-4o-mini",
            api_keys={"openai": "test-key"},
            cache_adapter=cache,
            budget_manager=budget_manager,
            batch_config=batch_config,
            enable_observability=True,
        )

        # Mock responses for different scenarios
        chat_call_count = 0
        stream_call_count = 0
        batch_call_count = 0

        async def mock_post(*args, **kwargs):
            nonlocal chat_call_count, batch_call_count
            if "stream" in kwargs.get("json", {}):
                return None  # Handled by stream mock

            if "batch" in str(kwargs.get("json", {})):
                batch_call_count += 1
                await asyncio.sleep(0.02)
            else:
                chat_call_count += 1
                await asyncio.sleep(0.015)

            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "id": "mixed-workload",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "gpt-4o-mini",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "Mixed workload response"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 15, "completion_tokens": 8, "total_tokens": 23},
            }
            mock_resp.status_code = 200
            mock_resp.raise_for_status.return_value = None
            return mock_resp

        async def mock_stream(*args, **kwargs):
            nonlocal stream_call_count
            stream_call_count += 1

            chunks = [
                'data: {"choices":[{"delta":{"role":"assistant","content":""}}]}',
                'data: {"choices":[{"delta":{"content":"Mixed"}}]}',
                'data: {"choices":[{"delta":{"content":" stream"}}]}',
                'data: {"choices":[{"delta":{}},"finish_reason":"stop"}],'
                '"usage":{"total_tokens":20}}',
                "data: [DONE]",
            ]

            async def delayed_chunks():
                for i, chunk in enumerate(chunks):
                    await asyncio.sleep(0.005)  # 5ms per chunk
                    yield (chunk + "\n").encode("utf-8")

            mock_response = MagicMock()
            mock_response.aiter_bytes.return_value = delayed_chunks()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            return mock_response

        with patch("httpx.AsyncClient.post", side_effect=mock_post), patch(
            "httpx.AsyncClient.stream"
        ) as mock_stream_patch:
            # Properly mock the async context manager
            mock_context_manager = MagicMock()
            mock_context_manager.__aenter__ = mock_stream
            mock_context_manager.__aexit__ = AsyncMock(return_value=None)
            mock_stream_patch.return_value = mock_context_manager

            # Create mixed workload
            mixed_tasks = []

            # Add regular chat requests (40%)
            for i in range(20):
                task = fiber.chat([ChatMessage.user(f"Mixed chat {i}")])
                mixed_tasks.append(("chat", task))

            # Add streaming requests (30%)
            for i in range(15):

                async def stream_task(idx=i):
                    events = []
                    async for event in fiber.chat_stream([ChatMessage.user(f"Mixed stream {idx}")]):
                        events.append(event)
                    return events

                mixed_tasks.append(("stream", stream_task()))

            # Add batch requests (30%)
            batch_requests = [
                BatchRequest(
                    f"mixed_batch_{i}", [ChatMessage.user(f"Mixed batch {i}")], "gpt-4o-mini"
                )
                for i in range(15)
            ]
            mixed_tasks.append(("batch", fiber.batch_chat(batch_requests)))

            # Execute mixed workload
            start_time = time.time()

            # Separate batch from individual tasks
            individual_tasks = [task for task_type, task in mixed_tasks if task_type != "batch"]
            batch_task = next(task for task_type, task in mixed_tasks if task_type == "batch")

            # Execute individual and batch tasks
            individual_results = await asyncio.gather(*individual_tasks, return_exceptions=True)
            batch_results = await batch_task

            total_duration = time.time() - start_time

            # Analyze results
            chat_results = individual_results[:20]  # First 20 are chat
            stream_results = individual_results[20:35]  # Next 15 are streams

            chat_success = len([r for r in chat_results if isinstance(r, ChatResult)])
            stream_success = len([r for r in stream_results if isinstance(r, list) and len(r) > 0])
            batch_success = len([r for r in batch_results if r.is_success])

            total_operations = chat_success + stream_success + batch_success
            overall_throughput = total_operations / total_duration

            print("Mixed workload results:")
            print(f"  Chat success: {chat_success}/20")
            print(f"  Stream success: {stream_success}/15")
            print(f"  Batch success: {batch_success}/15")
            print(f"  Total duration: {total_duration:.2f}s")
            print(f"  Overall throughput: {overall_throughput:.1f} ops/sec")

            # Performance assertions
            assert chat_success >= 19, f"Chat success rate too low: {chat_success}/20"
            assert stream_success >= 14, f"Stream success rate too low: {stream_success}/15"
            assert batch_success >= 14, f"Batch success rate too low: {batch_success}/15"
            assert overall_throughput > 15, (
                f"Mixed workload throughput too low: {overall_throughput} ops/sec"
            )

            # Verify all components were exercised
            assert chat_call_count > 0, "Chat requests not executed"
            assert stream_call_count > 0, "Stream requests not executed"
            # Batch requests go through regular post, so included in chat_call_count

    @pytest.mark.asyncio
    async def test_realistic_conversation_flows(self):
        """Test performance with realistic multi-turn conversations."""
        fiber = Fiber(
            default_model="gpt-4o-mini",
            api_keys={"openai": "test-key"},
            cache_adapter=MemoryCacheAdapter(max_size=100),
            enable_observability=False,
        )

        conversation_turn = 0

        async def mock_post(*args, **kwargs):
            nonlocal conversation_turn
            conversation_turn += 1

            # Longer delay for longer conversations (context processing)
            messages = kwargs.get("json", {}).get("messages", [])
            context_delay = len(messages) * 0.002  # 2ms per message in context
            await asyncio.sleep(0.01 + context_delay)

            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "id": f"conv-{conversation_turn}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "gpt-4o-mini",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": f"This is response {conversation_turn} in our conversation.",
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": len(messages) * 10,  # Growing context
                    "completion_tokens": 15,
                    "total_tokens": len(messages) * 10 + 15,
                },
            }
            mock_resp.status_code = 200
            mock_resp.raise_for_status.return_value = None
            return mock_resp

        with patch("httpx.AsyncClient.post", side_effect=mock_post):
            # Simulate realistic conversations of varying lengths
            conversation_metrics = []

            for conv_id in range(10):  # 10 conversations
                conversation = [ChatMessage.system("You are a helpful assistant.")]
                conversation_start = time.time()
                response_times = []

                # Each conversation has 3-7 turns
                turns = 3 + (conv_id % 5)  # 3-7 turns

                for turn in range(turns):
                    # Add user message
                    conversation.append(
                        ChatMessage.user(
                            f"Conversation {conv_id}, turn {turn + 1}: "
                            f"Tell me something interesting."
                        )
                    )

                    # Get response
                    turn_start = time.time()
                    result = await fiber.chat(conversation)
                    turn_duration = time.time() - turn_start

                    response_times.append(turn_duration)

                    # Add assistant response to conversation
                    conversation.append(ChatMessage.assistant(result.text))

                conversation_duration = time.time() - conversation_start
                avg_turn_time = statistics.mean(response_times)

                conversation_metrics.append(
                    {
                        "id": conv_id,
                        "turns": turns,
                        "total_duration": conversation_duration,
                        "avg_turn_time": avg_turn_time,
                        "final_context_length": len(conversation),
                    }
                )

                print(
                    f"Conversation {conv_id}: {turns} turns, {avg_turn_time:.3f}s avg/turn, "
                    f"{len(conversation)} total messages"
                )

            # Analyze conversation performance
            avg_turn_times = [m["avg_turn_time"] for m in conversation_metrics]
            overall_avg_turn_time = statistics.mean(avg_turn_times)

            short_conversations = [m for m in conversation_metrics if m["turns"] <= 4]
            long_conversations = [m for m in conversation_metrics if m["turns"] > 4]

            if short_conversations and long_conversations:
                short_avg = statistics.mean([m["avg_turn_time"] for m in short_conversations])
                long_avg = statistics.mean([m["avg_turn_time"] for m in long_conversations])

                print("Performance analysis:")
                print(f"  Overall avg turn time: {overall_avg_turn_time:.3f}s")
                print(f"  Short conversations (<= 4 turns): {short_avg:.3f}s avg")
                print(f"  Long conversations (> 4 turns): {long_avg:.3f}s avg")
                print(
                    f"  Context impact: {(long_avg / short_avg - 1) * 100:.1f}% "
                    f"slower for long conversations"
                )

                # Performance expectations
                assert overall_avg_turn_time < 0.1, (
                    f"Average turn time too slow: {overall_avg_turn_time:.3f}s"
                )
                assert long_avg < short_avg * 2, (
                    f"Long conversations too much slower: {long_avg / short_avg:.1f}x"
                )


if __name__ == "__main__":
    # Run performance tests with custom markers
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "-m",
            "not slow",  # Skip slow tests by default
            "--disable-warnings",
        ]
    )
