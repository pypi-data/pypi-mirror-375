# Transport / Core API

The Transport layer is the lowest-level, consistent interface to large language model (LLM) providers. It is designed for throughput, predictability, and observability, exposing a small surface:

- Async-first methods: chat() and chat_stream()
- Provider inference from model names via a model registry
- Normalized request/response types and streaming events
- Built-in timeouts, retries, and optional budgets (tokens/cost)
- Escape hatch to raw provider payloads

Higher-level ergonomics (e.g., ask(), batch helpers, context binding) are documented in the Ergonomics feature page. Prompt-as-a-function is documented in the Prompt API page.

---

## Goals

- Provide a uniform, minimal, provider-agnostic interface
- Preserve performance (low overhead, wire-speed streaming)
- Expose observability hooks (metrics/logging/traces) without forcing dependencies
- Keep the Transport API stable and predictable

---

## Scope

Included
- Core client construction and environment-based bootstrap
- Async chat and streaming APIs with normalized types
- Provider inference and per-call override
- Timeouts, retries, idempotency key pass-through
- Optional token and cost budgets (when tokenizers/pricing known)

Out of scope
- Prompt templating and ergonomics (see Ergonomics and Prompt API)
- Tool/function calling normalization (post-MVP)
- Caching adapters (planned)
- Structured outputs via pydantic (optional extra, post-MVP)

---

## Primary Entry Points

- Fiber(default_model=None, api_keys=None, base_urls=None, timeout=Timeouts(total=30), metrics=None, logger=None, ...)
- Fiber.from_env(default_model=None, prefer=("openai","anthropic","gemini"))

The client is providerless by default. It infers the provider from the model name using a small registry (configurable). Base URLs and API keys are attached to the client and can be loaded from environment variables via Fiber.from_env().

Environment variables (set only what you use):
- OPENAI_API_KEY
- ANTHROPIC_API_KEY
- GEMINI_API_KEY

---

## API Surface

### chat()
Async call that returns a normalized ChatResult.

Parameters (selected)
- model: str — model identifier; provider is inferred (overrideable per call)
- messages: list[ChatMessage | tuple | str] — conversation to send (see Messages Normalization)
- temperature: float | None
- max_tokens: int | None
- seed: int | None
- tools: provider-specific tool/function descriptors (normalization planned post-MVP)
- provider: Literal["openai", "anthropic", "gemini"] | None — force provider
- timeout_s: float | Timeouts | None — per-call override (see Timeouts)
- idempotency_key: str | None — passed through when supported
- token_budget: int | None — optional budget guard (requires tokenizer for accuracy)
- cost_ceiling_usd: float | None — optional budget guard (requires pricing data)
- context: dict[str, str] | None — extra labels for logs/metrics/traces

Returns
- ChatResult: access normalized fields and the raw provider payload via result.raw

Minimal example

    from llm_fiber import Fiber, ChatMessage

    fiber = Fiber.from_env(default_model="gpt-4o-mini")
    result = await fiber.chat(
        messages=[ChatMessage.user("Give me 3 bullet points about fiber optics.")],
        temperature=0.2,
        max_tokens=120,
    )
    print(result.text)
    print(result.usage)

### chat_stream()
Async streaming variant. Yields StreamEvent values.

Parameters
- Same as chat(), returning an async iterator of StreamEvent

Events
- chunk: partial assistant delta (text/token fragments)
- tool_call: provider-agnostic placeholder for tool/function call events (shape may evolve)
- usage: final usage and cost estimate at end-of-stream (if known)
- log: debug-level annotations/events (rare; can be disabled)

Example

    from llm_fiber import Fiber, ChatMessage

    async def run():
        fiber = Fiber.from_env()
        async for ev in fiber.chat_stream(
            model="gemini-1.5-pro",
            messages=[ChatMessage.user("Stream the alphabet quickly.")],
            temperature=0.0,
        ):
            if ev.type == "chunk":
                print(ev.delta, end="", flush=True)
            elif ev.type == "usage":
                print("\nusage:", ev.usage)

---

## Messages Normalization

The transport layer accepts flexible message inputs and normalizes to a consistent internal shape.

Accepted forms
- ChatMessage helpers:
  - ChatMessage.system("..."), ChatMessage.user("..."), ChatMessage.assistant("..."), ChatMessage.tool(name, payload)
- Tuple shorthand:
  - ("system", "..."), ("user", "..."), ("assistant", "...")
- Bare string:
  - "..." is treated as a user message

Examples

    messages = [
        ("system", "Be concise."),
        "Explain backpressure in 2 sentences.",
    ]

    # Equivalent, using helpers:
    from llm_fiber import ChatMessage
    messages = [
        ChatMessage.system("Be concise."),
        ChatMessage.user("Explain backpressure in 2 sentences."),
    ]

Notes
- Tool/function calling events are normalized at the event/type level; detailed normalization across providers is planned post-MVP.

---

## Return and Event Types

ChatResult
- text: str — final assistant concatenated text
- tool_calls: list — provider-agnostic container (shape may evolve)
- finish_reason: enum — normalized finish reason
- usage: Usage — tokens_in, tokens_out, tokens_total, cost_estimate (if known)
- raw: Any — provider-specific raw response payload

StreamEvent
- type: Literal["chunk","tool_call","usage","log"]
- timestamps: float fields for tracing/metrics correlation
- chunk: .delta (str) for text fragments
- usage: Usage at end-of-stream
- tool_call: normalized placeholder for function/tool events
- log: informational/debug data

Usage
- prompt, completion, total token counts (if available from provider)
- cost_estimate: float | None (based on pricing table when known)

---

## Provider Inference and Override

- Provider inference is based on a small registry mapping (prefix/exact matches), e.g.:
  - openai: gpt-*, o*, text-*
  - anthropic: claude-*
  - gemini: gemini-*
- You can override per call with provider="openai" | "anthropic" | "gemini".
- The model registry is customizable (prefix/exact mapping, preference order).
- Base URLs and API keys are attached to the client (from_env or constructor) and are not part of the registry.

See Model Registry & Routing for details.

---

## Timeouts, Retries, and Idempotency

Timeouts
- Timeouts(connect=5, read=30, total=30) provides explicit control and clarity.
- Pass timeout_s per call as either a simple float (overall) or a Timeouts object.

Retries
- Capped, jittered exponential backoff.
- Classification by HTTP status and provider error codes.
- retry_if(exc, attempt, ctx) hook available in the higher layers to customize behavior.

Idempotency
- Pass idempotency_key on calls.
- If the provider supports idempotency, the key is forwarded to the underlying request.
- Expected effect: safe retry of transient failures without duplicating side effects.

---

## Budgets: Tokens and Cost

- token_budget: hard or preflight checks when a tokenizer is available (e.g., via tiktoken adapter).
- cost_ceiling_usd: estimate and enforce per-call ceilings when pricing data is available.
- Failure mode is deterministic and typed (budget exceeded).

Note: token-counting precision depends on the tokenizer integration for the target model. Cost estimation depends on up-to-date pricing data.

---

## Error Model

All errors derive from FiberError and carry provider/model/attempt metadata.

Specialized exceptions include:
- FiberTimeout
- FiberRateLimited
- FiberAuthError
- FiberAPIError
- FiberParsingError

Guidelines
- Catch FiberError to handle all library errors consistently.
- Use specialized types for granular handling (e.g., rate-limit vs auth).

---

## Streaming Semantics and Guarantees

Ordering and lifecycle
- chunk events represent the assistant’s text in order; concatenating deltas yields the final text.
- usage is emitted once (end-of-stream) if available.
- tool_call events may interleave with chunk events depending on provider behavior (semantics may evolve).

Backpressure
- Async iteration respects consumer backpressure.
- For sync iteration, use the sync wrapper (see below).

Observability
- Metrics capture TTFB (first chunk latency) and overall latency, plus token counts and estimated cost.
- Logging correlates call-level fields (e.g., run_id when bound) with metrics/traces where enabled.

---

## Sync Wrappers

The transport layer exposes sync mirrors under fiber.sync for environments where async is not convenient.

- fiber.sync.chat(...)
- fiber.sync.chat_stream(...): yields events in a blocking iterator

Note: The sync wrappers orchestrate an internal event loop to drive the underlying async calls without exposing async machinery to the caller.

---

## Raw Escape Hatch

Every ChatResult includes result.raw with the provider-specific payload.

Usage
- Inspect raw for fields not yet normalized by llm-fiber.
- Prefer normalized fields for portability and stability; raw should be a last resort.

---

## Configuration and Construction

Preferred patterns
- Explicit constructor arguments for clarity and testability.
- Use Fiber.from_env() for convenience in apps with env-based secrets and base URLs.

Constructor knobs
- default_model, default_temperature, default_max_tokens
- api_keys and base_urls structures for multiple providers
- timeout (Timeouts) default for the client, overrideable per call
- metrics sink and logger integration

---

## Observability

Metrics (always-on in-memory; exporters optional)
- request_count{provider,model,ok}
- error_count{provider,model,code}
- retry_count{provider,model,reason}
- latency_ms (histogram), ttfb_ms (histogram)
- tokens_in, tokens_out, tokens_total
- estimated_cost_usd (when pricing known)

Logging
- Uses stdlib logging by default; optional structlog via extras.
- Correlation fields (e.g., request_id) and redaction of secrets.
- When context binding is used (DX layer), fields flow to metrics/traces.

---

## Examples

Minimal chat

    from llm_fiber import Fiber

    fiber = Fiber.from_env(default_model="gpt-4o-mini")
    res = fiber.sync.chat(messages=["Summarize fiber optics in one sentence."])
    print(res.text)

Provider override and budgets

    res = fiber.sync.chat(
        model="gemini-1.5-pro",
        provider="gemini",
        messages=[("system", "Be terse."), "List three key properties of glass fiber."],
        token_budget=256,
        cost_ceiling_usd=0.002,
    )
    print(res.text, res.usage)

Streaming

    from llm_fiber import Fiber, ChatMessage

    fiber = Fiber.from_env()
    for ev in fiber.sync.chat_stream(
        model="claude-3-haiku-20240307",
        messages=[ChatMessage.user("Stream A..Z quickly.")],
    ):
        if ev.type == "chunk":
            print(ev.delta, end="")
        elif ev.type == "usage":
            print("\nusage:", ev.usage)

---

## Design Notes and Contracts

- Uniform method shapes across providers; normalize messages and results.
- Separation of normalized public API vs raw provider payload.
- Retries use capped, jittered exponential backoff; timeouts are explicit and typed.
- Metrics and logs instrument the full lifecycle of a call and stream events.
- Deterministic cache keys (planned) are derived from normalized requests.

---

## Known Limitations (MVP)

- Tool/function calling normalization is planned post-MVP.
- Vertex AI compatibility (Gemini) is on the roadmap (auth/base_url differences).
- Structured outputs via pydantic-core is planned as an optional extra.

---

## See Also

- Ergonomics (DX): docs/features/ergonomics.md
- Streaming: docs/features/streaming.md
- Prompt API: docs/features/prompt-api.md
- Model Registry & Routing: docs/features/model-registry.md
- Observability: docs/features/observability.md
- Retries & Budgets: docs/features/retries-and-budgets.md
- Capabilities & Pricing: docs/features/capabilities-and-pricing.md
- Configuration: docs/features/configuration.md
