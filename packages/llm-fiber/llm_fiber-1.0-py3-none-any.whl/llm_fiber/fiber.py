"""Main Fiber client class for llm-fiber."""

from __future__ import annotations

import os
import time
from typing import Any, AsyncIterator, Dict, List, Optional

from .batch import BatchConfig, BatchProcessor, BatchRequest, BatchResult
from .budgets import Budget, BudgetExceededError, BudgetManager, BudgetWarningError
from .caching import (
    CacheAdapter,
    NoOpCacheAdapter,
    deserialize_chat_result,
    generate_cache_key,
    serialize_chat_result,
)
from .caching.memory import MemoryCacheAdapter
from .observability.logging import FiberLogger, NoOpLogger
from .observability.metrics import FiberMetrics, NoOpMetrics
from .providers.anthropic import AnthropicAdapter
from .providers.base import Provider
from .providers.gemini import GeminiAdapter
from .providers.openai import OpenAIAdapter
from .retry import RetryPolicy, retry_async
from .routing import ModelRegistry, default_registry
from .timeouts import Timeouts
from .types import (
    ChatMessage,
    ChatResult,
    FiberError,
    MessagesInput,
    StreamEvent,
    normalize_messages,
)


class Fiber:
    """Main client for llm-fiber operations."""

    def __init__(
        self,
        default_model: Optional[str] = None,
        api_keys: Optional[Dict[str, str]] = None,
        base_urls: Optional[Dict[str, str]] = None,
        timeout: Optional[Timeouts] = None,
        timeouts: Optional[Timeouts] = None,  # Alias for timeout
        retry_policy: Optional[RetryPolicy] = None,
        model_registry: Optional[ModelRegistry] = None,
        metrics: Optional[FiberMetrics] = None,
        logger: Optional[FiberLogger] = None,
        enable_observability: bool = True,
        cache_adapter: Optional[CacheAdapter] = None,
        budget_manager: Optional[BudgetManager] = None,
        batch_config: Optional[BatchConfig] = None,
    ):
        """Initialize Fiber client.

        Args:
            default_model: Default model to use if none specified
            api_keys: Provider API keys (overrides environment variables)
            base_urls: Custom base URLs for providers
            timeout: Timeout configuration
            timeouts: Alias for timeout parameter
            retry_policy: Retry policy for failed requests
            model_registry: Model registry for routing
            metrics: Metrics collector
            logger: Logger instance
            enable_observability: Whether to enable metrics and logging
            cache_adapter: Cache adapter for request caching
            budget_manager: Budget manager for cost controls
            batch_config: Configuration for batch operations
        """
        # Validate API keys
        if api_keys is not None:
            if not api_keys:
                raise ValueError("At least one API key must be provided")

            valid_providers = {"openai", "anthropic", "gemini"}
            invalid_providers = set(api_keys.keys()) - valid_providers
            if invalid_providers:
                raise ValueError(f"Invalid provider(s): {', '.join(invalid_providers)}")

        self.default_model = default_model
        self._api_keys = api_keys or {}
        self._base_urls = base_urls or {}

        # Handle both timeout and timeouts parameters
        timeout_config = timeouts or timeout or Timeouts()
        self.timeout = timeout_config
        # For backward compatibility
        self.timeouts = timeout_config
        self.retry_policy = retry_policy or RetryPolicy()
        self.model_registry = model_registry or default_registry
        self.enable_observability = enable_observability

        # Auto-select default model if not provided but we have API keys
        if not self.default_model and self._api_keys:
            preference_order = ["openai", "anthropic", "gemini"]
            for provider_name in preference_order:
                if provider_name in self._api_keys:
                    provider_config = self.model_registry.get_provider_config(provider_name)
                    if provider_config and provider_config.default_models:
                        self.default_model = provider_config.default_models[0]
                        break

        # Set up observability
        if enable_observability:
            self.metrics = metrics or FiberMetrics()
            self.logger = logger or FiberLogger()
        else:
            self.metrics = NoOpMetrics()
            self.logger = NoOpLogger()

        # Provider instances cache
        self._providers: Dict[str, Provider] = {}

        # v0.2 features
        self.cache_adapter = cache_adapter or NoOpCacheAdapter()
        self.budget_manager = budget_manager

        # Ensure budget manager has access to model registry for cost estimation
        if self.budget_manager and not self.budget_manager.estimator.model_registry:
            from .budgets import BudgetEstimator

            self.budget_manager.estimator = BudgetEstimator(self.model_registry)

        self.batch_processor = BatchProcessor(batch_config, self) if batch_config else None

    @property
    def _timeouts(self) -> Timeouts:
        """Compatibility proxy to `timeout` for legacy tests."""
        return self.timeout

    @_timeouts.setter
    def _timeouts(self, value: Timeouts):
        """Compatibility proxy to set `timeout` via `_timeouts`."""
        self.timeout = value

    @classmethod
    def from_env(
        cls,
        default_model: Optional[str] = None,
        prefer: Optional[List[str]] = None,
        timeout: Optional[Timeouts] = None,
        retry_policy: Optional[RetryPolicy] = None,
        enable_observability: bool = True,
        enable_memory_cache: bool = False,
        cache_max_size: int = 1000,
        budgets: Optional[List[Budget]] = None,
    ) -> Fiber:
        """Create Fiber client from environment variables.

        Args:
            default_model: Default model to use
            prefer: Provider preference order
            timeout: Timeout configuration
            retry_policy: Retry policy
            enable_observability: Whether to enable observability
            enable_memory_cache: Whether to enable memory caching
            cache_max_size: Maximum cache size if memory cache enabled
            budgets: Optional budget constraints

        Returns:
            Configured Fiber instance
        """
        # Read API keys from environment
        api_keys = {}

        if os.getenv("OPENAI_API_KEY"):
            api_keys["openai"] = os.getenv("OPENAI_API_KEY")
        if os.getenv("ANTHROPIC_API_KEY"):
            api_keys["anthropic"] = os.getenv("ANTHROPIC_API_KEY")
        if os.getenv("GEMINI_API_KEY"):
            api_keys["gemini"] = os.getenv("GEMINI_API_KEY")

        # Validate we found at least one API key
        if not api_keys:
            raise ValueError("No API keys found in environment variables")

        # Set up model registry with preferred providers
        registry = ModelRegistry()
        if prefer:
            registry.set_default_preference(prefer)

        # Auto-select default model if not provided
        if not default_model:
            preference_order = prefer or ["openai", "anthropic", "gemini"]
            for provider_name in preference_order:
                if provider_name in api_keys:
                    provider_config = registry.get_provider_config(provider_name)
                    if provider_config and provider_config.default_models:
                        default_model = provider_config.default_models[0]
                        break

        # Set up optional features
        cache_adapter = None
        if enable_memory_cache:
            cache_adapter = MemoryCacheAdapter(max_size=cache_max_size)

        budget_manager = None
        if budgets:
            budget_manager = BudgetManager(budgets, registry)

        return cls(
            default_model=default_model,
            api_keys=api_keys,
            timeout=timeout,
            retry_policy=retry_policy,
            model_registry=registry,
            enable_observability=enable_observability,
            cache_adapter=cache_adapter,
            budget_manager=budget_manager,
        )

    def _get_provider(self, provider_name: str) -> Provider:
        """Get or create a provider instance.

        Args:
            provider_name: Name of the provider

        Returns:
            Provider instance

        Raises:
            FiberError: If provider is not supported or not configured
        """
        if provider_name in self._providers:
            return self._providers[provider_name]

        # Get provider configuration
        provider_config = self.model_registry.get_provider_config(provider_name)
        if not provider_config:
            raise FiberError(f"Unknown provider: {provider_name}")

        # Get API key
        api_key = self._api_keys.get(provider_name)
        if not api_key:
            # Try environment variable
            api_key = os.getenv(provider_config.api_key_env)

        if not api_key:
            raise FiberError(
                f"No API key found for {provider_name}. "
                f"Set {provider_config.api_key_env} environment variable or "
                f"pass api_keys parameter."
            )

        # Get base URL
        base_url = self._base_urls.get(provider_name) or provider_config.base_url

        # Create provider instance
        if provider_name == "openai":
            provider = OpenAIAdapter(
                api_key=api_key,
                base_url=base_url,
                timeout_seconds=self.timeout.total or 30.0,
            )
        elif provider_name == "anthropic":
            provider = AnthropicAdapter(
                api_key=api_key,
                base_url=base_url,
                timeout_seconds=self.timeout.total or 30.0,
            )
        elif provider_name == "gemini":
            provider = GeminiAdapter(
                api_key=api_key,
                base_url=base_url,
                timeout_seconds=self.timeout.total or 30.0,
            )
        else:
            raise FiberError(f"Provider {provider_name} not yet implemented")

        self._providers[provider_name] = provider
        return provider

    async def chat(
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
        """Execute a chat completion request.

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
        # Resolve model
        resolved_model = model or self.default_model
        if not resolved_model:
            raise FiberError("No model specified and no default_model set")

        # Normalize messages
        if not messages:
            raise FiberError("Messages cannot be empty")
        normalized_messages = normalize_messages(messages)

        # Resolve provider
        provider_name = self.model_registry.resolve_provider(resolved_model, provider)
        provider_instance = self._get_provider(provider_name)

        # Create bound logger for this request
        bound_logger = self.logger.bind(
            provider=provider_name, model=resolved_model, operation="chat"
        )

        # Check budgets before making request
        if self.budget_manager:
            try:
                self.budget_manager.check_budgets_preflight(
                    model=resolved_model,
                    messages=normalized_messages,
                    max_tokens=max_tokens,
                )
            except BudgetWarningError as e:
                bound_logger.warning("Budget warning", warning=str(e))
                # Continue with request but log warning
            except BudgetExceededError as e:
                bound_logger.error("Budget exceeded", error=str(e))
                raise

        # Check cache first
        cache_key = None
        if self.cache_adapter and not isinstance(self.cache_adapter, NoOpCacheAdapter):
            cache_key = generate_cache_key(
                messages=normalized_messages,
                model=resolved_model,
                provider=provider_name,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                seed=seed,
                stop=stop,
                tools=tools,
                tool_choice=tool_choice,
                **kwargs,
            )

            try:
                cached_result = await self.cache_adapter.get(cache_key)
                if cached_result is not None:
                    bound_logger.info("Cache hit")
                    self.metrics.record_cache_hit(provider=provider_name, model=resolved_model)
                    return deserialize_chat_result(cached_result)
            except Exception as cache_error:
                bound_logger.warning("Cache read error", error=str(cache_error))
                # Continue without cache

        # Execute with retry logic
        async def _execute_chat():
            bound_logger.info("Starting chat request")

            return await provider_instance.chat(
                model=resolved_model,
                messages=normalized_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                seed=seed,
                stop=stop,
                tools=tools,
                tool_choice=tool_choice,
                timeout_seconds=timeout_s or self.timeout.total,
                idempotency_key=idempotency_key,
                **kwargs,
            )

        try:
            if getattr(self.retry_policy, "max_attempts", 1) <= 1:
                result = await _execute_chat()
            else:
                result = await retry_async(
                    _execute_chat, self.retry_policy, total_timeout=self.timeout.total
                )

            # Add cost estimation if not already present
            if result.usage and result.usage.cost_estimate is None:
                estimated_cost = self.model_registry.estimate_cost(
                    resolved_model, result.usage.prompt, result.usage.completion
                )
                if estimated_cost is not None:
                    # Create new Usage object with cost estimate
                    from .types import Usage

                    result.usage = Usage(
                        prompt=result.usage.prompt,
                        completion=result.usage.completion,
                        total=result.usage.total,
                        cost_estimate=estimated_cost,
                    )

            # Cache the result if caching is enabled
            if (
                cache_key
                and self.cache_adapter
                and not isinstance(self.cache_adapter, NoOpCacheAdapter)
            ):
                try:
                    serialized_result = serialize_chat_result(result)
                    await self.cache_adapter.set(cache_key, serialized_result)
                    bound_logger.debug("Result cached")
                    self.metrics.record_cache_write(provider=provider_name, model=resolved_model)
                except Exception as cache_error:
                    bound_logger.warning("Cache write error", error=str(cache_error))
                    # Continue without caching

            # Record success metrics
            self.metrics.record_request_success(
                provider=provider_name, model=resolved_model, operation="chat"
            )

            # Record token usage
            if result.usage:
                self.metrics.record_token_usage(
                    provider=provider_name,
                    model=resolved_model,
                    prompt_tokens=result.usage.prompt,
                    completion_tokens=result.usage.completion,
                    total_tokens=result.usage.total,
                    operation="chat",
                )

                # Record cost if available
                if result.usage.cost_estimate:
                    self.metrics.record_estimated_cost(
                        provider=provider_name,
                        model=resolved_model,
                        cost_usd=result.usage.cost_estimate,
                        operation="chat",
                    )

                # Record budget usage
                if self.budget_manager:
                    self.budget_manager.record_usage(result.usage, resolved_model)

            bound_logger.info("Chat request completed successfully")
            return result

        except Exception as e:
            # Record error metrics
            self.metrics.record_request_error(
                provider=provider_name,
                model=resolved_model,
                error_type=type(e).__name__,
                operation="chat",
            )

            bound_logger.error("Chat request failed", error=str(e))
            raise

    async def chat_stream(
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
    ) -> AsyncIterator[StreamEvent]:
        """Execute a streaming chat completion request.

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
        # Resolve model
        resolved_model = model or self.default_model
        if not resolved_model:
            raise FiberError("No model specified and no default_model set")

        # Normalize messages
        if not messages:
            raise FiberError("Messages cannot be empty")
        normalized_messages = normalize_messages(messages)

        # Resolve provider
        provider_name = self.model_registry.resolve_provider(resolved_model, provider)
        provider_instance = self._get_provider(provider_name)

        # Create bound logger for this request
        bound_logger = self.logger.bind(
            provider=provider_name, model=resolved_model, operation="stream"
        )

        bound_logger.info("Starting streaming chat request")

        try:
            # Track streaming metrics
            chunk_count = 0
            ttfb_recorded = False
            start_time = time.time()

            async for event in provider_instance.chat_stream(
                model=resolved_model,
                messages=normalized_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                seed=seed,
                stop=stop,
                tools=tools,
                tool_choice=tool_choice,
                timeout_seconds=timeout_s or self.timeout.total,
                idempotency_key=idempotency_key,
                **kwargs,
            ):
                # Record TTFB on first chunk
                if not ttfb_recorded and event.type.value == "chunk":
                    ttfb_ms = (time.time() - start_time) * 1000
                    # Only record TTFB if metrics are enabled (has _metrics attribute)
                    if hasattr(self.metrics, "_metrics"):
                        self.metrics._metrics.observe_histogram(
                            self.metrics.TTFB_MS,
                            ttfb_ms,
                            {
                                "provider": provider_name,
                                "model": resolved_model,
                                "operation": "stream",
                            },
                        )
                        bound_logger.debug("Recorded TTFB", ttfb_ms=ttfb_ms)
                    ttfb_recorded = True

                if event.type.value == "chunk":
                    chunk_count += 1

                yield event

                # Record final usage
                if event.type.value == "usage" and event.usage:
                    self.metrics.record_token_usage(
                        provider=provider_name,
                        model=resolved_model,
                        prompt_tokens=event.usage.prompt,
                        completion_tokens=event.usage.completion,
                        total_tokens=event.usage.total,
                        operation="stream",
                    )

                    if event.usage.cost_estimate:
                        self.metrics.record_estimated_cost(
                            provider=provider_name,
                            model=resolved_model,
                            cost_usd=event.usage.cost_estimate,
                            operation="stream",
                        )

            # Record success
            self.metrics.record_request_success(
                provider=provider_name, model=resolved_model, operation="stream"
            )

            bound_logger.info("Streaming chat request completed successfully")

        except Exception as e:
            # Record error
            self.metrics.record_request_error(
                provider=provider_name,
                model=resolved_model,
                error_type=type(e).__name__,
                operation="stream",
            )

            bound_logger.error("Streaming chat request failed", error=str(e))
            raise

    # Batch operations (v0.2)
    async def batch_chat(
        self, requests: List[BatchRequest], config: Optional[BatchConfig] = None
    ) -> List[BatchResult]:
        """Execute multiple chat requests in batch.

        Args:
            requests: List of batch requests
            config: Optional batch configuration override

        Returns:
            List of batch results

        Raises:
            FiberError: If batch processing fails
        """
        if not requests:
            return []

        # Use provided config or create processor with config
        if config:
            processor = BatchProcessor(config, self)
        elif self.batch_processor:
            processor = self.batch_processor
        else:
            processor = BatchProcessor(BatchConfig(), self)

        return await processor.process_async(requests)

    def batch_chat_sync(
        self, requests: List[BatchRequest], config: Optional[BatchConfig] = None
    ) -> List[BatchResult]:
        """Execute multiple chat requests in batch (synchronous).

        Args:
            requests: List of batch requests
            config: Optional batch configuration override

        Returns:
            List of batch results
        """
        if not requests:
            return []

        # Use provided config or create processor with config
        if config:
            processor = BatchProcessor(config, self)
        elif self.batch_processor:
            processor = self.batch_processor
        else:
            processor = BatchProcessor(BatchConfig(), self)

        return processor.process_sync(requests)

    # Cache management methods
    async def clear_cache(self) -> None:
        """Clear the cache if enabled."""
        if self.cache_adapter and not isinstance(self.cache_adapter, NoOpCacheAdapter):
            await self.cache_adapter.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if self.cache_adapter and not isinstance(self.cache_adapter, NoOpCacheAdapter):
            stats = self.cache_adapter.get_stats()
            return {
                "hits": stats.hits,
                "misses": stats.misses,
                "writes": stats.writes,
                "evictions": stats.evictions,
                "errors": stats.errors,
            }
        return {}

    # Budget management methods
    def get_budget_status(self) -> Dict[str, Any]:
        """Get budget status if budget manager is enabled."""
        if self.budget_manager:
            return self.budget_manager.get_budget_status()
        return {}

    def get_budget_summary(self) -> Dict[str, Any]:
        """Get budget summary if budget manager is enabled."""
        if self.budget_manager:
            return self.budget_manager.get_budget_summary()
        return {}

    def reset_budgets(self) -> None:
        """Reset all budgets if budget manager is enabled."""
        if self.budget_manager:
            self.budget_manager.reset_all_budgets()

    def capabilities(self, model: str) -> Dict[str, Any]:
        """Get normalized capability flags and pricing information for a model.

        Args:
            model: Model name to query capabilities for

        Returns:
            Dictionary containing model capabilities and pricing information

        Example:
            >>> fiber = Fiber()
            >>> caps = fiber.capabilities("gpt-4o")
            >>> print(caps["supports_tools"])  # True
            >>> print(caps["pricing"]["input_cost_per_1k_tokens"])  # 2.50
        """
        # Get model info from registry
        model_info = self.model_registry.get_model_info(model)

        # Get provider info
        provider_name = None
        provider_config = None
        try:
            provider_name = self.model_registry.resolve_provider(model)
            provider_config = self.model_registry.get_provider_config(provider_name)
        except Exception:
            pass

        # Build capabilities response
        capabilities = {
            "model": model,
            "provider": provider_name,
            "registered": model_info is not None,
            "supports_tools": model_info.supports_tools
            if model_info
            else (provider_config.supports_tools if provider_config else True),
            "supports_vision": model_info.supports_vision
            if model_info
            else (provider_config.supports_vision if provider_config else False),
            "supports_streaming": provider_config.supports_streaming if provider_config else True,
            "context_length": model_info.context_length if model_info else None,
            "pricing": {},
        }

        # Add pricing information if available
        if model_info and (model_info.input_cost_per_token or model_info.output_cost_per_token):
            capabilities["pricing"] = {
                "input_cost_per_token": model_info.input_cost_per_token,
                "output_cost_per_token": model_info.output_cost_per_token,
                "input_cost_per_1k_tokens": model_info.input_cost_per_token * 1000
                if model_info.input_cost_per_token
                else None,
                "output_cost_per_1k_tokens": model_info.output_cost_per_token * 1000
                if model_info.output_cost_per_token
                else None,
                "currency": "USD",
            }

        return capabilities

    def bind(self, **context) -> BoundFiber:
        """Create a bound client with persistent context.

        Args:
            **context: Context to bind (e.g., model, temperature, etc.)

        Returns:
            BoundFiber instance with bound context
        """
        return BoundFiber(self, context)

    async def ask(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> str:
        """Simple text-in, text-out interface.

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
        result = await self.chat(
            [ChatMessage.user(prompt)],
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        return result.text

    # Sync wrappers will be in a separate sync module
    @property
    def sync(self):
        """Access to synchronous wrappers."""
        from .sync import SyncFiber

        return SyncFiber(self)


class BoundFiber:
    """Fiber client bound to specific context."""

    def __init__(self, fiber: Fiber, context: Dict[str, Any]):
        self._fiber = fiber
        self._context = context

    def _merge_kwargs(self, **kwargs) -> Dict[str, Any]:
        """Merge bound context with call kwargs."""
        merged = self._context.copy()
        merged.update(kwargs)
        return merged

    async def chat(self, messages=None, **kwargs) -> ChatResult:
        """Execute chat with bound context."""
        if messages is not None:
            kwargs["messages"] = messages
        return await self._fiber.chat(**self._merge_kwargs(**kwargs))

    async def chat_stream(self, **kwargs) -> AsyncIterator[StreamEvent]:
        """Execute streaming chat with bound context."""
        async for event in self._fiber.chat_stream(**self._merge_kwargs(**kwargs)):
            yield event

    async def ask(self, prompt: str, **kwargs) -> str:
        """Execute ask with bound context."""
        return await self._fiber.ask(prompt, **self._merge_kwargs(**kwargs))

    async def batch_chat(
        self,
        requests: List[BatchRequest],
        config: Optional[BatchConfig] = None,
        **kwargs,
    ) -> List[BatchResult]:
        """Execute batch chat with bound context."""
        # Apply bound context to each request that doesn't override it
        updated_requests = []
        merged_context = self._merge_kwargs(**kwargs)

        for request in requests:
            # Create a new request with bound context applied
            request_dict = request.__dict__.copy()

            # Apply bound context only where request doesn't specify
            for key, value in merged_context.items():
                if key in request_dict and request_dict[key] is None:
                    request_dict[key] = value
                elif key not in request_dict:
                    if key in [
                        "model",
                        "temperature",
                        "max_tokens",
                        "top_p",
                        "seed",
                        "stop",
                        "tools",
                        "tool_choice",
                        "timeout_s",
                        "provider",
                        "idempotency_key",
                    ]:
                        request_dict[key] = value
                    else:
                        request_dict["kwargs"][key] = value

            updated_requests.append(BatchRequest(**request_dict))

        return await self._fiber.batch_chat(updated_requests, config)

    def batch_chat_sync(
        self,
        requests: List[BatchRequest],
        config: Optional[BatchConfig] = None,
        **kwargs,
    ) -> List[BatchResult]:
        """Execute batch chat with bound context (synchronous)."""
        # Apply bound context to each request that doesn't override it
        updated_requests = []
        merged_context = self._merge_kwargs(**kwargs)

        for request in requests:
            # Create a new request with bound context applied
            request_dict = request.__dict__.copy()

            # Apply bound context only where request doesn't specify
            for key, value in merged_context.items():
                if key in request_dict and request_dict[key] is None:
                    request_dict[key] = value
                elif key not in request_dict:
                    if key in [
                        "model",
                        "temperature",
                        "max_tokens",
                        "top_p",
                        "seed",
                        "stop",
                        "tools",
                        "tool_choice",
                        "timeout_s",
                        "provider",
                        "idempotency_key",
                    ]:
                        request_dict[key] = value
                    else:
                        request_dict["kwargs"][key] = value

            updated_requests.append(BatchRequest(**request_dict))

        return self._fiber.batch_chat_sync(updated_requests, config)

    def bind(self, **context) -> BoundFiber:
        """Create a new bound client with additional context."""
        merged_context = self._context.copy()
        merged_context.update(context)
        return BoundFiber(self._fiber, merged_context)

    @property
    def sync(self):
        """Access to synchronous wrappers."""
        from .sync import BoundSyncFiber

        return BoundSyncFiber(self)
