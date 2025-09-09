# Capabilities & Pricing

This page describes how `llm-fiber` surfaces provider and model capabilities, and how it estimates cost using a pluggable pricing registry. It covers the capability taxonomy, the capabilities query API, the pricing data model, estimation logic, overrides and TTL refresh, observability, limitations, and best practices.

The goals are:
- Provide a predictable way to answer “What can this model do?” (tools, JSON mode, vision, streaming, etc.)
- Offer a best-effort cost estimate per call using known token prices
- Keep the core light; make data sources and tokenizers pluggable
- Fail soft when data is unknown; never block requests solely due to missing pricing metadata

---

## Overview

- Capability discovery: return a stable set of support flags and limits (e.g., tool calls, JSON mode, max context).
- Pricing knowledge: return input/output prices per 1K tokens when known (USD), optionally with metadata like region or source.
- Estimation: when usage is available (tokens in/out), compute `estimated_cost_usd` on `Usage`.
- Pluggability:
  - Tokenizers (e.g., adapter to `tiktoken`) improve preflight token estimates.
  - Pricing registry can be updated/refreshed or overridden per environment.
- Safety:
  - When anything is unknown, estimation is omitted rather than guessed.
  - Budgets can still protect calls using conservative strategies (see Retries & Budgets).

---

## Capability taxonomy

Typical capability fields per model (subject to growth; names may vary slightly in your build):

- Core modes
  - `streaming`: bool — supports server-sent or chunked streaming
  - `json_mode`: bool — supports JSON-mode or equivalent constrained decoding
  - `tool_calls`: bool — supports function/tool calling
  - `vision`: bool — accepts image inputs or multimodal prompts
  - `system_prompt`: bool — supports a distinct “system” role or instruction channel
  - `response_formatting`: set[str] — e.g., {"text", "json"} (if the provider exposes them explicitly)
- Limits and shapes
  - `context_window_tokens`: int — max prompt + completion tokens
  - `max_output_tokens`: int | None — maximum tokens the model can emit in one call
  - `supports_seed`: bool — accepts a seed for deterministic sampling
  - `supports_tool_streaming`: bool — streams tool call deltas (if available)
- Quirks and flags
  - `requires_model_version`: bool — some providers require explicit versioning
  - `beta`: bool — experimental/preview model indicator
- Pricing (see below)
  - `pricing`: optional bundle with per-1K token prices for input/output (USD), and source metadata

Notes
- Capabilities are normalized for portability; a field’s meaning should remain stable across providers.
- Unknown fields are omitted or set to None rather than guessed.

---

## Querying capabilities

Use the capability query to learn what a model supports and, when available, its pricing.

    from llm_fiber import Fiber

    fiber = Fiber.from_env(default_model="gpt-4o-mini")

    caps = fiber.capabilities("gpt-4o-mini")  # or omit arg to use default_model

    # Example fields (names are representative):
    # caps.streaming == True
    # caps.json_mode == True
    # caps.tool_calls == True
    # caps.context_window_tokens == 128000
    # caps.pricing.input_per_1k_usd, caps.pricing.output_per_1k_usd

Notes
- Provider is inferred by the model registry unless explicitly given.
- If the model is unknown, the call returns a clear error or a minimal structure with `pricing=None` and conservative defaults, depending on configuration.
- Capabilities can be cached in-process to avoid repeated provider metadata lookups.

---

## Pricing data model

Per model (and sometimes per region), pricing is commonly expressed as USD per 1K tokens:

- `input_per_1k_usd`: float | None
- `output_per_1k_usd`: float | None
- Optional metadata:
  - `currency`: "USD" (future-friendly; conversions currently out of scope)
  - `source`: str (e.g., "provider_table_2025-04-01")
  - `region`: str | None
  - `updated_at`: datetime | None
  - `ttl_s`: int | None (time-to-live for the entry)

Notes
- Some providers publish multiple price tiers (batch, structured output, tool usage, image inputs); the initial registry focuses on “text input” and “text output” per 1K tokens.
- Image pricing, function/tool-call surcharges, and special modes can be added over time as additional fields.

---

## Cost estimation

When token usage is known (from provider or via tokenizer), the library sets `Usage.estimated_cost_usd`:

    estimated_cost_usd =
        (tokens_in / 1000.0) * input_per_1k_usd
      + (tokens_out / 1000.0) * output_per_1k_usd

Behavior:
- If either price is missing, estimation uses only the available side; if both are missing, the estimate is omitted.
- No hidden rounding is applied; values reflect a straightforward multiplication. Providers may round differently for billing; treat this as an estimate.
- For streaming, estimation is computed at end-of-stream if usage is available. If a stream is cancelled mid-call, final usage may be unavailable and no cost estimate is emitted.

Example (conceptual):

    res = fiber.sync.chat(messages=["Summarize fiber optics."])
    print(res.usage)  # tokens_in, tokens_out, tokens_total, estimated_cost_usd (if pricing known)

---

## Preflight budget checks

Budgets (see Retries & Budgets) can be enforced with help from capabilities and pricing:

- `token_budget`:
  - If a tokenizer is available and the model’s `max_output_tokens` is known, the library can estimate feasibility before sending the request.
- `cost_ceiling_usd`:
  - With known `input_per_1k_usd` and `output_per_1k_usd`, the library can conservatively estimate upper cost bounds (prompt + expected completion) and fail early if the ceiling would be exceeded.

When precision is limited:
- The library errs on the side of safety (conservative estimates).
- If no tokenizer/pricing data is available, preflight checks may not be performed or may be approximate.

---

## Data sourcing, refresh, and overrides

Pricing registry:
- Source: initially a static table bundled with the library or an optional data module; can be refreshed (TTL-based) from provider docs or your first-party source of truth.
- Refresh: a background TTL-triggered fetch, a lazy reload, or an explicit `refresh()` method (implementation-dependent).
- Overrides: you can inject updates at runtime to reflect negotiated discounts, gateway markups, or private model pricing.

    from llm_fiber import Fiber, PricingRegistry

    fiber = Fiber.from_env(default_model="gpt-4o-mini")

    # Swap entire registry
    custom = PricingRegistry.default()
    custom.set("gpt-4o-mini", input_per_1k_usd=0.005, output_per_1k_usd=0.015, source="internal-2025Q2")
    fiber.pricing_registry = custom

    # Or override a single model on the fly
    fiber.pricing_registry.set("claude-3-haiku-20240307", input_per_1k_usd=0.001, output_per_1k_usd=0.002, source="promo")

Notes
- The registry API is minimal and stable; details may vary slightly in your build.
- Always prefer explicit, versioned `source` labels in overrides for auditability.

---

## Provider specifics and caveats

- OpenAI
  - Prices are typically published per 1K tokens; some models have different JSON/tool pricing or structured output costs.
  - Azure/OpenAI-compatible gateways may apply different pricing; use overrides.
- Anthropic
  - Similar per-1K tokens model; different context window and output caps by family.
  - Tool/function calling costs may vary by model and are not always itemized.
- Google Gemini
  - Public Generative Language API pricing differs from Vertex AI; ensure you target the correct endpoint and pricing table.
  - Multimodal/image inputs may have separate pricing not covered by the base text table.

For all providers:
- Streamed response usage may be delayed or absent; `estimated_cost_usd` may not appear if final usage metrics are missing.
- Providers occasionally change prices; rely on TTL refresh or CI to keep tables updated.

---

## Examples

Query capabilities and print pricing:

    fiber = Fiber.from_env(default_model="gpt-4o-mini")
    caps = fiber.capabilities("gpt-4o-mini")

    if caps.pricing:
        print("Input $/1K:", caps.pricing.input_per_1k_usd)
        print("Output $/1K:", caps.pricing.output_per_1k_usd)
    else:
        print("Pricing unknown for this model.")

Guard cost with a ceiling:

    res = fiber.sync.chat(
        messages=["Three bullet points about glass fiber."],
        cost_ceiling_usd=0.002,  # refuse if conservative estimate exceeds this
    )
    print(res.text, res.usage.estimated_cost_usd)

Conservative token budget:

    res = fiber.sync.chat(
        messages=[("system", "Be terse."), "Define backpressure in two sentences."],
        token_budget=300,
    )
    print(res.text, res.usage)

---

## Observability

- `estimated_cost_usd` is included on `Usage` and may be emitted as a metric (e.g., gauge per call).
- Consider recording:
  - `request_count{provider,model,ok}`
  - `tokens_in/out/total`
  - `estimated_cost_usd`
  - `error_count{code}`, `retry_count{reason}`
- Bind context fields (e.g., `run_id`, `tenant_id`) to correlate costs with tenants/features.

---

## Limitations (MVP)

- Pricing covers only text input/output per 1K tokens; tool/image/mode-specific surcharges are not itemized.
- Some providers don’t emit accurate token usage for streamed responses; estimates may be missing.
- Tokenizer precision depends on the availability and correctness of model-specific tokenization.
- Vertex AI Gemini pricing differs from public Generative Language API; treat them separately via base URL and pricing overrides.

---

## Best practices

- Use `capabilities(model)` at startup to validate supported features and set guardrails (e.g., max output).
- Keep the pricing registry fresh via TTL or CI updates; include a `source` label for auditability.
- Enforce `token_budget` and `cost_ceiling_usd` in production to protect latency and spend.
- Prefer exact model identifiers in overrides; avoid wildcard overrides unless you control the model namespace.
- Treat `estimated_cost_usd` as an estimate; reconcile with provider invoices for authoritative accounting.

---

## See also

- Transport/Core API: ./transport.md
- Ergonomics (DX): ./ergonomics.md
- Streaming: ./streaming.md
- Prompt API: ./prompt-api.md
- Model Registry & Routing: ./model-registry.md
- Observability: ./observability.md
- Configuration: ./configuration.md
- Retries & Budgets: ./retries-and-budgets.md
