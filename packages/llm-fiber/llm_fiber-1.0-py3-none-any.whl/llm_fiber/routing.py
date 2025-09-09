"""Model registry and routing system for llm-fiber."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .types import FiberValidationError


@dataclass
class ProviderConfig:
    """Configuration for a provider."""

    name: str
    api_key_env: str
    base_url: Optional[str] = None
    default_models: List[str] = field(default_factory=list)
    supports_streaming: bool = True
    supports_tools: bool = True
    supports_vision: bool = False


@dataclass
class ModelInfo:
    """Information about a specific model."""

    name: str
    provider: str
    context_length: Optional[int] = None
    supports_tools: bool = True
    supports_vision: bool = False
    input_cost_per_token: Optional[float] = None  # USD per token
    output_cost_per_token: Optional[float] = None  # USD per token


class ModelRegistry:
    """Registry for mapping model names to providers with routing logic."""

    def __init__(self):
        self._providers: Dict[str, ProviderConfig] = {}
        self._models: Dict[str, ModelInfo] = {}
        self._prefix_mappings: Dict[str, str] = {}  # prefix -> provider
        self._exact_mappings: Dict[str, str] = {}  # model -> provider
        self._default_preference: List[str] = ["openai", "anthropic", "gemini"]

        # Initialize default providers and models
        self._initialize_defaults()

    def _initialize_defaults(self) -> None:
        """Initialize default provider configurations and model mappings."""

        # Register default providers
        self.register_provider(
            ProviderConfig(
                name="openai",
                api_key_env="OPENAI_API_KEY",
                base_url="https://api.openai.com/v1",
                default_models=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
                supports_streaming=True,
                supports_tools=True,
                supports_vision=True,
            )
        )

        self.register_provider(
            ProviderConfig(
                name="anthropic",
                api_key_env="ANTHROPIC_API_KEY",
                base_url="https://api.anthropic.com",
                default_models=["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
                supports_streaming=True,
                supports_tools=True,
                supports_vision=True,
            )
        )

        self.register_provider(
            ProviderConfig(
                name="gemini",
                api_key_env="GEMINI_API_KEY",
                base_url="https://generativelanguage.googleapis.com/v1beta",
                default_models=["gemini-1.5-pro", "gemini-1.5-flash"],
                supports_streaming=True,
                supports_tools=True,
                supports_vision=True,
            )
        )

        # Register common OpenAI models
        openai_models = [
            ModelInfo("gpt-4o", "openai", 128000, True, True, 0.0025 / 1000, 0.01 / 1000),
            ModelInfo("gpt-4o-mini", "openai", 128000, True, True, 0.00015 / 1000, 0.0006 / 1000),
            ModelInfo("gpt-4-turbo", "openai", 128000, True, True, 0.01 / 1000, 0.03 / 1000),
            ModelInfo("gpt-4", "openai", 8192, True, False, 0.03 / 1000, 0.06 / 1000),
            ModelInfo("gpt-3.5-turbo", "openai", 16385, True, False, 0.0005 / 1000, 0.0015 / 1000),
        ]

        # Register Anthropic models
        anthropic_models = [
            ModelInfo(
                "claude-3-5-sonnet-20241022",
                "anthropic",
                200000,
                True,
                True,
                0.003 / 1000,
                0.015 / 1000,
            ),
            ModelInfo(
                "claude-3-opus-20240229",
                "anthropic",
                200000,
                True,
                True,
                0.015 / 1000,
                0.075 / 1000,
            ),
            ModelInfo(
                "claude-3-sonnet-20240229",
                "anthropic",
                200000,
                True,
                True,
                0.003 / 1000,
                0.015 / 1000,
            ),
            ModelInfo(
                "claude-3-haiku-20240307",
                "anthropic",
                200000,
                True,
                True,
                0.00025 / 1000,
                0.00125 / 1000,
            ),
        ]

        # Register Gemini models
        gemini_models = [
            ModelInfo(
                "gemini-1.5-pro", "gemini", 1000000, True, True, 0.00125 / 1000, 0.005 / 1000
            ),
            ModelInfo(
                "gemini-1.5-flash", "gemini", 1000000, True, True, 0.000075 / 1000, 0.0003 / 1000
            ),
            ModelInfo("gemini-pro", "gemini", 30720, False, False, 0.0005 / 1000, 0.0015 / 1000),
        ]

        # Register all models
        for model in openai_models + anthropic_models + gemini_models:
            self.register_model(model)

        # Set up prefix mappings for common patterns
        self.add_prefix_mapping("gpt-", "openai")
        self.add_prefix_mapping("claude-", "anthropic")
        self.add_prefix_mapping("gemini-", "gemini")

        # Set up some exact mappings for aliases
        self.add_exact_mapping("gpt-4", "openai")
        self.add_exact_mapping("claude-3-sonnet", "anthropic")
        self.add_exact_mapping("gemini-pro", "gemini")

    def register_provider(self, config: ProviderConfig) -> None:
        """Register a new provider configuration."""
        self._providers[config.name] = config

    def register_model(self, model_info: ModelInfo) -> None:
        """Register a new model."""
        self._models[model_info.name] = model_info

    def add_prefix_mapping(self, prefix: str, provider: str) -> None:
        """Add a model prefix to provider mapping.

        Args:
            prefix: Model name prefix (e.g., "gpt-")
            provider: Provider name (e.g., "openai")
        """
        if provider not in self._providers:
            raise FiberValidationError(f"Unknown provider: {provider}")
        self._prefix_mappings[prefix] = provider

    def add_exact_mapping(self, model_name: str, provider: str) -> None:
        """Add an exact model name to provider mapping.

        Args:
            model_name: Exact model name
            provider: Provider name
        """
        if provider not in self._providers:
            raise FiberValidationError(f"Unknown provider: {provider}")
        self._exact_mappings[model_name] = provider

    def set_default_preference(self, providers: List[str]) -> None:
        """Set the default provider preference order.

        Args:
            providers: List of provider names in preference order
        """
        for provider in providers:
            if provider not in self._providers:
                raise FiberValidationError(f"Unknown provider: {provider}")
        self._default_preference = providers.copy()

    def resolve_provider(self, model: str, provider_override: Optional[str] = None) -> str:
        """Resolve which provider should handle a given model.

        Args:
            model: Model name to resolve
            provider_override: Optional explicit provider override

        Returns:
            Provider name

        Raises:
            FiberValidationError: If no suitable provider can be found
        """
        # 1. Check explicit provider override
        if provider_override:
            if provider_override not in self._providers:
                raise FiberValidationError(f"Unknown provider: {provider_override}")
            return provider_override

        # 2. Check exact mappings first
        if model in self._exact_mappings:
            return self._exact_mappings[model]

        # 3. Check if model is registered with specific provider
        if model in self._models:
            return self._models[model].provider

        # 4. Check prefix mappings
        for prefix, provider in self._prefix_mappings.items():
            if model.startswith(prefix):
                return provider

        # 5. Try to infer from model name patterns
        model_lower = model.lower()

        # Common OpenAI patterns
        if any(pattern in model_lower for pattern in ["gpt", "openai", "o1"]):
            return "openai"

        # Common Anthropic patterns
        if any(pattern in model_lower for pattern in ["claude", "anthropic"]):
            return "anthropic"

        # Common Google patterns
        if any(pattern in model_lower for pattern in ["gemini", "bard", "palm", "google"]):
            return "gemini"

        # 6. Fall back to first available provider in preference order
        for provider in self._default_preference:
            if provider in self._providers:
                return provider

        raise FiberValidationError(f"Cannot determine provider for model: {model}")

    def get_model_info(self, model: str) -> Optional[ModelInfo]:
        """Get information about a model if available.

        Args:
            model: Model name

        Returns:
            ModelInfo if available, None otherwise
        """
        return self._models.get(model)

    def get_provider_config(self, provider: str) -> Optional[ProviderConfig]:
        """Get configuration for a provider.

        Args:
            provider: Provider name

        Returns:
            ProviderConfig if available, None otherwise
        """
        return self._providers.get(provider)

    def list_providers(self) -> List[str]:
        """Get list of registered provider names."""
        return list(self._providers.keys())

    def list_models(self, provider: Optional[str] = None) -> List[str]:
        """Get list of registered model names.

        Args:
            provider: Optional provider filter

        Returns:
            List of model names
        """
        if provider is None:
            return list(self._models.keys())

        return [name for name, info in self._models.items() if info.provider == provider]

    def estimate_cost(
        self, model: str, prompt_tokens: int, completion_tokens: int
    ) -> Optional[float]:
        """Estimate cost for a model and token usage.

        Args:
            model: Model name
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens

        Returns:
            Estimated cost in USD, or None if pricing unknown
        """
        model_info = self.get_model_info(model)
        if not model_info:
            return None

        cost = 0.0
        if model_info.input_cost_per_token:
            cost += prompt_tokens * model_info.input_cost_per_token
        if model_info.output_cost_per_token:
            cost += completion_tokens * model_info.output_cost_per_token

        return cost if cost > 0 else None

    def validate_model_capabilities(
        self, model: str, requires_tools: bool = False, requires_vision: bool = False
    ) -> bool:
        """Validate that a model supports required capabilities.

        Args:
            model: Model name
            requires_tools: Whether tools/function calling is required
            requires_vision: Whether vision capabilities are required

        Returns:
            True if model supports all required capabilities
        """
        model_info = self.get_model_info(model)
        if not model_info:
            # If we don't have model info, assume it supports basic capabilities
            return not requires_vision  # Most models don't support vision yet

        if requires_tools and not model_info.supports_tools:
            return False
        if requires_vision and not model_info.supports_vision:
            return False

        return True

    def get_routing_diagnostics(
        self, model: str, provider_override: Optional[str] = None
    ) -> Dict[str, any]:
        """Get diagnostic information about how a model would be routed.

        Args:
            model: Model name
            provider_override: Optional provider override

        Returns:
            Dictionary with routing diagnostics
        """
        diagnostics = {
            "model": model,
            "provider_override": provider_override,
            "resolved_provider": None,
            "resolution_method": None,
            "model_registered": model in self._models,
            "exact_mapping": self._exact_mappings.get(model),
            "matching_prefixes": [p for p in self._prefix_mappings.keys() if model.startswith(p)],
            "inferred_patterns": [],
            "available_providers": self.list_providers(),
            "default_preference": self._default_preference,
        }

        try:
            resolved = self.resolve_provider(model, provider_override)
            diagnostics["resolved_provider"] = resolved

            # Determine resolution method
            if provider_override:
                diagnostics["resolution_method"] = "explicit_override"
            elif model in self._exact_mappings:
                diagnostics["resolution_method"] = "exact_mapping"
            elif model in self._models:
                diagnostics["resolution_method"] = "registered_model"
            elif any(model.startswith(p) for p in self._prefix_mappings.keys()):
                diagnostics["resolution_method"] = "prefix_matching"
            else:
                diagnostics["resolution_method"] = "pattern_inference_or_fallback"

        except FiberValidationError as e:
            diagnostics["error"] = str(e)
            diagnostics["resolution_method"] = "failed"

        # Check for inferred patterns
        model_lower = model.lower()
        if any(pattern in model_lower for pattern in ["gpt", "openai", "o1"]):
            diagnostics["inferred_patterns"].append("openai")
        if any(pattern in model_lower for pattern in ["claude", "anthropic"]):
            diagnostics["inferred_patterns"].append("anthropic")
        if any(pattern in model_lower for pattern in ["gemini", "bard", "palm", "google"]):
            diagnostics["inferred_patterns"].append("gemini")

        return diagnostics


# Global registry instance
default_registry = ModelRegistry()


def get_registry() -> ModelRegistry:
    """Get the default model registry instance."""
    return default_registry
