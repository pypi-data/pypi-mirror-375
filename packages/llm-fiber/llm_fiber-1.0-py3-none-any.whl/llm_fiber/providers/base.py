"""Base provider interface for llm-fiber."""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional

from ..types import ChatMessage, ChatResult, StreamEvent


class Provider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_seconds: float = 30.0,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self.name = self.__class__.__name__.lower().replace("adapter", "").replace("provider", "")

    @abstractmethod
    async def chat(
        self,
        model: str,
        messages: List[ChatMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        seed: Optional[int] = None,
        stop: Optional[List[str]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        idempotency_key: Optional[str] = None,
        **kwargs,
    ) -> ChatResult:
        """Execute a chat completion request.

        Args:
            model: Model identifier
            messages: List of chat messages
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            seed: Random seed for deterministic output
            stop: Stop sequences
            tools: Available tools/functions
            tool_choice: Tool selection strategy
            timeout_seconds: Request timeout override
            idempotency_key: Idempotency key for deduplication
            **kwargs: Additional provider-specific parameters

        Returns:
            ChatResult with response and metadata

        Raises:
            FiberError: On request failure
        """
        pass

    @abstractmethod
    async def chat_stream(
        self,
        model: str,
        messages: List[ChatMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        seed: Optional[int] = None,
        stop: Optional[List[str]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        idempotency_key: Optional[str] = None,
        **kwargs,
    ) -> AsyncIterator[StreamEvent]:
        """Execute a streaming chat completion request.

        Args:
            model: Model identifier
            messages: List of chat messages
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            seed: Random seed for deterministic output
            stop: Stop sequences
            tools: Available tools/functions
            tool_choice: Tool selection strategy
            timeout_seconds: Request timeout override
            idempotency_key: Idempotency key for deduplication
            **kwargs: Additional provider-specific parameters

        Yields:
            StreamEvent objects for each response chunk

        Raises:
            FiberError: On request failure
        """
        pass

    @abstractmethod
    def prepare_request(
        self,
        model: str,
        messages: List[ChatMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        seed: Optional[int] = None,
        stop: Optional[List[str]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Prepare a request payload for this provider.

        Args:
            model: Model identifier
            messages: List of chat messages
            **kwargs: Additional parameters

        Returns:
            Provider-specific request payload
        """
        pass

    @abstractmethod
    def parse_response(self, response: Dict[str, Any]) -> ChatResult:
        """Parse a provider response into standardized format.

        Args:
            response: Raw provider response

        Returns:
            Parsed ChatResult
        """
        pass

    def validate_model(self, model: str) -> bool:
        """Validate if this provider supports the given model.

        Args:
            model: Model identifier

        Returns:
            True if model is supported
        """
        # Default implementation - providers can override
        return True

    def get_headers(self, idempotency_key: Optional[str] = None) -> Dict[str, str]:
        """Get HTTP headers for requests.

        Args:
            idempotency_key: Optional idempotency key

        Returns:
            Dictionary of HTTP headers
        """
        headers = {"Content-Type": "application/json", "User-Agent": "llm-fiber/0.1.0"}

        if self.api_key:
            headers.update(self._get_auth_headers())

        if idempotency_key:
            headers.update(self._get_idempotency_headers(idempotency_key))

        return headers

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers. Override in subclasses.

        Returns:
            Dictionary of auth headers
        """
        return {"Authorization": f"Bearer {self.api_key}"}

    def _get_idempotency_headers(self, key: str) -> Dict[str, str]:
        """Get idempotency headers. Override in subclasses.

        Args:
            key: Idempotency key

        Returns:
            Dictionary of idempotency headers
        """
        return {"Idempotency-Key": key}

    def normalize_messages(self, messages: List[ChatMessage]) -> List[Dict[str, Any]]:
        """Convert ChatMessage objects to provider format.

        Args:
            messages: List of ChatMessage objects

        Returns:
            List of provider-formatted message dictionaries
        """
        return [msg.to_dict() for msg in messages]

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation. Override with provider-specific logic.

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        # Rough approximation: ~4 characters per token
        return max(1, len(text) // 4)

    def supports_feature(self, feature: str) -> bool:
        """Check if provider supports a specific feature.

        Args:
            feature: Feature name ('streaming', 'tools', 'vision', etc.)

        Returns:
            True if feature is supported
        """
        # Default implementations - override in subclasses
        supported_features = {
            "streaming": True,
            "tools": False,
            "vision": False,
            "json_mode": False,
            "system_messages": True,
        }
        return supported_features.get(feature, False)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', base_url='{self.base_url}')"


class HTTPMixin:
    """Mixin class providing HTTP client functionality."""

    def __init__(self):
        self._http_client = None

    async def _get_http_client(self):
        """Get or create HTTP client. Lazy initialization."""
        if self._http_client is None:
            try:
                import httpx

                self._http_client = httpx.AsyncClient(
                    timeout=httpx.Timeout(self.timeout_seconds), follow_redirects=True
                )
            except ImportError:
                raise ImportError(
                    "httpx is required for HTTP requests. Install with: pip install httpx"
                )
        return self._http_client

    async def _close_http_client(self):
        """Close HTTP client if it exists."""
        if self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None

    async def _make_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        json_data: Optional[Dict[str, Any]] = None,
        timeout_override: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request with error handling.

        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            json_data: Request body
            timeout_override: Override default timeout

        Returns:
            Response JSON data

        Raises:
            FiberError: On HTTP errors
        """
        client = await self._get_http_client()

        try:
            timeout = timeout_override or self.timeout_seconds
            if method.upper() == "POST":
                coro = client.post(url=url, headers=headers, json=json_data, timeout=timeout)
            else:
                coro = client.request(
                    method=method, url=url, headers=headers, json=json_data, timeout=timeout
                )
            # Enforce request-level timeout regardless of client behavior
            # (e.g., when patched in tests)
            response = await asyncio.wait_for(coro, timeout=timeout)

            # Handle HTTP errors
            if response.status_code >= 400:
                await self._handle_http_error(response)

            # Safely get JSON whether response.json is sync or async
            json_method = getattr(response, "json", None)
            if callable(json_method):
                result = json_method()
                if asyncio.iscoroutine(result):
                    return await result
                return result
            # Fallback: read and parse bytes if no json() available
            content = await response.aread()
            import json as _json

            try:
                return _json.loads(content.decode("utf-8", errors="ignore") or "{}")
            except Exception:
                return {"content": content.decode("utf-8", errors="ignore")}

        except Exception as e:
            await self._handle_request_exception(e)

    async def _make_streaming_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        json_data: Optional[Dict[str, Any]] = None,
        timeout_override: Optional[float] = None,
    ) -> AsyncIterator[bytes]:
        """Make streaming HTTP request.

        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            json_data: Request body
            timeout_override: Override default timeout

        Yields:
            Response chunks as bytes

        Raises:
            FiberError: On HTTP errors
        """
        client = await self._get_http_client()

        try:
            timeout = timeout_override or self.timeout_seconds
            async with client.stream(
                method=method, url=url, headers=headers, json=json_data, timeout=timeout
            ) as response:
                # Handle HTTP errors
                if response.status_code >= 400:
                    # Read the full response for error handling
                    error_content = await response.aread()
                    await self._handle_http_error_with_content(response, error_content)

                async for chunk in response.aiter_bytes(chunk_size=1024):
                    yield chunk

        except Exception as e:
            await self._handle_request_exception(e)

    async def _handle_http_error(self, response) -> None:
        """Handle HTTP error responses.

        Args:
            response: HTTP response object

        Raises:
            FiberError: Appropriate error type based on status code
        """
        content = await response.aread()
        await self._handle_http_error_with_content(response, content)

    async def _handle_http_error_with_content(self, response, content: bytes) -> None:
        """Handle HTTP error with response content.

        Args:
            response: HTTP response object
            content: Response content bytes

        Raises:
            FiberError: Appropriate error type based on status code
        """
        from ..types import (
            FiberAuthError,
            FiberProviderError,
            FiberQuotaError,
            FiberRateLimitError,
            FiberValidationError,
        )

        status_code = response.status_code
        error_text = content.decode("utf-8", errors="ignore")

        # Try to parse JSON error response from provided content without re-reading
        try:
            import json as _json

            _json.loads(error_text) if content else {}
        except Exception:
            pass

        # Map status codes to appropriate exceptions
        if status_code == 401:
            raise FiberAuthError(f"Authentication failed: {error_text}", provider=self.name)
        elif status_code == 403:
            raise FiberAuthError(f"Access forbidden: {error_text}", provider=self.name)
        elif status_code == 400:
            raise FiberValidationError(f"Invalid request: {error_text}", provider=self.name)
        elif status_code == 429:
            raise FiberRateLimitError(f"Rate limit exceeded: {error_text}", provider=self.name)
        elif status_code == 402:
            raise FiberQuotaError(f"Quota exceeded: {error_text}", provider=self.name)
        elif 500 <= status_code < 600:
            raise FiberProviderError(
                f"Server error ({status_code}): {error_text}",
                provider=self.name,
                status_code=status_code,
            )
        else:
            raise FiberProviderError(
                f"HTTP {status_code}: {error_text}", provider=self.name, status_code=status_code
            )

    async def _handle_request_exception(self, exception: Exception) -> None:
        """Handle request exceptions.

        Args:
            exception: The exception that occurred

        Raises:
            FiberError: Appropriate error type
        """
        from ..types import FiberConnectionError, FiberError, FiberProviderError, FiberTimeoutError

        # If it's already a FiberError, preserve it as-is
        if isinstance(exception, FiberError):
            raise exception

        # Map common exceptions to Fiber errors
        is_timeout = (
            isinstance(exception, asyncio.TimeoutError) or "timeout" in str(exception).lower()
        )

        # Check for httpx timeout exceptions
        try:
            import httpx

            if isinstance(exception, httpx.TimeoutException):
                is_timeout = True
        except ImportError:
            pass

        if is_timeout:
            raise FiberTimeoutError(f"Request timed out: {exception}", provider=self.name)
        elif "connection" in str(exception).lower():
            raise FiberConnectionError(f"Connection failed: {exception}", provider=self.name)
        else:
            # Re-raise as generic provider error
            raise FiberProviderError(f"Request failed: {exception}", provider=self.name)


class BaseProvider(Provider, HTTPMixin):
    """Base provider class with HTTP client functionality."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_seconds: float = 30.0,
    ):
        Provider.__init__(self, api_key, base_url, timeout_seconds)
        HTTPMixin.__init__(self)

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._close_http_client()
