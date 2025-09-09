"""Basic tests for llm-fiber functionality."""

import os
from unittest.mock import patch

import pytest

from llm_fiber import (
    ChatMessage,
    Fiber,
    RetryPolicy,
    StreamEvent,
    Timeouts,
    Usage,
)


class TestChatMessage:
    """Test ChatMessage functionality."""

    def test_system_message(self):
        msg = ChatMessage.system("You are a helpful assistant.")
        assert msg.role == "system"
        assert msg.content == "You are a helpful assistant."
        assert msg.name is None
        assert msg.tool_calls == []

    def test_user_message(self):
        msg = ChatMessage.user("Hello!", name="user1")
        assert msg.role == "user"
        assert msg.content == "Hello!"
        assert msg.name == "user1"

    def test_assistant_message(self):
        msg = ChatMessage.assistant("Hi there!", name="assistant1")
        assert msg.role == "assistant"
        assert msg.content == "Hi there!"
        assert msg.name == "assistant1"

    def test_tool_message(self):
        msg = ChatMessage.tool("Result: 42", tool_call_id="call_123")
        assert msg.role == "tool"
        assert msg.content == "Result: 42"
        assert msg.tool_call_id == "call_123"

    def test_to_dict(self):
        msg = ChatMessage.user("Hello!", name="test")
        result = msg.to_dict()
        expected = {"role": "user", "content": "Hello!", "name": "test"}
        assert result == expected


class TestUsage:
    """Test Usage functionality."""

    def test_basic_usage(self):
        usage = Usage(prompt=10, completion=20)
        assert usage.prompt == 10
        assert usage.completion == 20
        assert usage.total == 30  # Auto-calculated

    def test_explicit_total(self):
        usage = Usage(prompt=10, completion=20, total=30)
        assert usage.total == 30

    def test_cost_estimate(self):
        usage = Usage(prompt=10, completion=20, cost_estimate=0.001)
        assert usage.cost_estimate == 0.001


class TestTimeouts:
    """Test Timeouts functionality."""

    def test_default_timeouts(self):
        timeout = Timeouts()
        assert timeout.connect == 5.0
        assert timeout.read == 30.0
        assert timeout.total == 60.0

    def test_conservative_timeouts(self):
        timeout = Timeouts.conservative()
        assert timeout.connect == 10.0
        assert timeout.read == 60.0
        assert timeout.total == 120.0

    def test_aggressive_timeouts(self):
        timeout = Timeouts.aggressive()
        assert timeout.connect == 2.0
        assert timeout.read == 10.0
        assert timeout.total == 30.0

    def test_no_timeouts(self):
        timeout = Timeouts.none()
        assert timeout.connect is None
        assert timeout.read is None
        assert timeout.total is None

    def test_with_methods(self):
        timeout = Timeouts()
        new_timeout = timeout.with_total(120.0)
        assert new_timeout.total == 120.0
        assert new_timeout.connect == timeout.connect
        assert new_timeout.read == timeout.read

    def test_invalid_timeout_values(self):
        with pytest.raises(ValueError):
            Timeouts(connect=-1.0)

        with pytest.raises(ValueError):
            Timeouts(read=0.0)


class TestRetryPolicy:
    """Test RetryPolicy functionality."""

    def test_default_policy(self):
        policy = RetryPolicy()
        assert policy.max_attempts == 3
        assert policy.base_delay == 1.0
        assert policy.max_delay == 60.0
        assert policy.backoff_factor == 2.0
        assert policy.jitter is True

    def test_no_retry_policy(self):
        policy = RetryPolicy.none()
        assert policy.max_attempts == 1

    def test_conservative_policy(self):
        policy = RetryPolicy.conservative()
        assert policy.max_attempts == 5
        assert policy.base_delay == 2.0

    def test_calculate_delay(self):
        policy = RetryPolicy(jitter=False)  # Disable jitter for predictable testing

        # First retry
        delay1 = policy.calculate_delay(1)
        assert delay1 == 1.0

        # Second retry
        delay2 = policy.calculate_delay(2)
        assert delay2 == 2.0

        # Third retry
        delay3 = policy.calculate_delay(3)
        assert delay3 == 4.0

    def test_max_delay_cap(self):
        policy = RetryPolicy(base_delay=10.0, max_delay=15.0, backoff_factor=2.0, jitter=False)

        # Should be capped at max_delay
        delay = policy.calculate_delay(3)  # Would be 40.0 without cap
        assert delay == 15.0


class TestStreamEvent:
    """Test StreamEvent functionality."""

    def test_chunk_event(self):
        event = StreamEvent.create_chunk("Hello")
        assert event.type.value == "chunk"
        assert event.delta == "Hello"
        assert event.timestamp > 0

    def test_tool_call_event(self):
        tool_call = {"id": "call_123", "type": "function", "function": {"name": "test"}}
        event = StreamEvent.create_tool_call(tool_call)
        assert event.type.value == "tool_call"
        assert event.tool_call == tool_call

    def test_usage_event(self):
        usage = Usage(prompt=10, completion=20)
        event = StreamEvent.create_usage(usage)
        assert event.type.value == "usage"
        assert event.usage == usage

    def test_log_event(self):
        event = StreamEvent.create_log("Test message", level="warning")
        assert event.type.value == "log"
        assert event.log_message == "Test message"
        assert event.log_level == "warning"


class TestMessageNormalization:
    """Test message normalization functions."""

    def test_normalize_string(self):
        from llm_fiber.types import normalize_message

        msg = normalize_message("Hello!")
        assert isinstance(msg, ChatMessage)
        assert msg.role == "user"
        assert msg.content == "Hello!"

    def test_normalize_tuple(self):
        from llm_fiber.types import normalize_message

        msg = normalize_message(("system", "You are helpful"))
        assert isinstance(msg, ChatMessage)
        assert msg.role == "system"
        assert msg.content == "You are helpful"

    def test_normalize_dict(self):
        from llm_fiber.types import normalize_message

        msg_dict = {"role": "assistant", "content": "Hi there!", "name": "bot"}
        msg = normalize_message(msg_dict)
        assert isinstance(msg, ChatMessage)
        assert msg.role == "assistant"
        assert msg.content == "Hi there!"
        assert msg.name == "bot"

    def test_normalize_messages_list(self):
        from llm_fiber.types import normalize_messages

        messages = [
            "Hello!",
            ("system", "You are helpful"),
            {"role": "assistant", "content": "Hi!"},
        ]

        normalized = normalize_messages(messages)
        assert len(normalized) == 3
        assert all(isinstance(msg, ChatMessage) for msg in normalized)

        assert normalized[0].role == "user"
        assert normalized[0].content == "Hello!"

        assert normalized[1].role == "system"
        assert normalized[1].content == "You are helpful"

        assert normalized[2].role == "assistant"
        assert normalized[2].content == "Hi!"

    def test_normalize_messages_string(self):
        from llm_fiber.types import normalize_messages

        normalized = normalize_messages("Single message")
        assert len(normalized) == 1
        assert normalized[0].role == "user"
        assert normalized[0].content == "Single message"


class TestFiberClient:
    """Test Fiber client functionality."""

    @pytest.fixture
    def mock_env_vars(self):
        """Mock environment variables for testing."""
        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "test-openai-key",
                "ANTHROPIC_API_KEY": "test-anthropic-key",
                "GEMINI_API_KEY": "test-gemini-key",
            },
        ):
            yield

    def test_fiber_init(self):
        fiber = Fiber(
            default_model="gpt-4o-mini", api_keys={"openai": "test-key"}, enable_observability=False
        )
        assert fiber.default_model == "gpt-4o-mini"
        assert fiber._api_keys["openai"] == "test-key"

    def test_fiber_from_env(self, mock_env_vars):
        fiber = Fiber.from_env(enable_observability=False)

        # Should have detected API keys
        assert "openai" in fiber._api_keys
        assert "anthropic" in fiber._api_keys
        assert "gemini" in fiber._api_keys

        # Should have auto-selected a default model
        assert fiber.default_model is not None

    def test_fiber_from_env_with_preference(self, mock_env_vars):
        fiber = Fiber.from_env(prefer=["anthropic", "openai"], enable_observability=False)

        # Should respect preference order for default model selection
        assert fiber.default_model in ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"]

    def test_bind_context(self):
        fiber = Fiber(default_model="gpt-4o-mini", enable_observability=False)
        bound = fiber.bind(temperature=0.7, max_tokens=100)

        assert bound._context["temperature"] == 0.7
        assert bound._context["max_tokens"] == 100

    def test_bound_fiber_additional_bind(self):
        fiber = Fiber(default_model="gpt-4o-mini", enable_observability=False)
        bound1 = fiber.bind(temperature=0.7)
        bound2 = bound1.bind(max_tokens=100)

        assert bound2._context["temperature"] == 0.7
        assert bound2._context["max_tokens"] == 100

    def test_sync_property(self):
        fiber = Fiber(default_model="gpt-4o-mini", enable_observability=False)
        sync_fiber = fiber.sync

        # Should return a SyncFiber instance
        from llm_fiber.sync import SyncFiber

        assert isinstance(sync_fiber, SyncFiber)


class TestProviderRouting:
    """Test provider routing functionality."""

    def test_model_registry_resolve_openai(self):
        from llm_fiber.routing import ModelRegistry

        registry = ModelRegistry()
        provider = registry.resolve_provider("gpt-4o")
        assert provider == "openai"

    def test_model_registry_resolve_anthropic(self):
        from llm_fiber.routing import ModelRegistry

        registry = ModelRegistry()
        provider = registry.resolve_provider("claude-3-sonnet")
        assert provider == "anthropic"

    def test_model_registry_resolve_gemini(self):
        from llm_fiber.routing import ModelRegistry

        registry = ModelRegistry()
        provider = registry.resolve_provider("gemini-1.5-pro")
        assert provider == "gemini"

    def test_model_registry_provider_override(self):
        from llm_fiber.routing import ModelRegistry

        registry = ModelRegistry()
        provider = registry.resolve_provider("gpt-4o", provider_override="anthropic")
        assert provider == "anthropic"

    def test_model_registry_unknown_model(self):
        from llm_fiber.routing import ModelRegistry

        registry = ModelRegistry()

        # Should fall back to first available provider
        provider = registry.resolve_provider("unknown-model")
        assert provider in ["openai", "anthropic", "gemini"]

    def test_get_routing_diagnostics(self):
        from llm_fiber.routing import ModelRegistry

        registry = ModelRegistry()
        diagnostics = registry.get_routing_diagnostics("gpt-4o")

        assert diagnostics["model"] == "gpt-4o"
        assert diagnostics["resolved_provider"] == "openai"
        assert diagnostics["resolution_method"] == "registered_model"
        assert "gpt-" in diagnostics["matching_prefixes"]

    def test_estimate_cost(self):
        from llm_fiber.routing import ModelRegistry

        registry = ModelRegistry()
        cost = registry.estimate_cost("gpt-4o-mini", prompt_tokens=1000, completion_tokens=500)

        assert cost is not None
        assert cost > 0  # Should have some cost

    def test_validate_capabilities(self):
        from llm_fiber.routing import ModelRegistry

        registry = ModelRegistry()

        # Test tools support
        assert registry.validate_model_capabilities("gpt-4o", requires_tools=True)

        # Test vision support
        assert registry.validate_model_capabilities("gpt-4o", requires_vision=True)


if __name__ == "__main__":
    pytest.main([__file__])
