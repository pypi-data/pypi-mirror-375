"""Memory cache adapter with LRU+TTL eviction for llm-fiber."""

from __future__ import annotations

import asyncio
import time
from collections import OrderedDict
from typing import Any, Dict, Optional

from . import CacheAdapter, CacheEntry, CacheError, CachePolicy, InvalidCacheKeyError


class MemoryCacheAdapter(CacheAdapter):
    """Memory-based cache adapter with LRU+TTL eviction."""

    def __init__(
        self,
        max_size: int = 1000,
        policy: CachePolicy = CachePolicy.READ_THROUGH,
        default_ttl_seconds: Optional[float] = 3600,
        cleanup_interval_seconds: float = 300,
    ):
        """Initialize memory cache adapter.

        Args:
            max_size: Maximum number of entries to cache
            policy: Cache policy
            default_ttl_seconds: Default TTL for entries
            cleanup_interval_seconds: How often to clean up expired entries
        """
        # Initialize cleanup task early to prevent issues in __del__
        self._cleanup_task: Optional[asyncio.Task] = None

        super().__init__(policy, default_ttl_seconds)

        if max_size <= 0:
            raise ValueError("max_size must be greater than 0")

        if default_ttl_seconds is not None and default_ttl_seconds < 0:
            raise ValueError("default_ttl_seconds must be non-negative")

        self.max_size = max_size
        self.cleanup_interval_seconds = cleanup_interval_seconds

        # Use OrderedDict for LRU functionality
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = None

        # Defer starting background cleanup task until an event loop is running
        # It will be started lazily on first async operation

    def _start_cleanup_task(self) -> None:
        """Start the background cleanup task."""
        try:
            # Only start if there's a running loop
            asyncio.get_running_loop()
        except RuntimeError:
            return
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def _cleanup_loop(self) -> None:
        """Background task to clean up expired entries."""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval_seconds)
                await self._cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error but don't stop cleanup
                print(f"Cache cleanup error: {e}")

    async def _cleanup_expired(self) -> None:
        """Remove expired entries from cache."""
        async with self._lock:
            expired_keys = []

            for key, entry in self._cache.items():
                if entry.is_expired:
                    expired_keys.append(key)

            for key in expired_keys:
                del self._cache[key]
                self.stats.evictions += 1

            self.stats.size = len(self._cache)

    def _touch_entry(self, key: str) -> None:
        """Move entry to end (most recently used) and update access time."""
        if key in self._cache:
            entry = self._cache[key]
            entry.last_accessed = time.time()
            # Move to end in OrderedDict
            self._cache.move_to_end(key)

    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if self._cache:
            # OrderedDict.popitem(last=False) removes oldest item
            key, entry = self._cache.popitem(last=False)
            self.stats.evictions += 1
            self.stats.size = len(self._cache)

    def _validate_key(self, key: str) -> None:
        """Validate cache key."""
        if not key or not isinstance(key, str):
            raise InvalidCacheKeyError("Cache key must be a non-empty string")

    def _estimate_size(self, value: Any) -> int:
        """Estimate memory size of a value in bytes."""
        try:
            if isinstance(value, str):
                return len(value.encode("utf-8"))
            elif isinstance(value, (int, float)):
                return 8
            elif isinstance(value, dict):
                # Rough estimation for serialized dict
                import json

                return len(json.dumps(value).encode("utf-8"))
            else:
                # Fallback estimation
                return len(str(value).encode("utf-8"))
        except Exception:
            return 1024  # Default estimate

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from the memory cache."""
        self._validate_key(key)
        try:
            if self._lock is None:
                self._lock = asyncio.Lock()
                self._start_cleanup_task()
            async with self._lock:
                if key not in self._cache:
                    self.stats.misses += 1
                    return None

                entry = self._cache[key]

                # Check if expired
                if entry.is_expired:
                    del self._cache[key]
                    self.stats.evictions += 1
                    self.stats.misses += 1
                    self.stats.size = len(self._cache)
                    return None

                # Touch entry for LRU
                self._touch_entry(key)
                self.stats.hits += 1
                return entry.value

        except Exception as e:
            self.stats.errors += 1
            raise CacheError(f"Failed to get key '{key}': {e}")

    async def set(self, key: str, value: Any, ttl_seconds: Optional[float] = None) -> None:
        """Store a value in the memory cache."""
        self._validate_key(key)
        try:
            if self._lock is None:
                self._lock = asyncio.Lock()
                self._start_cleanup_task()
            async with self._lock:
                current_time = time.time()
                ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl_seconds
                size_bytes = self._estimate_size(value)

                # Create cache entry
                entry = CacheEntry(
                    key=key,
                    value=value,
                    created_at=current_time,
                    last_accessed=current_time,
                    ttl_seconds=ttl,
                    size_bytes=size_bytes,
                )

                # Check if we need to evict
                while len(self._cache) >= self.max_size:
                    self._evict_lru()

                # Store the entry
                self._cache[key] = entry
                self.stats.writes += 1
                self.stats.size = len(self._cache)

        except Exception as e:
            self.stats.errors += 1
            raise CacheError(f"Failed to set key '{key}': {e}")

    async def delete(self, key: str) -> bool:
        """Delete a value from the memory cache."""
        self._validate_key(key)
        try:
            if self._lock is None:
                self._lock = asyncio.Lock()
                self._start_cleanup_task()
            async with self._lock:
                if key in self._cache:
                    del self._cache[key]
                    self.stats.size = len(self._cache)
                    return True
                return False

        except Exception as e:
            self.stats.errors += 1
            raise CacheError(f"Failed to delete key '{key}': {e}")

    async def clear(self) -> None:
        """Clear all cached values."""
        try:
            if self._lock is None:
                self._lock = asyncio.Lock()
                self._start_cleanup_task()
            async with self._lock:
                self._cache.clear()
                self.stats.size = 0

        except Exception as e:
            self.stats.errors += 1
            raise CacheError(f"Failed to clear cache: {e}")

    async def size(self) -> int:
        """Get the number of cached entries."""
        try:
            async with self._lock:
                return len(self._cache)

        except Exception as e:
            self.stats.errors += 1
            raise CacheError(f"Failed to get cache size: {e}")

    async def get_memory_usage(self) -> Dict[str, Any]:
        """Get detailed memory usage information."""
        try:
            if self._lock is None:
                self._lock = asyncio.Lock()
                self._start_cleanup_task()
            async with self._lock:
                total_size_bytes = sum(entry.size_bytes for entry in self._cache.values())
                entry_count = len(self._cache)

                return {
                    "entry_count": entry_count,
                    "max_size": self.max_size,
                    "utilization": entry_count / self.max_size if self.max_size > 0 else 0,
                    "total_size_bytes": total_size_bytes,
                    "average_entry_size": total_size_bytes / entry_count if entry_count > 0 else 0,
                }

        except Exception as e:
            self.stats.errors += 1
            raise CacheError(f"Failed to get memory usage: {e}")

    async def get_expired_count(self) -> int:
        """Get count of expired entries (without removing them)."""
        try:
            async with self._lock:
                return sum(1 for entry in self._cache.values() if entry.is_expired)

        except Exception as e:
            self.stats.errors += 1
            raise CacheError(f"Failed to count expired entries: {e}")

    def __del__(self):
        """Cleanup when adapter is destroyed."""
        if hasattr(self, "_cleanup_task") and self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()

    async def close(self) -> None:
        """Explicitly close the cache adapter."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

    def reset_stats(self) -> None:
        """Reset cache statistics while preserving current cache size."""
        current_size = len(self._cache)
        super().reset_stats()
        self.stats.size = current_size
