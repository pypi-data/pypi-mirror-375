# llm-fiber Roadmap (to v1)

Status: living document
Source of truth: aligned with ADR-0001 “Project Scope and C4-lite Documentation Structure”

This roadmap translates the vision in the README into concrete, staged milestones with crisp acceptance criteria. It follows our C4-lite framing:
- L1 Context: a thin, fast, observable Python library between your app and multiple LLM providers.
- L2 Containers: Core Client, Provider Adapters, Model Registry, Ergonomics, Streaming, Observability, Prompt API, Reliability/Controls, Extensibility.
- L3 Components: `Fiber`, provider adapters, `ModelRegistry`, `Prompt`, streaming/event types, metrics/logging, retries/timeouts, budgets, pricing/capabilities.
- L4 Modules: see docs/index.md “Module (L4) Sketch”.

References:
- Features:
  - Transport/Core API — features/transport.md
  - Streaming — features/streaming.md
  - Ergonomics (DX) — features/ergonomics.md
  - Prompt API — features/prompt-api.md
  - Model Registry — features/model-registry.md
  - Providers — features/providers.md
  - Observability — features/observability.md
  - Configuration — features/configuration.md
  - Retries & Budgets — features/retries-and-budgets.md
  - Caching (planned) — features/caching.md
  - Capabilities & Pricing — features/capabilities-and-pricing.md
- Architecture decisions:
  - ADR-0001 — adrs/0001-project-scope-and-docs-structure.md

---

## Versioning and Stability Plan

- Pre-1.0 (v0.x): API can evolve. Breaking changes allowed with clear release notes and migration notes. Maintain best-effort stability for core types (`ChatResult`, `StreamEvent`, `Usage`) and method signatures.
- v1.0: Public APIs stabilized:
  - `Fiber`: constructor, `from_env`, `chat`, `chat_stream`, sync mirrors, `bind`.
  - Prompt API: `Prompt`, `PromptDefaults`, `call/acall`, `stream`.
  - Types: `ChatMessage`, `ChatResult`, `StreamEvent`, `Usage`, typed exceptions.
  - Model Routing: `ModelRegistry` surface.
  - Observability metric names and labels finalized.
  - Backward compatibility policy (SemVer): breaking changes require major release.

---

## Milestones

### v0.1 — MVP (Foundations)

Scope
- Providers: OpenAI, Anthropic, Google Gemini (public endpoints).
- Transport/Core API:
  - Async `chat()` and `chat_stream()` with normalized `ChatResult` and `StreamEvent`.
  - Sync wrappers (`fiber.sync.*`).
  - Messages normalization (helpers, tuples, bare strings).
- Providerless routing:
  - Small default model→provider registry; per-call override.
- Reliability:
  - `Timeouts(connect, read, total)`; retries with capped jittered backoff.
  - Typed exceptions (`FiberError` and specializations).
  - Idempotency key passthrough (if provider supports).
- Ergonomics:
  - `from_env`, `ask`, context `bind`, minimal batch helper (async path acceptable).
- Observability:
  - In-memory metrics, structured logging; histogram for latency and TTFB.
  - Usage propagation; basic token counts when provider reports.
- Docs:
  - C4-lite index and core feature pages complete.
- Tooling:
  - CI (tests, lint, type-check), editable install; pre-commit.

Acceptance Criteria
- “Hello world” works on each provider with real credentials.
- Streaming prints deltas in order; TTFB recorded.
- Retry classification covers timeouts, 429, 5xx; no retry on auth errors.
- Metrics counters/histograms present and labeled with provider/model.
- Minimal examples run from docs (Transport, Streaming, Ergonomics, Prompt API).
- Coverage ≥ 80% for core paths; type checks pass on strict mode for public interfaces.

Risk/Notes
- Tool/function call normalization deferred (placeholder `tool_call` event OK).
- Token usage/cost may be missing for streamed responses (provider limitation).

Related docs: features/transport.md, features/streaming.md, features/ergonomics.md, features/providers.md, features/observability.md, features/retries-and-budgets.md


### v0.2 — Tooling, Caching, Cost Controls

Scope
- Tool/function calling:
  - First normalization pass (non-breaking extension to `StreamEvent`).
  - Basic aggregator guidance in docs (still labeled “evolving”).
- Batch helpers:
  - Async and sync mirrors (where feasible), concurrency cap, `return_exceptions`, `fail_fast`.
- Caching (phase 1):
  - Deterministic keys over normalized requests.
  - Memory adapter (LRU+TTL) with policy (“off”, “read_through”, “write_through”).
  - Metrics for hit/miss/write/evict; fail-open on adapter errors.
- Pricing & budgets:
  - Pricing registry (static table + override API).
  - `cost_ceiling_usd` enforced with conservative preflight where possible.
- Streaming:
  - Event semantics clarified for tool-call deltas; docs updated.
- Docs/ADRs:
  - ADR for tool/function normalization V1.
  - Caching feature doc finalized (phase 1).

Acceptance Criteria
- Tool-call demo across at least OpenAI+Anthropic, surfaced as normalized events.
- Cache: reproducible hits on identical normalized calls; memory adapter stable under concurrency.
- Cost ceiling: preflight rejection when clearly unsatisfiable; deterministic error type.
- Metrics: cache_* counters visible; pricing estimates visible on `Usage` when known.
- Coverage ≥ 85% core + caching; tool-call paths unit-tested with fakes.

Related docs: features/caching.md, features/capabilities-and-pricing.md, features/streaming.md


### v0.3 — Structured Outputs, Tracing, Expanded Cache

Scope
- Structured outputs (optional extra):
  - `result.json(parse=MyModel)` using `pydantic-core` if installed.
  - Deterministic failure (`FiberParsingError`) when parse requested without dependency.
- Observability:
  - OpenTelemetry spans/metrics correlation; recommended attributes documented.
- Caching (phase 2):
  - Filesystem adapter (optional compression) and Redis adapter (TTL, namespace).
- Capabilities:
  - `capabilities(model)` returns flags and pricing info when known (cached).
- Model registry enhancements:
  - Improved diagnostics on unknown/ambiguous models; preference order behavior documented and tested.

Acceptance Criteria
- Structured output parse flow covered with/without extra installed; clear error path.
- OTel spans visible with provider/model attributes; TTFB event recorded.
- Filesystem/Redis cache adapters pass reliability and concurrency tests; metrics emitted.
- Capability query returns sensible defaults and pricing where available.

Related docs: features/observability.md, features/capabilities-and-pricing.md


### v1.0 — Stabilization and Hardening

Scope
- API freeze on public surfaces:
  - `Fiber`, sync wrappers, Prompt API, ModelRegistry, typed exceptions, types.
- Observability contracts:
  - Metric names and labels finalized; span/attribute names documented.
- Performance & reliability targets:
  - Baseline throughput (single-process async) documented for typical prompts.
  - p95 end-to-end latency and p99 TTFB SLIs captured in CI perf smoke (best-effort).
- Docs completeness:
  - All feature pages reviewed; examples runnable; “Known limitations” sections up-to-date.
  - README trimmed; points to docs; quickstart polished.
- Quality gates:
  - Coverage ≥ 90% (core and adapters).
  - Type checks strict on public modules.
  - Changelog and migration notes where any behavior changed since v0.3.

Acceptance Criteria
- Golden test suite across providers (smoke + streaming + tool-call + budgets).
- No open TODOs on public API surface.
- Backwards-compatible from v0.3 except for explicitly documented removals.

---

## Cross-Cutting Tracks

Observability (all milestones)
- Metrics: request_count, error_count, retry_count, latency_ms, ttfb_ms, tokens_*, estimated_cost_usd, cache_*.
- Logging: stdlib by default, structlog optional; redaction and context binding.
- OTel: spans+metrics optional (v0.3), correlation with bound context.

Reliability & Controls
- Budget semantics documented; deterministic failure modes.
- Idempotency passthrough clarified per provider.

Performance (ongoing)
- Backpressure correctness (streaming); no unbounded buffers.
- Minimal per-token overhead; small allocation profile.

Security
- No secrets in logs/metrics/cache keys/values.
- Optional cache encryption at rest (filesystem; backlog).

Docs & Tooling
- Docs tracked with features and ADRs; PR checklist includes docs touch.
- CI: tests, type check, lint, coverage; release flows (Trusted Publishing).

---

## Out of Scope (for v1)

- Heavy framework integrations (FastAPI/Flask plugins, etc.) — can live as separate packages.
- Complex prompt templating engines (conditionals/loops) — keep Prompt API simple.
- Broad provider matrix beyond OpenAI/Anthropic/Gemini initial adapters (e.g., bedrock, local runtimes) — may come post-v1.

---

## Backlog / Nice-to-Have

- Vertex AI compatibility mode for Gemini (auth/base URL parity).
- Request coalescing (in-flight dedupe) for identical calls.
- SWR (stale-while-revalidate) cache policy; async refresh.
- CLI utilities for quick smoke tests and benchmarking.
- More granular tool/function normalization (streaming arguments typing).
- Test fixtures/fakes packages for provider behavior.

---

## Release Cadence and Process

- Cadence: timeboxed minor releases roughly every 3–6 weeks in v0.x; v1 targeted when acceptance criteria met.
- Each release:
  - Update CHANGELOG, docs, and (if needed) ADRs.
  - Tag with SemVer; build wheels/sdist; publish via GitHub Actions.
  - Run compatibility smoke across supported Python versions and providers.

Release Checklist
- Tests green (unit/integration), coverage gate met.
- Type checks and lint pass.
- Docs updated: relevant feature pages, examples runnable.
- Metrics/OTel schema changes documented (if any).
- ADR added/updated if architecture or public API changed.

---

## Acceptance Test Matrix (summary)

- Providers: openai, anthropic, gemini (public endpoints; mock/fake variant in CI).
- Modes:
  - Non-streaming: simple Q&A; budgets; timeouts; retryable vs non-retryable errors.
  - Streaming: ordering, TTFB measured, cancellation behavior, final usage (if available).
  - Tool/function (v0.2+): event aggregation and completeness.
- Routing: default registry mapping, exact/prefix, preference order, per-call override precedence.
- Caching (v0.2+): deterministic hit/miss, TTL expiry, adapter fail-open behavior.
- Observability: metrics counters and histograms emitted; log fields; optional OTel spans.

---

## Migration Guidance (pre-v1)

- Breaking changes will be called out in the CHANGELOG under “Breaking”.
- Where possible, deprecations will be introduced before removal with clear alternatives.
- Public surfaces targeted for stability are listed in “Versioning and Stability Plan”.

---

## Links

- Architecture overview — docs/index.md
- ADRs — docs/adrs
- Feature docs — docs/features
