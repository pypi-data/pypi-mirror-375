# Configuration

This page describes how to configure llm-fiber for different environments and use cases. It covers environment variables, explicit construction, defaults and overrides, timeouts/retries, observability setup, and provider-specific base URL considerations.

The goal is to keep configuration explicit and predictable, while making it easy to bootstrap from environment variables in applications.

---

## Goals

- Make configuration obvious and explicit (constructor-first)
- Keep environment-driven setup ergonomic (`Fiber.from_env()`)
- Support per-client defaults and per-call overrides
- Provide clear precedence rules so behavior is predictable
- Keep secrets out of logs; support redaction by default

---

## Configuration Surface (at a glance)

Client construction
- `Fiber(default_model=None, api_keys=None, base_urls=None, timeout=Timeouts(total=30), metrics=None, logger=None, ...)`
- `Fiber.from_env(default_model=None, prefer=("openai","anthropic","gemini"))`

Common knobs
- Defaults: `default_model`, `default_temperature`, `default_max_tokens`
- Provider selection: inferred from model; optional per-call `provider="openai" | "anthropic" | "gemini"`
- API keys: attach via constructor or loaded via environment variables
- Base URLs: override provider endpoints per environment (e.g., Azure/OpenAI-compatible gateways, or Gemini variants)
- Timeouts: client-wide `Timeouts(connect, read, total)` and per-call `timeout_s`
- Retries: built-in capped, jittered exponential backoff; user hook to refine classification
- Observability: pass a `logger` and a metrics sink; enable optional exporters via extras
- Context binding: `with fiber.bind(...):` to flow tags into logs/metrics/traces

---

## Environment variables

Set only the keys you need:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY`

Then call:
    from llm_fiber import Fiber
    fiber = Fiber.from_env(default_model="gpt-4o-mini")

Notes
- Environment-based configuration is best for applications or CLIs.
- For libraries or tests, prefer explicit constructor arguments for clarity and control.

Base URLs
- Base URL overrides are configured on the client (constructor or `from_env()` if supported in your environment).
- The exact environment variable names for base URLs are implementation-specific; if supported in your setup, configure them consistently (for example, a single source-of-truth config loaded before calling `Fiber.from_env()`).
- If in doubt, pass base URLs explicitly via the constructor (see below).

---

## Explicit construction

You can construct the client with explicit keys and base URLs (recommended for tests and services with nonstandard endpoints).

    from llm_fiber import Fiber, Timeouts

    fiber = Fiber(
        default_model="gpt-4o-mini",
        api_keys={
            "openai": "...",
            "anthropic": "...",
            "gemini": "...",
        },
        base_urls={
            # Example: point OpenAI to an Azure/OpenAI-compatible gateway
            "openai": "https://example-gateway/v1",
            # Keep others default by omitting or leaving None
        },
        timeout=Timeouts(connect=5, read=30, total=30),
        metrics=None,   # attach a metrics sink if desired
        logger=None,    # pass an app logger (stdlib or structlog) if desired
    )

    # Use per-call overrides as needed:
    res = fiber.sync.chat(messages=["Hello"], provider="openai")
    print(res.text)

---

## Defaults and override precedence

Configuration is applied in this order (highest precedence first):
1) Per-call arguments (e.g., `provider`, `timeout_s`, `temperature`)
2) Prompt defaults (when calling through the Prompt API)
3) Client defaults (`default_model`, `default_temperature`, `default_max_tokens`, `timeout`)
4) Environment-derived values from `Fiber.from_env(...)` (API keys, base URLs)
5) Library defaults (e.g., `Timeouts(total=30)`)

Provider choice
- Per-call `provider` always wins.
- Otherwise, the `ModelRegistry` infers a provider from `model`.
- If no `model` is provided, `default_model` is used (and then inferred).

---

## Timeouts

Use `Timeouts` for clarity and predictability:
- `connect`: connection establishment
- `read`: gap between bytes/chunks
- `total`: overall call budget (including streaming)

Client default:
    from llm_fiber import Fiber, Timeouts
    fiber = Fiber.from_env(default_model="gpt-4o-mini")
    fiber.timeout = Timeouts(connect=5, read=30, total=30)

Per-call override:
    res = fiber.sync.chat(
        messages=["Summarize fiber optics."],
        timeout_s=Timeouts(connect=3, read=10, total=10),
    )

---

## Retries

Behavior
- Retries use capped, jittered exponential backoff.
- Classification considers HTTP status and provider error codes.

Customization
- A simple `retry_if(exc, attempt, ctx)` hook (if exposed in your build) can refine classification.

Conceptual example:
    from llm_fiber import Fiber, FiberAuthError, FiberRateLimited

    def retry_if(exc, attempt, ctx):
        if isinstance(exc, FiberAuthError):
            return False     # Never retry auth failures
        if isinstance(exc, FiberRateLimited):
            return attempt < 3
        return None          # Defer to default classification

    fiber = Fiber.from_env(default_model="gpt-4o-mini")
    fiber.retry_if = retry_if

Notes
- Mid-stream automatic retry is not performed, to avoid duplicating partial outputs.
- Use idempotency keys and higher-level strategies if you need replay semantics.

---

## Observability configuration

Metrics
- Always-on in-memory metrics by default.
- Optional exporters:
  - OpenTelemetry (`pip install "llm-fiber[otel]"`)
  - StatsD/DogStatsD (`pip install "llm-fiber[statsd]"`)
- Pass a metrics sink during construction if your build exposes a `metrics` parameter.

Logging
- Works with stdlib `logging` by default.
- Optional structlog integration:
  - `pip install "llm-fiber[structlog]"`
  - Pass a structlog logger during construction.

Context binding
- Use `with fiber.bind(run_id="...", tenant_id="..."):` to tag metrics/logs/traces.
- Secrets are redacted by default.

For details, see: docs/features/observability.md

---

## Provider endpoints (base URLs)

OpenAI-compatible gateways (e.g., Azure/OpenAI-compatible)
- Set `base_urls["openai"] = "https://example-gateway/v1"` on the client.
- Keep provider routing as `"openai"`; map any custom model prefixes in the `ModelRegistry` if needed.

Gemini and Vertex AI
- The default endpoint is Google’s Generative Language API.
- Vertex AI compatibility is on the roadmap (different auth/base URL).
- For now, configure `base_urls["gemini"]` explicitly if you use a compatible endpoint and your environment supports it.

Notes
- The `ModelRegistry` decides provider routing; API keys and base URLs live on the client.

---

## Model routing configuration

- The `ModelRegistry` maps model names to providers via exact and prefix matches.
- You can extend or override mappings, and set a preference order for tie-breaking.
- Per-call `provider` always wins.

Examples (conceptual):
    fiber.model_registry.map_prefix("acme-", "openai")
    fiber.model_registry.map_exact("my-claude", "anthropic")
    fiber.model_registry.set_preference_order(("anthropic", "openai", "gemini"))

See: docs/features/model-registry.md

---

## Per-call controls

All important knobs can be overridden per call:
- Provider inference: `provider="openai" | "anthropic" | "gemini"`
- Timeouts: `timeout_s=float | Timeouts`
- Tuning: `temperature`, `max_tokens`, `seed`
- Budgets: `token_budget`, `cost_ceiling_usd`
- Idempotency: `idempotency_key`
- Context: `context={...}` for ad-hoc tagging

Example:
    res = fiber.sync.chat(
        model="gemini-1.5-pro",
        messages=[("system", "Be terse."), "Three properties of glass fiber."],
        provider="gemini",
        token_budget=256,
        cost_ceiling_usd=0.002,
        timeout_s=15.0,
        context={"request_id": "abc123"},
    )

---

## Security and secrets

- Never log secrets; llm-fiber redacts keys by default.
- Prefer environment variables or a secrets manager over hardcoding secrets.
- Keep logs concise and scrubbed; avoid emitting raw prompts/responses in production unless scrubbed.

---

## Multi-env setup (dev/stage/prod)

- Use `Fiber.from_env(...)` with environment-specific variables in dev/stage/prod.
- For nonstandard endpoints, set per-environment base URLs on the client.
- Keep routing rules (Model Registry) centralized at startup.
- Ensure observability exporters are initialized before constructing `Fiber`, so they are picked up correctly.

---

## Examples

Minimal app setup
    from llm_fiber import Fiber
    fiber = Fiber.from_env(default_model="gpt-4o-mini")
    print(fiber.sync.ask("Give me two bullets on fiber optics."))

Custom base URL for OpenAI-compatible gateway
    from llm_fiber import Fiber
    fiber = Fiber(
        default_model="gpt-4o-mini",
        api_keys={"openai": "..."},
        base_urls={"openai": "https://example-gateway/v1"},
    )

Strict client defaults with per-call override
    from llm_fiber import Fiber, Timeouts
    fiber = Fiber(
        default_model="claude-3-haiku-20240307",
        timeout=Timeouts(connect=5, read=20, total=20),
    )
    # Override model and timeouts for a single call:
    res = fiber.sync.chat(
        model="gemini-1.5-pro",
        messages=["Summarize fiber optics."],
        timeout_s=Timeouts(connect=3, read=10, total=10),
    )

With bound context for observability
    from llm_fiber import Fiber
    fiber = Fiber.from_env(default_model="gpt-4o-mini")
    with fiber.bind(run_id="r-42", tenant_id="acme"):
        text = fiber.sync.ask("Latency vs TTFB?")
        print(text)

---

## Best practices

- Prefer explicit constructor configuration in libraries/services; use `from_env()` in applications.
- Set client defaults for `default_model` and `timeout` to keep call sites concise and consistent.
- Use `fiber.bind(...)` to propagate run/request context across logs/metrics/traces.
- Enforce budgets (`token_budget`, `cost_ceiling_usd`) in production.
- Keep the Model Registry minimal and intentional; prefer exact mappings for critical models.
- Monitor SLOs via metrics: p95 `latency_ms`, p99 `ttfb_ms`, error and retry rates.

---

## See also

- Transport/Core API: docs/features/transport.md
- Ergonomics (DX): docs/features/ergonomics.md
- Streaming: docs/features/streaming.md
- Prompt API: docs/features/prompt-api.md
- Model Registry & Routing: docs/features/model-registry.md
- Observability: docs/features/observability.md
- Retries & Budgets: docs/features/retries-and-budgets.md
