"""Logging utilities for llm-fiber observability."""

from __future__ import annotations

import logging
import sys
from typing import Any, Dict, Optional

# Try to import structlog for structured logging support
try:
    import structlog

    HAS_STRUCTLOG = True
except ImportError:
    HAS_STRUCTLOG = False


class FiberLogger:
    """Centralized logging for llm-fiber with structured logging support."""

    def __init__(
        self,
        name: str = "llm_fiber",
        level: int = logging.INFO,
        use_structlog: bool = False,
        redact_secrets: bool = True,
    ):
        self.name = name
        self.redact_secrets = redact_secrets

        if use_structlog and HAS_STRUCTLOG:
            self._setup_structlog()
            self._logger = structlog.get_logger(name)
            self._is_structlog = True
        else:
            self._logger = logging.getLogger(name)
            if not self._logger.handlers:
                self._setup_stdlib_logging(level)
            self._is_structlog = False

    def _setup_stdlib_logging(self, level: int) -> None:
        """Setup standard library logging."""
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)
        self._logger.setLevel(level)

    def _setup_structlog(self) -> None:
        """Setup structlog configuration."""
        if not structlog.is_configured():
            structlog.configure(
                processors=[
                    structlog.stdlib.filter_by_level,
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.PositionalArgumentsFormatter(),
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.processors.StackInfoRenderer(),
                    structlog.processors.format_exc_info,
                    structlog.processors.UnicodeDecoder(),
                    structlog.processors.JSONRenderer(),
                ],
                context_class=dict,
                logger_factory=structlog.stdlib.LoggerFactory(),
                cache_logger_on_first_use=True,
            )

    def _redact_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Redact sensitive information from context."""
        if not self.redact_secrets:
            return context

        redacted = context.copy()

        # Keys that should be redacted
        sensitive_keys = {
            "api_key",
            "apikey",
            "token",
            "secret",
            "password",
            "authorization",
            "auth",
            "bearer",
            "credential",
            "credentials",
        }

        for key, value in redacted.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                # Special case: passwords are always fully redacted
                if "password" in key_lower:
                    redacted[key] = "[REDACTED]"
                elif isinstance(value, str) and len(value) > 16:
                    redacted[key] = f"{value[:4]}...{value[-4:]}"
                else:
                    redacted[key] = "[REDACTED]"
            elif isinstance(value, dict):
                redacted[key] = self._redact_context(value)

        return redacted

    def _log(self, level: str, message: str, **context: Any) -> None:
        """Internal logging method."""
        if context:
            context = self._redact_context(context)

        if self._is_structlog:
            getattr(self._logger, level)(message, **context)
        else:
            # For stdlib logging, format context as string
            if context:
                try:
                    context_str = " ".join(f"{k}={v}" for k, v in context.items())
                    message = f"{message} | {context_str}"
                except Exception:
                    # Handle serialization errors gracefully
                    message = f"{message} | [context serialization error]"
            getattr(self._logger, level)(message)

    def debug(self, message: str, **context: Any) -> None:
        """Log debug message."""
        self._log("debug", message, **context)

    def info(self, message: str, **context: Any) -> None:
        """Log info message."""
        self._log("info", message, **context)

    def warning(self, message: str, **context: Any) -> None:
        """Log warning message."""
        self._log("warning", message, **context)

    def error(self, message: str, **context: Any) -> None:
        """Log error message."""
        self._log("error", message, **context)

    def critical(self, message: str, **context: Any) -> None:
        """Log critical message."""
        self._log("critical", message, **context)

    def log_request_start(
        self, provider: str, model: str, operation: str = "chat", request_id: Optional[str] = None
    ) -> None:
        """Log the start of a request."""
        self.info(
            "Request started",
            provider=provider,
            model=model,
            operation=operation,
            request_id=request_id,
        )

    def log_request_success(
        self,
        provider: str,
        model: str,
        operation: str = "chat",
        request_id: Optional[str] = None,
        latency_ms: Optional[float] = None,
        tokens_used: Optional[int] = None,
    ) -> None:
        """Log successful request completion."""
        context = {
            "provider": provider,
            "model": model,
            "operation": operation,
            "status": "success",
            "request_id": request_id,
        }

        if latency_ms is not None:
            context["latency_ms"] = latency_ms
        if tokens_used is not None:
            context["tokens_used"] = tokens_used

        self.info("Request completed successfully", **context)

    def log_request_error(
        self,
        provider: str,
        model: str,
        error: Exception,
        operation: str = "chat",
        request_id: Optional[str] = None,
        latency_ms: Optional[float] = None,
    ) -> None:
        """Log request error."""
        context = {
            "provider": provider,
            "model": model,
            "operation": operation,
            "status": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "request_id": request_id,
        }

        if latency_ms is not None:
            context["latency_ms"] = latency_ms

        self.error("Request failed", **context)

    def log_retry_attempt(
        self,
        provider: str,
        model: str,
        attempt: int,
        max_attempts: int,
        error: Exception,
        delay_ms: float,
        operation: str = "chat",
        request_id: Optional[str] = None,
    ) -> None:
        """Log retry attempt."""
        self.warning(
            "Retrying request",
            provider=provider,
            model=model,
            operation=operation,
            attempt=attempt,
            max_attempts=max_attempts,
            error_type=type(error).__name__,
            error_message=str(error),
            delay_ms=delay_ms,
            request_id=request_id,
        )

    def log_streaming_start(
        self, provider: str, model: str, request_id: Optional[str] = None
    ) -> None:
        """Log the start of streaming."""
        self.info(
            "Streaming started",
            provider=provider,
            model=model,
            operation="stream",
            request_id=request_id,
        )

    def log_streaming_chunk(
        self,
        provider: str,
        model: str,
        chunk_size: int,
        total_chunks: int,
        request_id: Optional[str] = None,
    ) -> None:
        """Log streaming chunk received."""
        self.debug(
            "Streaming chunk received",
            provider=provider,
            model=model,
            operation="stream",
            chunk_size=chunk_size,
            total_chunks=total_chunks,
            request_id=request_id,
        )

    def log_streaming_complete(
        self,
        provider: str,
        model: str,
        total_chunks: int,
        total_tokens: Optional[int] = None,
        latency_ms: Optional[float] = None,
        request_id: Optional[str] = None,
    ) -> None:
        """Log streaming completion."""
        context = {
            "provider": provider,
            "model": model,
            "operation": "stream",
            "status": "success",
            "total_chunks": total_chunks,
            "request_id": request_id,
        }

        if total_tokens is not None:
            context["total_tokens"] = total_tokens
        if latency_ms is not None:
            context["latency_ms"] = latency_ms

        self.info("Streaming completed", **context)

    def log_cache_hit(
        self,
        provider: str,
        model: str,
        cache_key: str,
        operation: str = "chat",
        request_id: Optional[str] = None,
    ) -> None:
        """Log cache hit."""
        self.debug(
            "Cache hit",
            provider=provider,
            model=model,
            operation=operation,
            cache_key=cache_key,
            request_id=request_id,
        )

    def log_cache_miss(
        self,
        provider: str,
        model: str,
        cache_key: str,
        operation: str = "chat",
        request_id: Optional[str] = None,
    ) -> None:
        """Log cache miss."""
        self.debug(
            "Cache miss",
            provider=provider,
            model=model,
            operation=operation,
            cache_key=cache_key,
            request_id=request_id,
        )

    def bind(self, **context: Any) -> BoundLogger:
        """Create a bound logger with persistent context."""
        return BoundLogger(self, context)


class BoundLogger:
    """Logger bound to specific context."""

    def __init__(self, logger: FiberLogger, context: Dict[str, Any]):
        self._logger = logger
        self._context = context

    def _merge_context(self, **additional: Any) -> Dict[str, Any]:
        """Merge bound context with additional context."""
        merged = self._context.copy()
        merged.update(additional)
        return merged

    def debug(self, message: str, **context: Any) -> None:
        """Log debug message with bound context."""
        self._logger.debug(message, **self._merge_context(**context))

    def info(self, message: str, **context: Any) -> None:
        """Log info message with bound context."""
        self._logger.info(message, **self._merge_context(**context))

    def warning(self, message: str, **context: Any) -> None:
        """Log warning message with bound context."""
        self._logger.warning(message, **self._merge_context(**context))

    def error(self, message: str, **context: Any) -> None:
        """Log error message with bound context."""
        self._logger.error(message, **self._merge_context(**context))

    def critical(self, message: str, **context: Any) -> None:
        """Log critical message with bound context."""
        self._logger.critical(message, **self._merge_context(**context))

    def bind(self, **context: Any) -> BoundLogger:
        """Create a new bound logger with additional context."""
        return BoundLogger(self._logger, self._merge_context(**context))


class NoOpLogger(FiberLogger):
    """No-op logger implementation for when logging is disabled."""

    def __init__(self):
        # Don't call super().__init__() to avoid setting up logging
        self.name = "noop"
        self.redact_secrets = False
        self._is_structlog = False

    def _log(self, level: str, message: str, **context: Any) -> None:
        """No-op logging method."""
        pass

    def bind(self, **context: Any) -> BoundLogger:
        """Return a bound no-op logger."""
        return BoundLogger(self, context)


# Default logger instance
default_logger = FiberLogger()


def get_logger(name: str = "llm_fiber") -> FiberLogger:
    """Get a logger instance."""
    return FiberLogger(name)
