"""Tests for logging configuration edge cases."""

import logging
from unittest.mock import MagicMock, call, patch

import pytest

from llm_fiber.observability.logging import (
    BoundLogger,
    FiberLogger,
    NoOpLogger,
    default_logger,
    get_logger,
)


class TestFiberLoggerStructlogUnavailable:
    """Test FiberLogger when structlog is unavailable."""

    def test_no_structlog_fallback_to_stdlib(self, monkeypatch):
        """Test that when structlog is unavailable, falls back to stdlib logging."""
        # Directly mock HAS_STRUCTLOG to False to simulate missing structlog
        with patch("llm_fiber.observability.logging.HAS_STRUCTLOG", False):
            logger = FiberLogger(use_structlog=True)
            assert not logger._is_structlog

    def test_stdlib_logging_setup(self):
        """Test standard library logging setup."""
        logger = FiberLogger(name="test_logger", level=logging.DEBUG, use_structlog=False)

        assert not logger._is_structlog
        assert logger.name == "test_logger"
        assert isinstance(logger._logger, logging.Logger)
        assert logger._logger.name == "test_logger"

    def test_stdlib_logging_with_context(self, capfd):
        """Test stdlib logging with context (should format as string)."""
        logger = FiberLogger(name="test_context", level=logging.INFO, use_structlog=False)

        logger.info("Test message", user_id=123, action="test")

        captured = capfd.readouterr()
        assert "Test message" in captured.out
        assert "user_id=123" in captured.out
        assert "action=test" in captured.out


class TestFiberLoggerStructlogPresent:
    """Test FiberLogger when structlog is present."""

    @pytest.fixture
    def mock_structlog(self):
        """Mock structlog module."""
        with patch("llm_fiber.observability.logging.HAS_STRUCTLOG", True):
            # Create mock structlog module
            mock_structlog = MagicMock()
            mock_structlog.is_configured.return_value = False
            mock_structlog.configure = MagicMock()
            mock_logger = MagicMock()
            mock_structlog.get_logger.return_value = mock_logger

            # Manually set the structlog attribute on the module
            import llm_fiber.observability.logging as logging_module

            setattr(logging_module, "structlog", mock_structlog)
            try:
                yield mock_structlog, mock_logger
            finally:
                # Clean up - remove the attribute we added
                if hasattr(logging_module, "structlog"):
                    delattr(logging_module, "structlog")

    def test_structlog_configuration(self, mock_structlog):
        """Test that structlog is configured correctly."""
        mock_structlog_module, mock_logger = mock_structlog

        logger = FiberLogger(use_structlog=True)

        # Should configure structlog
        mock_structlog_module.configure.assert_called_once()
        assert logger._is_structlog
        assert logger._logger is mock_logger

    def test_structlog_already_configured(self, mock_structlog):
        """Test behavior when structlog is already configured."""
        mock_structlog_module, mock_logger = mock_structlog
        mock_structlog_module.is_configured.return_value = True

        logger = FiberLogger(use_structlog=True)

        # Should not reconfigure if already configured
        mock_structlog_module.configure.assert_not_called()
        assert logger._is_structlog

    def test_structlog_json_renderer_config(self, mock_structlog):
        """Test that structlog is configured with JSON renderer."""
        mock_structlog_module, _ = mock_structlog

        FiberLogger(use_structlog=True)

        # Check that configure was called with processors including JSONRenderer
        configure_call = mock_structlog_module.configure.call_args
        processors = configure_call[1]["processors"]

        # Should have JSONRenderer as the last processor
        assert any("JSONRenderer" in str(processor) for processor in processors)


class TestFiberLoggerRedaction:
    """Test secret redaction functionality."""

    def test_redact_secrets_enabled(self):
        """Test that secrets are redacted when enabled."""
        logger = FiberLogger(redact_secrets=True, use_structlog=False)

        context = {
            "api_key": "sk-1234567890abcdef1234567890abcdef",
            "user_token": "token_abcdef123456",
            "password": "secret123",
            "normal_field": "normal_value",
        }

        redacted = logger._redact_context(context)

        assert redacted["api_key"] == "sk-1...cdef"
        assert redacted["user_token"] == "toke...3456"
        assert redacted["password"] == "[REDACTED]"  # Short password
        assert redacted["normal_field"] == "normal_value"

    def test_redact_secrets_disabled(self):
        """Test that secrets are not redacted when disabled."""
        logger = FiberLogger(redact_secrets=False, use_structlog=False)

        context = {"api_key": "sk-1234567890abcdef1234567890abcdef", "password": "secret123"}

        redacted = logger._redact_context(context)

        assert redacted["api_key"] == "sk-1234567890abcdef1234567890abcdef"
        assert redacted["password"] == "secret123"

    def test_redact_nested_context(self):
        """Test redaction in nested dictionaries."""
        logger = FiberLogger(redact_secrets=True, use_structlog=False)

        context = {
            "user": {"name": "John", "api_key": "sk-1234567890abcdef1234567890abcdef"},
            "config": {"timeout": 30, "authorization": "Bearer token123456789"},
        }

        redacted = logger._redact_context(context)

        assert redacted["user"]["name"] == "John"
        assert redacted["user"]["api_key"] == "sk-1...cdef"
        assert redacted["config"]["timeout"] == 30
        assert redacted["config"]["authorization"] == "Bear...6789"

    def test_redact_various_sensitive_keys(self):
        """Test redaction of various sensitive key patterns."""
        logger = FiberLogger(redact_secrets=True, use_structlog=False)

        context = {
            "API_KEY": "uppercase_key",
            "bearer_token": "bearer123",
            "user_credential": "cred123",
            "auth_header": "auth_value",
            "secret_config": "secret_val",
        }

        redacted = logger._redact_context(context)

        # All should be redacted due to containing sensitive keywords
        expected_redactions = {
            "API_KEY": "[REDACTED]",  # 12 chars, under threshold
            "bearer_token": "[REDACTED]",  # 9 chars, under threshold
            "user_credential": "[REDACTED]",  # 7 chars, under threshold
            "auth_header": "[REDACTED]",  # 10 chars, under threshold
            "secret_config": "[REDACTED]",  # 10 chars, under threshold
        }
        for key in context.keys():
            assert redacted[key] == expected_redactions[key]


class TestFiberLoggerMethods:
    """Test FiberLogger logging methods."""

    @pytest.fixture
    def logger_with_mock(self):
        """Create logger with mocked underlying logger."""
        logger = FiberLogger(use_structlog=False)
        logger._logger = MagicMock()
        return logger

    def test_debug_logging(self, logger_with_mock):
        """Test debug logging method."""
        logger_with_mock.debug("Debug message", test_key="test_value")
        logger_with_mock._logger.debug.assert_called_once()

    def test_info_logging(self, logger_with_mock):
        """Test info logging method."""
        logger_with_mock.info("Info message", test_key="test_value")
        logger_with_mock._logger.info.assert_called_once()

    def test_warning_logging(self, logger_with_mock):
        """Test warning logging method."""
        logger_with_mock.warning("Warning message", test_key="test_value")
        logger_with_mock._logger.warning.assert_called_once()

    def test_error_logging(self, logger_with_mock):
        """Test error logging method."""
        logger_with_mock.error("Error message", test_key="test_value")
        logger_with_mock._logger.error.assert_called_once()

    def test_critical_logging(self, logger_with_mock):
        """Test critical logging method."""
        logger_with_mock.critical("Critical message", test_key="test_value")
        logger_with_mock._logger.critical.assert_called_once()


class TestFiberLoggerRequestLogging:
    """Test request-specific logging methods."""

    @pytest.fixture
    def logger_with_mock(self):
        """Create logger with mocked _log method."""
        logger = FiberLogger(use_structlog=False)
        logger._log = MagicMock()
        return logger

    def test_log_request_start(self, logger_with_mock):
        """Test request start logging."""
        logger_with_mock.log_request_start("openai", "gpt-4", "chat", "req-123")

        logger_with_mock._log.assert_called_once_with(
            "info",
            "Request started",
            provider="openai",
            model="gpt-4",
            operation="chat",
            request_id="req-123",
        )

    def test_log_request_success(self, logger_with_mock):
        """Test successful request logging."""
        logger_with_mock.log_request_success(
            "openai", "gpt-4", "chat", "req-123", latency_ms=150.5, tokens_used=50
        )

        expected_context = {
            "provider": "openai",
            "model": "gpt-4",
            "operation": "chat",
            "status": "success",
            "request_id": "req-123",
            "latency_ms": 150.5,
            "tokens_used": 50,
        }

        logger_with_mock._log.assert_called_once_with(
            "info", "Request completed successfully", **expected_context
        )

    def test_log_request_error(self, logger_with_mock):
        """Test request error logging."""
        error = ValueError("Test error")
        logger_with_mock.log_request_error("openai", "gpt-4", error, "chat", "req-123", 100.0)

        expected_context = {
            "provider": "openai",
            "model": "gpt-4",
            "operation": "chat",
            "status": "error",
            "error_type": "ValueError",
            "error_message": "Test error",
            "request_id": "req-123",
            "latency_ms": 100.0,
        }

        logger_with_mock._log.assert_called_once_with("error", "Request failed", **expected_context)

    def test_log_retry_attempt(self, logger_with_mock):
        """Test retry attempt logging."""
        error = ConnectionError("Connection failed")
        logger_with_mock.log_retry_attempt(
            "openai", "gpt-4", 2, 3, error, 1000.0, "chat", "req-123"
        )

        expected_context = {
            "provider": "openai",
            "model": "gpt-4",
            "operation": "chat",
            "attempt": 2,
            "max_attempts": 3,
            "error_type": "ConnectionError",
            "error_message": "Connection failed",
            "delay_ms": 1000.0,
            "request_id": "req-123",
        }

        logger_with_mock._log.assert_called_once_with(
            "warning", "Retrying request", **expected_context
        )


class TestFiberLoggerStreamingMethods:
    """Test streaming-specific logging methods."""

    @pytest.fixture
    def logger_with_mock(self):
        """Create logger with mocked _log method."""
        logger = FiberLogger(use_structlog=False)
        logger._log = MagicMock()
        return logger

    def test_log_streaming_start(self, logger_with_mock):
        """Test streaming start logging."""
        logger_with_mock.log_streaming_start("openai", "gpt-4", "req-123")

        logger_with_mock._log.assert_called_once_with(
            "info",
            "Streaming started",
            provider="openai",
            model="gpt-4",
            operation="stream",
            request_id="req-123",
        )

    def test_log_streaming_chunk(self, logger_with_mock):
        """Test streaming chunk logging."""
        logger_with_mock.log_streaming_chunk("openai", "gpt-4", 50, 5, "req-123")

        logger_with_mock._log.assert_called_once_with(
            "debug",
            "Streaming chunk received",
            provider="openai",
            model="gpt-4",
            operation="stream",
            chunk_size=50,
            total_chunks=5,
            request_id="req-123",
        )

    def test_log_streaming_complete(self, logger_with_mock):
        """Test streaming completion logging."""
        logger_with_mock.log_streaming_complete("openai", "gpt-4", 10, 150, 2000.0, "req-123")

        expected_context = {
            "provider": "openai",
            "model": "gpt-4",
            "operation": "stream",
            "status": "success",
            "total_chunks": 10,
            "total_tokens": 150,
            "latency_ms": 2000.0,
            "request_id": "req-123",
        }

        logger_with_mock._log.assert_called_once_with(
            "info", "Streaming completed", **expected_context
        )


class TestFiberLoggerCacheMethods:
    """Test cache-specific logging methods."""

    @pytest.fixture
    def logger_with_mock(self):
        """Create logger with mocked _log method."""
        logger = FiberLogger(use_structlog=False)
        logger._log = MagicMock()
        return logger

    def test_log_cache_hit(self, logger_with_mock):
        """Test cache hit logging."""
        logger_with_mock.log_cache_hit("openai", "gpt-4", "cache-key-123", "chat", "req-123")

        logger_with_mock._log.assert_called_once_with(
            "debug",
            "Cache hit",
            provider="openai",
            model="gpt-4",
            operation="chat",
            cache_key="cache-key-123",
            request_id="req-123",
        )

    def test_log_cache_miss(self, logger_with_mock):
        """Test cache miss logging."""
        logger_with_mock.log_cache_miss("openai", "gpt-4", "cache-key-123", "chat", "req-123")

        logger_with_mock._log.assert_called_once_with(
            "debug",
            "Cache miss",
            provider="openai",
            model="gpt-4",
            operation="chat",
            cache_key="cache-key-123",
            request_id="req-123",
        )


class TestBoundLogger:
    """Test BoundLogger functionality."""

    def test_bound_logger_creation(self):
        """Test creating a bound logger."""
        base_logger = FiberLogger(use_structlog=False)
        context = {"request_id": "req-123", "user_id": "user-456"}

        bound_logger = base_logger.bind(**context)

        assert isinstance(bound_logger, BoundLogger)
        assert bound_logger._logger is base_logger
        assert bound_logger._context == context

    def test_bound_logger_context_merging(self):
        """Test that bound logger merges context correctly."""
        base_logger = FiberLogger(use_structlog=False)
        base_logger._log = MagicMock()

        bound_logger = base_logger.bind(request_id="req-123")
        bound_logger.info("Test message", user_id="user-456")

        expected_context = {"request_id": "req-123", "user_id": "user-456"}
        base_logger._log.assert_called_once_with("info", "Test message", **expected_context)

    def test_bound_logger_chaining(self):
        """Test chaining bound loggers."""
        base_logger = FiberLogger(use_structlog=False)
        base_logger._log = MagicMock()

        bound1 = base_logger.bind(request_id="req-123")
        bound2 = bound1.bind(user_id="user-456")
        bound2.info("Test message", action="test")

        expected_context = {"request_id": "req-123", "user_id": "user-456", "action": "test"}
        base_logger._log.assert_called_once_with("info", "Test message", **expected_context)

    def test_bound_logger_context_override(self):
        """Test that additional context overrides bound context."""
        base_logger = FiberLogger(use_structlog=False)
        base_logger._log = MagicMock()

        bound_logger = base_logger.bind(request_id="req-123", priority="low")
        bound_logger.info("Test message", priority="high", user_id="user-456")

        expected_context = {
            "request_id": "req-123",
            "priority": "high",  # Should override
            "user_id": "user-456",
        }
        base_logger._log.assert_called_once_with("info", "Test message", **expected_context)

    def test_bound_logger_all_levels(self):
        """Test that all logging levels work with bound logger."""
        base_logger = FiberLogger(use_structlog=False)
        base_logger._log = MagicMock()

        bound_logger = base_logger.bind(request_id="req-123")

        bound_logger.debug("Debug message")
        bound_logger.info("Info message")
        bound_logger.warning("Warning message")
        bound_logger.error("Error message")
        bound_logger.critical("Critical message")

        expected_calls = [
            call("debug", "Debug message", request_id="req-123"),
            call("info", "Info message", request_id="req-123"),
            call("warning", "Warning message", request_id="req-123"),
            call("error", "Error message", request_id="req-123"),
            call("critical", "Critical message", request_id="req-123"),
        ]

        base_logger._log.assert_has_calls(expected_calls)


class TestNoOpLogger:
    """Test NoOpLogger functionality."""

    def test_noop_logger_initialization(self):
        """Test NoOpLogger initialization."""
        logger = NoOpLogger()

        assert logger.name == "noop"
        assert not logger.redact_secrets
        assert not logger._is_structlog

    def test_noop_logger_methods_do_nothing(self):
        """Test that NoOpLogger methods don't perform any operations."""
        logger = NoOpLogger()

        # These should not raise any errors and should do nothing
        logger.debug("Debug message", test_key="test_value")
        logger.info("Info message", test_key="test_value")
        logger.warning("Warning message", test_key="test_value")
        logger.error("Error message", test_key="test_value")
        logger.critical("Critical message", test_key="test_value")

        # Should not cause any side effects
        logger.log_request_start("provider", "model")
        logger.log_request_success("provider", "model")
        logger.log_request_error("provider", "model", Exception("test"))

    def test_noop_logger_bind(self):
        """Test that NoOpLogger.bind returns a BoundLogger."""
        logger = NoOpLogger()
        bound = logger.bind(test_key="test_value")

        assert isinstance(bound, BoundLogger)
        assert bound._logger is logger


class TestModuleLevelFunctions:
    """Test module-level functions."""

    def test_get_logger_default_name(self):
        """Test get_logger with default name."""
        logger = get_logger()
        assert logger.name == "llm_fiber"
        assert isinstance(logger, FiberLogger)

    def test_get_logger_custom_name(self):
        """Test get_logger with custom name."""
        logger = get_logger("custom_logger")
        assert logger.name == "custom_logger"
        assert isinstance(logger, FiberLogger)

    def test_default_logger_instance(self):
        """Test default logger instance."""
        assert isinstance(default_logger, FiberLogger)
        assert default_logger.name == "llm_fiber"


class TestLoggerErrorHandling:
    """Test error handling in logger."""

    def test_invalid_log_level_handling(self):
        """Test handling of invalid log levels."""
        # This should not raise an error, but fall back gracefully
        logger = FiberLogger(level=999, use_structlog=False)  # Invalid level

        # Should still be able to log
        logger.info("Test message")
        assert isinstance(logger._logger, logging.Logger)

    def test_context_serialization_errors(self):
        """Test handling of context that can't be serialized."""
        logger = FiberLogger(use_structlog=False)

        # Create an object that might cause serialization issues
        class UnserializableObj:
            def __str__(self):
                raise Exception("Cannot serialize")

        # Should not raise an error
        logger.info("Test message", bad_obj=UnserializableObj())

    def test_redaction_with_non_dict_context(self):
        """Test redaction when context contains non-dict values."""
        logger = FiberLogger(redact_secrets=True, use_structlog=False)

        context = {
            "api_key": "sk-1234567890abcdef1234567890abcdef",
            "config": "not_a_dict",
            "list_value": [1, 2, 3],
        }

        # Should not raise an error
        redacted = logger._redact_context(context)
        assert redacted["api_key"] == "sk-1...cdef"
        assert redacted["config"] == "not_a_dict"
        assert redacted["list_value"] == [1, 2, 3]
