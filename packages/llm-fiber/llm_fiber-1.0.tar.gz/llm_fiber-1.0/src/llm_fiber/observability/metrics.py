"""Metrics collection and export for llm-fiber observability."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock
from typing import Dict, List, Optional


@dataclass
class MetricLabels:
    """Standard labels for llm-fiber metrics."""

    provider: Optional[str] = None
    model: Optional[str] = None
    operation: Optional[str] = None
    status: Optional[str] = None
    error_type: Optional[str] = None

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary, excluding None values."""
        return {
            k: v
            for k, v in {
                "provider": self.provider,
                "model": self.model,
                "operation": self.operation,
                "status": self.status,
                "error_type": self.error_type,
            }.items()
            if v is not None
        }


@dataclass
class CounterValue:
    """A counter metric value with labels."""

    value: int = 0
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class HistogramValue:
    """A histogram metric value with labels."""

    count: int = 0
    sum: float = 0.0
    buckets: Dict[float, int] = field(default_factory=dict)  # le -> count
    labels: Dict[str, str] = field(default_factory=dict)

    def add_observation(self, value: float) -> None:
        """Add a new observation to the histogram."""
        self.count += 1
        self.sum += value

        # Update buckets
        for bucket_le in self.buckets:
            if value <= bucket_le:
                self.buckets[bucket_le] += 1


class MetricsExporter(ABC):
    """Abstract base class for metrics exporters."""

    @abstractmethod
    def export_counter(self, name: str, value: CounterValue) -> None:
        """Export a counter metric."""
        pass

    @abstractmethod
    def export_histogram(self, name: str, value: HistogramValue) -> None:
        """Export a histogram metric."""
        pass


class InMemoryMetrics:
    """In-memory metrics collection with thread safety."""

    # Standard histogram buckets for latency (in milliseconds)
    DEFAULT_LATENCY_BUCKETS = [
        1,
        5,
        10,
        25,
        50,
        100,
        250,
        500,
        1000,
        2500,
        5000,
        10000,
        float("inf"),
    ]

    def __init__(self):
        self._counters: Dict[str, Dict[str, CounterValue]] = defaultdict(dict)
        self._histograms: Dict[str, Dict[str, HistogramValue]] = defaultdict(dict)
        self._lock = Lock()

    def _labels_key(self, labels: Dict[str, str]) -> str:
        """Create a consistent key from labels."""
        return "|".join(f"{k}={v}" for k, v in sorted(labels.items()))

    def increment_counter(
        self, name: str, value: int = 1, labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Increment a counter metric."""
        labels = labels or {}
        labels_key = self._labels_key(labels)

        with self._lock:
            if labels_key not in self._counters[name]:
                self._counters[name][labels_key] = CounterValue(0, labels)
            self._counters[name][labels_key].value += value

    def observe_histogram(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        buckets: Optional[List[float]] = None,
    ) -> None:
        """Add an observation to a histogram metric."""
        labels = labels or {}
        labels_key = self._labels_key(labels)
        buckets = buckets or self.DEFAULT_LATENCY_BUCKETS

        with self._lock:
            if labels_key not in self._histograms[name]:
                bucket_dict = {bucket: 0 for bucket in buckets}
                self._histograms[name][labels_key] = HistogramValue(
                    count=0, sum=0.0, buckets=bucket_dict, labels=labels
                )
            self._histograms[name][labels_key].add_observation(value)

    def get_counters(self) -> Dict[str, Dict[str, CounterValue]]:
        """Get all counter metrics."""
        with self._lock:
            # Return a deep copy to avoid external modification
            return {
                name: {
                    key: CounterValue(cv.value, cv.labels.copy()) for key, cv in counters.items()
                }
                for name, counters in self._counters.items()
            }

    def get_histograms(self) -> Dict[str, Dict[str, HistogramValue]]:
        """Get all histogram metrics."""
        with self._lock:
            # Return a deep copy to avoid external modification
            return {
                name: {
                    key: HistogramValue(hv.count, hv.sum, hv.buckets.copy(), hv.labels.copy())
                    for key, hv in histograms.items()
                }
                for name, histograms in self._histograms.items()
            }

    def export_to(self, exporter: MetricsExporter) -> None:
        """Export all metrics to an exporter."""
        counters = self.get_counters()
        histograms = self.get_histograms()

        for name, counter_values in counters.items():
            for counter_value in counter_values.values():
                exporter.export_counter(name, counter_value)

        for name, histogram_values in histograms.items():
            for histogram_value in histogram_values.values():
                exporter.export_histogram(name, histogram_value)

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._counters.clear()
            self._histograms.clear()


class FiberMetrics:
    """High-level metrics interface for llm-fiber operations."""

    # Standard metric names
    REQUEST_COUNT = "llm_fiber_requests_total"
    ERROR_COUNT = "llm_fiber_errors_total"
    RETRY_COUNT = "llm_fiber_retries_total"
    LATENCY_MS = "llm_fiber_latency_milliseconds"
    TTFB_MS = "llm_fiber_ttfb_milliseconds"
    TOKENS_PROMPT = "llm_fiber_tokens_prompt_total"
    TOKENS_COMPLETION = "llm_fiber_tokens_completion_total"
    TOKENS_TOTAL = "llm_fiber_tokens_total"
    ESTIMATED_COST_USD = "llm_fiber_estimated_cost_usd_total"

    # v0.2 Cache metrics
    CACHE_HITS = "llm_fiber_cache_hits_total"
    CACHE_MISSES = "llm_fiber_cache_misses_total"
    CACHE_WRITES = "llm_fiber_cache_writes_total"
    CACHE_EVICTIONS = "llm_fiber_cache_evictions_total"
    CACHE_ERRORS = "llm_fiber_cache_errors_total"

    # v0.2 Batch metrics
    BATCH_REQUESTS = "llm_fiber_batch_requests_total"
    BATCH_SUCCESSFUL = "llm_fiber_batch_successful_total"
    BATCH_FAILED = "llm_fiber_batch_failed_total"
    BATCH_DURATION_MS = "llm_fiber_batch_duration_milliseconds"

    def __init__(self, metrics: Optional[InMemoryMetrics] = None):
        self._metrics = metrics or InMemoryMetrics()

    def record_request_start(self, provider: str, model: str, operation: str = "chat") -> None:
        """Record the start of a request."""
        labels = MetricLabels(provider=provider, model=model, operation=operation).to_dict()
        self._metrics.increment_counter(self.REQUEST_COUNT, 1, labels)

    def record_request_success(
        self,
        provider: str,
        model: str,
        operation: str = "chat",
        latency_ms: float = 0.0,
        ttfb_ms: Optional[float] = None,
    ) -> None:
        """Record a successful request completion."""
        labels = MetricLabels(
            provider=provider, model=model, operation=operation, status="success"
        ).to_dict()

        if latency_ms > 0:
            self._metrics.observe_histogram(self.LATENCY_MS, latency_ms, labels)

        if ttfb_ms is not None and ttfb_ms > 0:
            self._metrics.observe_histogram(self.TTFB_MS, ttfb_ms, labels)

    def record_request_error(
        self,
        provider: str,
        model: str,
        error_type: str,
        operation: str = "chat",
        latency_ms: float = 0.0,
    ) -> None:
        """Record a failed request."""
        labels = MetricLabels(
            provider=provider,
            model=model,
            operation=operation,
            status="error",
            error_type=error_type,
        ).to_dict()

        self._metrics.increment_counter(self.ERROR_COUNT, 1, labels)

        if latency_ms > 0:
            self._metrics.observe_histogram(self.LATENCY_MS, latency_ms, labels)

    def record_retry(
        self, provider: str, model: str, error_type: str, operation: str = "chat", attempt: int = 1
    ) -> None:
        """Record a retry attempt."""
        labels = MetricLabels(
            provider=provider, model=model, operation=operation, error_type=error_type
        ).to_dict()
        labels["attempt"] = str(attempt)

        self._metrics.increment_counter(self.RETRY_COUNT, 1, labels)

    def record_token_usage(
        self,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        operation: str = "chat",
    ) -> None:
        """Record token usage."""
        labels = MetricLabels(provider=provider, model=model, operation=operation).to_dict()

        self._metrics.increment_counter(self.TOKENS_PROMPT, prompt_tokens, labels)
        self._metrics.increment_counter(self.TOKENS_COMPLETION, completion_tokens, labels)
        self._metrics.increment_counter(self.TOKENS_TOTAL, total_tokens, labels)

    def record_estimated_cost(
        self, provider: str, model: str, cost_usd: float, operation: str = "chat"
    ) -> None:
        """Record estimated cost."""
        labels = MetricLabels(provider=provider, model=model, operation=operation).to_dict()
        # Convert to hundredths of a cent for better precision as counter
        cost_hundredths = int(cost_usd * 10000)
        self._metrics.increment_counter(self.ESTIMATED_COST_USD, cost_hundredths, labels)

    # v0.2 Cache metrics methods
    def record_cache_hit(self, provider: str, model: str, operation: str = "chat") -> None:
        """Record a cache hit."""
        labels = MetricLabels(provider=provider, model=model, operation=operation).to_dict()
        self._metrics.increment_counter(self.CACHE_HITS, 1, labels)

    def record_cache_miss(self, provider: str, model: str, operation: str = "chat") -> None:
        """Record a cache miss."""
        labels = MetricLabels(provider=provider, model=model, operation=operation).to_dict()
        self._metrics.increment_counter(self.CACHE_MISSES, 1, labels)

    def record_cache_write(self, provider: str, model: str, operation: str = "chat") -> None:
        """Record a cache write."""
        labels = MetricLabels(provider=provider, model=model, operation=operation).to_dict()
        self._metrics.increment_counter(self.CACHE_WRITES, 1, labels)

    def record_cache_eviction(self, provider: str, model: str, operation: str = "chat") -> None:
        """Record a cache eviction."""
        labels = MetricLabels(provider=provider, model=model, operation=operation).to_dict()
        self._metrics.increment_counter(self.CACHE_EVICTIONS, 1, labels)

    def record_cache_error(
        self, provider: str, model: str, error_type: str, operation: str = "chat"
    ) -> None:
        """Record a cache error."""
        labels = MetricLabels(
            provider=provider, model=model, operation=operation, error_type=error_type
        ).to_dict()
        self._metrics.increment_counter(self.CACHE_ERRORS, 1, labels)

    # v0.2 Batch metrics methods
    def record_batch_operation(
        self, total_requests: int, successful: int, failed: int, duration_seconds: float
    ) -> None:
        """Record a batch operation."""
        labels = {"operation": "batch"}

        self._metrics.increment_counter(self.BATCH_REQUESTS, total_requests, labels)
        self._metrics.increment_counter(self.BATCH_SUCCESSFUL, successful, labels)
        self._metrics.increment_counter(self.BATCH_FAILED, failed, labels)
        self._metrics.observe_histogram(self.BATCH_DURATION_MS, duration_seconds * 1000, labels)

    def get_metrics(self) -> InMemoryMetrics:
        """Get the underlying metrics collector."""
        return self._metrics

    def export_to(self, exporter: MetricsExporter) -> None:
        """Export all metrics to an exporter."""
        self._metrics.export_to(exporter)

    def reset(self) -> None:
        """Reset all metrics."""
        self._metrics.reset()


class NoOpMetrics(FiberMetrics):
    """No-op metrics implementation for when metrics are disabled."""

    def __init__(self):
        # Don't call super().__init__() to avoid creating metrics storage
        pass

    def record_request_start(self, provider: str, model: str, operation: str = "chat") -> None:
        pass

    def record_request_success(
        self,
        provider: str,
        model: str,
        operation: str = "chat",
        latency_ms: float = 0.0,
        ttfb_ms: Optional[float] = None,
    ) -> None:
        pass

    def record_request_error(
        self,
        provider: str,
        model: str,
        error_type: str,
        operation: str = "chat",
        latency_ms: float = 0.0,
    ) -> None:
        pass

    def record_retry(
        self, provider: str, model: str, error_type: str, operation: str = "chat", attempt: int = 1
    ) -> None:
        pass

    def record_token_usage(
        self,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        operation: str = "chat",
    ) -> None:
        pass

    def record_estimated_cost(
        self, provider: str, model: str, cost_usd: float, operation: str = "chat"
    ) -> None:
        pass

    def record_cache_hit(self, provider: str, model: str, operation: str = "chat") -> None:
        pass

    def record_cache_miss(self, provider: str, model: str, operation: str = "chat") -> None:
        pass

    def record_cache_write(self, provider: str, model: str, operation: str = "chat") -> None:
        pass

    def record_cache_eviction(self, provider: str, model: str, operation: str = "chat") -> None:
        pass

    def record_cache_error(
        self, provider: str, model: str, error_type: str, operation: str = "chat"
    ) -> None:
        pass

    def record_batch_operation(
        self, total_requests: int, successful: int, failed: int, duration_seconds: float
    ) -> None:
        pass

    def get_metrics(self) -> InMemoryMetrics:
        return InMemoryMetrics()

    def export_to(self, exporter: MetricsExporter) -> None:
        pass

    def reset(self) -> None:
        pass


class TimingContext:
    """Context manager for timing operations."""

    def __init__(self, metrics: FiberMetrics, provider: str, model: str, operation: str = "chat"):
        self.metrics = metrics
        self.provider = provider
        self.model = model
        self.operation = operation
        self.start_time = 0.0
        self.ttfb_time: Optional[float] = None
        self.error_type: Optional[str] = None

    def __enter__(self) -> TimingContext:
        self.start_time = time.time()
        self.metrics.record_request_start(self.provider, self.model, self.operation)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        latency_ms = (time.time() - self.start_time) * 1000

        if exc_type is None:
            # Success
            self.metrics.record_request_success(
                self.provider, self.model, self.operation, latency_ms, self.ttfb_time
            )
        else:
            # Error
            error_type = self.error_type or exc_type.__name__
            self.metrics.record_request_error(
                self.provider, self.model, error_type, self.operation, latency_ms
            )

    def record_ttfb(self) -> None:
        """Record time to first byte."""
        if self.start_time > 0 and self.ttfb_time is None:
            self.ttfb_time = (time.time() - self.start_time) * 1000

    def record_error_type(self, error_type: str) -> None:
        """Set the error type for this operation."""
        self.error_type = error_type
