"""Tests for sync wrapper functionality."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from llm_fiber import ChatMessage, ChatResult, FiberError, Usage
from llm_fiber.sync import BoundSyncFiber, SyncFiber, _run_async


class TestRunAsync:
    """Test the _run_async utility function."""

    def test_run_async_no_loop(self):
        """Test _run_async when no event loop is running."""

        async def dummy_coro():
            await asyncio.sleep(0.01)
            return "success"

        result = _run_async(dummy_coro())
        assert result == "success"

    def test_run_async_exception_propagation(self):
        """Test that exceptions are properly propagated."""

        async def failing_coro():
            raise ValueError("test error")

        with pytest.raises(ValueError, match="test error"):
            _run_async(failing_coro())

    @pytest.mark.asyncio
    async def test_run_async_with_running_loop(self):
        """Test _run_async raises error when called from async context."""

        async def dummy_coro():
            return "should not reach here"

        # This should raise RuntimeError about running event loop
        with pytest.raises(
            RuntimeError, match="asyncio.run\\(\\) cannot be called from a running event loop"
        ):
            _run_async(dummy_coro())


class TestSyncFiber:
    """Test SyncFiber wrapper."""

    @pytest.fixture
    def mock_fiber(self):
        """Mock async Fiber instance."""
        fiber = MagicMock()
        fiber.chat = AsyncMock()
        fiber.ask = AsyncMock()
        fiber.bind = MagicMock()
        return fiber

    @pytest.fixture
    def sync_fiber(self, mock_fiber):
        """SyncFiber instance with mocked async fiber."""
        return SyncFiber(mock_fiber)

    def test_init(self, mock_fiber):
        """Test SyncFiber initialization."""
        sync_fiber = SyncFiber(mock_fiber)
        assert sync_fiber._fiber is mock_fiber

    def test_chat_success(self, sync_fiber, mock_fiber, sample_messages, sample_chat_result):
        """Test successful sync chat call."""
        mock_fiber.chat.return_value = sample_chat_result

        result = sync_fiber.chat(
            messages=sample_messages, model="gpt-4o-mini", temperature=0.7, max_tokens=100
        )

        assert result == sample_chat_result
        mock_fiber.chat.assert_called_once_with(
            sample_messages,
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=100,
            top_p=None,
            seed=None,
            stop=None,
            tools=None,
            tool_choice=None,
            timeout_s=None,
            provider=None,
            idempotency_key=None,
        )

    def test_chat_with_all_params(
        self, sync_fiber, mock_fiber, sample_messages, sample_chat_result
    ):
        """Test sync chat with all parameters."""
        mock_fiber.chat.return_value = sample_chat_result

        result = sync_fiber.chat(
            messages=sample_messages,
            model="gpt-4",
            temperature=0.8,
            max_tokens=200,
            top_p=0.9,
            seed=42,
            stop=["END"],
            tools=[{"name": "test"}],
            tool_choice="auto",
            timeout_s=30.0,
            provider="openai",
            idempotency_key="test-key",
            custom_param="value",
        )

        assert result == sample_chat_result
        mock_fiber.chat.assert_called_once_with(
            sample_messages,
            model="gpt-4",
            temperature=0.8,
            max_tokens=200,
            top_p=0.9,
            seed=42,
            stop=["END"],
            tools=[{"name": "test"}],
            tool_choice="auto",
            timeout_s=30.0,
            provider="openai",
            idempotency_key="test-key",
            custom_param="value",
        )

    def test_chat_exception_propagation(self, sync_fiber, mock_fiber, sample_messages):
        """Test that exceptions from async chat are propagated."""
        mock_fiber.chat.side_effect = FiberError("Test error")

        with pytest.raises(FiberError, match="Test error"):
            sync_fiber.chat(messages=sample_messages)

    def test_chat_timeout_exception(self, sync_fiber, mock_fiber, sample_messages):
        """Test timeout exception propagation."""
        mock_fiber.chat.side_effect = asyncio.TimeoutError("Request timed out")

        with pytest.raises(asyncio.TimeoutError, match="Request timed out"):
            sync_fiber.chat(messages=sample_messages)

    def test_ask_success(self, sync_fiber, mock_fiber):
        """Test successful sync ask call."""
        mock_fiber.ask.return_value = "This is the answer"

        result = sync_fiber.ask(prompt="What is 2+2?", model="gpt-3.5-turbo", temperature=0.1)

        assert result == "This is the answer"
        mock_fiber.ask.assert_called_once_with(
            prompt="What is 2+2?", model="gpt-3.5-turbo", temperature=0.1, max_tokens=None
        )

    def test_ask_with_all_params(self, sync_fiber, mock_fiber):
        """Test sync ask with all parameters."""
        mock_fiber.ask.return_value = "Answer with all params"

        result = sync_fiber.ask(
            prompt="Test prompt", model="gpt-4", temperature=0.9, max_tokens=50, custom_arg="value"
        )

        assert result == "Answer with all params"
        mock_fiber.ask.assert_called_once_with(
            prompt="Test prompt", model="gpt-4", temperature=0.9, max_tokens=50, custom_arg="value"
        )

    def test_ask_exception_propagation(self, sync_fiber, mock_fiber):
        """Test that exceptions from async ask are propagated."""
        mock_fiber.ask.side_effect = ValueError("Ask failed")

        with pytest.raises(ValueError, match="Ask failed"):
            sync_fiber.ask("test prompt")

    def test_bind_returns_bound_sync_fiber(self, sync_fiber, mock_fiber):
        """Test that bind returns a BoundSyncFiber instance."""
        mock_bound_fiber = MagicMock()
        mock_fiber.bind.return_value = mock_bound_fiber

        bound_sync = sync_fiber.bind(model="gpt-4", temperature=0.5)

        assert isinstance(bound_sync, BoundSyncFiber)
        assert bound_sync._bound_fiber is mock_bound_fiber
        mock_fiber.bind.assert_called_once_with(model="gpt-4", temperature=0.5)

    def test_chat_stream_basic_functionality(self, sync_fiber, mock_fiber, sample_messages):
        """Test basic chat_stream functionality without complex mocking."""
        # Simple test - just verify the method can be called and handles exceptions
        mock_fiber.chat_stream.side_effect = FiberError("Stream error")

        with pytest.raises(FiberError, match="Stream error"):
            list(sync_fiber.chat_stream(messages=sample_messages))


class TestBoundSyncFiber:
    """Test BoundSyncFiber wrapper."""

    @pytest.fixture
    def mock_bound_fiber(self):
        """Mock bound async Fiber instance."""
        bound_fiber = MagicMock()
        bound_fiber.chat = AsyncMock()
        bound_fiber.ask = AsyncMock()
        bound_fiber.bind = MagicMock()
        return bound_fiber

    @pytest.fixture
    def bound_sync_fiber(self, mock_bound_fiber):
        """BoundSyncFiber instance with mocked bound fiber."""
        return BoundSyncFiber(mock_bound_fiber)

    def test_init(self, mock_bound_fiber):
        """Test BoundSyncFiber initialization."""
        bound_sync = BoundSyncFiber(mock_bound_fiber)
        assert bound_sync._bound_fiber is mock_bound_fiber

    def test_chat_success(self, bound_sync_fiber, mock_bound_fiber, sample_chat_result):
        """Test successful bound sync chat call."""
        mock_bound_fiber.chat.return_value = sample_chat_result

        result = bound_sync_fiber.chat(messages=[ChatMessage.user("test")], max_tokens=100)

        assert result == sample_chat_result
        # Verify the mock was called at least once
        assert mock_bound_fiber.chat.called

    def test_chat_exception_propagation(self, bound_sync_fiber, mock_bound_fiber):
        """Test that exceptions from bound async chat are propagated."""
        mock_bound_fiber.chat.side_effect = FiberError("Bound chat error")

        with pytest.raises(FiberError, match="Bound chat error"):
            bound_sync_fiber.chat(messages=[ChatMessage.user("test")])

    def test_ask_success(self, bound_sync_fiber, mock_bound_fiber):
        """Test successful bound sync ask call."""
        mock_bound_fiber.ask.return_value = "Bound answer"

        result = bound_sync_fiber.ask("What is bound?", max_tokens=50)

        assert result == "Bound answer"
        mock_bound_fiber.ask.assert_called_once_with("What is bound?", max_tokens=50)

    def test_ask_exception_propagation(self, bound_sync_fiber, mock_bound_fiber):
        """Test that exceptions from bound async ask are propagated."""
        mock_bound_fiber.ask.side_effect = RuntimeError("Bound ask error")

        with pytest.raises(RuntimeError, match="Bound ask error"):
            bound_sync_fiber.ask("test prompt")

    def test_bind_chaining(self, bound_sync_fiber, mock_bound_fiber):
        """Test that bind can be chained on BoundSyncFiber."""
        mock_new_bound_fiber = MagicMock()
        mock_bound_fiber.bind.return_value = mock_new_bound_fiber

        new_bound_sync = bound_sync_fiber.bind(temperature=0.8, max_tokens=200)

        assert isinstance(new_bound_sync, BoundSyncFiber)
        assert new_bound_sync._bound_fiber is mock_new_bound_fiber
        mock_bound_fiber.bind.assert_called_once_with(temperature=0.8, max_tokens=200)

    def test_chat_stream_basic_functionality(self, bound_sync_fiber, mock_bound_fiber):
        """Test basic chat_stream functionality."""
        mock_bound_fiber.chat_stream.side_effect = FiberError("Bound stream error")

        with pytest.raises(FiberError, match="Bound stream error"):
            list(bound_sync_fiber.chat_stream(messages=[ChatMessage.user("test")]))


class TestSyncFiberIntegration:
    """Integration tests for sync wrapper with event loop scenarios."""

    def test_sync_methods_from_outside_event_loop(self, fiber_client, sample_messages):
        """Test sync methods work when no event loop is running."""
        # Create sync wrapper
        sync_fiber = SyncFiber(fiber_client)

        # Mock the underlying async methods
        async def mock_chat_coro(*args, **kwargs):
            return ChatResult(
                text="Sync test response",
                tool_calls=[],
                finish_reason="stop",
                usage=Usage(prompt=10, completion=5, total=15),
                raw={"test": True},
            )

        async def mock_ask_coro(*args, **kwargs):
            return "Simple sync response"

        with patch.object(fiber_client, "chat", side_effect=mock_chat_coro), patch.object(
            fiber_client, "ask", side_effect=mock_ask_coro
        ):
            # Test chat
            result = sync_fiber.chat(messages=sample_messages)
            assert result.text == "Sync test response"

            # Test ask
            ask_result = sync_fiber.ask("Test prompt")
            assert ask_result == "Simple sync response"

    @pytest.mark.asyncio
    async def test_sync_methods_fail_in_async_context(self, fiber_client, sample_messages):
        """Test sync methods raise error when called from async context."""
        sync_fiber = SyncFiber(fiber_client)

        # These should all raise RuntimeError about running event loop
        with pytest.raises(
            RuntimeError, match="asyncio.run\\(\\) cannot be called from a running event loop"
        ):
            sync_fiber.chat(messages=sample_messages)

        with pytest.raises(
            RuntimeError, match="asyncio.run\\(\\) cannot be called from a running event loop"
        ):
            sync_fiber.ask("Test prompt")

        with pytest.raises(
            RuntimeError, match="asyncio.run\\(\\) cannot be called from a running event loop"
        ):
            list(sync_fiber.chat_stream(messages=sample_messages))

    def test_bound_sync_fiber_from_sync_fiber(self, fiber_client):
        """Test creating and using bound sync fiber."""
        sync_fiber = SyncFiber(fiber_client)

        # Mock bind method
        with patch.object(fiber_client, "bind") as mock_bind:
            mock_bound_fiber = MagicMock()

            async def mock_bound_ask(*args, **kwargs):
                return "Bound response"

            mock_bound_fiber.ask = AsyncMock(side_effect=mock_bound_ask)
            mock_bind.return_value = mock_bound_fiber

            # Create bound sync fiber
            bound_sync = sync_fiber.bind(model="gpt-4", temperature=0.3)

            # Test bound method
            result = bound_sync.ask("Bound test")
            assert result == "Bound response"

            # Verify binding was called correctly
            mock_bind.assert_called_once_with(model="gpt-4", temperature=0.3)

    def test_exception_types_preserved(self, fiber_client, sample_messages):
        """Test that different exception types are preserved through sync wrapper."""
        sync_fiber = SyncFiber(fiber_client)

        # Test various exception types
        exceptions_to_test = [
            FiberError("Fiber specific error"),
            ValueError("Value error"),
            RuntimeError("Runtime error"),
            asyncio.TimeoutError("Timeout error"),
            ConnectionError("Connection error"),
        ]

        for exception in exceptions_to_test:

            async def failing_chat(*args, **kwargs):
                raise exception

            with patch.object(fiber_client, "chat", side_effect=failing_chat):
                with pytest.raises(type(exception), match=str(exception)):
                    sync_fiber.chat(messages=sample_messages)

    def test_timeout_handling(self, fiber_client, sample_messages):
        """Test timeout parameter is passed through correctly."""
        sync_fiber = SyncFiber(fiber_client)

        async def mock_timeout_chat(*args, **kwargs):
            return ChatResult(
                text="Timeout test",
                tool_calls=[],
                finish_reason="stop",
                usage=Usage(prompt=5, completion=3, total=8),
                raw={},
            )

        with patch.object(fiber_client, "chat", side_effect=mock_timeout_chat) as mock_chat:
            # Test with timeout parameter
            sync_fiber.chat(messages=sample_messages, timeout_s=30.0)

            # Verify timeout was passed
            mock_chat.assert_called_once()
            call_kwargs = mock_chat.call_args[1]
            assert call_kwargs["timeout_s"] == 30.0
