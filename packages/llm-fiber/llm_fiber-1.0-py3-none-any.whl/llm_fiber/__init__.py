"""llm-fiber: A thin, fast, observable Python client for LLMs.

Async-first with wire‑speed streaming, consistent ergonomics across providers,
and built-in observability.
"""

from .batch import (
    BatchConfig,
    BatchProcessor,
    BatchRequest,
    BatchResult,
    BatchStrategy,
    BatchSummary,
    create_batch_from_conversations,
    create_batch_from_prompts,
    create_batch_request,
)
from .budgets import (
    Budget,
    BudgetError,
    BudgetExceededError,
    BudgetManager,
    BudgetPeriod,
    BudgetType,
    BudgetWarningError,
    create_cost_budget,
    create_request_budget,
    create_token_budget,
)

# v0.2 features
from .caching import CacheAdapter, CachePolicy, NoOpCacheAdapter
from .caching.memory import MemoryCacheAdapter
from .fiber import BoundFiber, Fiber
from .observability.logging import FiberLogger
from .observability.metrics import FiberMetrics, InMemoryMetrics

# Provider adapters (optional - can be imported directly if needed)
from .providers import AnthropicAdapter, GeminiAdapter, OpenAIAdapter
from .retry import RetryPolicy
from .routing import ModelRegistry, default_registry
from .timeouts import Timeouts
from .types import (
    ChatMessage,
    ChatResult,
    FiberAuthError,
    FiberConnectionError,
    FiberError,
    FiberParsingError,
    FiberProviderError,
    FiberQuotaError,
    FiberRateLimitError,
    FiberTimeoutError,
    FiberValidationError,
    MessageInput,
    MessagesInput,
    NormalizedToolCall,
    StreamEvent,
    StreamEventType,
    Usage,
    create_tool_response_message,
    extract_tool_calls_from_stream_events,
    normalize_message,
    normalize_messages,
    normalize_tool_call,
    validate_tool_call_format,
)

# Version
__version__ = "1.0"

# Main exports
__all__ = [
    # Core client
    "Fiber",
    "BoundFiber",
    # Types and data structures
    "ChatMessage",
    "ChatResult",
    "StreamEvent",
    "StreamEventType",
    "Usage",
    "MessageInput",
    "MessagesInput",
    # Exceptions
    "FiberError",
    "FiberAuthError",
    "FiberConnectionError",
    "FiberParsingError",
    "FiberProviderError",
    "FiberQuotaError",
    "FiberRateLimitError",
    "FiberTimeoutError",
    "FiberValidationError",
    # Message utilities
    "normalize_message",
    "normalize_messages",
    # Tool call utilities
    "NormalizedToolCall",
    "normalize_tool_call",
    "validate_tool_call_format",
    "create_tool_response_message",
    "extract_tool_calls_from_stream_events",
    # Configuration
    "Timeouts",
    "RetryPolicy",
    "ModelRegistry",
    "default_registry",
    # Observability
    "FiberMetrics",
    "InMemoryMetrics",
    "FiberLogger",
    # v0.2 Caching
    "CacheAdapter",
    "CachePolicy",
    "NoOpCacheAdapter",
    "MemoryCacheAdapter",
    # v0.2 Batch operations
    "BatchProcessor",
    "BatchRequest",
    "BatchResult",
    "BatchSummary",
    "BatchConfig",
    "BatchStrategy",
    "create_batch_request",
    "create_batch_from_prompts",
    "create_batch_from_conversations",
    # v0.2 Budget/cost controls
    "BudgetManager",
    "Budget",
    "BudgetType",
    "BudgetPeriod",
    "BudgetError",
    "BudgetExceededError",
    "BudgetWarningError",
    "create_cost_budget",
    "create_token_budget",
    "create_request_budget",
    # Provider adapters
    "OpenAIAdapter",
    "AnthropicAdapter",
    "GeminiAdapter",
    # Version
    "__version__",
]
