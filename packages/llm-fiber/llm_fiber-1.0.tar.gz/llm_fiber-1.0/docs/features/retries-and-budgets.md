# Retries & Budgets

Resiliency and spend control are first-class concerns in llm-fiber. This page describes how retries, timeouts, idempotency, and per-call budgets (tokens and cost) interact to give you predictable behavior under failure and saturation while protecting performance and cost.

---

## Goals

- Transparent, predictable retry behavior with capped, jittered exponential backoff
- Clear separation of connect/read/total timeouts
- Idempotency support when providers offer it
- Deterministic budget enforcement (tokens and/or cost) when counting/pricing are available
- Strong observability for retry reasons, error categories, latency, and usage

---

## Timeouts

Timeouts are explicit via a `Timeouts` value and can be set on the client and/or per call.

Dimensions
- connect: max time to establish the HTTP connection
- read: max gap between received bytes/chunks (relevant for streaming)
- total: overall cap for the call, inclusive of retries and streaming

Precedence
1) Per-call `timeout_s` (float or `Timeouts`) — highest
2) Client default `fiber.timeout`
3) Library default (e.g., `Timeouts(total=30)`)

Notes
- For streaming, `read` bounds the maximum inter-chunk silence.
- The `total` budget applies across all attempts; retried attempts must fit within it.

Example (per call)

    from llm_fiber import Fiber, Timeouts
    fiber = Fiber.from_env(default_model="gpt-4o-mini")

    res = fiber.sync.chat(
        messages=["Summarize fiber optics."],
        timeout_s=Timeouts(connect=5, read=20, total=20),
    )
    print(res.text)

---

## Retries

llm-fiber uses capped, jittered exponential backoff with error classification informed by HTTP status and provider error codes.

Principles
- Retry only on transient errors (e.g., timeouts, 5xx, rate limits, certain network errors).
- Never retry on permanent errors (e.g., authentication/authorization failures).
- Respect the per-call `total` timeout; retries stop when the budget is exhausted.
- Mid-stream automatic retries are not performed to avoid duplicating partial outputs.

Backoff (conceptual)
- delay = min(cap, base * 2**(attempt-1)) + jitter
- jitter is a small random value to prevent thundering herds
- Attempts are capped; classification decides if the next attempt is permitted

Classification (typical)
- Retryable: HTTP 429 (rate limit), 5xx, network/transient I/O, connect/read timeouts
- Non-retryable: 4xx auth (invalid key), malformed requests, explicit provider denials
- Provider-specific codes are mapped into these buckets

Customization with `retry_if` hook (if exposed in your build)

    from llm_fiber import Fiber, FiberAuthError, FiberRateLimited

    def retry_if(exc, attempt, ctx):
        # Never retry on auth errors
        if isinstance(exc, FiberAuthError):
            return False
        # Retry rate limits up to 3 attempts total
        if isinstance(exc, FiberRateLimited):
            return attempt < 3
        # None => fall back to default classification
        return None

    fiber = Fiber.from_env(default_model="gpt-4o-mini")
    fiber.retry_if = retry_if

Streaming
- Pre-stream errors (connect/handshake) may be retried.
- Once streaming begins, automatic retries are avoided to prevent duplicate output.
- If you need replay semantics, design idempotent workflows at the application level.

Observability
- `retry_count{provider,model,reason}` increments per attempt.
- `error_count{provider,model,code}` tracks terminal failures.
- `latency_ms` includes retries within the `total` timeout budget.

---

## Idempotency

Idempotency keys help prevent duplicate side effects during retries when the provider supports them.

Usage
- Pass `idempotency_key="..."` on calls.
- Keys should be unique per intended “unit of work” (e.g., request UUID).
- When supported, providers use the key to deduplicate repeated attempts.

Notes
- Idempotency is provider-dependent; the library forwards the key if available.
- For purely read-like operations (most chat calls), idempotency primarily prevents duplicated billing or repeated tool side effects where applicable.
- Idempotency does not create mid-stream retry; it only ensures that retried requests are deduplicated server-side.

Example

    res = fiber.sync.chat(
        messages=["One-line definition of backpressure."],
        idempotency_key="req-12345",
    )
    print(res.text)

---

## Budgets: Tokens and Cost

Budgets enforce per-call ceilings to contain cost and latency. They fail deterministically with a typed error when exceeded.

- token_budget: maximum allowed tokens (prompt + completion)
- cost_ceiling_usd: maximum allowed estimated cost for the call

Enforcement modes
- Preflight: When tokenizers/pricing are available, the library may estimate and fail before issuing the request if the budget is impossible to satisfy.
- Soft-stop (stream-aware): When supported, the library may terminate the stream upon hitting a ceiling (exact behavior depends on provider capabilities and configuration).

Precision & availability
- Token accuracy depends on a tokenizer integration (e.g., adapter to tiktoken).
- Cost estimates depend on pricing tables; these are pluggable and can refresh with TTL.
- When precise counting is unavailable, conservative estimates may be used or budget enforcement may be disabled.

Examples

    # Token guard (requires tokenizer support for precise counts)
    res = fiber.sync.chat(
        messages=["Summarize fiber optics in two sentences."],
        token_budget=300,
    )
    print(res.text, res.usage)

    # Cost guard (requires pricing for the target model)
    res = fiber.sync.chat(
        messages=["List five properties of glass fiber."],
        cost_ceiling_usd=0.002,
    )
    print(res.text, res.usage)

Failure mode
- Exceeding a budget raises a typed error derived from `FiberError`.
- When a stream is terminated due to budget, a final `usage` event may not be emitted if the provider does not report it for partial streams.

Observability
- Budget failures appear in `error_count` with a specific code/category.
- Usage and estimated cost are recorded where available.
- Consider alerting on budget-induced errors to tune ceilings.

---

## Putting It Together

Recommended defaults
- Set a sensible `Timeouts` on the client (e.g., connect=5s, read=20–30s, total=20–30s).
- Allow retries on 429/5xx/timeouts with jitter and caps.
- Pass idempotency keys for calls that might be replayed by your application layer.
- Configure `token_budget` and/or `cost_ceiling_usd` in production to guard spend.

Batch scenarios
- Use batch helpers with `concurrency` caps; combine with budgets per job.
- Prefer async batch to maximize throughput within provider or network limits.
- Consider `fail_fast` or `return_exceptions` policies depending on your pipeline’s tolerance.

Streaming
- Rely on `read` timeout to catch stalled streams.
- Avoid mid-stream automatic retries; if you must resume, design an application-level protocol to detect progress and restart safely.
- Expect partial output to be valid up to the last `chunk` received; do not assume a final `usage` event on early termination.

---

## Troubleshooting

- Too many retries / high latency:
  - Tighten `total` timeout or reduce max attempts.
  - Inspect retry reasons; rate limit spikes may need provider-level quota changes.
- Early budget failures:
  - Ensure tokenizers/pricing are correctly configured for your models.
  - Increase budgets or reduce prompt size/max_tokens.
- Missing usage/cost on streams:
  - Some providers omit usage for streamed responses; prefer non-streaming calls when precise accounting is critical.

---

## Best Practices

- Always set `timeout_s` per critical call path if you need tighter bounds than the client default.
- Attach context via `with fiber.bind(...)` so retry reasons and budget failures are searchable by run/request IDs.
- Enforce budgets for production traffic; start conservative and tune up as needed.
- Prefer explicit provider overrides only when the registry behavior is insufficient; keep routing simple and intentional.
- Keep backoff jitter enabled; disable only for testing.

---

## See Also

- Transport/Core API: ./transport.md
- Streaming: ./streaming.md
- Ergonomics (DX): ./ergonomics.md
- Prompt API: ./prompt-api.md
- Model Registry & Routing: ./model-registry.md
- Observability: ./observability.md
- Configuration: ./configuration.md
