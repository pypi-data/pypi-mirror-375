# Model Registry & Routing

The Model Registry maps LLM model identifiers to providers and drives providerless routing. It enables a simple, ergonomic API where you specify only a model (e.g., "gpt-4o-mini"), and the library infers the correct provider (e.g., "openai"). You can customize mappings, set a preference order, and always override the provider per call.

This page covers default mappings, customization, precedence rules, examples, and guidance for testing and best practices.

---

## Goals

- Provide predictable, lightweight routing from model name to provider
- Keep defaults sensible while allowing easy customization
- Support both prefix-based and exact model mappings
- Stay explicit: unknown models should fail fast unless you specify the provider

---

## Responsibilities

- Infer provider from model name using:
  - Exact matches (highest precedence)
  - Prefix matches (e.g., gpt-*, claude-*, gemini-*)
  - Preference order to break ties
- Allow per-call provider override (always wins)
- Expose a small, stable API for mapping and resolution

Out of scope:
- API keys and base URLs (configured on the client, not in the registry)
- Tokenization, pricing, or capabilities (separate modules/registries)

---

## Default Mapping

Built-in defaults (subject to change as ecosystems evolve):

- openai: gpt-*, o*, text-*
- anthropic: claude-*
- gemini: gemini-*

Notes:
- Matching is case-sensitive by default; use consistent case for model strings.
- These defaults are intentionally small; extend or override as needed for your environment.

---

## Provider Override (Call-time)

You can always force a provider per call:

- provider="openai" | "anthropic" | "gemini"

This bypasses the registry for that call and is the highest-precedence signal.

Example:

    text = fiber.sync.ask(
        "Test routing",
        model="gpt-4o-mini",
        provider="openai",  # explicit override
    )

---

## API Surface

ModelRegistry (conceptual interface; names may vary slightly in your build):

- map_prefix(prefix: str, provider: str) -> None
  - Route all models with the given prefix to provider
- map_exact(model: str, provider: str) -> None
  - Route a specific model name to provider
- set_preference_order(order: tuple[str, ...]) -> None
  - Preference list to break ties when multiple providers match
- provider_for_model(model: str) -> str
  - Determine provider using exact > prefix > preference order
  - Raises a clear error for unknown or ambiguous mapping
- default() -> ModelRegistry
  - Construct a registry pre-populated with default mappings

Additional common helpers (if present in your build):
- remove_prefix(prefix: str) -> None
- remove_exact(model: str) -> None
- clear() -> None

---

## Precedence and Resolution

1) Per-call override (provider=...) always wins.
2) Exact mapping (map_exact) has higher precedence than prefix mapping.
3) If multiple prefixes match a model, preference order breaks ties.
4) If resolution is impossible (unknown/ambiguous), a clear error is raised indicating:
   - Which model failed to resolve
   - Any candidates considered
   - Suggestions (add mapping, set preference order, or set provider explicitly)

Examples of tie-breaking:
- If you map prefixes "gpt-" -> "openai" and "gpt-" -> "anthropic" accidentally, the preference order decides.
- If a model exactly matches an entry (e.g., "my-claude"), the exact mapping is used even if a prefix (e.g., "claude-") would also match.

---

## Configuration Lives on the Client

- API keys are configured on the client (Fiber.from_env or constructor)
- Base URLs are on the client (for Azure/OpenRouter-compatible OpenAI endpoints, Vertex AI for Gemini, etc.)
- The registry only decides which provider to use for a model; it does not hold credentials or URLs

---

## Customization Examples

Route custom prefixes:

    from llm_fiber import Fiber

    fiber = Fiber.from_env(default_model="gpt-4o-mini")
    fiber.model_registry.map_prefix("acme-", "openai")

Exact mapping:

    fiber.model_registry.map_exact("my-claude", "anthropic")

Preference order:

    fiber.model_registry.set_preference_order(("anthropic", "openai", "gemini"))

Per-call override (always wins):

    text = fiber.sync.ask(
        "Test routing",
        model="gpt-4o-mini",
        provider="openai",
    )

Swap the entire registry:

    from llm_fiber import ModelRegistry

    reg = ModelRegistry.default()
    reg.map_prefix("research-", "gemini")
    fiber.model_registry = reg

---

## Edge Cases

- Unknown model: If a model matches neither an exact nor a prefix mapping, resolution fails with a clear error. Provide an explicit provider or add a mapping.
- Ambiguous model: If multiple mappings match and preference order cannot break the tie (e.g., equal precedence or missing preference), resolution fails with a clear error. Set a preference order or supply a per-call provider.
- Case sensitivity: Treat model names as case-sensitive to avoid accidental collisions or mismatches.

Conservative behavior: Fail fast on unknown/ambiguous mappings to prevent silent misrouting.

---

## Testing

Recommended checks:
- Exact-before-prefix precedence
- Preference order tie-breaking
- Per-call override enforcement
- Unknown model error path with actionable messaging
- Registry mutations (add/remove/clear) and their effects

Example (pseudo-test):

    reg = ModelRegistry.default()
    reg.map_exact("my-claude", "anthropic")
    assert reg.provider_for_model("my-claude") == "anthropic"

    reg.map_prefix("acme-", "openai")
    assert reg.provider_for_model("acme-1") == "openai"

    reg.set_preference_order(("gemini", "openai", "anthropic"))
    reg.map_prefix("x-", "openai")
    reg.map_prefix("x-", "gemini")  # tie; preference picks "gemini"
    assert reg.provider_for_model("x-foo") == "gemini"

---

## Best Practices

- Prefer exact mappings for critical or proprietary model IDs
- Keep prefix mappings minimal and intentional; wide prefixes can match more than intended
- Set a clear preference order aligned with your organization’s cost/latency/reliability policy
- Centralize registry customization during app startup; avoid dynamic mutations during hot paths
- Always allow per-call override for power users and special cases

---

## Known Limitations (MVP)

- No fuzzy matching: resolution is strictly exact or prefix-based
- The registry does not hold credentials or URLs; those must be configured on the client
- Capabilities/pricing are separate concerns (see related feature pages)

---

## See Also

- Transport/Core API: ./transport.md
- Ergonomics (DX): ./ergonomics.md
- Supported Providers: ./providers.md
- Configuration: ./configuration.md
- Capabilities & Pricing: ./capabilities-and-pricing.md
