"""Performance metrics collection system."""

import time
from collections import deque
from dataclasses import dataclass, field
from threading import Lock
from typing import Any, Dict, List, Optional


@dataclass
class PerformanceMetric:
    """Individual performance metric."""

    name: str
    value: float
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OperationMetrics:
    """Metrics for a specific operation."""

    operation_name: str
    call_count: int = 0
    total_time: float = 0.0
    min_time: float = float("inf")
    max_time: float = 0.0
    avg_time: float = 0.0
    error_count: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    last_called: Optional[float] = None

    def update(self, execution_time: float, cached: bool = False, error: bool = False):
        """Update metrics with new execution data."""
        self.call_count += 1
        self.last_called = time.time()

        if error:
            self.error_count += 1
            return

        if cached:
            self.cache_hits += 1
        else:
            self.cache_misses += 1

        self.total_time += execution_time
        self.min_time = min(self.min_time, execution_time)
        self.max_time = max(self.max_time, execution_time)
        self.avg_time = (
            self.total_time / (self.call_count - self.error_count)
            if (self.call_count - self.error_count) > 0
            else 0.0
        )

    def get_cache_hit_rate(self) -> float:
        """Get cache hit rate as percentage."""
        total_cache_requests = self.cache_hits + self.cache_misses
        return (self.cache_hits / total_cache_requests * 100) if total_cache_requests > 0 else 0.0


class MetricsCollector:
    """Centralized metrics collection system."""

    def __init__(self, max_history_size: int = 1000):
        """Initialize metrics collector.

        Args:
            max_history_size: Maximum number of historical metrics to keep
        """
        self.max_history_size = max_history_size
        self._lock = Lock()

        # Operation-specific metrics
        self.operation_metrics: Dict[str, OperationMetrics] = {}

        # System-wide metrics
        self.system_metrics = {
            "total_requests": 0,
            "total_errors": 0,
            "total_cache_hits": 0,
            "total_cache_misses": 0,
            "server_start_time": time.time(),
            "peak_memory_usage": 0.0,
            "current_memory_usage": 0.0,
        }

        # Historical metrics (time-series data)
        self.metrics_history: deque = deque(maxlen=max_history_size)

        # Performance thresholds
        self.thresholds = {
            "slow_operation_ms": 1000,  # Operations slower than 1s
            "high_error_rate": 5.0,  # Error rate > 5%
            "low_cache_hit_rate": 50.0,  # Cache hit rate < 50%
        }

    def record_operation(
        self,
        operation_name: str,
        execution_time: float,
        cached: bool = False,
        error: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record metrics for an operation.

        Args:
            operation_name: Name of the operation
            execution_time: Execution time in seconds
            cached: Whether result was cached
            error: Whether operation resulted in error
            metadata: Additional metadata
        """
        with self._lock:
            # Update operation-specific metrics
            if operation_name not in self.operation_metrics:
                self.operation_metrics[operation_name] = OperationMetrics(operation_name)

            self.operation_metrics[operation_name].update(execution_time, cached, error)

            # Update system-wide metrics
            self.system_metrics["total_requests"] += 1
            if error:
                self.system_metrics["total_errors"] += 1
            if cached:
                self.system_metrics["total_cache_hits"] += 1
            else:
                self.system_metrics["total_cache_misses"] += 1

            # Record historical metric
            metric = PerformanceMetric(
                name=operation_name,
                value=execution_time,
                timestamp=time.time(),
                metadata=metadata or {},
            )
            self.metrics_history.append(metric)

    def record_memory_usage(self, memory_mb: float) -> None:
        """Record memory usage.

        Args:
            memory_mb: Memory usage in MB
        """
        with self._lock:
            self.system_metrics["current_memory_usage"] = memory_mb
            self.system_metrics["peak_memory_usage"] = max(
                self.system_metrics["peak_memory_usage"], memory_mb
            )

    def get_operation_metrics(self, operation_name: str) -> Optional[OperationMetrics]:
        """Get metrics for a specific operation.

        Args:
            operation_name: Name of the operation

        Returns:
            Operation metrics or None if not found
        """
        with self._lock:
            return self.operation_metrics.get(operation_name)

    def get_all_operation_metrics(self) -> Dict[str, OperationMetrics]:
        """Get metrics for all operations.

        Returns:
            Dictionary of operation metrics
        """
        with self._lock:
            return self.operation_metrics.copy()

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide metrics.

        Returns:
            Dictionary of system metrics
        """
        with self._lock:
            metrics = self.system_metrics.copy()

            # Calculate derived metrics
            uptime = time.time() - metrics["server_start_time"]
            metrics["uptime_seconds"] = uptime
            metrics["uptime_hours"] = uptime / 3600

            total_requests = metrics["total_requests"]
            if total_requests > 0:
                metrics["error_rate"] = (metrics["total_errors"] / total_requests) * 100
                metrics["requests_per_second"] = total_requests / uptime if uptime > 0 else 0

                total_cache_requests = metrics["total_cache_hits"] + metrics["total_cache_misses"]
                if total_cache_requests > 0:
                    metrics["cache_hit_rate"] = (
                        metrics["total_cache_hits"] / total_cache_requests
                    ) * 100
                else:
                    metrics["cache_hit_rate"] = 0.0
            else:
                metrics["error_rate"] = 0.0
                metrics["requests_per_second"] = 0.0
                metrics["cache_hit_rate"] = 0.0

            return metrics

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary.

        Returns:
            Dictionary with performance summary
        """
        with self._lock:
            system_metrics = self.get_system_metrics()

            # Top operations by call count
            top_operations = sorted(
                self.operation_metrics.values(), key=lambda x: x.call_count, reverse=True
            )[:10]

            # Slowest operations
            slowest_operations = sorted(
                [op for op in self.operation_metrics.values() if op.call_count > 0],
                key=lambda x: x.avg_time,
                reverse=True,
            )[:10]

            # Operations with high error rates
            error_prone_operations = [
                op
                for op in self.operation_metrics.values()
                if op.call_count > 0
                and (op.error_count / op.call_count * 100) > self.thresholds["high_error_rate"]
            ]

            # Operations with low cache hit rates
            low_cache_operations = [
                op
                for op in self.operation_metrics.values()
                if (op.cache_hits + op.cache_misses) > 0
                and op.get_cache_hit_rate() < self.thresholds["low_cache_hit_rate"]
            ]

            return {
                "system_metrics": system_metrics,
                "top_operations": [
                    {
                        "name": op.operation_name,
                        "call_count": op.call_count,
                        "avg_time_ms": op.avg_time * 1000,
                        "cache_hit_rate": op.get_cache_hit_rate(),
                    }
                    for op in top_operations
                ],
                "slowest_operations": [
                    {
                        "name": op.operation_name,
                        "avg_time_ms": op.avg_time * 1000,
                        "max_time_ms": op.max_time * 1000,
                        "call_count": op.call_count,
                    }
                    for op in slowest_operations
                ],
                "error_prone_operations": [
                    {
                        "name": op.operation_name,
                        "error_rate": (op.error_count / op.call_count * 100),
                        "error_count": op.error_count,
                        "total_calls": op.call_count,
                    }
                    for op in error_prone_operations
                ],
                "low_cache_operations": [
                    {
                        "name": op.operation_name,
                        "cache_hit_rate": op.get_cache_hit_rate(),
                        "cache_hits": op.cache_hits,
                        "cache_misses": op.cache_misses,
                    }
                    for op in low_cache_operations
                ],
                "performance_alerts": self._generate_performance_alerts(),
            }

    def get_time_series_data(
        self, operation_name: Optional[str] = None, minutes: int = 60
    ) -> List[Dict[str, Any]]:
        """Get time series data for metrics visualization.

        Args:
            operation_name: Specific operation to filter by (None for all)
            minutes: Number of minutes of history to return

        Returns:
            List of time series data points
        """
        with self._lock:
            cutoff_time = time.time() - (minutes * 60)

            filtered_metrics = [
                metric
                for metric in self.metrics_history
                if metric.timestamp >= cutoff_time
                and (operation_name is None or metric.name == operation_name)
            ]

            return [
                {
                    "timestamp": metric.timestamp,
                    "operation": metric.name,
                    "execution_time_ms": metric.value * 1000,
                    "metadata": metric.metadata,
                }
                for metric in filtered_metrics
            ]

    def _generate_performance_alerts(self) -> List[Dict[str, Any]]:
        """Generate performance alerts based on thresholds.

        Returns:
            List of performance alerts
        """
        alerts = []

        # Check for slow operations
        for op in self.operation_metrics.values():
            if op.avg_time * 1000 > self.thresholds["slow_operation_ms"]:
                alerts.append(
                    {
                        "type": "slow_operation",
                        "operation": op.operation_name,
                        "avg_time_ms": op.avg_time * 1000,
                        "threshold_ms": self.thresholds["slow_operation_ms"],
                        "severity": "warning",
                    }
                )

        # Check for high error rates
        for op in self.operation_metrics.values():
            if op.call_count > 0:
                error_rate = (op.error_count / op.call_count) * 100
                if error_rate > self.thresholds["high_error_rate"]:
                    alerts.append(
                        {
                            "type": "high_error_rate",
                            "operation": op.operation_name,
                            "error_rate": error_rate,
                            "threshold": self.thresholds["high_error_rate"],
                            "severity": "error",
                        }
                    )

        # Check for low cache hit rates
        for op in self.operation_metrics.values():
            cache_hit_rate = op.get_cache_hit_rate()
            if (op.cache_hits + op.cache_misses) > 10 and cache_hit_rate < self.thresholds[
                "low_cache_hit_rate"
            ]:
                alerts.append(
                    {
                        "type": "low_cache_hit_rate",
                        "operation": op.operation_name,
                        "cache_hit_rate": cache_hit_rate,
                        "threshold": self.thresholds["low_cache_hit_rate"],
                        "severity": "warning",
                    }
                )

        return alerts

    def reset_metrics(self) -> None:
        """Reset all metrics (useful for testing)."""
        with self._lock:
            self.operation_metrics.clear()
            self.metrics_history.clear()
            self.system_metrics = {
                "total_requests": 0,
                "total_errors": 0,
                "total_cache_hits": 0,
                "total_cache_misses": 0,
                "server_start_time": time.time(),
                "peak_memory_usage": 0.0,
                "current_memory_usage": 0.0,
            }

    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format.

        Args:
            format: Export format ('json', 'csv', 'prometheus')

        Returns:
            Formatted metrics string
        """
        if format == "json":
            import json

            return json.dumps(self.get_performance_summary(), indent=2, default=str)

        elif format == "csv":
            import csv
            import io

            output = io.StringIO()
            writer = csv.writer(output)

            # Write headers
            writer.writerow(
                [
                    "operation",
                    "call_count",
                    "avg_time_ms",
                    "min_time_ms",
                    "max_time_ms",
                    "error_count",
                    "cache_hit_rate",
                ]
            )

            # Write data
            for op in self.operation_metrics.values():
                writer.writerow(
                    [
                        op.operation_name,
                        op.call_count,
                        op.avg_time * 1000,
                        op.min_time * 1000,
                        op.max_time * 1000,
                        op.error_count,
                        op.get_cache_hit_rate(),
                    ]
                )

            return output.getvalue()

        elif format == "prometheus":
            # Basic Prometheus format
            lines = []
            for op in self.operation_metrics.values():
                safe_name = op.operation_name.replace("-", "_").replace(".", "_")
                lines.append(
                    f'calculator_operation_calls_total{{operation="{op.operation_name}"}} {op.call_count}'
                )
                lines.append(
                    f'calculator_operation_duration_seconds{{operation="{op.operation_name}",quantile="avg"}} {op.avg_time}'
                )
                lines.append(
                    f'calculator_operation_errors_total{{operation="{op.operation_name}"}} {op.error_count}'
                )

            return "\n".join(lines)

        else:
            raise ValueError(f"Unsupported export format: {format}")


# Global metrics collector instance
metrics_collector = MetricsCollector()
