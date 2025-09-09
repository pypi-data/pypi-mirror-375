"""Unit tests for caching functionality."""

import asyncio
import json
from typing import Optional

import pytest

from llm_fiber.caching import (
    CacheAdapter,
    CacheError,
    CachePolicy,
    CacheStats,
    InvalidCacheKeyError,
    NoOpCacheAdapter,
    deserialize_chat_result,
    generate_cache_key,
    serialize_chat_result,
)
from llm_fiber.caching.memory import MemoryCacheAdapter
from llm_fiber.types import ChatMessage, ChatResult, Usage


class TestCachePolicy:
    """Test CachePolicy enum functionality."""

    def test_cache_policy_values(self):
        """Test cache policy enum values."""
        assert CachePolicy.OFF.value == "off"
        assert CachePolicy.READ_THROUGH.value == "read_through"
        assert CachePolicy.WRITE_THROUGH.value == "write_through"

    def test_cache_policy_from_string(self):
        """Test creating cache policy from string."""
        assert CachePolicy("off") == CachePolicy.OFF
        assert CachePolicy("read_through") == CachePolicy.READ_THROUGH
        assert CachePolicy("write_through") == CachePolicy.WRITE_THROUGH


class TestCacheStats:
    """Test CacheStats functionality."""

    def test_cache_stats_init(self):
        """Test cache stats initialization."""
        stats = CacheStats()
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.writes == 0
        assert stats.evictions == 0
        assert stats.errors == 0
        assert stats.size == 0

    def test_cache_stats_hit_rate_no_requests(self):
        """Test hit rate calculation with no requests."""
        stats = CacheStats()
        assert stats.hit_rate == 0.0

    def test_cache_stats_hit_rate_with_requests(self):
        """Test hit rate calculation with requests."""
        stats = CacheStats(hits=80, misses=20)
        assert stats.hit_rate == 0.8

    def test_cache_stats_total_requests(self):
        """Test total requests calculation."""
        stats = CacheStats(hits=60, misses=40)
        assert stats.total_requests == 100

    def test_cache_stats_str_representation(self):
        """Test string representation of cache stats."""
        stats = CacheStats(hits=80, misses=20, writes=50, evictions=5, errors=2, size=100)
        str_repr = str(stats)
        assert "hits=80" in str_repr
        assert "misses=20" in str_repr
        assert "hit_rate=0.8" in str_repr


class TestCacheKeyGeneration:
    """Test cache key generation functionality."""

    def test_generate_cache_key_basic(self):
        """Test basic cache key generation."""
        messages = [ChatMessage.user("Hello")]
        model = "gpt-4o-mini"

        key = generate_cache_key(messages, model)

        assert isinstance(key, str)
        assert len(key) == 64  # SHA256 hex digest length

    def test_generate_cache_key_deterministic(self):
        """Test cache key generation is deterministic."""
        messages = [ChatMessage.user("Hello")]
        model = "gpt-4o-mini"

        key1 = generate_cache_key(messages, model)
        key2 = generate_cache_key(messages, model)

        assert key1 == key2

    def test_generate_cache_key_different_messages(self):
        """Test different messages produce different keys."""
        messages1 = [ChatMessage.user("Hello")]
        messages2 = [ChatMessage.user("Hi")]
        model = "gpt-4o-mini"

        key1 = generate_cache_key(messages1, model)
        key2 = generate_cache_key(messages2, model)

        assert key1 != key2

    def test_generate_cache_key_different_models(self):
        """Test different models produce different keys."""
        messages = [ChatMessage.user("Hello")]

        key1 = generate_cache_key(messages, "gpt-4o-mini")
        key2 = generate_cache_key(messages, "claude-3-haiku")

        assert key1 != key2

    def test_generate_cache_key_with_kwargs(self):
        """Test cache key generation with additional kwargs."""
        messages = [ChatMessage.user("Hello")]
        model = "gpt-4o-mini"

        key1 = generate_cache_key(messages, model)
        key2 = generate_cache_key(messages, model, temperature=0.7)
        key3 = generate_cache_key(messages, model, temperature=0.8)

        assert key1 != key2
        assert key2 != key3

    def test_generate_cache_key_complex_messages(self):
        """Test cache key with complex message structures."""
        messages = [
            ChatMessage.system("You are helpful."),
            ChatMessage.user("What is Python?"),
            ChatMessage.assistant("Python is a programming language."),
            ChatMessage.user("Tell me more."),
        ]
        model = "gpt-4o"

        key = generate_cache_key(messages, model, max_tokens=100, temperature=0.5)

        assert isinstance(key, str)
        assert len(key) == 64

    def test_generate_cache_key_message_order_matters(self):
        """Test that message order affects cache key."""
        msg1 = ChatMessage.user("Hello")
        msg2 = ChatMessage.assistant("Hi")

        key1 = generate_cache_key([msg1, msg2], "gpt-4o-mini")
        key2 = generate_cache_key([msg2, msg1], "gpt-4o-mini")

        assert key1 != key2

    def test_generate_cache_key_kwargs_order_independent(self):
        """Test that kwargs order doesn't affect cache key."""
        messages = [ChatMessage.user("Hello")]
        model = "gpt-4o-mini"

        # Different order of kwargs
        key1 = generate_cache_key(messages, model, temperature=0.7, max_tokens=100)
        key2 = generate_cache_key(messages, model, max_tokens=100, temperature=0.7)

        assert key1 == key2


class TestChatResultSerialization:
    """Test chat result serialization/deserialization."""

    def test_serialize_chat_result(self):
        """Test serializing a chat result."""
        usage = Usage(prompt=10, completion=20, cost_estimate=0.001)
        result = ChatResult(
            text="Hello world",
            tool_calls=[],
            finish_reason="stop",
            usage=usage,
            raw={"id": "test-123"},
        )

        serialized = serialize_chat_result(result)

        assert isinstance(serialized, str)
        # Should be valid JSON
        data = json.loads(serialized)
        assert data["text"] == "Hello world"
        assert data["finish_reason"] == "stop"

    def test_deserialize_chat_result(self):
        """Test deserializing a chat result."""
        usage = Usage(prompt=10, completion=20, cost_estimate=0.001)
        original = ChatResult(
            text="Hello world",
            tool_calls=[],
            finish_reason="stop",
            usage=usage,
            raw={"id": "test-123"},
        )

        serialized = serialize_chat_result(original)
        deserialized = deserialize_chat_result(serialized)

        assert deserialized.text == original.text
        assert deserialized.finish_reason == original.finish_reason
        assert deserialized.tool_calls == original.tool_calls
        assert deserialized.usage.prompt == original.usage.prompt
        assert deserialized.usage.completion == original.usage.completion
        assert deserialized.raw == original.raw

    def test_serialize_deserialize_roundtrip(self):
        """Test serialization/deserialization roundtrip."""
        usage = Usage(prompt=100, completion=50, total=150, cost_estimate=0.005)
        original = ChatResult(
            text="This is a test response with more content.",
            tool_calls=[{"id": "call_123", "function": {"name": "test"}}],
            finish_reason="tool_calls",
            usage=usage,
            raw={"id": "test-456", "model": "gpt-4o", "created": 1234567890},
        )

        serialized = serialize_chat_result(original)
        deserialized = deserialize_chat_result(serialized)

        # Check all fields match
        assert deserialized.text == original.text
        assert deserialized.tool_calls == original.tool_calls
        assert deserialized.finish_reason == original.finish_reason
        assert deserialized.usage.prompt == original.usage.prompt
        assert deserialized.usage.completion == original.usage.completion
        assert deserialized.usage.total == original.usage.total
        assert deserialized.usage.cost_estimate == original.usage.cost_estimate
        assert deserialized.raw == original.raw

    def test_deserialize_invalid_json(self):
        """Test deserializing invalid JSON raises error."""
        with pytest.raises(CacheError):
            deserialize_chat_result("invalid json")

    def test_serialize_result_with_none_values(self):
        """Test serializing result with None values."""
        result = ChatResult(text="Hello", tool_calls=[], finish_reason=None, usage=None, raw={})

        serialized = serialize_chat_result(result)
        deserialized = deserialize_chat_result(serialized)

        assert deserialized.text == "Hello"
        assert deserialized.finish_reason is None
        assert deserialized.usage is None
        assert deserialized.raw == {}


class TestNoOpCacheAdapter:
    """Test NoOpCacheAdapter functionality."""

    @pytest.fixture
    def noop_cache(self):
        """Create a NoOpCacheAdapter instance."""
        return NoOpCacheAdapter()

    @pytest.mark.asyncio
    async def test_noop_get_returns_none(self, noop_cache):
        """Test that NoOpCacheAdapter.get always returns None."""
        result = await noop_cache.get("test_key")
        assert result is None

    @pytest.mark.asyncio
    async def test_noop_set_succeeds(self, noop_cache):
        """Test that NoOpCacheAdapter.set always succeeds."""
        await noop_cache.set("test_key", "test_value")
        # Should not raise any exception

    @pytest.mark.asyncio
    async def test_noop_delete_succeeds(self, noop_cache):
        """Test that NoOpCacheAdapter.delete always succeeds."""
        await noop_cache.delete("test_key")
        # Should not raise any exception

    @pytest.mark.asyncio
    async def test_noop_clear_succeeds(self, noop_cache):
        """Test that NoOpCacheAdapter.clear always succeeds."""
        await noop_cache.clear()
        # Should not raise any exception

    def test_noop_get_stats(self, noop_cache):
        """Test that NoOpCacheAdapter stats are always zero."""
        stats = noop_cache.get_stats()
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.writes == 0
        assert stats.evictions == 0
        assert stats.errors == 0
        assert stats.size == 0


class TestMemoryCacheAdapter:
    """Test MemoryCacheAdapter functionality."""

    @pytest.fixture
    def memory_cache(self):
        """Create a MemoryCacheAdapter instance."""
        return MemoryCacheAdapter(max_size=5, default_ttl_seconds=3600)

    @pytest.fixture
    def small_cache(self):
        """Create a small cache for eviction testing."""
        return MemoryCacheAdapter(max_size=2, default_ttl_seconds=3600)

    @pytest.fixture
    def short_ttl_cache(self):
        """Create a cache with short TTL for expiration testing."""
        return MemoryCacheAdapter(max_size=10, default_ttl_seconds=0.1)

    @pytest.mark.asyncio
    async def test_memory_cache_basic_operations(self, memory_cache):
        """Test basic get/set operations."""
        # Initially empty
        result = await memory_cache.get("key1")
        assert result is None

        # Set and get
        await memory_cache.set("key1", "value1")
        result = await memory_cache.get("key1")
        assert result == "value1"

        # Set another key
        await memory_cache.set("key2", "value2")
        result = await memory_cache.get("key2")
        assert result == "value2"

        # First key should still be there
        result = await memory_cache.get("key1")
        assert result == "value1"

    @pytest.mark.asyncio
    async def test_memory_cache_overwrite(self, memory_cache):
        """Test overwriting existing keys."""
        await memory_cache.set("key1", "value1")
        await memory_cache.set("key1", "value2")

        result = await memory_cache.get("key1")
        assert result == "value2"

    @pytest.mark.asyncio
    async def test_memory_cache_delete(self, memory_cache):
        """Test deleting keys."""
        await memory_cache.set("key1", "value1")
        await memory_cache.set("key2", "value2")

        # Delete one key
        await memory_cache.delete("key1")

        result = await memory_cache.get("key1")
        assert result is None

        result = await memory_cache.get("key2")
        assert result == "value2"

    @pytest.mark.asyncio
    async def test_memory_cache_clear(self, memory_cache):
        """Test clearing all keys."""
        await memory_cache.set("key1", "value1")
        await memory_cache.set("key2", "value2")
        await memory_cache.set("key3", "value3")

        await memory_cache.clear()

        assert await memory_cache.get("key1") is None
        assert await memory_cache.get("key2") is None
        assert await memory_cache.get("key3") is None

    @pytest.mark.asyncio
    async def test_memory_cache_lru_eviction(self, small_cache):
        """Test LRU eviction when cache is full."""
        # Fill cache to capacity
        await small_cache.set("key1", "value1")
        await small_cache.set("key2", "value2")

        # Both should be there
        assert await small_cache.get("key1") == "value1"
        assert await small_cache.get("key2") == "value2"

        # Add third item, should evict oldest (key1)
        await small_cache.set("key3", "value3")

        assert await small_cache.get("key1") is None  # Evicted
        assert await small_cache.get("key2") == "value2"  # Still there
        assert await small_cache.get("key3") == "value3"  # New item

    @pytest.mark.asyncio
    async def test_memory_cache_lru_access_updates_order(self, small_cache):
        """Test that accessing an item updates its position in LRU order."""
        await small_cache.set("key1", "value1")
        await small_cache.set("key2", "value2")

        # Access key1 to make it recently used
        await small_cache.get("key1")

        # Add third item, should evict key2 (not key1 which was accessed)
        await small_cache.set("key3", "value3")

        assert await small_cache.get("key1") == "value1"  # Should still be there
        assert await small_cache.get("key2") is None  # Should be evicted
        assert await small_cache.get("key3") == "value3"

    @pytest.mark.asyncio
    async def test_memory_cache_ttl_expiration(self, short_ttl_cache):
        """Test TTL-based expiration."""
        await short_ttl_cache.set("key1", "value1")

        # Should be available immediately
        result = await short_ttl_cache.get("key1")
        assert result == "value1"

        # Wait for TTL to expire
        await asyncio.sleep(0.15)

        # Should be expired now
        result = await short_ttl_cache.get("key1")
        assert result is None

    @pytest.mark.asyncio
    async def test_memory_cache_custom_ttl(self, memory_cache):
        """Test setting custom TTL for individual items."""
        # Set with very short TTL
        await memory_cache.set("key1", "value1", ttl_seconds=0.1)

        # Should be available immediately
        result = await memory_cache.get("key1")
        assert result == "value1"

        # Wait for custom TTL to expire
        await asyncio.sleep(0.15)

        # Should be expired now
        result = await memory_cache.get("key1")
        assert result is None

    def test_memory_cache_stats_basic(self, memory_cache):
        """Test basic stats functionality."""
        stats = memory_cache.get_stats()
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.writes == 0
        assert stats.evictions == 0
        assert stats.errors == 0
        assert stats.size == 0

    @pytest.mark.asyncio
    async def test_memory_cache_stats_tracking(self, memory_cache):
        """Test that stats are tracked correctly."""
        # Miss
        await memory_cache.get("nonexistent")
        stats = memory_cache.get_stats()
        assert stats.misses == 1
        assert stats.hits == 0
        assert stats.size == 0

        # Write
        await memory_cache.set("key1", "value1")
        stats = memory_cache.get_stats()
        assert stats.writes == 1
        assert stats.size == 1

        # Hit
        await memory_cache.get("key1")
        stats = memory_cache.get_stats()
        assert stats.hits == 1
        assert stats.misses == 1

    @pytest.mark.asyncio
    async def test_memory_cache_stats_eviction_tracking(self, small_cache):
        """Test that evictions are tracked in stats."""
        # Fill cache
        await small_cache.set("key1", "value1")
        await small_cache.set("key2", "value2")

        stats = small_cache.get_stats()
        assert stats.evictions == 0

        # Trigger eviction
        await small_cache.set("key3", "value3")

        stats = small_cache.get_stats()
        assert stats.evictions == 1

    @pytest.mark.asyncio
    async def test_memory_cache_concurrent_access(self):
        """Test concurrent access doesn't cause issues."""
        # Use a larger cache for this test to avoid eviction
        memory_cache = MemoryCacheAdapter(max_size=50, default_ttl_seconds=3600)

        async def write_keys(start_idx, count):
            for i in range(count):
                await memory_cache.set(f"key_{start_idx}_{i}", f"value_{start_idx}_{i}")

        async def read_keys(start_idx, count):
            results = []
            for i in range(count):
                result = await memory_cache.get(f"key_{start_idx}_{i}")
                results.append(result)
            return results

        # Start concurrent writes
        tasks = [
            write_keys(0, 10),
            write_keys(10, 10),
            write_keys(20, 10),
        ]

        await asyncio.gather(*tasks)

        # All keys should be accessible
        for start_idx in [0, 10, 20]:
            for i in range(10):
                key = f"key_{start_idx}_{i}"
                value = await memory_cache.get(key)
                assert value == f"value_{start_idx}_{i}"

    def test_memory_cache_reset_stats(self, memory_cache):
        """Test resetting cache statistics."""
        # Generate some stats
        asyncio.run(memory_cache.set("key1", "value1"))
        asyncio.run(memory_cache.get("key1"))
        asyncio.run(memory_cache.get("nonexistent"))

        stats = memory_cache.get_stats()
        assert stats.hits > 0 or stats.misses > 0 or stats.writes > 0

        # Reset stats
        memory_cache.reset_stats()

        stats = memory_cache.get_stats()
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.writes == 0
        assert stats.evictions == 0
        assert stats.errors == 0
        # Size should not be reset
        assert stats.size == 1

    @pytest.mark.asyncio
    async def test_memory_cache_invalid_key(self, memory_cache):
        """Test handling of invalid cache keys."""
        with pytest.raises(InvalidCacheKeyError):
            await memory_cache.set("", "value")

        with pytest.raises(InvalidCacheKeyError):
            await memory_cache.get("")

    @pytest.mark.asyncio
    async def test_memory_cache_cleanup_expired_entries(self, short_ttl_cache):
        """Test that cleanup removes expired entries."""
        # Add some entries
        await short_ttl_cache.set("key1", "value1")
        await short_ttl_cache.set("key2", "value2")
        await short_ttl_cache.set("key3", "value3")

        stats = short_ttl_cache.get_stats()
        assert stats.size == 3

        # Wait for expiration
        await asyncio.sleep(0.15)

        # Trigger cleanup by trying to access each key
        await short_ttl_cache.get("key1")
        await short_ttl_cache.get("key2")
        await short_ttl_cache.get("key3")

        # Should have cleaned up expired entries
        stats = short_ttl_cache.get_stats()
        assert stats.size == 0

    def test_memory_cache_initialization_parameters(self):
        """Test cache initialization with various parameters."""
        # Test default parameters
        cache = MemoryCacheAdapter()
        assert cache.max_size == 1000
        assert cache.default_ttl_seconds == 3600

        # Test custom parameters
        cache = MemoryCacheAdapter(
            max_size=100, default_ttl_seconds=1800, cleanup_interval_seconds=30
        )
        assert cache.max_size == 100
        assert cache.default_ttl_seconds == 1800

    def test_memory_cache_invalid_initialization(self):
        """Test cache initialization with invalid parameters."""
        with pytest.raises(ValueError):
            MemoryCacheAdapter(max_size=0)

        with pytest.raises(ValueError):
            MemoryCacheAdapter(max_size=-1)

        with pytest.raises(ValueError):
            MemoryCacheAdapter(default_ttl_seconds=-1)


class TestCacheIntegration:
    """Test caching integration scenarios."""

    @pytest.fixture
    def cache_with_policy(self):
        """Create cache adapter with different policies for testing."""
        return MemoryCacheAdapter(max_size=10, default_ttl_seconds=3600)

    @pytest.mark.asyncio
    async def test_cache_policy_integration(self, cache_with_policy):
        """Test cache behavior with different policies."""
        # This would typically be tested at the Fiber client level
        # Here we test the cache adapter behavior that supports policies

        # Simulate READ_THROUGH behavior
        result = await cache_with_policy.get("nonexistent_key")
        assert result is None

        # Simulate WRITE_THROUGH behavior
        await cache_with_policy.set("test_key", "test_value")
        result = await cache_with_policy.get("test_key")
        assert result == "test_value"

    @pytest.mark.asyncio
    async def test_cache_error_handling(self):
        """Test cache error handling and fail-open behavior."""

        # Create a mock cache that raises errors
        class FailingCache(CacheAdapter):
            async def get(self, key: str) -> Optional[str]:
                raise CacheError("Simulated cache failure")

            async def set(self, key: str, value: str, ttl_seconds: Optional[int] = None):
                raise CacheError("Simulated cache failure")

            async def delete(self, key: str):
                raise CacheError("Simulated cache failure")

            async def clear(self):
                raise CacheError("Simulated cache failure")

            def get_stats(self) -> CacheStats:
                return CacheStats(errors=1)

            async def size(self) -> int:
                raise CacheError("Simulated cache failure")

        failing_cache = FailingCache()

        # Errors should be raised (fail-open behavior would be handled at higher level)
        with pytest.raises(CacheError):
            await failing_cache.get("test_key")

        with pytest.raises(CacheError):
            await failing_cache.set("test_key", "test_value")

    @pytest.mark.asyncio
    async def test_cache_with_real_chat_results(self, memory_cache):
        """Test caching with realistic ChatResult objects."""
        # Create a realistic ChatResult
        usage = Usage(prompt=150, completion=75, total=225, cost_estimate=0.01)
        chat_result = ChatResult(
            text=(
                "This is a comprehensive answer about Python programming. "
                "Python is a high-level, interpreted programming language "
                "known for its simplicity and readability."
            ),
            tool_calls=[],
            finish_reason="stop",
            usage=usage,
            raw={
                "id": "chatcmpl-test123",
                "object": "chat.completion",
                "created": 1234567890,
                "model": "gpt-4o",
                "system_fingerprint": "fp_test",
            },
        )

        # Generate cache key for a typical request
        messages = [
            ChatMessage.system("You are a helpful programming assistant."),
            ChatMessage.user("What is Python?"),
        ]
        cache_key = generate_cache_key(messages, "gpt-4o", temperature=0.7, max_tokens=500)

        # Serialize and cache the result
        serialized_result = serialize_chat_result(chat_result)
        await memory_cache.set(cache_key, serialized_result)

        # Retrieve and verify
        cached_data = await memory_cache.get(cache_key)
        assert cached_data is not None

        deserialized_result = deserialize_chat_result(cached_data)
        assert deserialized_result.text == chat_result.text
        assert deserialized_result.usage.prompt == chat_result.usage.prompt
        assert deserialized_result.usage.completion == chat_result.usage.completion
        assert deserialized_result.raw["id"] == chat_result.raw["id"]

    @pytest.mark.asyncio
    async def test_cache_key_normalization(self, memory_cache):
        """Test that cache keys are properly normalized for consistent behavior."""
        # Same semantic request should produce same key
        messages1 = [ChatMessage.user("Hello world")]
        messages2 = [ChatMessage.user("Hello world")]

        key1 = generate_cache_key(messages1, "gpt-4o-mini", temperature=0.5, max_tokens=100)
        key2 = generate_cache_key(messages2, "gpt-4o-mini", max_tokens=100, temperature=0.5)

        assert key1 == key2

        # Cache should work consistently
        await memory_cache.set(key1, "cached_response")

        result = await memory_cache.get(key2)
        assert result == "cached_response"

    @pytest.mark.asyncio
    async def test_cache_size_management(self, memory_cache):
        """Test cache size is managed properly."""
        initial_stats = memory_cache.get_stats()
        assert initial_stats.size == 0

        # Add items and verify size increases
        for i in range(3):
            await memory_cache.set(f"key_{i}", f"value_{i}")

        stats = memory_cache.get_stats()
        assert stats.size == 3

        # Delete one item
        await memory_cache.delete("key_1")

        stats = memory_cache.get_stats()
        assert stats.size == 2

        # Clear all items
        await memory_cache.clear()

        stats = memory_cache.get_stats()
        assert stats.size == 0
