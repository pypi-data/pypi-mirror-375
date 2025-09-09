# Supported Providers

llm-fiber ships with first-class support for three LLM providers out of the box and normalizes their request/response/streaming shapes into a consistent interface.

- OpenAI (and Azure OpenAI/OpenAI-compatible endpoints)
- Anthropic
- Google Gemini

This page summarizes provider-specific details, configuration, and caveats, and how they fit into the provider-agnostic Fiber API.

---

## Quick recap: Providerless by default

- The provider is inferred from the `model` via a small, configurable Model Registry.
- You can override the provider per call with `provider="openai" | "anthropic" | "gemini"`.
- API keys and base URLs live on the client (constructor or `from_env()`), not in the registry.

See also: Model Registry & Routing.

---

## OpenAI

- Base URL
  - Default: https://api.openai.com/v1
  - Override for Azure/OpenAI-compatible gateways (e.g., OpenRouter): set a custom base URL on the client.
- Auth
  - Header: `Authorization: Bearer OPENAI_API_KEY`
  - Environment: `OPENAI_API_KEY`
- Models
  - Any chat-completions-capable model (e.g., `gpt-*`, `o*`, `text-*`) depending on your account access.
- Notes
  - Messages and streaming are normalized into Fiber’s common shapes.
  - Tool/function calling normalization is planned post-MVP; expect minimal, provider-agnostic placeholders initially.
  - Idempotency keys are passed through when supported by the underlying API.

Configuration sketch

    # Construct with a custom base URL (e.g., Azure/OpenAI-compatible gateway)
    # Exact argument names may vary in your build; conceptually:
    # Fiber(default_model=..., api_keys=..., base_urls={"openai": "https://.../v1"})
    #
    # Or rely on Fiber.from_env() and set environment variables accordingly.

---

## Anthropic

- Base URL
  - Default: https://api.anthropic.com/v1
- Auth
  - Header: `x-api-key: ANTHROPIC_API_KEY`
  - Environment: `ANTHROPIC_API_KEY`
- Models
  - Claude 3 family and newer chat-capable models.
- Notes
  - Messages and streaming are normalized into Fiber’s common shapes.
  - Tool/function calling normalization is planned post-MVP.
  - Typed exceptions include rate limit, auth, timeout, and API errors with provider/model context.

---

## Google Gemini

- Base URL
  - Default: https://generativelanguage.googleapis.com
  - Vertex AI compatibility is on the roadmap (separate auth/base_url).
- Auth
  - API key via query param or header (transport-dependent):
    - `GEMINI_API_KEY` (environment)
- Models
  - Gemini 1.5 family and later.
- Notes
  - Messages and streaming are normalized into Fiber’s common shapes.
  - Some endpoints may differ between public Generative Language API and Vertex AI; see roadmap note.
  - Pricing/usage may differ by endpoint; usage accuracy for streamed responses can vary.

---

## Environment variables

Set only those you need:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY`

Use `Fiber.from_env(...)` to load keys and base URLs. You can also pass keys/URLs explicitly into the constructor for tests or services where explicit configuration is preferred.

---

## Base URL overrides and compatibility

- OpenAI-compatible APIs
  - Azure OpenAI/OpenRouter/Ollama-compatible endpoints can be targeted by setting the OpenAI base URL on the client.
  - Keep the provider as `"openai"` for routing; use the gateway’s models or map them in the Model Registry.
- Gemini on Vertex AI
  - Planned compatibility requires different auth/base URL. Track the roadmap for availability.
- Per-provider base URLs
  - Configure `base_urls` on the client (constructor or `from_env()`) with keys matching provider names.

---

## Streaming behavior

- All built-in providers support streaming; Fiber normalizes incremental output as `StreamEvent(type="chunk", delta=...)` with final `usage` when available.
- `ttfb_ms` and end-to-end `latency_ms` are recorded in metrics.
- If usage is not reported for streamed responses by a provider, the `usage` event may be absent or partial.

See also: Streaming.

---

## Tool/function calling

- Normalization is planned post-MVP.
- During MVP, tool/function calling signals may be surfaced via a `tool_call` event with a minimal, provider-agnostic shape that can evolve over time.
- Prefer guarding application logic from provider-specific shapes; keep a translation layer if you need richer semantics.

---

## Idempotency & retries

- Pass `idempotency_key` on calls; Fiber will forward it when the provider supports it.
- Retries use capped, jittered exponential backoff with classification by HTTP status and provider error codes.
- Mid-stream automatic retries are not attempted to avoid duplicating partial outputs.

See also: Retries & Budgets.

---

## Pricing and usage

- Fiber can estimate costs when pricing is known for the target model; estimates appear on `usage.cost_estimate`.
- Pricing tables are pluggable and intended to refresh with TTL; exact mechanics may be behind an optional component/extra.
- Token counting accuracy depends on tokenizer availability/integration for the target model (e.g., `tiktoken`).

See also: Capabilities & Pricing.

---

## Errors and observability

- Typed exceptions:
  - `FiberTimeout`, `FiberRateLimited`, `FiberAuthError`, `FiberAPIError`, `FiberParsingError`
  - All derive from `FiberError` and include provider/model/attempt metadata.
- Metrics (counters/histograms by provider/model):
  - `request_count`, `error_count`, `retry_count`, `latency_ms`, `ttfb_ms`, `tokens_*`, `estimated_cost_usd`
- Logging:
  - Stdlib `logging` by default; optional `structlog` integration.
  - Bind fields (e.g., `run_id`, `tenant_id`) via `fiber.bind(...)` for correlation.

---

## Model names and routing

- Defaults:
  - openai: `gpt-*`, `o*`, `text-*`
  - anthropic: `claude-*`
  - gemini: `gemini-*`
- Customize:
  - Add exact or prefix mappings; set a preference order for tie-breaking.
  - Per-call `provider=...` always wins.
- Unknown/ambiguous mappings:
  - Fail fast with a clear error; provide an explicit `provider` or add a mapping.

See also: Model Registry & Routing.

---

## Best practices

- Keep provider configuration (keys and base URLs) on the client; do not put secrets into the registry.
- Use the Model Registry to codify your organization’s routing rules; prefer exact mappings for critical/proprietary model IDs.
- Bind context (run/request/tenant IDs) for strong observability across providers.
- Enforce budgets (tokens/cost) in production to protect latency and spend.
- Prefer normalized result fields (`text`, `usage`, `finish_reason`) for portability; only use `raw` for provider-specific edge cases.

---

## Known limitations (MVP)

- Tool/function calling normalization is limited; richer normalization is planned post-MVP.
- Some providers may not report accurate token usage for streamed responses.
- Vertex AI compatibility (Gemini) is on the roadmap.
- Capability/pricing registries may start minimal and evolve over time.

---

## See also

- Transport/Core API: ./transport.md
- Streaming: ./streaming.md
- Ergonomics (DX): ./ergonomics.md
- Model Registry & Routing: ./model-registry.md
- Observability: ./observability.md
- Configuration: ./configuration.md
- Retries & Budgets: ./retries-and-budgets.md
- Capabilities & Pricing: ./capabilities-and-pricing.md
