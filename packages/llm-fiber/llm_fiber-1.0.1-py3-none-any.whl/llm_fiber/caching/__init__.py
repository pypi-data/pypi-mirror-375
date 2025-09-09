"""Caching system for llm-fiber."""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from ..types import ChatMessage, ChatResult


class CachePolicy(Enum):
    """Cache policies for request handling."""

    OFF = "off"  # No caching
    READ_THROUGH = "read_through"  # Read from cache, write on miss
    WRITE_THROUGH = "write_through"  # Always write to cache


@dataclass
class CacheStats:
    """Cache statistics for observability."""

    hits: int = 0
    misses: int = 0
    writes: int = 0
    evictions: int = 0
    errors: int = 0
    size: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total

    @property
    def total_requests(self) -> int:
        """Calculate total cache requests."""
        return self.hits + self.misses

    def __str__(self) -> str:
        """String representation of cache stats."""
        return (
            f"CacheStats(hits={self.hits}, misses={self.misses}, "
            f"writes={self.writes}, evictions={self.evictions}, "
            f"errors={self.errors}, size={self.size}, "
            f"hit_rate={self.hit_rate:.1f})"
        )


@dataclass
class CacheEntry:
    """A single cache entry with metadata."""

    key: str
    value: Any
    created_at: float
    last_accessed: float
    ttl_seconds: Optional[float] = None
    size_bytes: int = 0

    @property
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.ttl_seconds is None:
            return False

        import time

        return (time.time() - self.created_at) > self.ttl_seconds


class CacheError(Exception):
    """Base exception for cache-related errors."""

    pass


class InvalidCacheKeyError(CacheError):
    """Raised when a cache key is invalid or malformed."""

    pass


class CacheAdapter(ABC):
    """Abstract base class for cache adapters."""

    def __init__(
        self,
        policy: CachePolicy = CachePolicy.READ_THROUGH,
        default_ttl_seconds: Optional[float] = 3600,
    ):
        self.policy = policy
        self.default_ttl_seconds = default_ttl_seconds
        self.stats = CacheStats()

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found

        Raises:
            CacheError: On cache adapter failures (should be caught and logged)
        """
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: Optional[float] = None) -> None:
        """Store a value in the cache.

        Args:
            key: Cache key
            value: Value to store
            ttl_seconds: Time to live in seconds (uses default if None)

        Raises:
            CacheError: On cache adapter failures (should be caught and logged)
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a value from the cache.

        Args:
            key: Cache key

        Returns:
            True if key existed and was deleted, False otherwise

        Raises:
            CacheError: On cache adapter failures (should be caught and logged)
        """
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all cached values.

        Raises:
            CacheError: On cache adapter failures (should be caught and logged)
        """
        pass

    @abstractmethod
    async def size(self) -> int:
        """Get the number of cached entries.

        Returns:
            Number of entries in cache

        Raises:
            CacheError: On cache adapter failures (should be caught and logged)
        """
        pass

    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        return self.stats

    def reset_stats(self) -> None:
        """Reset cache statistics."""
        self.stats = CacheStats()


class NoOpCacheAdapter(CacheAdapter):
    """No-operation cache adapter that doesn't actually cache anything."""

    def __init__(self):
        super().__init__(policy=CachePolicy.OFF)

    async def get(self, key: str) -> Optional[Any]:
        """Always return None (cache miss)."""
        self.stats.misses += 1
        return None

    async def set(self, key: str, value: Any, ttl_seconds: Optional[float] = None) -> None:
        """Do nothing."""
        pass

    async def delete(self, key: str) -> bool:
        """Always return False."""
        return False

    async def clear(self) -> None:
        """Do nothing."""
        pass

    async def size(self) -> int:
        """Always return 0."""
        return 0


def generate_cache_key(
    messages: List[ChatMessage],
    model: str,
    provider: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    top_p: Optional[float] = None,
    seed: Optional[int] = None,
    stop: Optional[List[str]] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    tool_choice: Optional[str] = None,
    **kwargs,
) -> str:
    """Generate a deterministic cache key for a chat request.

    Args:
        messages: List of chat messages
        model: Model name
        provider: Provider name (defaults to "default" if not provided)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        top_p: Nucleus sampling parameter
        seed: Random seed
        stop: Stop sequences
        tools: Available tools/functions
        tool_choice: Tool selection strategy
        **kwargs: Additional parameters

    Returns:
        Deterministic cache key string
    """
    # Use default provider if not specified
    if provider is None:
        provider = "default"

    # Create a dictionary with all the request parameters
    key_data = {
        "provider": provider,
        "model": model,
        "messages": [msg.to_dict() for msg in messages],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "seed": seed,
        "stop": stop,
        "tools": tools,
        "tool_choice": tool_choice,
    }

    # Add additional kwargs
    key_data.update(kwargs)

    # Remove None values for consistency
    key_data = {k: v for k, v in key_data.items() if v is not None}

    # Sort keys for deterministic ordering
    normalized_data = json.dumps(key_data, sort_keys=True, separators=(",", ":"))

    # Generate hash
    return hashlib.sha256(normalized_data.encode("utf-8")).hexdigest()


def serialize_chat_result(result: ChatResult) -> str:
    """Serialize a ChatResult for caching.

    Args:
        result: ChatResult to serialize

    Returns:
        JSON string representation suitable for caching
    """
    data = {
        "text": result.text,
        "tool_calls": result.tool_calls,
        "finish_reason": result.finish_reason,
        "usage": {
            "prompt": result.usage.prompt,
            "completion": result.usage.completion,
            "total": result.usage.total,
            "cost_estimate": result.usage.cost_estimate,
        }
        if result.usage
        else None,
        "raw": result.raw,
    }
    return json.dumps(data, separators=(",", ":"))


def deserialize_chat_result(json_data: str) -> ChatResult:
    """Deserialize a cached ChatResult.

    Args:
        json_data: JSON string representation from cache

    Returns:
        ChatResult object
    """
    from ..types import Usage  # Import here to avoid circular imports

    try:
        data = json.loads(json_data)
    except json.JSONDecodeError as e:
        raise CacheError(f"Invalid JSON in cached result: {e}") from e
    usage_data = data.get("usage")
    usage = None
    if usage_data is not None:
        usage = Usage(
            prompt=usage_data["prompt"],
            completion=usage_data["completion"],
            total=usage_data["total"],
            cost_estimate=usage_data.get("cost_estimate"),
        )

    return ChatResult(
        text=data["text"],
        tool_calls=data.get("tool_calls", []),
        finish_reason=data.get("finish_reason"),
        usage=usage,
        raw=data.get("raw", {}),
    )


__all__ = [
    "CachePolicy",
    "CacheStats",
    "CacheEntry",
    "CacheError",
    "InvalidCacheKeyError",
    "CacheAdapter",
    "NoOpCacheAdapter",
    "generate_cache_key",
    "serialize_chat_result",
    "deserialize_chat_result",
]
