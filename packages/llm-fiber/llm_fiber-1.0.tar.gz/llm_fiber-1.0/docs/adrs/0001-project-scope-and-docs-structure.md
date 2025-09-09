# ADR 0001: Project Scope and C4-lite Documentation Structure

- Status: Accepted
- Date: 2025-09-06
- Authors: Aimless
- Deciders: Aimless
- Tags: docs, architecture, C4, scope, roadmap

## Context

The initial `README.md` is comprehensive but has grown too large and mixes multiple concerns (vision, API reference, examples, architecture, roadmap, tooling). This makes it harder to navigate, onboard contributors, and evolve the documentation alongside the code.

We need a durable, navigable documentation structure that:
- Presents a clear architectural view (what the library is and how it fits into the ecosystem).
- Separates features into focused pages.
- Records architectural decisions and their rationale.
- Guides the roadmap to an initial stable v1 release target.

The team prefers pragmatic documentation with low ceremony and high signal. Full C4 with detailed diagrams is not required; a C4-lite narrative format suffices.

## Decision

Adopt a C4-lite documentation structure and explicitly scope the project toward a lean v1:

1) Documentation layout under `docs/`
   - `docs/index.md` — primary entry point with a C4-lite overview:
     - L1 System Context
     - L2 Containers (library subsystems)
     - L3 Key Components
     - L4 module sketch (non-authoritative)
     - Navigation to feature pages, ADRs, and roadmap
   - `docs/features/` — one page per feature/topic:
     - `transport.md` — core/transport API
     - `streaming.md` — streaming model and semantics
     - `ergonomics.md` — DX helpers (ask/batch/bind), results, parsing
     - `prompt-api.md` — prompt-as-a-function
     - `model-registry.md` — provider inference/routing
     - `providers.md` — supported providers and notes
     - `observability.md` — metrics/logging/tracing
     - `configuration.md` — env/constructor/defaults/overrides
     - `retries-and-budgets.md` — timeouts/retries/idempotency/budgets
     - `caching.md` — design (planned)
     - `capabilities-and-pricing.md` — capability flags and cost estimates
   - `docs/adrs/` — Architecture Decision Records
     - `0001-project-scope-and-docs-structure.md` (this ADR)
     - Future ADRs incrementally numbered
   - `docs/roadmap.md` — phased delivery to v1 with milestones based on MVP → v0.2 → v0.3 → v1 progression

2) C4-lite approach
   - Use concise narrative form to describe System Context (L1), Containers (L2), Components (L3).
   - Include an L4 module sketch in text to keep costs low; diagrams optional.
   - Keep the documentation readable in GitHub without requiring a site generator; optionally publish with MkDocs later.

3) Scope toward v1 (high-level)
   - Deliver a thin, fast, observable Python client for multi-provider LLM chat with first-class streaming and minimal dependencies.
   - MVP (v0.1): OpenAI/Anthropic/Gemini adapters; async transport and streaming (with sync wrappers); retries/timeouts/basic budgets; built-in metrics and structured logging; usage propagation; basic token counts when available.
   - v0.2: tool/function calling normalization; cache adapters; batch helpers; cost ceilings and improved pricing registry; improved streaming event semantics.
   - v0.3: structured outputs (optional extra); OTel traces correlation; polish.
   - v1: stabilize APIs, docs, and observability interfaces; compatibility guarantees per SemVer for public APIs and event/type shapes.

4) Documentation principles
   - Single source of truth: feature definitions live in `docs/features/`; `index.md` provides the high-level map.
   - Code-first: feature pages align with package/module names and public API semantics.
   - Examples: keep short, runnable snippets that reflect the actual API.
   - Observability-first: document metrics/logging/tracing for every critical flow.
   - Non-goals explicitly called out to reduce ambiguity.

5) ADR policy
   - Record decisions that materially affect public APIs, provider contracts, streaming semantics, observability schema, budgets/retries behavior, or the docs structure.
   - Keep ADRs short; prefer decision/rationale/consequences over design treatises.
   - Status transitions: Proposed → Accepted/Rejected → Superseded (when applicable).

## Status

Accepted. Initial structure created:
- `docs/index.md`
- Feature pages under `docs/features/`
- `docs/adrs/0001-project-scope-and-docs-structure.md`
- `docs/roadmap.md`

## Consequences

Positive:
- Easier navigation and onboarding; clear separation of concerns.
- Faster iteration on feature pages without bloating the README.
- Decision trail via ADRs increases maintainability and team alignment.
- Clear path from MVP to v1 with staged milestones.

Negative/Risks:
- Requires discipline to keep docs in sync with code.
- More files to touch per change (feature page + ADR when applicable).
- Without automated docs checks, drift may occur.

Mitigations:
- Add a PR checklist item: “Updated relevant feature page(s) and ADRs?”
- Document owners: assign maintainers for each feature page.
- Periodic docs review (release milestone gates).

## Options Considered

1) Keep a monolithic `README.md`
   - Pros: single file, easy to link.
   - Cons: unscalable as features grow; discoverability suffers; harder to maintain architecture overview.

2) Full C4 with detailed diagrams
   - Pros: highly expressive and communicative visual model.
   - Cons: higher overhead; diagrams drift risk; slows iteration; not necessary at current scope.

3) Sphinx + reStructuredText for full documentation
   - Pros: powerful ecosystem for large projects.
   - Cons: higher ceremony; less frictionless for quick edits; overkill for a lean library.

4) MkDocs + mkdocstrings with the same structure (optional later)
   - Pros: good balance; easy publishing.
   - Cons: build step adds complexity; not required immediately.

Decision: C4-lite with Markdown in-repo now; optionally add MkDocs later.

## Detailed Structure

- `docs/index.md`
  - L1: System Context (llm-fiber within app and providers)
  - L2: Containers (core client, providers, model registry, ergonomics, streaming, observability, prompt API, reliability/budgets, extensibility)
  - L3: Key Components (primary classes/types and responsibilities)
  - L4: Module sketch (illustrative; not normative)
  - Navigation to features, ADRs, roadmap

- `docs/features/`
  - `transport.md`: `Fiber` entry points (`chat`, `chat_stream`), normalized types (`ChatResult`, `StreamEvent`, `Usage`), messages normalization, timeouts/retries/idempotency, budgets, raw escape hatch, sync wrappers, observability.
  - `streaming.md`: event model (`chunk`/`tool_call`/`usage`/`log`), ordering/TTFB, backpressure/cancellation, timeouts, errors/retries (no mid-stream retry), observability.
  - `ergonomics.md`: `from_env`, `ask`, batch helpers, context binding, budgets, results & parsing (`pydantic-core` extra), typed exceptions, sync mirrors, best practices.
  - `prompt-api.md`: prompt-as-a-function model, `Prompt`/`PromptDefaults`, call/stream variants, templating, overrides, budgets, structured outputs.
  - `model-registry.md`: prefix/exact mapping, preference order, provider override precedence, testing and best practices.
  - `providers.md`: OpenAI/Anthropic/Gemini specifics, base URLs, auth, streaming notes, tool calls state, idempotency, pricing caveats.
  - `observability.md`: metrics, logging, OTel/StatsD exporters, context binding, sampling and cardinality, security and privacy.
  - `configuration.md`: env vs constructor, defaults/precedence, per-call controls, provider endpoints, model routing setup.
  - `retries-and-budgets.md`: `Timeouts`, retry classification/jitter/backoff, idempotency keys, token/cost budgets, observability, troubleshooting.
  - `caching.md`: planned design for deterministic keys, adapters (memory/fs/redis), policies, TTL/eviction, safety, observability, roadmap.
  - `capabilities-and-pricing.md`: capability taxonomy and query, pricing registry, estimation formula, overrides and TTL refresh, observability.

- `docs/adrs/`
  - ADRs using `NNNN-title.md`, where NNNN is zero-padded sequence (e.g., `0002-...`)

- `docs/roadmap.md`
  - Phased milestones: v0.1 (MVP), v0.2, v0.3, v1 criteria
  - Links to feature pages and ADRs

## Scope Toward v1 (summarized)

Must-have before v1:
- Core multi-provider chat and streaming with normalized types.
- Provider inference via model registry with override.
- Observability: request metrics, latency/TTFB histograms, error/retry counters; structured logs; optional OTel/StatsD exporters.
- Reliability: explicit timeouts; retries with capped jittered backoff; idempotency pass-through.
- Ergonomics: `from_env`, `ask`, message normalization, context binding; typed exceptions.
- Prompt API: minimal, stable prompt-as-a-function with defaults and streaming.
- Capabilities query and basic pricing estimates; budgets (tokens and cost).
- Documentation: C4-lite index + feature pages, ADRs, roadmap.

Nice-to-have by v1 (if time permits; else v1.x):
- Tool/function calling normalization.
- Basic caching (memory) with deterministic keys.
- Structured outputs (optional extra) and traces correlation.

Out-of-scope for v1 (explicit non-goals):
- Heavy framework integrations.
- Complex diagram maintenance; non-essential generators.
- Broad provider surface beyond OpenAI/Anthropic/Gemini initial adapters.

## Decision Drivers

- Developer experience: simple, consistent API across providers.
- Performance: async-first, streaming, low overhead.
- Observability: insightful metrics/logs with minimal setup.
- Maintainability: clear boundaries and decision traceability.
- Minimal dependencies in core; extras for integrations.

## Trade-offs

- C4-lite favors speed and text clarity over visual diagrams; easier to evolve, less visual fidelity.
- Splitting docs increases file count but enhances discoverability.
- Deferring full tool/function normalization to post-MVP reduces complexity now at the cost of initial feature breadth.

## Adoption Plan

- Port relevant parts of `README.md` into `docs/index.md` and feature pages.
- Keep `README.md` short: purpose, install, quickstart, and link to `docs/`.
- Add PR checklist entries:
  - “Updated feature docs?”
  - “Requires ADR?” If yes, add `docs/adrs/NNNN-...`.
- Review docs at each milestone (v0.1, v0.2, v0.3, v1), updating roadmap and ADRs.

## Unresolved Questions

- Whether to publish with MkDocs initially or defer until v0.2.
- The detailed schema for tool/function calling normalization (post-MVP).
- Exact tokenizer/pricing sources and refresh cadence (configurable via registry; finalize in v0.2).

## References

- Project `README.md` (source of initial content and roadmap)
- C4 Model (Simon Brown): used as inspiration; we apply a narrative “lite” variant.
