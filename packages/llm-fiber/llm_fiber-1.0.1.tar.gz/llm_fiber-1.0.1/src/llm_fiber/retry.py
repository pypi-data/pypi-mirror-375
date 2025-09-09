"""Retry policy and backoff implementation for llm-fiber."""

from __future__ import annotations

import asyncio
import random
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional, Type

from .types import (
    FiberAuthError,
    FiberConnectionError,
    FiberProviderError,
    FiberQuotaError,
    FiberRateLimitError,
    FiberTimeoutError,
    FiberValidationError,
)


@dataclass(frozen=True)
class RetryPolicy:
    """Configuration for retry behavior.

    Args:
        max_attempts: Maximum number of attempts (including initial attempt)
        base_delay: Base delay in seconds before first retry
        max_delay: Maximum delay in seconds between retries
        backoff_factor: Multiplier for exponential backoff
        jitter: Whether to add random jitter to delays
        retryable_exceptions: Exception types that should trigger retries
        retryable_status_codes: HTTP status codes that should trigger retries
    """

    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    jitter: bool = True
    retryable_exceptions: tuple[Type[Exception], ...] = (
        FiberConnectionError,
        FiberTimeoutError,
        FiberRateLimitError,
    )
    retryable_status_codes: tuple[int, ...] = (
        429,  # Too Many Requests
        500,  # Internal Server Error
        502,  # Bad Gateway
        503,  # Service Unavailable
        504,  # Gateway Timeout
    )

    def __post_init__(self):
        """Validate policy parameters."""
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if self.base_delay <= 0:
            raise ValueError("base_delay must be positive")
        if self.max_delay < self.base_delay:
            raise ValueError("max_delay must be >= base_delay")
        if self.backoff_factor <= 0:
            raise ValueError("backoff_factor must be positive")

    @classmethod
    def none(cls) -> RetryPolicy:
        """No retries - fail immediately."""
        return cls(max_attempts=1)

    @classmethod
    def conservative(cls) -> RetryPolicy:
        """Conservative retry policy for production."""
        return cls(max_attempts=5, base_delay=2.0, max_delay=120.0, backoff_factor=2.0, jitter=True)

    @classmethod
    def aggressive(cls) -> RetryPolicy:
        """Aggressive retry policy for development."""
        return cls(max_attempts=2, base_delay=0.5, max_delay=10.0, backoff_factor=1.5, jitter=True)

    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """Determine if an exception should trigger a retry.

        Args:
            exception: The exception that occurred
            attempt: The current attempt number (1-based)

        Returns:
            True if the request should be retried
        """
        if attempt >= self.max_attempts:
            return False

        # Never retry validation or auth errors
        if isinstance(exception, (FiberValidationError, FiberAuthError, FiberQuotaError)):
            return False

        # Check if exception type is retryable
        if isinstance(exception, self.retryable_exceptions):
            return True

        # Check status codes for provider errors
        if isinstance(exception, FiberProviderError) and exception.status_code:
            return exception.status_code in self.retryable_status_codes

        return False

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay before next retry attempt.

        Args:
            attempt: The attempt number that just failed (1-based)

        Returns:
            Delay in seconds before next attempt
        """
        # Calculate exponential backoff
        delay = self.base_delay * (self.backoff_factor ** (attempt - 1))

        # Cap at max_delay
        delay = min(delay, self.max_delay)

        # Add jitter if enabled
        if self.jitter:
            # Add ±25% jitter
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)
            # Ensure delay is still positive
            delay = max(0.1, delay)

        return delay


class RetryContext:
    """Context for tracking retry state during request execution."""

    def __init__(self, policy: RetryPolicy):
        self.policy = policy
        self.attempt = 0
        self.start_time = time.time()
        self.last_exception: Optional[Exception] = None
        self.total_delay = 0.0

    def next_attempt(self) -> int:
        """Increment and return the next attempt number."""
        self.attempt += 1
        return self.attempt

    def record_exception(self, exception: Exception) -> None:
        """Record the latest exception."""
        self.last_exception = exception

    def should_retry(self, exception: Exception) -> bool:
        """Check if we should retry after this exception."""
        return self.policy.should_retry(exception, self.attempt)

    def calculate_delay(self) -> float:
        """Calculate delay before next retry."""
        delay = self.policy.calculate_delay(self.attempt)
        self.total_delay += delay
        return delay

    def elapsed_time(self) -> float:
        """Get total elapsed time since start."""
        return time.time() - self.start_time

    def is_timeout_exceeded(self, total_timeout: Optional[float]) -> bool:
        """Check if total timeout would be exceeded by next delay."""
        if total_timeout is None:
            return False

        elapsed = self.elapsed_time()
        next_delay = self.policy.calculate_delay(self.attempt)
        return (elapsed + next_delay) > total_timeout


async def retry_async(
    func: Callable[..., Any],
    policy: RetryPolicy,
    total_timeout: Optional[float] = None,
    on_retry: Optional[Callable[[RetryContext], None]] = None,
    *args,
    **kwargs,
) -> Any:
    """Execute an async function with retry logic.

    Args:
        func: Async function to execute
        policy: Retry policy to use
        total_timeout: Maximum total time including retries
        on_retry: Optional callback called before each retry
        *args, **kwargs: Arguments to pass to func

    Returns:
        Result of successful function call

    Raises:
        The last exception if all retries are exhausted
    """
    context = RetryContext(policy)

    while True:
        context.next_attempt()

        try:
            return await func(*args, **kwargs)
        except Exception as e:
            context.record_exception(e)

            # Check if we should retry
            if not context.should_retry(e):
                raise e

            # Check if total timeout would be exceeded
            if context.is_timeout_exceeded(total_timeout):
                raise FiberTimeoutError(
                    f"Total timeout would be exceeded. Elapsed: {context.elapsed_time():.2f}s, "
                    f"Timeout: {total_timeout}s"
                )

            # Calculate delay and wait
            delay = context.calculate_delay()

            # Call retry callback if provided
            if on_retry:
                on_retry(context)

            await asyncio.sleep(delay)


def retry_sync(
    func: Callable[..., Any],
    policy: RetryPolicy,
    total_timeout: Optional[float] = None,
    on_retry: Optional[Callable[[RetryContext], None]] = None,
    *args,
    **kwargs,
) -> Any:
    """Execute a sync function with retry logic.

    Args:
        func: Sync function to execute
        policy: Retry policy to use
        total_timeout: Maximum total time including retries
        on_retry: Optional callback called before each retry
        *args, **kwargs: Arguments to pass to func

    Returns:
        Result of successful function call

    Raises:
        The last exception if all retries are exhausted
    """
    context = RetryContext(policy)

    while True:
        context.next_attempt()

        try:
            return func(*args, **kwargs)
        except Exception as e:
            context.record_exception(e)

            # Check if we should retry
            if not context.should_retry(e):
                raise e

            # Check if total timeout would be exceeded
            if context.is_timeout_exceeded(total_timeout):
                raise FiberTimeoutError(
                    f"Total timeout would be exceeded. Elapsed: {context.elapsed_time():.2f}s, "
                    f"Timeout: {total_timeout}s"
                )

            # Calculate delay and wait
            delay = context.calculate_delay()

            # Call retry callback if provided
            if on_retry:
                on_retry(context)

            time.sleep(delay)


# Default retry policy
DEFAULT_RETRY_POLICY = RetryPolicy()
