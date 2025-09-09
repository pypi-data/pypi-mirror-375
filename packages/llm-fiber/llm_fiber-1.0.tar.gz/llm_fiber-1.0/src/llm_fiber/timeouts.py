"""Timeout configuration for llm-fiber."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Timeouts:
    """Timeout configuration for HTTP requests.

    All timeouts are in seconds. None means no timeout.

    Args:
        connect: Maximum time to wait for a connection to be established
        read: Maximum time to wait for data to be received
        total: Maximum total time for the entire request (including retries)
    """

    connect: Optional[float] = 5.0
    read: Optional[float] = 30.0
    total: Optional[float] = 60.0

    def __post_init__(self):
        """Validate timeout values."""
        if self.connect is not None and self.connect <= 0:
            raise ValueError("connect timeout must be positive")
        if self.read is not None and self.read <= 0:
            raise ValueError("read timeout must be positive")
        if self.total is not None and self.total <= 0:
            raise ValueError("total timeout must be positive")

        # Warn if total < connect + read (but don't error since read may be per-chunk)
        if (
            self.total is not None
            and self.connect is not None
            and self.read is not None
            and self.total < self.connect + self.read
        ):
            import warnings

            warnings.warn(
                f"total timeout ({self.total}s) is less than connect + read "
                f"({self.connect + self.read}s). This may cause unexpected timeouts.",
                UserWarning,
            )

    @classmethod
    def conservative(cls) -> Timeouts:
        """Conservative timeouts for production use."""
        return cls(connect=10.0, read=60.0, total=120.0)

    @classmethod
    def aggressive(cls) -> Timeouts:
        """Aggressive timeouts for low-latency scenarios."""
        return cls(connect=2.0, read=10.0, total=30.0)

    @classmethod
    def none(cls) -> Timeouts:
        """No timeouts (infinite wait)."""
        return cls(connect=None, read=None, total=None)

    def with_total(self, total: Optional[float]) -> Timeouts:
        """Return new Timeouts with different total timeout."""
        return Timeouts(connect=self.connect, read=self.read, total=total)

    def with_read(self, read: Optional[float]) -> Timeouts:
        """Return new Timeouts with different read timeout."""
        return Timeouts(connect=self.connect, read=read, total=self.total)

    def with_connect(self, connect: Optional[float]) -> Timeouts:
        """Return new Timeouts with different connect timeout."""
        return Timeouts(connect=connect, read=self.read, total=self.total)
