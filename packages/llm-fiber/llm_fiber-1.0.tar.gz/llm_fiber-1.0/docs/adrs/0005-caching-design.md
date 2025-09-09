# ADR 0005: Caching Design (Deterministic Read/Write-Through Cache)

- Status: Proposed
- Date: 2025-09-06
- Authors: Aimless
- Deciders: Aimless
- Tags: caching, performance, determinism, keys, adapters, policy, streaming, observability

## Context

llm-fiber aims to be a thin, fast, observable client across LLM providers. Some workloads (dashboards, CI-like checks, idempotent content generation) can benefit substantially from caching identical requests to reduce latency, cost, and rate-limit pressure.

The README and feature docs outline a planned cache:
- Deterministic keys derived from normalized requests (provider-agnostic).
- Optional policies (“off”, “read_through”, “write_through”).
- Pluggable adapters (memory, filesystem, Redis).
- Safe-by-default mindset (no secrets in keys/values, fail open).
- Strong observability (hits, misses, writes, evictions).

See also:
- docs/features/caching.md (planned design)
- ADR-0001 Project Scope and C4-lite Docs Structure
- ADR-0004 Observability Schema and Exporters

This ADR codifies the intent and open questions before the first implementation lands.

## Problem

- Latency/cost pressure for repeated, identical requests.
- Rate limiting under bursty traffic.
- Need for deterministic behavior across providers with a normalized transport layer.
- Safety/side-effect concerns around caching, especially with tool/function calls.

## Goals

- Deterministic cache keys based on normalized requests (canonicalization).
- Predictable cache policies: off, read_through, write_through.
- Pluggable adapters with simple, stable interfaces.
- Fail-open behavior: cache failures must not fail requests.
- Zero secrets in keys/values; support TTL/capacity constraints.
- Clear observability: hit/miss/write/evict metrics; concise logs.
- Minimal coupling to provider-specific payloads.

## Non-goals (initial)

- Mid-stream caching of partial outputs (only cache terminal results for non-streaming initially).
- Request coalescing / in-flight deduplication.
- Schema migration of on-disk cache entries across breaking changes (use versioned keys).

## Decision (Proposed)

Introduce a cache layer under the transport boundary:

1) Canonical Keys
- Build a canonical JSON payload from the normalized request after all merges (client defaults, prompt defaults, per-call args).
- Include fields that change semantics (provider, model, normalized messages, sampling params, tool specs, response format flags, etc.).
- Exclude fields that don’t affect semantics (timeouts, budgets, idempotency keys, observability context).
- Serialize with sorted keys and no whitespace; produce a digest (e.g., SHA-256).
- Prefix with a schema version (e.g., lf:v{schema_v}:{digest}) to enable safe invalidation.

2) Values
- Store a compact, provider-agnostic representation of ChatResult:
  - text, tool_calls (normalized), finish_reason, usage (tokens/cost), created_at, provider/model echo.
  - Optional: raw provider payload (off by default).
- No secrets persisted. Keep values small.

3) Policies
- off (default): no cache reads/writes.
- read_through: attempt read; on miss, call provider but do not write.
- write_through: attempt read; on miss, call provider and write on success.
- Future optional modes (deferred): refresh, read_only, stale-while-revalidate.

4) Adapters
- Memory (LRU+TTL).
- Filesystem (file-per-key; TTL via metadata; optional compression).
- Redis (TTL; namespace).
- Common interface: get/set/delete/clear/close; adapter errors are logged and ignored (fail open).

5) TTL, Capacity, Invalidation
- Per-entry TTL optional; adapter-level defaults permitted.
- Memory adapter uses capacity-bounded LRU eviction.
- Global invalidation by bumping schema_v.
- Manual invalidation via delete/clear; namespaces for isolation (adapter-dependent).

6) Streaming
- v0.2: Cache only non-streaming results.
- v0.3+: Optional write of final assembled streamed results for reuse in non-streamed calls (opt-in, to be evaluated).

7) Safety & Side Effects
- Default behavior: cache pure chat responses only.
- Tool/function calls:
  - Either disable caching for requests that can trigger side effects, or
  - Require explicit opt-in with strict keying (tool spec + args) and “side_effects_ok=false” guard.
- Operators may set adapter-level policies to disable caching for sensitive flows.

8) Observability
- Metrics: cache_hit_count, cache_miss_count, cache_write_count, cache_evict_count (+ latency for get/set where supported).
- Logs: concise hit/miss/write entries with key digest and policy; WARN on adapter errors; DEBUG for canonicalization when enabled.

9) Compatibility
- schema_v embedded in key prefix; changing canonicalization increments schema_v (global invalidation).
- Adapters must tolerate unknown versions (just produce misses).

## Rationale

- Deterministic keys ensure provider-agnostic correctness and portability.
- Simple policies support common needs; more sophisticated behavior (SWR, coalescing) can be added later.
- Fail-open avoids availability impact.
- Observability provides immediate feedback to tune TTL/capacity and detect drift.
- Deferring streamed caching reduces complexity and correctness risks initially.

## Alternatives Considered

- Caching partial streamed deltas mid-call:
  - Rejected initially: complexity and correctness concerns; limited utility vs final result caching.
- Embedding cache inside provider adapters:
  - Rejected: duplicates concerns across adapters; less consistent semantics; weaker determinism.
- Using fuzzy keys (e.g., approximate prompts):
  - Rejected: risks collisions and non-determinism; violates principle of predictable behavior.

## Open Questions

- Key set for tool/function calls:
  - Minimum fields to guarantee idempotence and avoid stale/tool-side effects?
- Raw payload storage:
  - Do we allow adapter-level gating for raw-in-value? Default stays “off”.
- TTL defaults:
  - Reasonable defaults per adapter? Global vs per-model?
- Compression for filesystem:
  - Worth the CPU cost for typical value sizes?
- Namespacing strategy:
  - Drill-down by provider/model vs one global namespace?
- Streamed write-back (v0.3):
  - Should streamed final results populate non-stream cache by default or be opt-in?

## Risks

- Key drift leading to low hit rates if canonicalization is too sensitive.
- Silent staleness if TTLs are too long and models change behavior.
- Over-caching with tool calls causing unintended side effects.
- Adapter outages causing increased provider load (mitigated by fail-open + observability).

## Migration / Rollout

- v0.2: Memory adapter + policies; default off. Gate behind explicit client configuration.
- v0.2.x: Filesystem + Redis adapters; docs/examples; metrics dashboards.
- v0.3: Optional streamed write-back and additional policies (SWR), pending validation.

## Test Strategy (High-level)

- Canonicalization determinism across processes and platforms.
- Include/exclude list correctness for key derivation.
- Adapter conformance (get/set/delete/clear), TTL/eviction behavior, concurrency safety.
- Fail-open behavior when adapter is unavailable.
- Observability counters: hits/misses/writes/evictions reflect reality.
- Performance baselines: overhead vs no-cache and provider calls.

## Observability

- Metrics per ADR-0004; ensure stable names/labels.
- INFO on hit/miss/write; WARN on adapter errors; DEBUG for key details (redacted).
- Document recommended dashboards: hit ratio, miss ratio, write rate, evictions, cache latency.

## References

- docs/features/caching.md
- ADR-0001 Project Scope and C4-lite Docs Structure
- ADR-0004 Observability Schema and Exporters
