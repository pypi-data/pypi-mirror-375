"""Synchronous wrappers for llm-fiber."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Iterator, List, Optional

from .types import ChatResult, MessagesInput, StreamEvent


def _run_async(coro):
    """Run an async coroutine synchronously."""
    try:
        # Try to get the current event loop
        loop = asyncio.get_running_loop()
        if loop.is_running():
            # We're already in an async context, can't run sync
            raise RuntimeError(
                "Cannot call sync methods from within an async context. "
                "Use the async methods directly instead."
            )
    except RuntimeError:
        # No running loop, we can create one
        pass

    return asyncio.run(coro)


class SyncFiber:
    """Synchronous wrapper for Fiber client."""

    def __init__(self, fiber):
        self._fiber = fiber

    def chat(
        self,
        messages: MessagesInput,
        *,
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
    ) -> ChatResult:
        """Execute a chat completion request synchronously.

        Args:
            messages: Chat messages (required)
            model: Model to use (defaults to default_model)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            seed: Random seed
            stop: Stop sequences
            tools: Available tools/functions
            tool_choice: Tool selection strategy
            timeout_s: Request timeout in seconds
            provider: Provider override
            idempotency_key: Idempotency key
            **kwargs: Additional provider-specific parameters

        Returns:
            ChatResult with response and metadata

        Raises:
            FiberError: On request failure
        """
        return _run_async(
            self._fiber.chat(
                messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                seed=seed,
                stop=stop,
                tools=tools,
                tool_choice=tool_choice,
                timeout_s=timeout_s,
                provider=provider,
                idempotency_key=idempotency_key,
                **kwargs,
            )
        )

    def chat_stream(
        self,
        messages: MessagesInput,
        *,
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
    ) -> Iterator[StreamEvent]:
        """Execute a streaming chat completion request synchronously.

        Args:
            messages: Chat messages (required)
            model: Model to use (defaults to default_model)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            seed: Random seed
            stop: Stop sequences
            tools: Available tools/functions
            tool_choice: Tool selection strategy
            timeout_s: Request timeout in seconds
            provider: Provider override
            idempotency_key: Idempotency key
            **kwargs: Additional provider-specific parameters

        Yields:
            StreamEvent objects for each response chunk

        Raises:
            FiberError: On request failure
        """

        async def _stream():
            events = []
            async for event in self._fiber.chat_stream(
                messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                seed=seed,
                stop=stop,
                tools=tools,
                tool_choice=tool_choice,
                timeout_s=timeout_s,
                provider=provider,
                idempotency_key=idempotency_key,
                **kwargs,
            ):
                events.append(event)
            return events

        events = _run_async(_stream())
        for event in events:
            yield event

    def ask(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> str:
        """Simple text-in, text-out interface synchronously.

        Args:
            prompt: User prompt
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Returns:
            Generated text response

        Raises:
            FiberError: On request failure
        """
        return _run_async(
            self._fiber.ask(
                prompt=prompt, model=model, temperature=temperature, max_tokens=max_tokens, **kwargs
            )
        )

    def bind(self, **context):
        """Create a bound sync client with persistent context.

        Args:
            **context: Context to bind (e.g., model, temperature, etc.)

        Returns:
            BoundSyncFiber instance with bound context
        """
        bound_async = self._fiber.bind(**context)
        return BoundSyncFiber(bound_async)


class BoundSyncFiber:
    """Synchronous wrapper for BoundFiber client."""

    def __init__(self, bound_fiber):
        self._bound_fiber = bound_fiber

    def chat(self, **kwargs) -> ChatResult:
        """Execute chat with bound context synchronously."""
        return _run_async(self._bound_fiber.chat(**kwargs))

    def chat_stream(self, **kwargs) -> Iterator[StreamEvent]:
        """Execute streaming chat with bound context synchronously."""

        async def _stream():
            events = []
            async for event in self._bound_fiber.chat_stream(**kwargs):
                events.append(event)
            return events

        events = _run_async(_stream())
        for event in events:
            yield event

    def ask(self, prompt: str, **kwargs) -> str:
        """Execute ask with bound context synchronously."""
        return _run_async(self._bound_fiber.ask(prompt, **kwargs))

    def bind(self, **context):
        """Create a new bound sync client with additional context."""
        bound_async = self._bound_fiber.bind(**context)
        return BoundSyncFiber(bound_async)
