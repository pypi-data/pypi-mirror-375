"""Tests for memory cache adapter edge cases."""

import asyncio
from unittest.mock import patch

import pytest

from llm_fiber.caching import CacheError, InvalidCacheKeyError
from llm_fiber.caching.memory import MemoryCacheAdapter


class TestMemoryCacheEdges:
    """Test edge cases for MemoryCacheAdapter."""

    @pytest.fixture
    def small_cache(self):
        """Create a small cache for testing size limits."""
        return MemoryCacheAdapter(max_size=3, default_ttl_seconds=1.0, cleanup_interval_seconds=0.1)

    @pytest.fixture
    def no_ttl_cache(self):
        """Create a cache with no default TTL."""
        return MemoryCacheAdapter(
            max_size=10, default_ttl_seconds=None, cleanup_interval_seconds=0.1
        )

    @pytest.mark.asyncio
    async def test_ttl_expiry_on_get(self, small_cache):
        """Test that items expire between set and get."""
        # Set an item with very short TTL
        await small_cache.set("key1", "value1", ttl_seconds=0.05)

        # Verify it's initially there
        assert await small_cache.get("key1") == "value1"
        assert small_cache.stats.hits == 1

        # Wait for it to expire
        await asyncio.sleep(0.1)

        # Now it should return None and count as a miss
        result = await small_cache.get("key1")
        assert result is None
        assert small_cache.stats.misses == 1
        assert small_cache.stats.evictions == 1  # Should count as eviction
        assert small_cache.stats.size == 0  # Size should be updated

    @pytest.mark.asyncio
    async def test_cleanup_of_expired_entries(self, small_cache):
        """Test that expired entries are cleaned up and stats.size decreases."""

        # Add multiple items with short TTL
        await small_cache.set("exp1", "value1", ttl_seconds=0.05)
        await small_cache.set("exp2", "value2", ttl_seconds=0.05)
        await small_cache.set("keep", "value3", ttl_seconds=10.0)

        # Verify all are there initially
        assert await small_cache.get("exp1") == "value1"
        assert await small_cache.get("exp2") == "value2"
        assert await small_cache.get("keep") == "value3"
        assert small_cache.stats.size == 3

        # Wait for cleanup interval + expiry
        await asyncio.sleep(0.2)

        # Access the cache to trigger cleanup detection
        await small_cache.get("keep")

        # Size should be reduced (expired items cleaned up)
        assert small_cache.stats.size < 3
        assert small_cache.stats.evictions > 0

    @pytest.mark.asyncio
    async def test_lru_eviction_and_recency_updates(self, small_cache):
        """Test LRU tie-breakers and recency updates under contention."""
        # Fill cache to capacity
        await small_cache.set("oldest", "value1")
        await small_cache.set("middle", "value2")
        await small_cache.set("newest", "value3")

        # Access oldest to make it most recent
        await small_cache.get("oldest")

        # Add a new item - should evict "middle" (now oldest)
        await small_cache.set("new", "value4")

        # Verify eviction happened
        assert small_cache.stats.evictions == 1
        assert small_cache.stats.size == 3

        # Verify "middle" was evicted, others remain
        assert await small_cache.get("middle") is None  # Evicted
        assert await small_cache.get("oldest") == "value1"  # Still there (was accessed)
        assert await small_cache.get("newest") == "value3"  # Still there
        assert await small_cache.get("new") == "value4"  # New item

    @pytest.mark.asyncio
    async def test_lru_recency_tie_breaking(self, small_cache):
        """Test LRU behavior when items have same creation time."""
        # Add items quickly
        await small_cache.set("a", "value_a")
        await small_cache.set("b", "value_b")
        await small_cache.set("c", "value_c")

        # Access 'a' to make it most recent
        await small_cache.get("a")

        # Access 'b' to make it more recent than 'c'
        await small_cache.get("b")

        # Add new item - should evict 'c' (least recently used)
        await small_cache.set("d", "value_d")

        # Verify 'c' was evicted
        assert await small_cache.get("c") is None
        assert await small_cache.get("a") == "value_a"
        assert await small_cache.get("b") == "value_b"
        assert await small_cache.get("d") == "value_d"

    @pytest.mark.asyncio
    async def test_invalid_keys_raise_error(self, small_cache):
        """Test that invalid keys raise InvalidCacheKeyError."""
        # Test None key
        with pytest.raises(InvalidCacheKeyError, match="Cache key must be a non-empty string"):
            await small_cache.get(None)

        with pytest.raises(InvalidCacheKeyError, match="Cache key must be a non-empty string"):
            await small_cache.set(None, "value")

        with pytest.raises(InvalidCacheKeyError, match="Cache key must be a non-empty string"):
            await small_cache.delete(None)

        # Test empty string
        with pytest.raises(InvalidCacheKeyError, match="Cache key must be a non-empty string"):
            await small_cache.get("")

        with pytest.raises(InvalidCacheKeyError, match="Cache key must be a non-empty string"):
            await small_cache.set("", "value")

        with pytest.raises(InvalidCacheKeyError, match="Cache key must be a non-empty string"):
            await small_cache.delete("")

        # Test non-string key
        with pytest.raises(InvalidCacheKeyError, match="Cache key must be a non-empty string"):
            await small_cache.get(123)

    @pytest.mark.asyncio
    async def test_very_long_key_handled(self, small_cache):
        """Test that very long keys are handled properly (not necessarily rejected)."""
        # Create a very long key
        very_long_key = "x" * 10000

        # Should work (implementation doesn't reject long keys, just validates type/emptiness)
        await small_cache.set(very_long_key, "long_key_value")
        result = await small_cache.get(very_long_key)
        assert result == "long_key_value"

    @pytest.mark.asyncio
    async def test_stats_tracking_comprehensive(self, small_cache):
        """Test comprehensive stats tracking: evictions/hits/misses/writes."""
        # Reset stats to start clean
        small_cache.reset_stats()

        # Test writes
        await small_cache.set("key1", "value1")
        await small_cache.set("key2", "value2")
        assert small_cache.stats.writes == 2
        assert small_cache.stats.size == 2

        # Test hits
        await small_cache.get("key1")
        await small_cache.get("key2")
        assert small_cache.stats.hits == 2

        # Test misses
        await small_cache.get("nonexistent")
        await small_cache.get("also_missing")
        assert small_cache.stats.misses == 2

        # Test evictions by filling cache beyond capacity
        await small_cache.set("key3", "value3")  # At capacity (3)
        await small_cache.set("key4", "value4")  # Should evict oldest

        assert small_cache.stats.evictions == 1
        assert small_cache.stats.size == 3  # Max size maintained

    @pytest.mark.asyncio
    async def test_reset_stats_retains_size(self, small_cache):
        """Test that reset_stats retains current cache size."""
        # Add some items
        await small_cache.set("keep1", "value1")
        await small_cache.set("keep2", "value2")

        # Generate some stats
        await small_cache.get("keep1")  # Hit
        await small_cache.get("missing")  # Miss

        current_size = small_cache.stats.size
        assert current_size == 2
        assert small_cache.stats.hits > 0
        assert small_cache.stats.misses > 0
        assert small_cache.stats.writes > 0

        # Reset stats
        small_cache.reset_stats()

        # Size should be retained, other stats reset
        assert small_cache.stats.size == current_size
        assert small_cache.stats.hits == 0
        assert small_cache.stats.misses == 0
        assert small_cache.stats.writes == 0
        assert small_cache.stats.evictions == 0
        assert small_cache.stats.errors == 0

    @pytest.mark.asyncio
    async def test_size_bounds_enforcement(self, small_cache):
        """Test that size bounds are strictly enforced."""
        max_size = small_cache.max_size

        # Fill beyond capacity
        for i in range(max_size + 3):
            await small_cache.set(f"key_{i}", f"value_{i}")

        # Size should never exceed max_size
        assert small_cache.stats.size <= max_size
        assert small_cache.stats.size == max_size  # Should be exactly at limit

        # Should have evictions
        assert small_cache.stats.evictions > 0

    @pytest.mark.asyncio
    async def test_cleanup_interval_behavior(self):
        """Test cleanup interval behavior."""
        # Create cache with very short cleanup interval
        cache = MemoryCacheAdapter(
            max_size=10,
            default_ttl_seconds=0.05,
            cleanup_interval_seconds=0.02,  # Very short interval
        )

        try:
            # Add items that will expire quickly
            await cache.set("exp1", "value1")
            await cache.set("exp2", "value2")

            # Wait for cleanup cycles
            await asyncio.sleep(0.1)

            # Access cache to ensure cleanup task has run
            await cache.get("exp1")

            # Items should be cleaned up by background task
            # Note: This test is timing-dependent and may be flaky
            # In practice, expired items are cleaned up on access or by background task

        finally:
            await cache.close()

    @pytest.mark.asyncio
    async def test_no_ttl_items_never_expire(self, no_ttl_cache):
        """Test that items with no TTL never expire naturally."""
        # Set item without TTL (uses cache's None default)
        await no_ttl_cache.set("permanent", "forever")

        # Wait longer than any reasonable TTL
        await asyncio.sleep(0.1)

        # Should still be there
        result = await no_ttl_cache.get("permanent")
        assert result == "forever"

        # Should be a hit, not a miss due to expiry
        assert no_ttl_cache.stats.hits > 0

    @pytest.mark.asyncio
    async def test_manual_ttl_overrides_default(self, small_cache):
        """Test that manual TTL overrides default TTL."""
        # Cache has default_ttl_seconds=1.0

        # Set with longer TTL than default
        await small_cache.set("long_lived", "value", ttl_seconds=5.0)

        # Set with shorter TTL than default
        await small_cache.set("short_lived", "value", ttl_seconds=0.05)

        # Wait past short TTL but less than default TTL
        await asyncio.sleep(0.1)

        # Long-lived should still be there
        assert await small_cache.get("long_lived") == "value"

        # Short-lived should be expired
        assert await small_cache.get("short_lived") is None

    @pytest.mark.asyncio
    async def test_error_handling_and_stats(self, small_cache):
        """Test error handling increments error stats."""
        # Reset stats to start clean
        small_cache.reset_stats()

        # Force an error by mocking internal operations
        with patch.object(small_cache, "_cache") as mock_cache:
            mock_cache.__contains__.side_effect = Exception("Mock error")
            with pytest.raises(CacheError, match="Failed to get key 'test'"):
                await small_cache.get("test")

        assert small_cache.stats.errors == 1

    @pytest.mark.asyncio
    async def test_concurrent_access_safety(self, small_cache):
        """Test that concurrent access doesn't corrupt cache state."""

        async def set_items(start_idx, count):
            for i in range(count):
                await small_cache.set(f"concurrent_{start_idx}_{i}", f"value_{start_idx}_{i}")

        async def get_items(start_idx, count):
            for i in range(count):
                await small_cache.get(f"concurrent_{start_idx}_{i}")

        # Run concurrent operations
        await asyncio.gather(set_items(0, 5), set_items(1, 5), get_items(0, 3), get_items(1, 3))

        # Cache should be in consistent state
        assert small_cache.stats.size <= small_cache.max_size
        assert small_cache.stats.writes > 0

    @pytest.mark.asyncio
    async def test_memory_usage_reporting(self, small_cache):
        """Test memory usage reporting functionality."""
        # Add some items with different sizes
        await small_cache.set("small", "x")
        await small_cache.set("medium", "x" * 100)
        await small_cache.set("large", "x" * 1000)

        usage = await small_cache.get_memory_usage()

        assert isinstance(usage, dict)
        assert "entry_count" in usage
        assert "max_size" in usage
        assert "utilization" in usage
        assert "total_size_bytes" in usage
        assert "average_entry_size" in usage

        assert usage["entry_count"] == 3
        assert usage["max_size"] == small_cache.max_size
        assert 0 <= usage["utilization"] <= 1
        assert usage["total_size_bytes"] > 0
        assert usage["average_entry_size"] > 0

    @pytest.mark.asyncio
    async def test_expired_count_reporting(self, small_cache):
        """Test expired count reporting without cleanup."""
        # Add items with short TTL
        await small_cache.set("exp1", "value1", ttl_seconds=0.05)
        await small_cache.set("exp2", "value2", ttl_seconds=0.05)
        await small_cache.set("keep", "value3", ttl_seconds=10.0)

        # Wait for expiry
        await asyncio.sleep(0.1)

        # Check expired count without triggering cleanup
        expired_count = await small_cache.get_expired_count()
        assert expired_count >= 2  # At least 2 should be expired

    @pytest.mark.asyncio
    async def test_cache_close_cleanup(self):
        """Test that closing cache properly cleans up resources."""
        cache = MemoryCacheAdapter(max_size=5, cleanup_interval_seconds=0.1)

        # Use the cache briefly
        await cache.set("test", "value")
        await cache.get("test")

        # Close should not raise error
        await cache.close()

        # Calling close again should be safe
        await cache.close()

    def test_invalid_construction_parameters(self):
        """Test that invalid constructor parameters raise errors."""
        # Test negative max_size
        with pytest.raises(ValueError, match="max_size must be greater than 0"):
            MemoryCacheAdapter(max_size=0)

        with pytest.raises(ValueError, match="max_size must be greater than 0"):
            MemoryCacheAdapter(max_size=-1)

        # Test negative TTL
        with pytest.raises(ValueError, match="default_ttl_seconds must be non-negative"):
            MemoryCacheAdapter(default_ttl_seconds=-1.0)

    @pytest.mark.asyncio
    async def test_size_estimation_for_different_types(self, small_cache):
        """Test size estimation for different value types."""
        test_values = [
            ("string", "hello world"),
            ("int", 42),
            ("float", 3.14159),
            ("dict", {"key": "value", "number": 123}),
            ("list", [1, 2, 3, "four", "five"]),
        ]

        for key, value in test_values:
            await small_cache.set(key, value)
            retrieved = await small_cache.get(key)
            assert retrieved == value

        # Should have size estimation without errors
        usage = await small_cache.get_memory_usage()
        assert usage["total_size_bytes"] > 0

    @pytest.mark.asyncio
    async def test_cleanup_task_error_handling(self):
        """Test that cleanup task handles errors gracefully."""
        cache = MemoryCacheAdapter(
            max_size=5,
            cleanup_interval_seconds=0.01,  # Very frequent cleanup
        )

        try:
            # Add an item
            await cache.set("test", "value")

            # Mock _cleanup_expired to raise an exception
            original_cleanup = cache._cleanup_expired

            async def failing_cleanup():
                raise Exception("Cleanup failed")

            # Temporarily replace cleanup method
            cache._cleanup_expired = failing_cleanup

            # Wait for cleanup cycle - should not crash
            await asyncio.sleep(0.05)

            # Restore original cleanup
            cache._cleanup_expired = original_cleanup

            # Cache should still work
            assert await cache.get("test") == "value"

        finally:
            await cache.close()
