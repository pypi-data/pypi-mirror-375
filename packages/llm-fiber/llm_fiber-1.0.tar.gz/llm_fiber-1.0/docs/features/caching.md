# Caching (planned)

Status: Planned for v0.2–v0.3. This page captures the intended design and contracts for a pluggable, deterministic cache layer in llm-fiber.

llm-fiber will support read-through and write-through caching for normalized chat results. The cache is optional, disabled by default, and designed to be deterministic, portable across providers, and easy to operate.

---

## Goals

- Reduce latency, cost, and rate-limit pressure by reusing identical results
- Deterministic keys based on normalized requests (provider-agnostic)
- Predictable cache policies (off, read-through, write-through)
- Pluggable adapters (in-memory, filesystem, Redis)
- Safe-by-default: no secrets in keys/values; explicit opt-in for non-pure flows
- Strong observability for cache hits/misses/evictions

## Non-goals (initially)

- Caching partial streams mid-flight (only cache terminal results)
- Cross-request dedupe of in-flight calls (future: request coalescing)
- Automatic schema migration of stored values across breaking changes (use versioned keys)

---

## High-level design

- The cache sits below the public API, in the Transport layer boundary, after input normalization and before provider invocation.
- Cache keys are derived from a canonical, minimized representation of the normalized request.
- Values are a compact, provider-agnostic serialization of the normalized ChatResult (and optionally the provider raw payload).
- Policies regulate whether reads and/or writes consult the cache.
- The cache is purely a performance/cost optimization; correctness assumes chat calls are pure functions of inputs.

---

## Cache keys

Deterministic keys are computed from a canonical JSON representation of the normalized request, then hashed.

Included fields (affect semantics and must be part of the key):
- provider (resolved)
- model (resolved)
- normalized messages (roles, content, order)
- temperature, top_p (when supported), max_tokens, seed
- tool/function spec (when present), tool choice setting (if any)
- response format mode (e.g., JSON mode) when applicable
- prompt defaults that affect the resulting request shape (post-merge)
- library cache schema version (e.g., schema_v)

Excluded fields (should not affect semantics):
- timeouts (connect/read/total)
- retry config and backoff parameters
- budgets (token_budget, cost_ceiling_usd)
- idempotency_key
- observability fields (context, bind fields)
- request_id, correlation IDs

Key structure (conceptual):
- Step 1: Build canonical payload: stable dict with sorted keys and normalized message structure
- Step 2: Serialize to JSON with sorted keys, no whitespace
- Step 3: Compute digest (e.g., SHA-256), final key = "lf:v{schema_v}:{digest}"

Notes:
- schema_v increments when the cache schema or canonicalization changes.
- Tool calling remains in flux post-MVP. For safety, include tool spec and tool selection policy in keys; consider disabling caching when tool execution has side effects (see Safety).

---

## Cache values

Store a compact representation of the normalized result:
- text (final assistant output)
- tool_calls (provider-agnostic shape, may evolve)
- finish_reason (normalized enum)
- usage (tokens_in, tokens_out, tokens_total, cost_estimate when known)
- created_at (timestamp)
- provider/model echo (for validation)
- optional: raw (provider payload) — off by default to minimize size and coupling

Value constraints:
- No secrets
- Prefer forward-compatible structure gated by value_schema_v
- Keep small; target sub-10KB for typical results (depends on output size)

---

## Policies

- off (default): never read/write cache
- read_through: check cache; if hit, return value; if miss, invoke provider and return without writing
- write_through: check cache; if miss, invoke provider and write the result on success

Optional modes (later):
- refresh: bypass read but write new value (for rewarming content)
- read_only: read if present, never call provider (useful in offline or integration tests)
- stale_while_revalidate (SWR): return stale hit and revalidate asynchronously (advanced)

Configuration points:
- Client-level default policy: `Fiber(cache_policy="off"|"read_through"|"write_through")`
- Per-call override: `cache_policy=...`

---

## Adapters

Initial adapters (planned):
- memory: process-local, size/TTL-bounded LRU
- filesystem: directory-backed, file-per-key, TTL via metadata; optional compression
- redis: shared, TTL-based; optional namespaces; support for basic metrics

Adapter interface (conceptual):
- get(key: str) -> Optional[CacheValue]
- set(key: str, value: CacheValue, ttl_s: Optional[int] = None) -> None
- delete(key: str) -> None
- clear() -> None
- close() -> None

Construction:
- `Fiber(cache_adapter=MemoryCache(...), cache_policy="write_through")`
- Or via convenience factory: `Fiber.with_memory_cache(max_entries=10_000, ttl_s=3600, policy="write_through")`

---

## TTL, capacity, and invalidation

- TTL per entry (default none, adapter-specific defaults allowed)
- Capacity limit (LRU/LFU) for in-memory adapter
- Manual invalidation:
  - delete(key) for surgical removal
  - clear() for wholesale flush (e.g., during deploy)
  - schema_v bump to invalidate globally on format changes
- Namespacing:
  - Key prefix includes schema version; adapters may support additional namespaces per model/provider

---

## Streaming

Policy for streaming responses:
- Do not emit cached partial chunks mid-call
- Option A (initial): cache non-streaming calls only
- Option B (optional): allow caching the final assembled result of a completed stream
  - Implementation detail: assemble text while streaming; on successful termination, write a value that later powers non-streamed `chat()` or streamed replay as pre-buffered single return (not recommended to fake streaming)

Recommendation for MVP:
- Cache only terminal results from non-streaming calls
- Consider an opt-in to cache completed streams by writing their final result for future non-streamed reuse

---

## Safety and side effects

Cachable by default:
- Pure “chat” responses with no tool calls or with tool calls that are purely informational and included in the model output

Caution or opt-out:
- Tool/function calls with external side effects (DB writes, API calls)
  - Either disable caching for such requests
  - Or include tool arguments and a “side_effects_ok=false” flag in the key policy and require explicit opt-in

Provider drift:
- Model updates can change outputs over time even for identical inputs
- Operators should consider TTL, or pin model versions if strict determinism is required

---

## Observability

Counters/histograms:
- cache_hit_count{provider,model,policy}
- cache_miss_count{provider,model,policy}
- cache_write_count{provider,model}
- cache_evict_count{adapter}
- cache_get_latency_ms, cache_set_latency_ms

Logs:
- INFO on hit/miss with key digest and policy
- WARN on adapter errors (non-fatal; cache failures should not fail requests)
- Optional DEBUG for canonicalization details (guarded by debug flag)

---

## Example usage (conceptual)

Enable memory cache with write-through:

```python
from llm_fiber import Fiber

fiber = Fiber.from_env(
    default_model="gpt-4o-mini",
    # Convenience builder; exact API may vary
    # e.g., fiber.enable_memory_cache(max_entries=10000, ttl_s=3600, policy="write_through")
)
fiber.cache_policy = "write_through"
fiber.cache_adapter = MemoryCache(max_entries=10000, ttl_s=3600)

# First call: miss -> provider -> write
text1 = fiber.sync.ask("Give me 3 bullets about fiber optics.", temperature=0.2)

# Second call (same normalized request): hit -> return cached
text2 = fiber.sync.ask("Give me 3 bullets about fiber optics.", temperature=0.2)
assert text1 == text2
```

Per-call policy override:

```python
# Bypass cache for this call (e.g., user-requested refresh)
res = fiber.sync.chat(messages=["..."], cache_policy="off")

# Read-through only (return cached if present; do not write)
res = fiber.sync.chat(messages=["..."], cache_policy="read_through")
```

Filesystem adapter:

```python
fiber.cache_adapter = FileSystemCache(root_dir="/var/cache/llm_fiber", compress=True)
fiber.cache_policy = "write_through"
```

Redis adapter:

```python
fiber.cache_adapter = RedisCache(url="redis://localhost:6379/0", namespace="llm_fiber")
fiber.cache_policy = "write_through"
```

---

## Testing

- Determinism: given the same normalized request, the computed key must be stable across processes
- Canonicalization: message normalization must collapse equivalent inputs into identical canonical forms
- Exclusion list: verify timeouts, budgets, and idempotency do not affect keys
- Adapters: latency, TTL expiry, eviction behavior, error handling (fail open)
- Concurrency: parallel hits/misses should not corrupt values (adapter-dependent locks/atomicity)
- Backward compatibility: schema_v bump invalidates prior keys; ensure graceful misses

---

## Security and privacy

- Never store secrets in keys or values
- Consider encrypting at rest for filesystem caches (optional)
- PII: cache only when acceptable for your data policy; support adapter-level encryption/slashing if needed
- Ensure OS-level permissions on filesystem directories

---

## Roadmap (tentative)

- v0.2
  - Memory cache (LRU+TTL), read-through and write-through policies
  - Deterministic canonicalization and key hashing
  - Basic metrics for hits/misses/writes/evictions
- v0.2.x
  - Filesystem cache (optional compression), tunable TTL
  - Redis cache (TTL, namespace)
- v0.3
  - Optional stream result caching (post-completion)
  - Request coalescing (in-flight dedupe) — if demand justifies
  - SWR (stale-while-revalidate) policy as opt-in
  - Fine-grained tool-call caching guardrails

---

## Best practices

- Start with write-through memory cache for biggest wins with minimal complexity
- Use TTLs to mitigate model drift and stale content risk
- For critical paths, add request IDs and policy tags to logs for quick cache debugging
- Disable caching when tool calls have side effects or when strict freshness is required
- Prefer exact model versions if you need strong determinism (or keep TTL short)

---

## See also

- Transport/Core API: ./transport.md
- Ergonomics (DX): ./ergonomics.md
- Streaming: ./streaming.md
- Prompt API: ./prompt-api.md
- Model Registry & Routing: ./model-registry.md
- Observability: ./observability.md
- Retries & Budgets: ./retries-and-budgets.md
- Capabilities & Pricing: ./capabilities-and-pricing.md
