"""Pytest configuration and fixtures for llm-fiber tests."""

import asyncio
import os

# Import llm-fiber modules
import sys
from typing import List

import pytest
import pytest_asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from llm_fiber import (
    AnthropicAdapter,
    BatchConfig,
    BatchStrategy,
    BudgetManager,
    BudgetPeriod,
    ChatMessage,
    ChatResult,
    Fiber,
    GeminiAdapter,
    MemoryCacheAdapter,
    OpenAIAdapter,
    StreamEvent,
    Usage,
    create_cost_budget,
    create_token_budget,
)


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as unit test (fast, no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (may require API keys)"
    )
    config.addinivalue_line("markers", "slow: mark test as slow (may take several seconds)")
    config.addinivalue_line("markers", "requires_api_key: mark test as requiring real API keys")


# Event loop fixture for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Basic fixtures
@pytest.fixture
def sample_messages() -> List[ChatMessage]:
    """Sample chat messages for testing."""
    return [
        ChatMessage.system("You are a helpful assistant."),
        ChatMessage.user("What is 2+2?"),
        ChatMessage.assistant("2+2 equals 4."),
        ChatMessage.user("Thank you!"),
    ]


@pytest.fixture
def sample_usage() -> Usage:
    """Sample usage object for testing."""
    return Usage(prompt=100, completion=50, total=150, cost_estimate=0.003)


@pytest.fixture
def sample_chat_result(sample_usage) -> ChatResult:
    """Sample chat result for testing."""
    return ChatResult(
        text="This is a sample response from the AI assistant.",
        tool_calls=[],
        finish_reason="stop",
        usage=sample_usage,
        raw={"id": "test-123", "model": "gpt-4o-mini"},
    )


# Mock response fixtures
@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "id": "chatcmpl-test123",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-4o-mini",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "Mock response from OpenAI"},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30},
    }


@pytest.fixture
def mock_anthropic_response():
    """Mock Anthropic API response."""
    return {
        "id": "msg_test123",
        "type": "message",
        "role": "assistant",
        "content": [{"type": "text", "text": "Mock response from Anthropic"}],
        "model": "claude-3-haiku-20240307",
        "stop_reason": "end_turn",
        "usage": {"input_tokens": 25, "output_tokens": 15, "total_tokens": 40},
    }


@pytest.fixture
def mock_gemini_response():
    """Mock Gemini API response."""
    return {
        "candidates": [
            {
                "content": {"parts": [{"text": "Mock response from Gemini"}], "role": "model"},
                "finishReason": "STOP",
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 30,
            "candidatesTokenCount": 20,
            "totalTokenCount": 50,
        },
    }


@pytest.fixture
def mock_streaming_chunks():
    """Mock OpenAI streaming response chunks."""
    import json

    # Create JSON chunks programmatically to avoid escaping issues
    base_chunk = {
        "id": "chatcmpl-stream123",
        "object": "chat.completion.chunk",
        "created": 1234567890,
        "model": "gpt-4o-mini",
    }

    chunks = []

    # Role chunk
    role_chunk = {
        **base_chunk,
        "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}],
    }
    chunks.append(f"data: {json.dumps(role_chunk)}\n")

    # Content chunks
    content_parts = ["Hello", " there!", " How", " can", " I", " help?"]
    for content in content_parts:
        content_chunk = {
            **base_chunk,
            "choices": [{"index": 0, "delta": {"content": content}, "finish_reason": None}],
        }
        chunks.append(f"data: {json.dumps(content_chunk)}\n")

    # Final chunk with usage
    final_chunk = {
        **base_chunk,
        "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 20, "completion_tokens": 30, "total_tokens": 50},
    }
    chunks.append(f"data: {json.dumps(final_chunk)}\n")

    # Done marker
    chunks.append("data: [DONE]\n")

    return chunks


# Provider fixtures
@pytest.fixture
def openai_adapter():
    """OpenAI adapter instance for testing."""
    return OpenAIAdapter(api_key="test-key-openai")


@pytest.fixture
def anthropic_adapter():
    """Anthropic adapter instance for testing."""
    return AnthropicAdapter(api_key="test-key-anthropic")


@pytest.fixture
def gemini_adapter():
    """Gemini adapter instance for testing."""
    return GeminiAdapter(api_key="test-key-gemini")


# Caching fixtures
@pytest.fixture
def memory_cache():
    """Memory cache adapter for testing."""
    return MemoryCacheAdapter(max_size=10, default_ttl_seconds=60, cleanup_interval_seconds=1)


@pytest.fixture
async def populated_cache(memory_cache, sample_chat_result):
    """Memory cache with some test data."""
    from llm_fiber.caching import serialize_chat_result

    # Add some test entries
    await memory_cache.set("test_key_1", serialize_chat_result(sample_chat_result))
    await memory_cache.set("test_key_2", serialize_chat_result(sample_chat_result))

    return memory_cache


# Budget fixtures
@pytest.fixture
def cost_budget():
    """Cost budget for testing."""
    return create_cost_budget(
        name="test_cost", limit_usd=1.0, period=BudgetPeriod.DAILY, hard_limit=True
    )


@pytest.fixture
def token_budget():
    """Token budget for testing."""
    return create_token_budget(
        name="test_tokens", limit_tokens=1000, period=BudgetPeriod.HOURLY, hard_limit=False
    )


@pytest.fixture
def budget_manager(cost_budget, token_budget):
    """Budget manager with test budgets."""
    return BudgetManager([cost_budget, token_budget])


# Batch fixtures
@pytest.fixture
def batch_requests():
    """Sample batch requests for testing."""
    prompts = ["What is Python?", "What is JavaScript?", "What is Go?"]

    from llm_fiber.batch import create_batch_from_prompts

    return create_batch_from_prompts(prompts, model="gpt-4o-mini", max_tokens=100)


@pytest.fixture
def batch_config():
    """Batch configuration for testing."""
    return BatchConfig(
        max_concurrent=2,
        strategy=BatchStrategy.CONCURRENT,
        return_exceptions=True,
        timeout_per_request=10.0,
    )


# Fiber client fixtures
@pytest.fixture
def fiber_client():
    """Basic Fiber client for testing (standard fixture name)."""
    return Fiber(
        default_model="gpt-4o-mini",
        api_keys={"openai": "test-key", "anthropic": "test-key", "gemini": "test-key"},
        enable_observability=False,  # Disable for faster tests
    )


@pytest.fixture
def basic_fiber():
    """Basic Fiber client for testing."""
    return Fiber(
        default_model="gpt-4o-mini",
        api_keys={"openai": "test-key", "anthropic": "test-key", "gemini": "test-key"},
        enable_observability=False,  # Disable for faster tests
    )


@pytest.fixture
def fiber_with_cache(memory_cache):
    """Fiber client with caching enabled."""
    return Fiber(
        default_model="gpt-4o-mini",
        api_keys={"openai": "test-key"},
        cache_adapter=memory_cache,
        enable_observability=False,
    )


@pytest.fixture
def fiber_with_budgets(budget_manager):
    """Fiber client with budget management."""
    return Fiber(
        default_model="gpt-4o-mini",
        api_keys={"openai": "test-key"},
        budget_manager=budget_manager,
        enable_observability=False,
    )


@pytest.fixture
def fiber_with_batching(batch_config):
    """Fiber client with batch processing."""
    return Fiber(
        default_model="gpt-4o-mini",
        api_keys={"openai": "test-key"},
        batch_config=batch_config,
        enable_observability=False,
    )


@pytest.fixture
def full_featured_fiber(memory_cache, budget_manager, batch_config):
    """Fully featured Fiber client with all v0.2 features."""
    return Fiber(
        default_model="gpt-4o-mini",
        api_keys={"openai": "test-key", "anthropic": "test-key", "gemini": "test-key"},
        cache_adapter=memory_cache,
        budget_manager=budget_manager,
        batch_config=batch_config,
        enable_observability=True,
    )


# Mock async generators for streaming
@pytest.fixture
def mock_stream_events():
    """Mock stream events for testing."""

    async def _create_events():
        events = [
            StreamEvent.create_chunk("Hello", sequence=0),
            StreamEvent.create_chunk(" world", sequence=1),
            StreamEvent.create_chunk("!", sequence=2),
            StreamEvent.create_usage(Usage(prompt=10, completion=3, total=13)),
        ]

        for event in events:
            yield event

    return _create_events


# Mock HTTP responses
@pytest.fixture
def mock_http_success_response():
    """Mock successful HTTP response."""

    class MockResponse:
        def __init__(self, json_data, status_code=200):
            self.json_data = json_data
            self.status_code = status_code

        async def json(self):
            return self.json_data

        async def aread(self):
            return b"mock response content"

    return MockResponse


@pytest.fixture
def mock_http_error_response():
    """Mock HTTP error response."""

    class MockErrorResponse:
        def __init__(self, status_code=400, error_message="Bad Request"):
            self.status_code = status_code
            self.error_message = error_message

        async def json(self):
            return {"error": {"message": self.error_message}}

        async def aread(self):
            return self.error_message.encode()

    return MockErrorResponse


# Environment fixtures
@pytest.fixture
def mock_env_with_keys(monkeypatch):
    """Mock environment with API keys set."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")


@pytest.fixture
def mock_env_no_keys(monkeypatch):
    """Mock environment with no API keys."""
    for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"]:
        monkeypatch.delenv(key, raising=False)


# Utility functions for tests
@pytest.fixture
def assert_usage_valid():
    """Helper function to validate Usage objects."""

    def _assert_usage_valid(usage: Usage):
        assert isinstance(usage, Usage)
        assert usage.prompt >= 0
        assert usage.completion >= 0
        assert usage.total >= 0
        assert usage.total == usage.prompt + usage.completion
        if usage.cost_estimate is not None:
            assert usage.cost_estimate >= 0

    return _assert_usage_valid


@pytest.fixture
def assert_chat_result_valid():
    """Helper function to validate ChatResult objects."""

    def _assert_chat_result_valid(result: ChatResult):
        assert isinstance(result, ChatResult)
        assert isinstance(result.text, str)
        assert isinstance(result.tool_calls, list)
        assert result.finish_reason is None or isinstance(result.finish_reason, str)
        assert result.usage is None or isinstance(result.usage, Usage)
        assert isinstance(result.raw, dict)

    return _assert_chat_result_valid


# Async testing helpers
@pytest_asyncio.fixture
async def async_mock_chat():
    """Async mock for chat method."""

    async def _mock_chat(**kwargs):
        # Simulate some processing time
        await asyncio.sleep(0.01)

        messages = kwargs.get("messages", [])
        prompt_content = messages[0].content if messages else "test"

        return ChatResult(
            text=f"Mock response for: {prompt_content}",
            tool_calls=[],
            finish_reason="stop",
            usage=Usage(prompt=50, completion=25, total=75, cost_estimate=0.002),
            raw={"mock": True},
        )

    return _mock_chat


@pytest_asyncio.fixture
async def async_mock_chat_stream():
    """Async mock for chat_stream method."""

    async def _mock_chat_stream(**kwargs):
        chunks = ["Mock ", "streaming ", "response"]

        for i, chunk in enumerate(chunks):
            await asyncio.sleep(0.01)
            yield StreamEvent.create_chunk(chunk, sequence=i)

        # Final usage event
        yield StreamEvent.create_usage(Usage(prompt=30, completion=15, total=45))

    return _mock_chat_stream


# Test data
@pytest.fixture
def test_models():
    """Test model names for different providers."""
    return {
        "openai": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
        "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
        "gemini": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"],
    }


@pytest.fixture
def test_prompts():
    """Test prompts for various scenarios."""
    return {
        "simple": "Hello, world!",
        "question": "What is the capital of France?",
        "creative": "Write a haiku about artificial intelligence.",
        "technical": "Explain the difference between list and tuple in Python.",
        "long": (
            "Write a detailed explanation of quantum computing, including its "
            "principles, applications, and current limitations."
        )
        * 10,
    }
