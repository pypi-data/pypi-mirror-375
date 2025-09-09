"""Tests for metrics configuration and edge cases."""

import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from llm_fiber.observability.metrics import (
    CounterValue,
    FiberMetrics,
    HistogramValue,
    InMemoryMetrics,
    MetricLabels,
    MetricsExporter,
    NoOpMetrics,
    TimingContext,
)


class MockMetricsExporter(MetricsExporter):
    """Mock metrics exporter for testing."""

    def __init__(self):
        self.exported_counters = []
        self.exported_histograms = []
        self.export_error = None

    def export_counter(self, name: str, value: CounterValue) -> None:
        if self.export_error:
            raise self.export_error
        self.exported_counters.append((name, value))

    def export_histogram(self, name: str, value: HistogramValue) -> None:
        if self.export_error:
            raise self.export_error
        self.exported_histograms.append((name, value))


class TestMetricLabels:
    """Test MetricLabels functionality."""

    def test_metric_labels_creation(self):
        """Test creating MetricLabels with all fields."""
        labels = MetricLabels(
            provider="openai",
            model="gpt-4",
            operation="chat",
            status="success",
            error_type="ValueError",
        )

        assert labels.provider == "openai"
        assert labels.model == "gpt-4"
        assert labels.operation == "chat"
        assert labels.status == "success"
        assert labels.error_type == "ValueError"

    def test_metric_labels_partial(self):
        """Test creating MetricLabels with partial fields."""
        labels = MetricLabels(provider="anthropic", model="claude-3")

        assert labels.provider == "anthropic"
        assert labels.model == "claude-3"
        assert labels.operation is None
        assert labels.status is None
        assert labels.error_type is None

    def test_metric_labels_to_dict_excludes_none(self):
        """Test that to_dict excludes None values."""
        labels = MetricLabels(provider="openai", model="gpt-4")
        result = labels.to_dict()

        expected = {"provider": "openai", "model": "gpt-4"}
        assert result == expected
        assert "operation" not in result
        assert "status" not in result
        assert "error_type" not in result

    def test_metric_labels_empty(self):
        """Test MetricLabels with no fields set."""
        labels = MetricLabels()
        result = labels.to_dict()

        assert result == {}


class TestCounterValue:
    """Test CounterValue functionality."""

    def test_counter_value_creation(self):
        """Test creating a CounterValue."""
        labels = {"provider": "openai", "model": "gpt-4"}
        counter = CounterValue(value=42, labels=labels)

        assert counter.value == 42
        assert counter.labels == labels

    def test_counter_value_defaults(self):
        """Test CounterValue with default values."""
        counter = CounterValue()

        assert counter.value == 0
        assert counter.labels == {}


class TestHistogramValue:
    """Test HistogramValue functionality."""

    def test_histogram_value_creation(self):
        """Test creating a HistogramValue."""
        labels = {"provider": "openai"}
        buckets = {1.0: 0, 5.0: 0, 10.0: 0}
        histogram = HistogramValue(count=5, sum=15.5, buckets=buckets, labels=labels)

        assert histogram.count == 5
        assert histogram.sum == 15.5
        assert histogram.buckets == buckets
        assert histogram.labels == labels

    def test_histogram_add_observation(self):
        """Test adding observations to histogram."""
        buckets = {1.0: 0, 5.0: 0, 10.0: 0, float("inf"): 0}
        histogram = HistogramValue(buckets=buckets)

        # Add observation that fits in 5.0 bucket
        histogram.add_observation(3.5)

        assert histogram.count == 1
        assert histogram.sum == 3.5
        assert histogram.buckets[1.0] == 0  # 3.5 > 1.0
        assert histogram.buckets[5.0] == 1  # 3.5 <= 5.0
        assert histogram.buckets[10.0] == 1  # 3.5 <= 10.0
        assert histogram.buckets[float("inf")] == 1

    def test_histogram_multiple_observations(self):
        """Test multiple observations in histogram."""
        buckets = {5.0: 0, 10.0: 0, float("inf"): 0}
        histogram = HistogramValue(buckets=buckets)

        histogram.add_observation(2.0)  # <= 5.0
        histogram.add_observation(7.0)  # <= 10.0
        histogram.add_observation(15.0)  # <= inf

        assert histogram.count == 3
        assert histogram.sum == 24.0
        assert histogram.buckets[5.0] == 1
        assert histogram.buckets[10.0] == 2
        assert histogram.buckets[float("inf")] == 3

    def test_histogram_defaults(self):
        """Test HistogramValue with default values."""
        histogram = HistogramValue()

        assert histogram.count == 0
        assert histogram.sum == 0.0
        assert histogram.buckets == {}
        assert histogram.labels == {}


class TestInMemoryMetrics:
    """Test InMemoryMetrics functionality."""

    def test_increment_counter_new_metric(self):
        """Test incrementing a new counter metric."""
        metrics = InMemoryMetrics()
        labels = {"provider": "openai", "model": "gpt-4"}

        metrics.increment_counter("test_counter", 5, labels)

        counters = metrics.get_counters()
        assert "test_counter" in counters

        labels_key = "model=gpt-4|provider=openai"  # Sorted by key
        assert labels_key in counters["test_counter"]
        assert counters["test_counter"][labels_key].value == 5
        assert counters["test_counter"][labels_key].labels == labels

    def test_increment_counter_existing_metric(self):
        """Test incrementing an existing counter metric."""
        metrics = InMemoryMetrics()
        labels = {"provider": "openai"}

        metrics.increment_counter("test_counter", 3, labels)
        metrics.increment_counter("test_counter", 7, labels)

        counters = metrics.get_counters()
        labels_key = "provider=openai"
        assert counters["test_counter"][labels_key].value == 10

    def test_increment_counter_no_labels(self):
        """Test incrementing counter without labels."""
        metrics = InMemoryMetrics()

        metrics.increment_counter("test_counter", 1)

        counters = metrics.get_counters()
        assert "" in counters["test_counter"]  # Empty labels key
        assert counters["test_counter"][""].value == 1

    def test_observe_histogram_new_metric(self):
        """Test observing a new histogram metric."""
        metrics = InMemoryMetrics()
        labels = {"provider": "anthropic"}

        metrics.observe_histogram("test_histogram", 2.5, labels)

        histograms = metrics.get_histograms()
        assert "test_histogram" in histograms

        labels_key = "provider=anthropic"
        histogram = histograms["test_histogram"][labels_key]
        assert histogram.count == 1
        assert histogram.sum == 2.5
        assert histogram.labels == labels

        # Check that buckets were created with default values
        assert len(histogram.buckets) == len(InMemoryMetrics.DEFAULT_LATENCY_BUCKETS)
        assert histogram.buckets[5.0] == 1  # 2.5 <= 5.0
        assert histogram.buckets[1.0] == 0  # 2.5 > 1.0

    def test_observe_histogram_custom_buckets(self):
        """Test histogram with custom buckets."""
        metrics = InMemoryMetrics()
        custom_buckets = [1.0, 10.0, 100.0]

        metrics.observe_histogram("test_histogram", 5.0, buckets=custom_buckets)

        histograms = metrics.get_histograms()
        histogram = histograms["test_histogram"][""]

        assert set(histogram.buckets.keys()) == set(custom_buckets)
        assert histogram.buckets[1.0] == 0
        assert histogram.buckets[10.0] == 1
        assert histogram.buckets[100.0] == 1

    def test_labels_key_consistency(self):
        """Test that labels are consistently keyed."""
        metrics = InMemoryMetrics()

        # Same labels in different order should create same key
        labels1 = {"a": "1", "b": "2"}
        labels2 = {"b": "2", "a": "1"}

        key1 = metrics._labels_key(labels1)
        key2 = metrics._labels_key(labels2)

        assert key1 == key2
        assert key1 == "a=1|b=2"  # Should be sorted

    def test_thread_safety_counters(self):
        """Test thread safety of counter operations."""
        metrics = InMemoryMetrics()
        num_threads = 10
        increments_per_thread = 100

        def increment_worker():
            for _ in range(increments_per_thread):
                metrics.increment_counter("thread_test", 1, {"worker": "test"})

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(increment_worker) for _ in range(num_threads)]
            for future in futures:
                future.result()

        counters = metrics.get_counters()
        expected_total = num_threads * increments_per_thread
        actual_total = counters["thread_test"]["worker=test"].value
        assert actual_total == expected_total

    def test_thread_safety_histograms(self):
        """Test thread safety of histogram operations."""
        metrics = InMemoryMetrics()
        num_threads = 5
        observations_per_thread = 50

        def observe_worker(worker_id):
            for i in range(observations_per_thread):
                metrics.observe_histogram("thread_histogram", float(i), {"worker": str(worker_id)})

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(observe_worker, i) for i in range(num_threads)]
            for future in futures:
                future.result()

        histograms = metrics.get_histograms()

        # Each worker should have its own histogram
        assert len(histograms["thread_histogram"]) == num_threads

        # Verify total observations
        total_count = sum(h.count for h in histograms["thread_histogram"].values())
        assert total_count == num_threads * observations_per_thread

    def test_export_to_exporter(self):
        """Test exporting metrics to an exporter."""
        metrics = InMemoryMetrics()
        exporter = MockMetricsExporter()

        # Add some test data
        metrics.increment_counter("test_counter", 42, {"label": "value"})
        metrics.observe_histogram("test_histogram", 1.5, {"label": "value"})

        metrics.export_to(exporter)

        # Verify exports
        assert len(exporter.exported_counters) == 1
        assert len(exporter.exported_histograms) == 1

        counter_name, counter_value = exporter.exported_counters[0]
        assert counter_name == "test_counter"
        assert counter_value.value == 42
        assert counter_value.labels == {"label": "value"}

        histogram_name, histogram_value = exporter.exported_histograms[0]
        assert histogram_name == "test_histogram"
        assert histogram_value.count == 1
        assert histogram_value.sum == 1.5

    def test_reset_metrics(self):
        """Test resetting all metrics."""
        metrics = InMemoryMetrics()

        # Add some data
        metrics.increment_counter("counter", 10)
        metrics.observe_histogram("histogram", 5.0)

        # Verify data exists
        assert len(metrics.get_counters()) == 1
        assert len(metrics.get_histograms()) == 1

        # Reset
        metrics.reset()

        # Verify data is cleared
        assert len(metrics.get_counters()) == 0
        assert len(metrics.get_histograms()) == 0

    def test_get_metrics_returns_copy(self):
        """Test that get_* methods return copies to prevent external modification."""
        metrics = InMemoryMetrics()
        labels = {"test": "label"}

        metrics.increment_counter("test", 5, labels)

        # Get counters and modify the returned data
        counters = metrics.get_counters()
        counters["test"]["test=label"].value = 999

        # Original should be unchanged
        original_counters = metrics.get_counters()
        assert original_counters["test"]["test=label"].value == 5


class TestFiberMetrics:
    """Test FiberMetrics functionality."""

    @pytest.fixture
    def metrics(self):
        """Create FiberMetrics instance for testing."""
        return FiberMetrics()

    def test_record_request_start(self, metrics):
        """Test recording request start."""
        metrics.record_request_start("openai", "gpt-4", "chat")

        counters = metrics.get_metrics().get_counters()
        assert FiberMetrics.REQUEST_COUNT in counters

        labels_key = "model=gpt-4|operation=chat|provider=openai"
        assert counters[FiberMetrics.REQUEST_COUNT][labels_key].value == 1

    def test_record_request_success(self, metrics):
        """Test recording successful request."""
        metrics.record_request_success("openai", "gpt-4", "chat", latency_ms=150.0, ttfb_ms=50.0)

        histograms = metrics.get_metrics().get_histograms()
        assert FiberMetrics.LATENCY_MS in histograms
        assert FiberMetrics.TTFB_MS in histograms

        labels_key = "model=gpt-4|operation=chat|provider=openai|status=success"

        latency_histogram = histograms[FiberMetrics.LATENCY_MS][labels_key]
        assert latency_histogram.count == 1
        assert latency_histogram.sum == 150.0

        ttfb_histogram = histograms[FiberMetrics.TTFB_MS][labels_key]
        assert ttfb_histogram.count == 1
        assert ttfb_histogram.sum == 50.0

    def test_record_request_success_without_ttfb(self, metrics):
        """Test recording success without TTFB."""
        metrics.record_request_success("anthropic", "claude-3", latency_ms=200.0)

        histograms = metrics.get_metrics().get_histograms()
        assert FiberMetrics.LATENCY_MS in histograms
        assert FiberMetrics.TTFB_MS not in histograms

    def test_record_request_error(self, metrics):
        """Test recording request error."""
        metrics.record_request_error("openai", "gpt-4", "TimeoutError", "chat", latency_ms=5000.0)

        counters = metrics.get_metrics().get_counters()
        histograms = metrics.get_metrics().get_histograms()

        # Check error counter
        assert FiberMetrics.ERROR_COUNT in counters
        error_labels_key = (
            "error_type=TimeoutError|model=gpt-4|operation=chat|provider=openai|status=error"
        )
        assert counters[FiberMetrics.ERROR_COUNT][error_labels_key].value == 1

        # Check latency histogram
        assert FiberMetrics.LATENCY_MS in histograms
        latency_labels_key = (
            "error_type=TimeoutError|model=gpt-4|operation=chat|provider=openai|status=error"
        )
        histogram = histograms[FiberMetrics.LATENCY_MS][latency_labels_key]
        assert histogram.sum == 5000.0

    def test_record_retry(self, metrics):
        """Test recording retry attempt."""
        metrics.record_retry("openai", "gpt-4", "RateLimitError", "chat", attempt=2)

        counters = metrics.get_metrics().get_counters()
        assert FiberMetrics.RETRY_COUNT in counters

        labels_key = (
            "attempt=2|error_type=RateLimitError|model=gpt-4|operation=chat|provider=openai"
        )
        assert counters[FiberMetrics.RETRY_COUNT][labels_key].value == 1

    def test_record_token_usage(self, metrics):
        """Test recording token usage."""
        metrics.record_token_usage("openai", "gpt-4", 100, 50, 150, "chat")

        counters = metrics.get_metrics().get_counters()
        labels_key = "model=gpt-4|operation=chat|provider=openai"

        assert counters[FiberMetrics.TOKENS_PROMPT][labels_key].value == 100
        assert counters[FiberMetrics.TOKENS_COMPLETION][labels_key].value == 50
        assert counters[FiberMetrics.TOKENS_TOTAL][labels_key].value == 150

    def test_record_estimated_cost(self, metrics):
        """Test recording estimated cost."""
        metrics.record_estimated_cost("openai", "gpt-4", 0.0025, "chat")

        counters = metrics.get_metrics().get_counters()
        labels_key = "model=gpt-4|operation=chat|provider=openai"

        # Cost should be converted to hundredths of cents (0.0025 * 10000 = 25)
        assert counters[FiberMetrics.ESTIMATED_COST_USD][labels_key].value == 25

    def test_record_cache_operations(self, metrics):
        """Test recording cache operations."""
        metrics.record_cache_hit("openai", "gpt-4")
        metrics.record_cache_miss("openai", "gpt-4")
        metrics.record_cache_write("openai", "gpt-4")
        metrics.record_cache_eviction("openai", "gpt-4")
        metrics.record_cache_error("openai", "gpt-4", "CacheError")

        counters = metrics.get_metrics().get_counters()
        labels_key = "model=gpt-4|operation=chat|provider=openai"
        error_labels_key = "error_type=CacheError|model=gpt-4|operation=chat|provider=openai"

        assert counters[FiberMetrics.CACHE_HITS][labels_key].value == 1
        assert counters[FiberMetrics.CACHE_MISSES][labels_key].value == 1
        assert counters[FiberMetrics.CACHE_WRITES][labels_key].value == 1
        assert counters[FiberMetrics.CACHE_EVICTIONS][labels_key].value == 1
        assert counters[FiberMetrics.CACHE_ERRORS][error_labels_key].value == 1

    def test_record_batch_operation(self, metrics):
        """Test recording batch operation."""
        metrics.record_batch_operation(10, 8, 2, 5.5)

        counters = metrics.get_metrics().get_counters()
        histograms = metrics.get_metrics().get_histograms()
        labels_key = "operation=batch"

        assert counters[FiberMetrics.BATCH_REQUESTS][labels_key].value == 10
        assert counters[FiberMetrics.BATCH_SUCCESSFUL][labels_key].value == 8
        assert counters[FiberMetrics.BATCH_FAILED][labels_key].value == 2

        # Duration should be converted to milliseconds (5.5 * 1000 = 5500)
        duration_histogram = histograms[FiberMetrics.BATCH_DURATION_MS][labels_key]
        assert duration_histogram.sum == 5500.0

    def test_export_to_exporter(self, metrics):
        """Test exporting FiberMetrics to exporter."""
        exporter = MockMetricsExporter()

        metrics.record_request_start("openai", "gpt-4")
        metrics.record_request_success("openai", "gpt-4", latency_ms=100.0)

        metrics.export_to(exporter)

        # Should have exported both counter and histogram
        assert len(exporter.exported_counters) > 0
        assert len(exporter.exported_histograms) > 0

    def test_reset_metrics(self, metrics):
        """Test resetting FiberMetrics."""
        metrics.record_request_start("openai", "gpt-4")

        # Verify data exists
        counters_before = metrics.get_metrics().get_counters()
        assert len(counters_before) > 0

        metrics.reset()

        # Verify data is cleared
        counters_after = metrics.get_metrics().get_counters()
        assert len(counters_after) == 0


class TestNoOpMetrics:
    """Test NoOpMetrics functionality."""

    def test_noop_metrics_initialization(self):
        """Test NoOpMetrics initialization."""
        metrics = NoOpMetrics()

        # Should not have _metrics attribute since it doesn't call super().__init__()
        assert not hasattr(metrics, "_metrics")

    def test_noop_methods_do_nothing(self):
        """Test that NoOpMetrics methods perform no operations."""
        metrics = NoOpMetrics()

        # These should all execute without error and without side effects
        metrics.record_request_start("openai", "gpt-4")
        metrics.record_request_success("openai", "gpt-4", latency_ms=100.0, ttfb_ms=50.0)
        metrics.record_request_error("openai", "gpt-4", "Error", latency_ms=100.0)
        metrics.record_retry("openai", "gpt-4", "Error", attempt=1)
        metrics.record_token_usage("openai", "gpt-4", 100, 50, 150)
        metrics.record_estimated_cost("openai", "gpt-4", 0.01)
        metrics.record_cache_hit("openai", "gpt-4")
        metrics.record_cache_miss("openai", "gpt-4")
        metrics.record_cache_write("openai", "gpt-4")
        metrics.record_cache_eviction("openai", "gpt-4")
        metrics.record_cache_error("openai", "gpt-4", "CacheError")
        metrics.record_batch_operation(10, 8, 2, 1.0)

        # Get metrics should return empty InMemoryMetrics
        empty_metrics = metrics.get_metrics()
        assert isinstance(empty_metrics, InMemoryMetrics)
        assert len(empty_metrics.get_counters()) == 0
        assert len(empty_metrics.get_histograms()) == 0

        # Export should do nothing
        exporter = MockMetricsExporter()
        metrics.export_to(exporter)
        assert len(exporter.exported_counters) == 0
        assert len(exporter.exported_histograms) == 0

        # Reset should do nothing
        metrics.reset()


class TestTimingContext:
    """Test TimingContext functionality."""

    def test_timing_context_success(self):
        """Test timing context for successful operation."""
        metrics = FiberMetrics()

        with TimingContext(metrics, "openai", "gpt-4", "chat") as ctx:
            time.sleep(0.01)  # Small delay to ensure measurable time
            ctx.record_ttfb()

        # Verify request start was recorded
        counters = metrics.get_metrics().get_counters()
        assert FiberMetrics.REQUEST_COUNT in counters

        # Verify success was recorded with latency
        histograms = metrics.get_metrics().get_histograms()
        assert FiberMetrics.LATENCY_MS in histograms
        assert FiberMetrics.TTFB_MS in histograms

        # Verify latency is positive (time passed)
        latency_labels = "model=gpt-4|operation=chat|provider=openai|status=success"
        latency_histogram = histograms[FiberMetrics.LATENCY_MS][latency_labels]
        assert latency_histogram.count == 1
        assert latency_histogram.sum > 0

        # Verify TTFB was recorded
        ttfb_histogram = histograms[FiberMetrics.TTFB_MS][latency_labels]
        assert ttfb_histogram.count == 1
        assert ttfb_histogram.sum > 0

    def test_timing_context_error(self):
        """Test timing context for failed operation."""
        metrics = FiberMetrics()

        try:
            with TimingContext(metrics, "openai", "gpt-4", "chat"):
                time.sleep(0.01)
                raise ValueError("Test error")
        except ValueError:
            pass

        # Verify error was recorded
        counters = metrics.get_metrics().get_counters()
        assert FiberMetrics.ERROR_COUNT in counters

        error_labels = (
            "error_type=ValueError|model=gpt-4|operation=chat|provider=openai|status=error"
        )
        assert counters[FiberMetrics.ERROR_COUNT][error_labels].value == 1

        # Verify error latency was recorded
        histograms = metrics.get_metrics().get_histograms()
        error_latency = histograms[FiberMetrics.LATENCY_MS][error_labels]
        assert error_latency.count == 1
        assert error_latency.sum > 0

    def test_timing_context_custom_error_type(self):
        """Test timing context with custom error type."""
        metrics = FiberMetrics()

        try:
            with TimingContext(metrics, "openai", "gpt-4") as ctx:
                ctx.record_error_type("CustomError")
                raise RuntimeError("Runtime error")
        except RuntimeError:
            pass

        # Verify custom error type was used instead of exception type
        counters = metrics.get_metrics().get_counters()
        error_labels = (
            "error_type=CustomError|model=gpt-4|operation=chat|provider=openai|status=error"
        )
        assert counters[FiberMetrics.ERROR_COUNT][error_labels].value == 1

    def test_timing_context_multiple_ttfb_calls(self):
        """Test that multiple TTFB calls only record the first one."""
        metrics = FiberMetrics()

        with TimingContext(metrics, "openai", "gpt-4") as ctx:
            ctx.record_ttfb()  # First call
            time.sleep(0.01)
            ctx.record_ttfb()  # Second call should be ignored

        histograms = metrics.get_metrics().get_histograms()
        ttfb_labels = "model=gpt-4|operation=chat|provider=openai|status=success"
        ttfb_histogram = histograms[FiberMetrics.TTFB_MS][ttfb_labels]

        # TTFB should be close to 0 (first call) not the sleep time
        assert ttfb_histogram.sum < 5.0  # Less than 5ms


class TestMetricsErrorHandling:
    """Test error handling and edge cases in metrics."""

    def test_exporter_error_handling(self):
        """Test handling of exporter errors."""
        metrics = InMemoryMetrics()
        exporter = MockMetricsExporter()
        exporter.export_error = RuntimeError("Export failed")

        # Add some data
        metrics.increment_counter("test_counter", 1)
        metrics.observe_histogram("test_histogram", 1.0)

        # Export should propagate the error
        with pytest.raises(RuntimeError, match="Export failed"):
            metrics.export_to(exporter)

    def test_histogram_with_empty_buckets(self):
        """Test histogram behavior with empty buckets."""
        histogram = HistogramValue(buckets={})

        # Should not raise error
        histogram.add_observation(5.0)

        assert histogram.count == 1
        assert histogram.sum == 5.0
        assert histogram.buckets == {}  # Should remain empty

    def test_negative_histogram_observations(self):
        """Test histogram with negative observations."""
        metrics = InMemoryMetrics()
        custom_buckets = [-10.0, -1.0, 0.0, 1.0, 10.0]

        metrics.observe_histogram("negative_test", -5.0, buckets=custom_buckets)

        histograms = metrics.get_histograms()
        histogram = histograms["negative_test"][""]

        assert histogram.count == 1
        assert histogram.sum == -5.0
        assert histogram.buckets[-10.0] == 0  # -5.0 > -10.0
        assert histogram.buckets[-1.0] == 1  # -5.0 <= -1.0, so it's counted in this bucket
        assert histogram.buckets[0.0] == 1  # -5.0 <= 0.0

    def test_large_counter_values(self):
        """Test handling of large counter values."""
        metrics = InMemoryMetrics()

        # Test with very large increment values
        large_value = 999999999
        metrics.increment_counter("large_counter", large_value)

        counters = metrics.get_counters()
        assert counters["large_counter"][""].value == large_value

    def test_zero_latency_handling(self):
        """Test handling of zero latency values."""
        metrics = FiberMetrics()

        # Zero latency should not be recorded
        metrics.record_request_success("openai", "gpt-4", latency_ms=0.0)

        histograms = metrics.get_metrics().get_histograms()
        # Should not create histogram entry for zero latency
        assert FiberMetrics.LATENCY_MS not in histograms

    def test_concurrent_metrics_operations(self):
        """Test concurrent operations on metrics."""
        metrics = FiberMetrics()
        num_operations = 100

        def worker():
            for i in range(num_operations):
                metrics.record_request_start("openai", "gpt-4")
                metrics.record_request_success("openai", "gpt-4", latency_ms=float(i + 1))
                metrics.record_token_usage("openai", "gpt-4", i, i, i * 2)

        threads = []
        num_threads = 5

        for _ in range(num_threads):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Verify all operations were recorded
        counters = metrics.get_metrics().get_counters()
        histograms = metrics.get_metrics().get_histograms()

        request_labels = "model=gpt-4|operation=chat|provider=openai"
        success_labels = "model=gpt-4|operation=chat|provider=openai|status=success"

        expected_requests = num_threads * num_operations

        assert counters[FiberMetrics.REQUEST_COUNT][request_labels].value == expected_requests
        assert histograms[FiberMetrics.LATENCY_MS][success_labels].count == expected_requests

    def test_metric_labels_special_characters(self):
        """Test metric labels with special characters."""
        metrics = FiberMetrics()

        # Test with labels containing special characters
        metrics.record_request_start("provider/test", "model-name_v1.2", "chat|stream")

        counters = metrics.get_metrics().get_counters()
        # Should handle special characters in labels
        # Should handle special characters in labels
        assert any("provider/test" in key for key in counters[FiberMetrics.REQUEST_COUNT].keys())

    def test_histogram_bucket_edge_cases(self):
        """Test histogram bucket edge cases."""
        metrics = InMemoryMetrics()

        # Test with infinity bucket
        metrics.observe_histogram("edge_test", float("inf"), buckets=[1.0, float("inf")])

        histograms = metrics.get_histograms()
        histogram = histograms["edge_test"][""]

        assert histogram.buckets[float("inf")] == 1
        assert histogram.sum == float("inf")

    def test_metrics_with_none_values(self):
        """Test metrics methods with None values where applicable."""
        metrics = FiberMetrics()

        # These should handle None values gracefully
        metrics.record_request_success("openai", "gpt-4", ttfb_ms=None)  # None TTFB

        histograms = metrics.get_metrics().get_histograms()
        # Should only have latency, not TTFB
        assert FiberMetrics.TTFB_MS not in histograms

    def test_timing_context_without_sleep(self):
        """Test timing context with very fast operations."""
        metrics = FiberMetrics()

        with TimingContext(metrics, "openai", "gpt-4"):
            pass  # No operation, should still record metrics

        histograms = metrics.get_metrics().get_histograms()
        success_labels = "model=gpt-4|operation=chat|provider=openai|status=success"

        assert FiberMetrics.LATENCY_MS in histograms
        latency_histogram = histograms[FiberMetrics.LATENCY_MS][success_labels]
        assert latency_histogram.count == 1
        assert latency_histogram.sum >= 0  # Should be non-negative even if very small
