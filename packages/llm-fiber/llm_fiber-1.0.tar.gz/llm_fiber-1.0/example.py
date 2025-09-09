#!/usr/bin/env python3
"""
llm-fiber Comprehensive Examples

This script demonstrates all the key features of llm-fiber v0.2:
- Multi-provider support (OpenAI, Anthropic, Gemini)
- Caching system with memory adapter
- Batch operations for concurrent processing
- Budget controls and cost management
- Enhanced observability and metrics
- Advanced features integration

Usage:
    python example.py

Environment Variables:
    OPENAI_API_KEY - OpenAI API key (optional)
    ANTHROPIC_API_KEY - Anthropic API key (optional)
    GEMINI_API_KEY - Google Gemini API key (optional)

Note: Examples will work without API keys, but will use mock responses.
"""

import asyncio
import os
from contextlib import contextmanager
from typing import Any, AsyncGenerator, Dict

from llm_fiber import (
    BatchConfig,
    BatchStrategy,
    BudgetPeriod,
    ChatMessage,
    ChatResult,
    Fiber,
    StreamEvent,
    StreamEventType,
    Usage,
    create_batch_from_prompts,
    create_cost_budget,
    create_token_budget,
)

# ==============================================================================
# Example Utilities
# ==============================================================================


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def print_subsection(title: str):
    """Print a formatted subsection header."""
    print(f"\n--- {title} ---")


def get_available_api_keys() -> Dict[str, str]:
    """Get available API keys from environment."""
    keys = {}
    if os.getenv("OPENAI_API_KEY"):
        keys["openai"] = os.getenv("OPENAI_API_KEY")
    if os.getenv("ANTHROPIC_API_KEY"):
        keys["anthropic"] = os.getenv("ANTHROPIC_API_KEY")
    if os.getenv("GEMINI_API_KEY"):
        keys["gemini"] = os.getenv("GEMINI_API_KEY")
    return keys


def get_default_model_for_provider(provider: str) -> str:
    """Get default model for a provider."""
    defaults = {
        "openai": "gpt-4o-mini",
        "anthropic": "claude-3-haiku-20240307",
        "gemini": "gemini-1.5-flash",
    }
    return defaults.get(provider, "gpt-4o-mini")


class MockProvider:
    """A mock provider to simulate API calls for demonstration."""

    def __init__(self, fiber: Fiber):
        self.fiber = fiber
        self._original_chat = fiber.chat
        self._original_chat_stream = fiber.chat_stream

    async def mock_chat(self, **kwargs: Any) -> ChatResult:
        """Simulate a chat response."""
        await asyncio.sleep(0.1)  # Simulate network delay
        model = kwargs.get("model", "mock-model")
        messages = kwargs.get("messages", [])
        prompt = messages[0].content if messages else "..."
        return ChatResult(
            text=f"Mock response for '{prompt[:30]}...' from {model}.",
            tool_calls=[],
            finish_reason="stop",
            usage=Usage(prompt=50, completion=75, total=125, cost_estimate=0.0001),
            raw={"mock": True, "model": model},
        )

    async def mock_chat_stream(self, **kwargs: Any) -> AsyncGenerator[StreamEvent, None]:
        """Simulate a streaming chat response."""
        text_chunks = ["This ", "is ", "a ", "streamed ", "mock ", "response."]
        for i, chunk in enumerate(text_chunks):
            await asyncio.sleep(0.05)
            yield StreamEvent.create_chunk(chunk, sequence=i)
        yield StreamEvent.create_usage(Usage(prompt=20, completion=30, total=50))

    def __enter__(self):
        self.fiber.chat = self.mock_chat
        self.fiber.chat_stream = self.mock_chat_stream
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fiber.chat = self._original_chat
        self.fiber.chat_stream = self._original_chat_stream


# ==============================================================================
# README Example: A Quick Start
# ==============================================================================


async def example_readme_quickstart():
    """A simple, clean example perfect for a README file."""
    print_section("Quick Start: README Example")

    # Create a Fiber client, automatically detecting API keys from environment
    try:
        fiber = Fiber.from_env()
    except ValueError:
        # Fallback when no API keys are present in env
        fiber = Fiber()

    # Determine if we should use a mock provider for demonstration
    use_mock = not get_available_api_keys()
    if use_mock:
        print("Using mock provider for demonstration.")

    try:
        # Define a model to use (will be routed to the correct provider)
        model = "gpt-4o-mini"
        print(f"Sending request to model: {model}")

        # Make a chat request
        with MockProvider(fiber) if use_mock else open_context():
            result = await fiber.chat(
                model=model,
                messages=[ChatMessage.user("Explain quantum computing in one sentence.")],
                max_tokens=50,
            )

        print(f"\nResponse: {result.text}")
        if result.usage:
            print(f"Usage: {result.usage.total} tokens")
            if result.usage.cost_estimate:
                print(f"Estimated Cost: ${result.usage.cost_estimate:.6f}")

    except Exception as e:
        print(f"An error occurred: {e}")


# ==============================================================================
# Core Features
# ==============================================================================


async def example_multi_provider_routing():
    """Demonstrate automatic routing to different LLM providers."""
    print_section("Core Feature: Multi-Provider Routing")

    try:
        fiber = Fiber.from_env()
    except ValueError:
        fiber = Fiber()
    registry = fiber.model_registry

    print("Resolving models to their respective providers:")
    test_models = [
        "gpt-4o",
        "gpt-3.5-turbo",  # OpenAI
        "claude-3-5-sonnet-20240620",
        "claude-3-haiku-20240307",  # Anthropic
        "gemini-1.5-pro",
        "gemini-1.5-flash",  # Gemini
        "non-existent-model",  # Expected to fail
    ]

    for model in test_models:
        try:
            provider = registry.resolve_provider(model)
            print(f"  - {model:<30} -> {provider.name}")
        except ValueError as e:
            print(f"  - {model:<30} -> Error: {e}")


async def example_streaming():
    """Demonstrate streaming capabilities."""
    print_section("Core Feature: Streaming")

    try:
        fiber = Fiber.from_env()
    except ValueError:
        fiber = Fiber()
    use_mock = not get_available_api_keys()

    print(f"Streaming a response... (using {'mock' if use_mock else 'real'} provider)")
    print("\nResponse: ", end="", flush=True)

    async def stream_and_collect():
        final_usage = None
        with MockProvider(fiber) if use_mock else open_context():
            async for event in fiber.chat_stream(
                model=get_default_model_for_provider("openai"),
                messages=[ChatMessage.user("Why is streaming important for user experience?")],
            ):
                if event.type == StreamEventType.CHUNK:
                    print(event.delta, end="", flush=True)
                elif event.type == StreamEventType.USAGE:
                    final_usage = event.usage
        return final_usage

    usage = await stream_and_collect()
    print()
    if usage:
        print(f"\nUsage: {usage.total} tokens")


# ==============================================================================
# Advanced Features
# ==============================================================================


async def example_caching_system():
    """Demonstrate the caching system."""
    print_section("Advanced Feature: Caching")

    try:
        fiber = Fiber.from_env(
            enable_memory_cache=True, cache_max_size=50, cache_default_ttl_seconds=300
        )
    except ValueError:
        fiber = Fiber()

    print("Cache configured: MemoryCacheAdapter (max_size=50, ttl=300s)")

    messages = [ChatMessage.user("What is artificial intelligence?")]
    model = "gpt-4o-mini"

    with MockProvider(fiber):
        # First call: Cache Miss
        print("\n1. First request (Cache Miss)")
        await fiber.chat(model=model, messages=messages)

        # Second call: Cache Hit
        print("2. Identical second request (Cache Hit)")
        await fiber.chat(model=model, messages=messages)

        # Third call (different param): Cache Miss
        print("3. Different parameter (Cache Miss)")
        await fiber.chat(model=model, messages=messages, temperature=0.8)

    print(f"\nFinal Cache Stats: {fiber.get_cache_stats()}")


async def example_batch_operations():
    """Demonstrate batch processing capabilities."""
    print_section("Advanced Feature: Batch Operations")

    try:
        fiber = Fiber.from_env()
    except ValueError:
        fiber = Fiber()
    prompts = [
        "Explain quantum computing in one sentence.",
        "What is the capital of Australia?",
        "Write a haiku about programming.",
    ]
    batch_requests = create_batch_from_prompts(prompts, model="gpt-4o-mini")

    batch_config = BatchConfig(
        max_concurrent=3,
        strategy=BatchStrategy.CONCURRENT,
        retry_failed=True,
        max_retries=3,
    )
    print(f"Processing {len(prompts)} prompts with {batch_config.strategy.value} strategy...")

    with MockProvider(fiber):
        batch_results = await fiber.batch_chat(batch_requests, batch_config)

        print("\nBatch Results:")
        for result in batch_results:
            status = "✓" if result.is_success else "✗"
            duration = f"{(result.duration_ms or 0) / 1000:.2f}s"
            preview = (
                (result.result.text[:30] + "...") if result.result and result.result.text else ""
            )
            print(f"  {status} [{duration}] id={result.id} {preview}")

    print(f"\nTotal processed: {len(batch_results)}")


async def example_budget_controls():
    """Demonstrate budget and cost controls."""
    print_section("Advanced Feature: Budget Controls")

    budgets = [
        create_cost_budget("daily_spending", 0.10, BudgetPeriod.DAILY, hard_limit=True),
        create_token_budget("hourly_tokens", 500, BudgetPeriod.HOURLY),
    ]
    try:
        fiber = Fiber.from_env(budgets=budgets)
    except ValueError:
        fiber = Fiber()

    print("Budgets configured:")
    for budget in budgets:
        print(
            f"  - {budget.name}: {budget.limit} {budget.budget_type.value} "
            f"per {budget.period.value}"
        )

    with MockProvider(fiber):
        for i in range(5):
            print(f"\nRequest {i + 1}:")
            try:
                await fiber.chat(
                    model="gpt-4o-mini",
                    messages=[ChatMessage.user("Tell me a short story.")],
                )
                print("  - Request successful.")
                for name, status in fiber.get_budget_status().items():
                    print(f"    - {name}: {status['utilization']:.1%} used")
            except Exception as e:
                print(f"  - Request blocked: {e}")
                break

    print(f"\nFinal Budget Summary: {fiber.get_budget_summary()}")


async def example_observability():
    """Demonstrate observability and metrics."""
    print_section("Advanced Feature: Observability & Metrics")

    try:
        fiber = Fiber.from_env(enable_observability=True, enable_memory_cache=True)
    except ValueError:
        fiber = Fiber(enable_observability=True)
    print("Observability enabled (metrics for requests, tokens, cost, cache, etc.)")

    with MockProvider(fiber):
        # Generate some activity
        await fiber.chat(model="gpt-4o-mini", messages=[ChatMessage.user("Test 1")])
        await fiber.chat(model="claude-3-haiku-20240307", messages=[ChatMessage.user("Test 2")])
        await fiber.chat(model="gpt-4o-mini", messages=[ChatMessage.user("Test 1")])  # Cache hit

    print("\nCollected Metrics:")
    metrics = fiber.metrics.get_metrics()

    counters = metrics.get_counters()
    for name, labels in counters.items():
        if "request_total" in name:
            total = sum(c.value for c in labels.values())
            print(f"  - {name}: {total}")

    print(f"  - Cache Metrics: {fiber.get_cache_stats()}")


# ==============================================================================
# Main Execution
# ==============================================================================

# A dummy context manager for when no mock is needed.


@contextmanager
def open_context():
    yield


async def main():
    """Run all examples."""
    print("🚀 llm-fiber v0.2 - Comprehensive Examples")
    print("Demonstrating multi-provider support, caching, batching, budgets & more")

    keys = get_available_api_keys()
    if keys:
        print(f"\n🔑 API keys found for: {', '.join(keys.keys())}")
        print("Examples will make real API calls.")
    else:
        print("\n⚠️  No API keys found. Using mock responses for demonstration.")
        print("Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY to use real providers.")

    # Run examples
    await example_readme_quickstart()
    await example_multi_provider_routing()
    await example_streaming()
    await example_caching_system()
    await example_batch_operations()
    await example_budget_controls()
    await example_observability()

    print_section("✅ All Examples Complete!")
    print("llm-fiber features demonstrated successfully.")
    if not keys:
        print("\n💡 Tip: Set your API keys to see these examples run with real models!")


if __name__ == "__main__":
    asyncio.run(main())
