# Streaming

Low-latency, backpressure-friendly token streaming is a first-class feature in llm-fiber. The streaming API lets you render tokens as they arrive, observe time-to-first-byte (TTFB), and receive final usage metrics when available.

This page covers the streaming interfaces, event model, ordering guarantees, cancellation, error handling, and observability.

---

## Overview

APIs
- Async:
  - `Fiber.chat_stream(...) -> async iterator[StreamEvent]`
- Sync wrappers:
  - `fiber.sync.chat_stream(...) -> iterator[StreamEvent]`
- Prompt API:
  - `Prompt.stream(fiber, ...) -> iterator[StreamEvent]`
  - `await Prompt.astream(fiber, ...) -> async iterator[StreamEvent]` (name may vary; see actual implementation)

Core goals
- Low-latency token delivery (wire-speed when possible)
- Simple iteration surface with strong ordering guarantees
- Metrics and logs that reflect streaming behavior (including TTFB)
- Consistent event types across providers

---

## Event Model

Events are yielded incrementally. The current set is deliberately small and stable:

- `chunk`
  - A partial assistant output segment (token or text delta).
  - Fields: `type="chunk"`, `delta: str`, `ts_first`, `ts_now` (timestamps).
- `tool_call`
  - A normalized placeholder for tool/function calling signals.
  - Fields: `type="tool_call"`, `name: str | None`, `arguments_delta: str | bytes | None`, `index: int | None`, timestamps.
  - Note: Tool/function calling normalization is improving post-MVP. Treat as experimental.
- `usage`
  - Emitted at end-of-stream when usage is known.
  - Fields: `type="usage"`, `usage: {prompt, completion, total, cost_estimate?}`, timestamps.
- `log`
  - Occasional debug or lifecycle annotations.
  - Fields: `type="log"`, `level: str`, `message: str`, timestamps.
  - Typically disabled or rare in production.

Notes
- Only one `usage` event is emitted, and only at the end-of-stream if usage is available from the provider.
- Concatenating all `chunk.delta` in order yields the final assistant text for the stream.

---

## Ordering & Lifecycle

- Ordering: Events are yielded in provider order. `chunk` events arrive in the same order as produced by the provider.
- Lifecycle:
  1) Stream starts (internal connection established).
  2) First `chunk` marks TTFB.
  3) Additional `chunk` and possibly `tool_call` events.
  4) Final `usage` event (if available).
  5) Iterator completes.

Invariants
- At most one `usage` event.
- No further events after an error is raised or after iteration completes.
- The aggregated text is the concatenation of all `chunk.delta` values in order.

---

## Backpressure & Flow Control

- Async iteration naturally respects consumer backpressure: the provider stream is read as the consumer advances the iterator.
- Sync wrapper uses an internal loop to bridge async-to-sync while preserving event order and minimal buffering.
- If you must slow consumption (e.g., to update a UI), simply delay the next `next()`/`await anext()` call; backpressure is respected.

---

## Cancellation

You can cancel a stream at any time:
- Async: By cancelling the task or breaking the `async for` loop early.
- Sync: By breaking the `for` loop early.

Effects:
- The underlying HTTP stream is aborted and cleaned up.
- No `usage` event is emitted after cancellation (since the stream didn’t complete).
- Partial output remains valid (all `chunk` events observed before cancelling are yours to keep).

Example (async cancellation with timeout):
```python
import asyncio
from contextlib import asynccontextmanager
from llm_fiber import Fiber, ChatMessage

async def main():
    fiber = Fiber.from_env()
    try:
        async with asyncio.timeout(1.5):
            async for ev in fiber.chat_stream(
                model="gpt-4o-mini",
                messages=[ChatMessage.user("Stream something long...")],
            ):
                if ev.type == "chunk":
                    print(ev.delta, end="", flush=True)
    except TimeoutError:
        # Timed out mid-stream; partial output printed already.
        pass

asyncio.run(main())
```

---

## Errors & Retries

- Errors during streaming propagate as exceptions (e.g., `FiberTimeout`, `FiberRateLimited`, `FiberAuthError`, `FiberAPIError`), all deriving from `FiberError`.
- Retries:
  - Pre-stream (connect/handshake errors) can be retried according to the retry policy.
  - Mid-stream retries are not attempted automatically, as they would duplicate partial outputs (unless you control idempotency semantics end-to-end).
  - If you require resilient replays, consider:
    - Emitting idempotency keys (when supported),
    - Tracking progress and resuming at a higher level (application semantics),
    - Or falling back to non-streaming calls when exact reproducibility is required.

---

## Timeouts

- `Timeouts` support connect, read, and total bounds. They apply to streaming as follows:
  - Connect timeout: before the provider starts sending.
  - Read timeout: between chunks (e.g., no data arriving for too long).
  - Total timeout: overall call budget including all stream time.
- Per-call override via `timeout_s` or `Timeouts` instance.

Example:
```python
from llm_fiber import Fiber, ChatMessage, Timeouts

fiber = Fiber.from_env()
async for ev in fiber.chat_stream(
    model="gemini-1.5-pro",
    messages=[ChatMessage.user("Stream A..Z quickly.")],
    timeout_s=Timeouts(connect=5, read=20, total=20),
):
    ...
```

---

## Observability

Metrics (always-on in-memory; exporters optional):
- `request_count{provider,model,ok}`
- `error_count{provider,model,code}`
- `retry_count{provider,model,reason}`
- `latency_ms` (histogram, stream end-to-end)
- `ttfb_ms` (histogram, time to first `chunk`)
- `tokens_in`, `tokens_out`, `tokens_total`
- `estimated_cost_usd` (on final usage if known)

Logging:
- Stdlib `logging` by default; optional `structlog` integration.
- Context binding (via `fiber.bind(...)`) propagates run/request IDs into logs and metrics.
- Secrets and keys are redacted by default.

---

## Examples

Async streaming:
```python
import asyncio
from llm_fiber import Fiber, ChatMessage

async def main():
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

asyncio.run(main())
```

Sync streaming:
```python
from llm_fiber import Fiber, ChatMessage

fiber = Fiber.from_env()
for ev in fiber.sync.chat_stream(
    model="claude-3-haiku-20240307",
    messages=[ChatMessage.user("Stream three short lines:")],
):
    if ev.type == "chunk":
        print(ev.delta, end="")
    elif ev.type == "usage":
        print("\nfinal usage:", ev.usage)
```

Prompt API streaming:
```python
from llm_fiber import Fiber, Prompt, PromptDefaults

fiber = Fiber.from_env(default_model="gpt-4o-mini")
stream_three = Prompt(
    template="Stream a numbered list of three concise items about {topic}.",
    inputs=["topic"],
    defaults=PromptDefaults(temperature=0.2, max_tokens=120),
)

for ev in stream_three.stream(fiber, topic="fiber optics"):
    if ev.type == "chunk":
        print(ev.delta, end="")
    elif ev.type == "usage":
        print("\nusage:", ev.usage)
```

With context binding (adds fields to logs/metrics):
```python
from llm_fiber import Fiber, ChatMessage

fiber = Fiber.from_env()
with fiber.bind(run_id="r-42", tenant_id="acme"):
    for ev in fiber.sync.chat_stream(
        messages=[("system", "Be terse."), "Stream three facts about latency."],
    ):
        if ev.type == "chunk":
            print(ev.delta, end="")
```

Error handling:
```python
from llm_fiber import Fiber, ChatMessage, FiberError

fiber = Fiber.from_env()
try:
    for ev in fiber.sync.chat_stream(messages=[ChatMessage.user("...")]):
        if ev.type == "chunk":
            ...
        elif ev.type == "usage":
            ...
except FiberError as exc:
    # Handle timeouts, rate limits, auth issues, API errors uniformly
    print(f"Streaming failed: {exc}")
```

---

## Working With `tool_call` Events (Early)

- The `tool_call` event is a normalized placeholder for provider function/tool-calling streams.
- Expect fields like `name`, `arguments_delta`, `index`. These may arrive interleaved with `chunk` events.
- Recommended approach:
  - Maintain an aggregator keyed by `index`.
  - Concatenate `arguments_delta` across events to reconstruct the final arguments payload.
  - When the stream completes, dispatch to your tool runner if appropriate.

Normalization of tool/function calling will improve post-MVP.

---

## Practical Tips

- Accumulating text:
  - Prefer appending to a Python list and `''.join()` at the end for performance.
- Output encoding:
  - `chunk.delta` is a Python `str`. If you need raw tokens, you’ll need provider-specific behavior or a tokenizer integration.
- JSON streaming:
  - If you need structured JSON, consider non-streaming calls or robust partial-JSON assembly; streamed deltas may be transiently invalid JSON.
- Deterministic budgets:
  - Budgets are enforced on requests; mid-stream enforcement may stop the stream early if a ceiling is hit (depending on your configuration).

---

## Design Constraints & Guarantees

- Minimal dependency footprint; streaming built on async HTTP primitives.
- Strong ordering and a simple event model for portability across providers.
- Observability that reflects real streaming behavior (TTFB and end-to-end latency).
- No mid-stream automatic retry: avoids duplicating partial outputs.

---

## Known Limitations (MVP)

- `tool_call` normalization is evolving; shapes may change slightly.
- Some providers do not return accurate usage for streamed responses; the `usage` event may be absent or partial.
- Vertex AI-compatible streaming for Gemini is on the roadmap.

---

## See Also

- Transport/Core API: ./transport.md
- Ergonomics (DX): ./ergonomics.md
- Prompt API: ./prompt-api.md
- Retries & Budgets: ./retries-and-budgets.md
- Observability: ./observability.md
