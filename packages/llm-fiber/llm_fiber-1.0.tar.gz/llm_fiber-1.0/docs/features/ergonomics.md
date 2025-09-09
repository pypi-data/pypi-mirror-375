# Ergonomics (DX)

Ergonomics features help you ship quickly without losing control. They layer on top of the Transport/Core API to streamline common tasks, enforce guardrails, and improve observability—while preserving the same normalized results and typed exceptions.

This page covers construction helpers, simple calls (`ask()`), message normalization, batching, context binding, timeouts and retries, budgets, results and parsing, and sync wrappers.

---

## Goals

- Speed up common flows with minimal surface area
- Keep behavior explicit and predictable
- Integrate logging/metrics/traces without heavy dependencies
- Provide useful defaults with easy overrides
- Fail fast and deterministically when budgets and constraints are exceeded

---

## Construction & Defaults

Use `Fiber.from_env()` for convenience; set explicit defaults on the client for consistent behavior across calls.

Environment variables (set only what you need):
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY`

Common client defaults:
- `default_model`
- `default_temperature`
- `default_max_tokens`
- `timeout` (as a `Timeouts` value)

Example:
```python
from llm_fiber import Fiber, Timeouts

fiber = Fiber.from_env(
    default_model="gpt-4o-mini",
)
# Adjust client-wide timeout defaults
fiber.timeout = Timeouts(connect=5, read=30, total=30)
```

Notes:
- Provider is inferred from the model name via the Model Registry; you can always override with `provider="..."` per call.
- Prefer passing explicit constructor args in libraries/tests; use env in applications for convenience.

---

## ask(): the simplest path to text

`ask()` returns the assistant text directly. It’s a thin wrapper over `chat()` that:
- Infers provider from `model` or uses `default_model`
- Accepts the same tuning knobs (`temperature`, `max_tokens`, `timeout`, budgets, etc.)
- Raises the same typed exceptions as `chat()`

Examples:
```python
from llm_fiber import Fiber

fiber = Fiber.from_env(default_model="gpt-4o-mini")

# Minimal
text = fiber.sync.ask("Give me 3 bullet points about fiber optics.", temperature=0.2, max_tokens=120)
print(text)

# Force provider (optional; normally inferred from model)
text = fiber.sync.ask("Explain backpressure in 2 sentences.", model="claude-3-haiku-20240307", provider="anthropic")
print(text)
```

---

## Messages Normalization

You can pass messages in multiple ergonomic forms; the library normalizes them to a common shape for providers.

Accepted forms:
- ChatMessage helpers:
  - `ChatMessage.system("...")`, `ChatMessage.user("...")`, `ChatMessage.assistant("...")`, `ChatMessage.tool(name, payload)`
- Tuple shorthand:
  - `("system", "...")`, `("user", "...")`, `("assistant", "...")`
- Bare string:
  - `"..."` is treated as a user message

Example equivalencies:
```python
from llm_fiber import Fiber, ChatMessage

fiber = Fiber.from_env(default_model="gpt-4o-mini")

# Tuple + bare string shorthand
res = fiber.sync.chat(messages=[("system", "Be terse."), "Summarize fiber optics."])
print(res.text)

# Helpers
res = fiber.sync.chat(messages=[ChatMessage.system("Be terse."), ChatMessage.user("Summarize fiber optics.")])
print(res.text)
```

---

## Batch helpers

Batch multiple independent chat jobs with concurrency control and error handling policy.

Key knobs (typical):
- `concurrency` (limit async inflight)
- `return_exceptions` (collect exceptions as results)
- `fail_fast` (cancel outstanding tasks on first failure)

Examples:
```python
import asyncio
from llm_fiber import Fiber

async def main():
    fiber = Fiber.from_env(default_model="gpt-4o-mini")

    jobs = [
        {"messages": ["Explain latency vs throughput in one sentence."]},
        {"messages": ["Three bullet points on backpressure."]},
        {"messages": ["Define idempotency."]},
    ]
    # Returns list[ChatResult] (or exceptions if return_exceptions=True)
    results = await fiber.batch_chat(jobs, concurrency=8, return_exceptions=False)
    for r in results:
        print(r.text)

asyncio.run(main())
```

Sync mirror (if provided in your build):
```python
fiber = Fiber.from_env(default_model="gpt-4o-mini")
results = fiber.sync.batch_chat(
    [
        {"messages": ["Short definition of TTFB."]},
        {"messages": ["One-line summary of jittered backoff."]},
    ],
    concurrency=4,
)
for r in results:
    print(r.text)
```

Notes:
- Input job items mirror `chat()` parameters (e.g., you can pass `model`, `temperature`, `context`, budgets, etc. per job).
- For large batches, prefer async usage for optimal throughput.

---

## Context binding (logs/metrics/traces)

Bind contextual fields to a `Fiber` instance so they flow into logs, metrics, and traces (when exporters are enabled). This is invaluable for correlating calls across a request, tenant, or run.

```python
from llm_fiber import Fiber

fiber = Fiber.from_env(default_model="gpt-4o-mini")

with fiber.bind(run_id="r-42", tenant_id="acme", request_id="abc123"):
    text = fiber.sync.ask("Latency vs TTFB difference?", model="gemini-1.5-pro")
    print(text)

# Outside the 'with', bound fields are no longer attached.
```

Notes:
- Bound fields are redacted when appropriate (e.g., secrets).
- Bound fields also inform metrics (e.g., as tags/labels) and traces (via OTel exporters when installed).

---

## Timeouts

Time is a first-class control. Use `Timeouts` for clarity and per-call overrides.

Client-wide default:
```python
from llm_fiber import Fiber, Timeouts

fiber = Fiber.from_env(default_model="gpt-4o-mini",)
fiber.timeout = Timeouts(connect=5, read=30, total=30)
```

Per-call override:
```python
from llm_fiber import Timeouts

res = fiber.sync.chat(
    messages=["Summarize fiber optics."],
    timeout_s=Timeouts(connect=3, read=10, total=10),
)
print(res.text)
```

Notes:
- `connect` bounds the time to establish a connection to the provider.
- `read` bounds the gap between bytes/chunks.
- `total` bounds the full call duration, including streaming time.

---

## Retries and `retry_if` hook

The library uses capped, jittered exponential backoff with classification by HTTP status and provider error codes. You can customize retry behavior via a simple hook.

Conceptual example:
```python
from llm_fiber import Fiber, FiberAuthError, FiberRateLimited

def retry_if(exc: Exception, attempt: int, ctx: dict) -> bool:
    # Never retry on auth errors
    if isinstance(exc, FiberAuthError):
        return False
    # Retry rate limits up to 3 attempts total
    if isinstance(exc, FiberRateLimited):
        return attempt < 3
    # Fallback to default classification for other errors
    return None  # None delegates to default policy

fiber = Fiber.from_env(default_model="gpt-4o-mini")
fiber.retry_if = retry_if  # attach hook globally

# Or pass per-call if supported in your build
res = fiber.sync.chat(messages=["Hello"],)
```

Notes:
- Hooks receive the exception, attempt number, and context (contains provider/model and bound fields).
- Returning True/False overrides; returning None defers to the built-in classification.

---

## Budgets: tokens and cost

Guard your calls with token and/or monetary budgets. When tokenizers/pricing are available, the library can preflight or enforce ceilings deterministically.

- `token_budget`: limit on tokens (prompt + completion)
- `cost_ceiling_usd`: estimated max cost per call
- Failure mode is deterministic (typed exception) and can happen preflight or mid-call depending on configuration

Examples:
```python
# Token guard (requires tokenizer integration for precise counts)
res = fiber.sync.chat(
    messages=["Summarize fiber optics in two sentences."],
    token_budget=300,
)
print(res.text)

# Cost guard (requires pricing data for the target model)
res = fiber.sync.chat(
    messages=["List five properties of glass fiber."],
    cost_ceiling_usd=0.002,
)
print(res.text)
```

Notes:
- Budget guards are best-effort when exact counts are unavailable; conservative estimates may be used.
- If your environment doesn’t include a tokenizer/pricing registry, budget enforcement may be unavailable or reduced in precision.

---

## Results and parsing

`ChatResult` provides normalized fields and `raw` for provider escape hatch:
- `text`: final assistant text
- `tool_calls`: placeholder for tool/function calls
- `finish_reason`: normalized enum
- `usage`: prompt/completion/total tokens and `cost_estimate` (if known)
- `raw`: provider-specific payload

Structured outputs (optional):
- `result.json()` returns `dict` when the provider responded in JSON or when the library constructed a JSON object.
- `result.json(parse=MyModel)` uses `pydantic-core` (optional extra) to parse into a typed model.
  - If `pydantic-core` is not installed and `parse=` is provided, a `FiberParsingError` is raised with a clear message.
  - If you call `result.json()` without `parse=`, a `dict` is returned (when applicable).

Example:
```python
from typing import TypedDict
from llm_fiber import Fiber, FiberParsingError

class MySummary(TypedDict):
    title: str
    bullets: list[str]

fiber = Fiber.from_env(default_model="gpt-4o-mini")

res = fiber.sync.chat(
    messages=[
        ("system", "Respond in JSON."),
        "Summarize fiber optics in 3 bullets with a short title.",
    ],
)

# Get raw JSON dict (if response is valid JSON)
data = res.json()  # dict
print(data)

# Parse into a typed model (requires pydantic-core installed)
try:
    summary = res.json(parse=MySummary)  # MySummary
    print(summary["title"])
except FiberParsingError as exc:
    print(f"Parsing unavailable or failed: {exc}")
```

---

## Typed exceptions

Catch `FiberError` to handle all library errors uniformly, or use specialized types:
- `FiberTimeout`
- `FiberRateLimited`
- `FiberAuthError`
- `FiberAPIError`
- `FiberParsingError`

Example:
```python
from llm_fiber import Fiber, FiberError, FiberRateLimited

fiber = Fiber.from_env(default_model="gpt-4o-mini")
try:
    text = fiber.sync.ask("Hello world")
    print(text)
except FiberRateLimited as exc:
    # Specific handling
    print("Rate limited, retry later:", exc)
except FiberError as exc:
    # Generic handling
    print("Request failed:", exc)
```

---

## Sync wrappers

The ergonomic layer includes sync mirrors to avoid async ceremony:

- `fiber.sync.ask(...) -> str`
- `fiber.sync.chat(...) -> ChatResult`
- `fiber.sync.chat_stream(...) -> Iterator[StreamEvent]`
- `fiber.sync.batch_chat(...) -> list[ChatResult]` (if available in your build)

Example:
```python
from llm_fiber import Fiber

fiber = Fiber.from_env(default_model="gpt-4o-mini")
print(fiber.sync.ask("One-line definition of backpressure."))
```

---

## Best practices

- Set client defaults (`default_model`, `timeout`) so call sites are short but predictable.
- Use `with fiber.bind(...):` to propagate context (run/request/tenant IDs) for strong observability.
- Enforce budgets in production (tokens and/or cost ceilings) to protect reliability and spend.
- Prefer normalized fields (`text`, `usage`, `finish_reason`) for portability; only use `raw` when absolutely necessary.
- Handle `FiberError` at the boundary of your system to centralize error mapping/logging.
- If you depend on structured outputs, add `pydantic-core` and always validate with `parse=`.

---

## Known limitations (MVP)

- Tool/function calling normalization is limited in MVP; shapes and streaming of tool calls may evolve.
- Some providers may not report accurate token usage for streamed responses, so final usage can be absent or partial.
- Caching adapters (memory/filesystem/Redis) are planned; cache policy may be experimental early-on.

---

## See also

- Transport/Core API: ./transport.md
- Streaming: ./streaming.md
- Prompt API: ./prompt-api.md
- Model Registry & Routing: ./model-registry.md
- Observability: ./observability.md
- Retries & Budgets: ./retries-and-budgets.md
- Configuration: ./configuration.md
