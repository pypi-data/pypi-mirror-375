# Observability

First-class observability is a core design goal of llm-fiber. Out of the box you get lightweight, always-on in-memory metrics, structured logs that are easy to wire into your logging strategy, and optional exporters for OpenTelemetry and StatsD/DogStatsD. The aim is to make performance, reliability, and cost visible without imposing heavy dependencies.

This page describes the metrics and logs emitted by the library, how to connect exporters, which labels/attributes are available, how streaming is represented, and recommended practices around sampling and PII redaction.

---

## Goals

- Make latency, TTFB, retries, token usage, and cost visible by default
- Keep core overhead small; enable heavy-duty exporters only when needed
- Provide stable metric names and label sets across providers
- Propagate app context (run/request/tenant IDs) to correlate signals
- Avoid logging secrets by default; support safe redaction

---

## What is instrumented

- Calls (chat and chat_stream) across all providers
- Streaming token delivery (time-to-first-byte vs end-to-end completion)
- Error and retry classification (HTTP status and provider codes)
- Token usage and cost estimation (when data available)
- Optional: Prompt API calls (delegating to the same transport instrumentation)

---

## Metrics

Always-on in-memory metrics are recorded; exporters are optional.

Metric names (stable):
- request_count{provider, model, ok}
- error_count{provider, model, code}
- retry_count{provider, model, reason}
- latency_ms histogram (end-to-end)
- ttfb_ms histogram (time to first streamed chunk)
- tokens_in, tokens_out, tokens_total (counters/gauges per call)
- estimated_cost_usd (gauge per call when pricing known)

Label dimensions:
- provider: "openai" | "anthropic" | "gemini" | custom
- model: model identifier you called (e.g., "gpt-4o-mini")
- ok: "true" | "false" (request_count dimension)
- code: error code/category (e.g., "rate_limited", "timeout", "auth", "http_500")
- reason: retry reason/classification (e.g., "5xx", "rate_limit", "timeout")
- stream: "true" | "false" (optional; indicates streaming)
- finish_reason: normalized end condition, when available (e.g., "stop", "length")
- custom context fields: keys bound via `fiber.bind(...)` may be exported as tags/attributes (see Context Binding)

Timing semantics:
- latency_ms: measures the full span of the call (request→final response or stream termination)
- ttfb_ms: measures time from request start to first streamed chunk only; absent for non-streaming calls

Token/cost semantics:
- tokens_in, tokens_out, tokens_total: based on provider-reported usage; if absent, may be estimated when a tokenizer is available; otherwise null/omitted
- estimated_cost_usd: derived from pricing tables (when available). Treat as an estimate.

Cardinality guidance:
- Prefer small sets for model and provider
- Keep custom tags bounded; avoid high-cardinality values (e.g., raw user IDs)
- Redact long or unique strings; sample if necessary

---

## Logging

llm-fiber works with stdlib logging by default and supports optional structlog integration via an extra. Logs are structured and include correlation fields, timings, and error metadata.

Typical fields in call lifecycle logs (names are representative, actual keys may vary by implementation):
- level: INFO on success; WARN/ERROR on issues
- event: "chat_call", "chat_stream", "retry", "error"
- provider, model
- request_id: short, unique id per call (auto-generated)
- run_id, tenant_id, user-defined fields (when using `fiber.bind(...)`)
- attempt: current attempt number (1-based), total_attempts
- latency_ms, ttfb_ms (if streaming)
- finish_reason (when available)
- tokens_in, tokens_out, tokens_total, estimated_cost_usd (when available)
- error_kind (e.g., FiberTimeout, FiberRateLimited, FiberAuthError, FiberAPIError)
- http_status (when relevant)
- message: concise, actionable message

Redaction:
- API keys and secrets are never logged
- User-supplied fields may be redacted if configured to do so
- Avoid logging raw prompts/responses in production unless explicitly desired and scrubbed

Example (conceptual, stdlib):
    INFO llm_fiber call=chat provider=openai model=gpt-4o-mini request_id=Rq9Xa run_id=r-42 latency_ms=312 tokens_in=57 tokens_out=128 cost_usd=0.00094 ok=true

Retry example:
    WARN llm_fiber event=retry provider=anthropic model=claude-3-haiku-20240307 attempt=2 reason=rate_limit backoff_ms=400

---

## Tracing (OpenTelemetry)

When the OpenTelemetry extra is installed and configured, the library can emit spans and metrics to your OTel SDK/exporter.

Span model (typical):
- Root span per call: "llm_fiber.chat" or "llm_fiber.chat_stream"
- Attributes:
  - llm.provider, llm.model
  - llm.request_id
  - llm.finish_reason (when available)
  - llm.tokens.in, llm.tokens.out, llm.tokens.total
  - llm.cost.estimated_usd (when available)
  - app context fields (e.g., run_id, tenant_id) as attributes
- Events:
  - "retry" with reason, attempt, backoff
  - "first_chunk" for streaming indicating TTFB
  - Errors recorded with status and exception details

Recommended setup:
- Configure OTel SDK in your application (TracerProvider, MeterProvider)
- Export via OTLP to a collector (Prometheus/Tempo/Jaeger/Datadog/New Relic/etc.)
- Keep sampling reasonable (e.g., traces at 5–20% depending on traffic)

---

## Exporters

OpenTelemetry (optional extra: "otel"):
- Packages: opentelemetry-api, opentelemetry-sdk, opentelemetry-exporter-otlp
- Enable spans and metrics via your app’s OTel initialization
- The library tags spans/metrics with provider/model and stream context

StatsD/DogStatsD (optional extra: "statsd"):
- Package: statsd
- Configure a client (host/port) and pass as the metrics sink (or via constructor options)
- Metrics are emitted with tags such as provider:model:ok:finish_reason, etc.

Stdlib logging (default):
- All logs go to Python’s logging module
- Configure handlers/formatters/levels in your app
- Redaction on by default for secrets

structlog (optional extra: "structlog"):
- If installed and a structlog logger is passed, logs will be emitted as structured events
- Include context fields, latency, and usage data as event keys

---

## Context binding

Use `fiber.bind(...)` to attach contextual fields that propagate to logs, metrics, and traces:
- Example keys: run_id, tenant_id, request_id, session_id
- These are added as labels/tags/attributes where supported
- Avoid high-cardinality values; hash or bucket if needed

Example:
    from llm_fiber import Fiber
    fiber = Fiber.from_env(default_model="gpt-4o-mini")
    with fiber.bind(run_id="r-42", tenant_id="acme"):
        text = fiber.sync.ask("Explain TTFB vs latency.")
        print(text)

---

## Streaming specifics

- TTFB (time to first byte) is recorded when the first `chunk` event arrives
- End-to-end latency measures stream open to completion
- If a stream is cancelled, you will not receive a final `usage` event and metrics will reflect cancellation
- Usage reporting may not be available for all streamed responses; metrics/logs handle absence gracefully

---

## Configuration

Prefer explicit constructor arguments in libraries/services; use environment variables in applications.

Common patterns:
- Enable exporters via extras: "otel", "statsd", "structlog"
- Initialize OTel SDK early in your process and choose sampling/export policy
- Provide a metrics sink/logger in the `Fiber` constructor when you need custom routing
- Control log level and format via stdlib logging or structlog config
- Configure redaction policy (if applicable in your build)

---

## Sampling and cardinality

- Keep tags bounded; use coarse-grained run/tenant IDs or hashed values
- Sample traces (e.g., 5–20%) if throughput is high
- Keep log levels INFO/WARN/ERROR; avoid DEBUG in production unless investigating issues
- Avoid per-request unique labels in metrics (e.g., request_id); that belongs on logs or tracing attributes, not metric tags

---

## Security and privacy

- Secrets (API keys) are never logged
- Redact prompts/responses or specific fields by default if configured
- PII/PHI: ensure your application policy enforces scrubbed content before logging
- Use encryption and transport security for exporters (e.g., OTLP over TLS)
- Follow your organization’s data retention and access controls

---

## Examples

Stdlib logging:
    import logging
    from llm_fiber import Fiber

    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger("my_app")
    fiber = Fiber.from_env(default_model="gpt-4o-mini", logger=log)

    text = fiber.sync.ask("Three bullets about fiber optics.", temperature=0.2)
    print(text)

OpenTelemetry (simplified sketch):
    from opentelemetry import trace, metrics
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

    resource = Resource.create({"service.name": "my-llm-service"})
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(tracer_provider)

    metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter())
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    # Construct Fiber after OTel is configured so it can pick up tracer/meter
    fiber = Fiber.from_env(default_model="gpt-4o-mini")
    res = fiber.sync.chat(messages=["Summarize: fiber optics"])
    print(res.text)

StatsD (Datadog Agent on localhost):
    from statsd import StatsClient
    from llm_fiber import Fiber

    stats = StatsClient(host="127.0.0.1", port=8125, prefix="llm_fiber")
    # Construct Fiber with a StatsD sink if your build exposes such a hook
    fiber = Fiber.from_env(default_model="gpt-4o-mini", metrics=stats)
    _ = fiber.sync.ask("Latency vs TTFB?")

---

## Best practices

- Always bind request/run context to correlate metrics/logs/traces
- Track SLOs: p95 latency_ms and p99 ttfb_ms per provider/model
- Alert on error_count rate and retry_count spikes
- Set budgets (tokens and cost) to manage spend and prevent runaway latency
- Keep log messages concise and actionable; add IDs for correlation, not full payloads
- Use OTel for cross-service correlation when fiber is in a distributed system

---

## Troubleshooting

- No metrics exported:
  - Ensure your exporter (OTLP/StatsD) is initialized and reachable
  - Verify that the library is picking up the tracer/meter or metrics sink
- Missing usage/cost:
  - Some providers omit token usage on streaming; consider non-streaming calls if accurate usage is critical
  - Ensure tokenizer/pricing data is available if you rely on preflight estimates
- High latency or poor TTFB:
  - Check provider status and network path
  - Review timeouts, retries, and concurrency settings
  - Inspect logs for rate limiting or backoffs

---

## See also

- Transport/Core API: ./transport.md
- Streaming: ./streaming.md
- Ergonomics (DX): ./ergonomics.md
- Prompt API: ./prompt-api.md
- Retries & Budgets: ./retries-and-budgets.md
- Configuration: ./configuration.md
- Capabilities & Pricing: ./capabilities-and-pricing.md
