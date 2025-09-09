# llm-fiber – C4-lite Architecture & Developer Guide

A thin, fast, observable Python client for LLMs. Async-first with wire-speed streaming, consistent ergonomics across providers, and built-in observability.

This documentation restructures the large `README.md` into a navigable reference organized using a C4-lite approach: System Context (L1), Containers (L2), Components (L3), plus key flows, quality attributes, and links to detailed feature pages and ADRs.

---

## L1 — System Context

- Primary system: `llm-fiber` (a Python library)
- Primary users: application engineers integrating LLMs; backend/ML services; CLI tools
- External systems:
  - LLM Providers: OpenAI, Anthropic, Google Gemini (and compatible endpoints)
  - Observability sinks: OpenTelemetry backends, StatsD/DogStatsD
  - Logging: stdlib `logging`, optional `structlog`
  - Token counting: optional tokenizers (e.g., `tiktoken`)
  - Cache backends: memory, filesystem, Redis (planned adapters)
  - CI/CD & packaging: PyPI, GitHub Actions (release automation)

Context sketch:
- Your app → `llm-fiber` → provider adapter → LLM HTTP API
- Observability hooks export metrics/logs/traces (optional extras)
- Tokenizers/pricing/caches are pluggable and optional

Goals:
- High throughput, low latency
- Provider-agnostic ergonomics
- First-class streaming & observability
- Minimal core dependencies; extras for integrations

---

## L2 — Containers (Library Subsystems)

- Core Client (`Fiber`)
  - Providerless entrypoint, env/config, sync wrappers
  - Uniform chat and streaming API
- Provider Adapters
  - OpenAI, Anthropic, Gemini (normalize messages, requests, responses)
- Model Registry
  - Model prefix/exact mapping to provider; preference order; per-call override
- Ergonomics Layer (DX helpers)
  - `ask()`, batch, messages normalization, context binding, `Timeouts`, budgets, typed exceptions
- Streaming Orchestrator
  - Backpressure-friendly iteration; `chunk`/`tool_call`/`usage`/`log` events
- Observability Layer
  - Metrics counters/histograms; optional OTel/StatsD exporters; structured logs
- Prompt API
  - Prompt-as-a-function (templates, defaults, typed placeholders, streaming)
- Reliability & Controls
  - Timeouts, retries with jittered backoff, idempotency, token/cost budgets
- Extensibility Points
  - Cache interface; tokenizer & pricing registries; middleware hooks

---

## L3 — Key Components

Core Client
- `Fiber`: configuration, context binding, call routing
- Chat API: `chat()`, `chat_stream()`, sync mirrors; normalized `ChatResult`
- Message Normalizer: flexible input normalization (str/tuples/helpers)

Provider Adapters
- `Provider` interface: `prepare()`, `invoke()`, `parse()`, `stream()`
- Built-ins: `OpenAIAdapter`, `AnthropicAdapter`, `GeminiAdapter`

Routing
- `ModelRegistry`: prefix/exact model mapping; preference order; per-call override

DX Helpers
- `ask()`, `batch_chat()`, `bind()`, `Timeouts`, `retry_if`, typed exceptions

Streaming
- `StreamEvent`: `chunk` | `tool_call` | `usage` | `log` with timestamps
- Histograms for TTFB and overall latency

Prompt API
- `Prompt`, `PromptDefaults`; `call()/acall()`, `stream()`
- Prompt compilation to normalized messages at call time

Observability
- Metrics: `request_count`, `error_count`, `retry_count`, `latency_ms`, `ttfb_ms`, `tokens_*`, `estimated_cost_usd`
- Logging: stdlib logger by default; optional `structlog` support

Controls
- `Timeouts(connect, read, total)`; retries (capped, jittered exponential backoff)
- Budgets: token budgets, cost ceilings (soft-stop or preflight)

Extensibility
- Cache adapters (planned): memory, filesystem, Redis
- Tokenizer adapters (optional): e.g., `tiktoken`
- Pricing registry with TTL refresh and overrides

---

## Interfaces (Public API Summary)

Primary entrypoint
- `Fiber(default_model=None, api_keys=None, base_urls=None, timeout=Timeouts(total=30), metrics=None, logger=None, ...)`
- `Fiber.from_env(default_model=None, prefer=("openai","anthropic","gemini"))`

Calls
- `chat(model, messages, temperature=None, max_tokens=None, seed=None, tools=None, timeout_s=None, idempotency_key=None) -> ChatResult`
- `chat_stream(...) -> async iterator[StreamEvent]`

Sync wrappers
- `fiber.sync.chat(...)`
- `fiber.sync.ask(...)`
- `fiber.sync.chat_stream(...)`

Types
- `ChatMessage.system|user|assistant|tool(...)`
- `ChatResult`: `text`, `tool_calls`, `finish_reason`, `usage`, `raw`
- `StreamEvent`: `chunk` | `tool_call` | `usage` | `log`
- `Usage`: `prompt`, `completion`, `total`, `cost_estimate`

Reliability & budgets
- Retries with jittered backoff; error classification by HTTP status/provider codes
- `Timeouts`, idempotency keys (when provider supports)
- Token/cost budgets (optional)

More details are in feature pages under `docs/features`.

---

## Key Flows

1) Providerless `ask()`

    from llm_fiber import Fiber

    fiber = Fiber.from_env(default_model="gpt-4o-mini")
    text = fiber.sync.ask(
        "Give me 3 bullet points about fiber optics.",
        temperature=0.2,
        max_tokens=120,
    )
    print(text)

2) Streaming (async)

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

3) Prompt-as-a-function

    from llm_fiber import Fiber, Prompt, PromptDefaults

    fiber = Fiber.from_env(default_model="gpt-4o-mini")

    summarize = Prompt(
        template="You are concise. Summarize: {text}",
        inputs=["text"],
        defaults=PromptDefaults(
            model="claude-3-haiku-20240307",
            temperature=0.2,
            max_tokens=150,
        ),
    )

    res = summarize.call(fiber, text="Fiber optics transmit light through strands of glass or plastic...")
    print(res.text)

---

## Quality Attributes (NFRs)

- Throughput and latency (async-first, streaming, low overhead)
- Reliability (timeouts, retries, idempotency)
- Observability (metrics/logs/traces; redaction; correlations)
- Extensibility (providers, caches, tokenizers, pricing)
- Predictability (typed results, consistent errors, deterministic keys)
- Small core dependency footprint

---

## C4-lite: Module (L4) Sketch

Proposed package layout (illustrative):

    src/llm_fiber/
      __init__.py
      fiber.py            # Fiber client, sync wrappers, binding
      types.py            # ChatMessage, ChatResult, StreamEvent, Usage, exceptions
      timeouts.py         # Timeouts type
      retry.py            # retry/backoff policy + hooks
      routing.py          # ModelRegistry + provider inference
      providers/
        base.py           # Provider interface
        openai.py         # OpenAI adapter
        anthropic.py      # Anthropic adapter
        gemini.py         # Gemini adapter
      streaming.py        # iterator, event shaping, backpressure
      prompt.py           # Prompt API
      observability/
        metrics.py        # counters/histograms, exporters (extras)
        logging.py        # structured logging helpers
      cache/
        base.py           # cache interface (planned)
        memory.py         # in-memory adapter (planned)
      tokens/
        base.py           # tokenizer adapter (optional)
        tiktoken.py       # tiktoken adapter (optional)
      pricing/
        registry.py       # pricing tables and TTL refresh (planned)

---

## Navigation

- Features:
  - Transport/Core API — docs/features/transport.md
  - Streaming — docs/features/streaming.md
  - Ergonomics (DX) — docs/features/ergonomics.md
  - Prompt API — docs/features/prompt-api.md
  - Model Registry & Routing — docs/features/model-registry.md
  - Supported Providers — docs/features/providers.md
  - Observability — docs/features/observability.md
  - Configuration — docs/features/configuration.md
  - Retries & Budgets — docs/features/retries-and-budgets.md
  - Caching — docs/features/caching.md
  - Capabilities & Pricing — docs/features/capabilities-and-pricing.md

- Architecture Decision Records (ADRs): docs/adrs
- Project Roadmap: docs/roadmap.md

---

## Glossary

- Chunk: an incremental streamed piece of assistant output
- TTFB: time to first streamed token
- Budget: token or monetary limit for a single call
- Providerless: provider inferred from model name, not specified explicitly
