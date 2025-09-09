"""Batch operations for llm-fiber."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .retry import RetryPolicy, retry_async
from .types import ChatMessage, ChatResult, FiberError, MessagesInput


class BatchError(FiberError):
    """Error related to batch operations."""

    pass


class BatchStrategy(Enum):
    """Strategy for handling batch operations."""

    CONCURRENT = "concurrent"  # Process all requests concurrently
    SEQUENTIAL = "sequential"  # Process requests one by one
    ADAPTIVE = "adaptive"  # Adapt based on error rates


@dataclass
class BatchRequest:
    """A single request in a batch operation."""

    id: str  # Unique identifier for this request
    model: Optional[str] = None
    messages: Optional[MessagesInput] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    seed: Optional[int] = None
    stop: Optional[List[str]] = None
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[str] = None
    timeout_s: Optional[float] = None
    provider: Optional[str] = None
    idempotency_key: Optional[str] = None
    kwargs: Dict[str, Any] = field(default_factory=dict)

    def __init__(
        self,
        id: str,
        messages: Optional[MessagesInput] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        seed: Optional[int] = None,
        stop: Optional[List[str]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        timeout_s: Optional[float] = None,
        provider: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        **kwargs,
    ):
        """Initialize BatchRequest with arbitrary kwargs support."""
        self.id = id
        self.messages = messages
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.seed = seed
        self.stop = stop
        self.tools = tools
        self.tool_choice = tool_choice
        self.timeout_s = timeout_s
        self.provider = provider
        self.idempotency_key = idempotency_key
        self.kwargs = kwargs

        # Set kwargs as attributes for easy access
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """Convert batch request to dictionary."""
        result_dict = {
            "model": self.model,
            "messages": self.messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "seed": self.seed,
            "stop": self.stop,
            "tools": self.tools,
            "tool_choice": self.tool_choice,
            "timeout_s": self.timeout_s,
            "provider": self.provider,
            "idempotency_key": self.idempotency_key,
        }
        # Add kwargs
        result_dict.update(self.kwargs)
        return result_dict


@dataclass
class BatchResult:
    """Result of a batch operation."""

    id: str
    result: Optional[ChatResult] = None
    error: Optional[Exception] = None
    duration_ms: Optional[float] = None

    @property
    def is_success(self) -> bool:
        """Return True if the batch request was successful."""
        return self.error is None

    def to_dict(self) -> Dict[str, Any]:
        """Convert batch request to dictionary."""
        result_dict = {
            "id": self.id,
            "result": self.result.to_dict() if self.result else None,
            "error": str(self.error) if self.error else None,
            "duration_ms": self.duration_ms,
            "is_success": self.is_success,
        }
        return result_dict


class BatchSummary:
    """Summary of batch operation results."""

    def __init__(self, results: List[BatchResult]):
        """Initialize BatchSummary from a list of BatchResult objects."""
        self.results = results
        self.total_requests = len(results)

        # Calculate success/failure counts
        successful_results = [r for r in results if r.is_success]
        failed_results = [r for r in results if not r.is_success]

        self.successful_requests = len(successful_results)
        self.failed_requests = len(failed_results)

        # Calculate duration statistics
        durations = [r.duration_ms for r in results if r.duration_ms is not None]
        if durations:
            self.total_duration_ms = sum(durations)
            self.average_duration_ms = self.total_duration_ms / len(durations)
            self.max_duration_ms = max(durations)
            self.min_duration_ms = min(durations)
        else:
            self.total_duration_ms = 0.0
            self.average_duration_ms = 0.0
            self.max_duration_ms = 0.0
            self.min_duration_ms = 0.0

        # Calculate total usage
        from .types import Usage

        total_prompt = 0
        total_completion = 0
        total_cost = 0.0

        for result in successful_results:
            if result.result and result.result.usage:
                usage = result.result.usage
                total_prompt += usage.prompt
                total_completion += usage.completion
                if usage.cost_estimate:
                    total_cost += usage.cost_estimate

        self.total_usage = Usage(
            prompt=total_prompt,
            completion=total_completion,
            total=total_prompt + total_completion,
            cost_estimate=total_cost,
        )

        # Collect error messages
        self.errors = [str(r.error) for r in failed_results if r.error]


@dataclass
class BatchConfig:
    """Configuration for batch operations."""

    max_concurrent: int = 10
    strategy: BatchStrategy = BatchStrategy.CONCURRENT
    return_exceptions: bool = True
    fail_fast: bool = False
    timeout_per_request: Optional[float] = 60.0
    retry_failed: bool = False
    max_retries: int = 3

    def __post_init__(self):
        """Validate configuration parameters."""
        if self.max_concurrent <= 0:
            raise ValueError("max_concurrent must be greater than 0")

        if self.timeout_per_request is not None and self.timeout_per_request <= 0:
            raise ValueError("timeout_per_request must be greater than 0")

        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")


class BatchProcessor:
    """Processor for batch operations."""

    def __init__(self, config: Optional[BatchConfig] = None, fiber_client=None):
        """Initialize batch processor.

        Args:
            config: Batch configuration
            fiber_client: Fiber client instance (optional)
        """
        self.fiber = fiber_client
        self.config = config or BatchConfig()

    async def process_batch(
        self, requests: List[BatchRequest], chat_function: Callable
    ) -> List[BatchResult]:
        """Process batch requests using the provided chat function.

        Args:
            requests: List of batch requests
            chat_function: Chat function to use for processing

        Returns:
            List of batch results

        Raises:
            FiberError: If fail_fast is True and any request fails
        """
        self._chat_function = chat_function
        return await self.process_async(requests)

    async def process_async(self, requests: List[BatchRequest]) -> List[BatchResult]:
        """Process batch requests asynchronously.

        Args:
            requests: List of batch requests

        Returns:
            List of batch results

        Raises:
            FiberError: If fail_fast is True and any request fails
        """
        if not requests:
            return []

        # Track timing
        import time

        start_time = time.time()

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.config.max_concurrent)

        # Process requests based on strategy
        if self.config.strategy == BatchStrategy.SEQUENTIAL:
            results = await self._process_sequential(requests, semaphore)
        elif self.config.strategy == BatchStrategy.CONCURRENT:
            results = await self._process_concurrent(requests, semaphore)
        elif self.config.strategy == BatchStrategy.ADAPTIVE:
            results = await self._process_adaptive(requests, semaphore)
        else:
            raise ValueError(f"Unknown batch strategy: {self.config.strategy}")

        # Record metrics if available
        total_duration = time.time() - start_time
        if hasattr(self.fiber, "metrics"):
            self.fiber.metrics.record_batch_operation(
                total_requests=len(requests),
                successful=sum(1 for r in results if r.is_success),
                failed=sum(1 for r in results if not r.is_success),
                duration_seconds=total_duration,
            )

        return results

    def process_sync(self, requests: List[BatchRequest]) -> List[BatchResult]:
        """Process batch requests synchronously.

        Args:
            requests: List of batch requests

        Returns:
            List of batch results
        """
        # Run async method in event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.process_async(requests))

    async def _process_sequential(
        self, requests: List[BatchRequest], semaphore: asyncio.Semaphore
    ) -> List[BatchResult]:
        """Process requests sequentially."""
        results = []

        for request in requests:
            result = await self._process_single_request(request, semaphore)
            results.append(result)

            # Handle fail_fast
            if self.config.fail_fast and not result.is_success:
                if not self.config.return_exceptions:
                    raise result.error
                break

        return results

    async def _process_concurrent(
        self, requests: List[BatchRequest], semaphore: asyncio.Semaphore
    ) -> List[BatchResult]:
        """Process requests concurrently."""
        # Create tasks for all requests
        tasks = [
            asyncio.create_task(self._process_single_request(request, semaphore))
            for request in requests
        ]

        if self.config.fail_fast and not self.config.return_exceptions:
            # Use as_completed to stop on first failure
            results = []
            pending = set(tasks)

            while pending:
                done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)

                for task in done:
                    result = await task
                    results.append(result)

                    if not result.is_success:
                        # Cancel remaining tasks
                        for p in pending:
                            p.cancel()
                        raise BatchError(
                            f"Batch processing failed: {result.error}"
                        ) from result.error

            return results
        else:
            # Process all tasks and return results/exceptions
            if self.config.return_exceptions:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                # Convert any exceptions to BatchResult objects
                processed_results = []
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        processed_results.append(
                            BatchResult(id=requests[i].id, error=result, duration_ms=0.0)
                        )
                    else:
                        processed_results.append(result)
                return processed_results
            else:
                return await asyncio.gather(*tasks, return_exceptions=False)

    async def _process_adaptive(
        self, requests: List[BatchRequest], semaphore: asyncio.Semaphore
    ) -> List[BatchResult]:
        """Process requests with adaptive strategy based on error rates."""
        # Start with concurrent processing
        results = []
        error_count = 0
        total_processed = 0

        # Process in chunks to adapt
        chunk_size = min(self.config.max_concurrent, len(requests))

        for i in range(0, len(requests), chunk_size):
            chunk = requests[i : i + chunk_size]

            # Decide strategy based on error rate
            error_rate = error_count / max(total_processed, 1)

            if error_rate > 0.3:  # High error rate, go sequential
                chunk_results = await self._process_sequential(chunk, semaphore)
            else:
                chunk_results = await self._process_concurrent(chunk, semaphore)

            results.extend(chunk_results)

            # Update error tracking
            error_count += sum(1 for r in chunk_results if not r.is_success)
            total_processed += len(chunk_results)

            # Handle fail_fast
            if self.config.fail_fast:
                failed_result = next((r for r in chunk_results if not r.is_success), None)
                if failed_result and not self.config.return_exceptions:
                    raise failed_result.error

        return results

    async def _process_single_request(
        self, request: BatchRequest, semaphore: asyncio.Semaphore
    ) -> BatchResult:
        """Process a single request with error handling and timing."""
        async with semaphore:
            import time

            start_time = time.time()

            # Create retry policy for this request
            retry_policy = (
                RetryPolicy(max_attempts=self.config.max_retries)
                if self.config.retry_failed
                else RetryPolicy.none()
            )

            async def _execute_request():
                """Execute the actual request - this will be retried."""
                # Extract timeout
                timeout_s = request.timeout_s or self.config.timeout_per_request

                # Make the request with timeout handling
                if hasattr(self, "_chat_function"):
                    chat_coro = self._chat_function(
                        model=request.model,
                        messages=request.messages,
                        temperature=request.temperature,
                        max_tokens=request.max_tokens,
                        top_p=request.top_p,
                        seed=request.seed,
                        stop=request.stop,
                        tools=request.tools,
                        tool_choice=request.tool_choice,
                        timeout_s=timeout_s,
                        provider=request.provider,
                        idempotency_key=request.idempotency_key,
                        **request.kwargs,
                    )
                else:
                    chat_coro = self.fiber.chat(
                        model=request.model,
                        messages=request.messages,
                        temperature=request.temperature,
                        max_tokens=request.max_tokens,
                        top_p=request.top_p,
                        seed=request.seed,
                        stop=request.stop,
                        tools=request.tools,
                        tool_choice=request.tool_choice,
                        timeout_s=timeout_s,
                        provider=request.provider,
                        idempotency_key=request.idempotency_key,
                        **request.kwargs,
                    )

                # Apply timeout if specified
                if timeout_s is not None:
                    return await asyncio.wait_for(chat_coro, timeout=timeout_s)
                else:
                    return await chat_coro

            try:
                # Execute with retry logic if enabled
                if self.config.retry_failed:

                    def on_retry_callback(retry_context):
                        """Log retry attempts."""
                        if hasattr(self.fiber, "logger") and self.fiber.logger:
                            self.fiber.logger.log_retry_attempt(
                                provider=request.provider or "unknown",
                                model=request.model,
                                operation="batch_request",
                                attempt=retry_context.attempt,
                                max_attempts=retry_policy.max_attempts,
                                error=retry_context.last_exception,
                                delay_ms=int(retry_context.calculate_delay() * 1000),
                                request_id=request.id,
                            )

                        # Record retry metrics if available
                        if hasattr(self.fiber, "metrics") and self.fiber.metrics:
                            error_type = type(retry_context.last_exception).__name__
                            self.fiber.metrics.record_retry(
                                provider=request.provider or "unknown",
                                model=request.model,
                                error_type=error_type,
                                operation="batch_request",
                                attempt=retry_context.attempt,
                            )

                    result = await retry_async(
                        _execute_request,
                        retry_policy,
                        total_timeout=self.config.timeout_per_request,
                        on_retry=on_retry_callback,
                    )
                else:
                    result = await _execute_request()

                duration = time.time() - start_time

                return BatchResult(
                    id=request.id,
                    result=result,
                    duration_ms=duration * 1000,  # Convert to milliseconds
                )

            except asyncio.TimeoutError:
                duration = time.time() - start_time
                timeout_error = Exception(
                    f"Request timed out after {self.config.timeout_per_request}s"
                )
                return BatchResult(
                    id=request.id,
                    error=timeout_error,
                    duration_ms=duration * 1000,  # Convert to milliseconds
                )

            except Exception as e:
                duration = time.time() - start_time

                return BatchResult(
                    id=request.id,
                    error=e,
                    duration_ms=duration * 1000,  # Convert to milliseconds
                )

    def create_summary(self, results: List[BatchResult]) -> BatchSummary:
        """Create a summary of batch results."""
        return BatchSummary(results)


# Convenience functions for creating batch requests
def create_batch_request(
    messages: MessagesInput, id: Optional[str] = None, model: Optional[str] = None, **kwargs
) -> BatchRequest:
    """Create a batch request with common parameters."""
    import time

    # Handle request_id kwarg for backwards compatibility
    if "request_id" in kwargs:
        id = kwargs.pop("request_id")

    # Auto-generate ID if not provided
    if id is None:
        import uuid

        id = f"batch_req_{int(time.time() * 1000)}_{str(uuid.uuid4())[:8]}"

    return BatchRequest(id=id, model=model, messages=messages, **kwargs)


def create_batch_from_prompts(
    prompts: List[str],
    model: Optional[str] = None,
    id_prefix: str = "req",
    system_message: Optional[str] = None,
    **kwargs,
) -> List[BatchRequest]:
    """Create batch requests from a list of prompts."""

    def create_messages(prompt: str) -> List[ChatMessage]:
        messages = []
        if system_message:
            messages.append(ChatMessage(role="system", content=system_message))
        messages.append(ChatMessage(role="user", content=prompt))
        return messages

    return [
        BatchRequest(id=f"{id_prefix}_{i}", model=model, messages=create_messages(prompt), **kwargs)
        for i, prompt in enumerate(prompts)
    ]


def create_batch_from_conversations(
    conversations: List[List[ChatMessage]],
    model: Optional[str] = None,
    id_prefix: str = "conv",
    system_message: Optional[str] = None,
    **kwargs,
) -> List[BatchRequest]:
    """Create batch requests from a list of conversations."""

    def add_system_message(conversation: List[ChatMessage]) -> List[ChatMessage]:
        if system_message:
            return [ChatMessage(role="system", content=system_message)] + conversation
        return conversation

    return [
        BatchRequest(
            id=f"{id_prefix}_{i}", model=model, messages=add_system_message(conversation), **kwargs
        )
        for i, conversation in enumerate(conversations)
    ]


__all__ = [
    "BatchStrategy",
    "BatchRequest",
    "BatchResult",
    "BatchSummary",
    "BatchConfig",
    "BatchProcessor",
    "create_batch_request",
    "create_batch_from_prompts",
    "create_batch_from_conversations",
]
