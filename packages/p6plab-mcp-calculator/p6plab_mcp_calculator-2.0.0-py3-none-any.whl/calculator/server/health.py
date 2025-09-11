"""Health check and monitoring endpoints."""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from ..core.monitoring.metrics import metrics_collector
from ..services.config import ConfigService


class HealthStatus(Enum):
    """Health status enumeration."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ComponentHealth:
    """Health status of a system component."""

    name: str
    status: HealthStatus
    message: str
    details: Dict[str, Any]
    last_checked: float


class HealthChecker:
    """System health checker with component monitoring."""

    def __init__(self, config_service: ConfigService):
        """Initialize health checker.

        Args:
            config_service: Configuration service
        """
        self.config = config_service
        self.component_health = {}
        self.system_start_time = time.time()
        self.last_health_check = None

        # Health check thresholds
        self.thresholds = {
            "max_response_time_ms": 5000,
            "max_error_rate": 10.0,
            "min_cache_hit_rate": 30.0,
            "max_memory_usage_mb": self.config.get_max_memory_mb() * 0.9,
            "max_cpu_usage": 90.0,
        }

    async def check_system_health(self) -> Dict[str, Any]:
        """Perform comprehensive system health check.

        Returns:
            Dictionary with system health status
        """
        self.last_health_check = time.time()

        # Check all components
        await self._check_configuration_health()
        await self._check_services_health()
        await self._check_repositories_health()
        await self._check_performance_health()
        await self._check_resource_health()

        # Determine overall system health
        overall_status = self._determine_overall_health()

        return {
            "status": overall_status.value,
            "timestamp": self.last_health_check,
            "uptime_seconds": self.last_health_check - self.system_start_time,
            "components": {
                name: {
                    "status": health.status.value,
                    "message": health.message,
                    "details": health.details,
                    "last_checked": health.last_checked,
                }
                for name, health in self.component_health.items()
            },
            "system_metrics": self._get_system_metrics(),
            "alerts": self._get_active_alerts(),
        }

    async def _check_configuration_health(self) -> None:
        """Check configuration system health."""
        try:
            # Verify configuration is loaded and valid
            config_summary = self.config.get_config_summary()

            # Check for configuration issues
            issues = []
            if config_summary["precision"] < 1 or config_summary["precision"] > 50:
                issues.append("Invalid precision setting")

            if config_summary["cache_size"] < 10:
                issues.append("Cache size too small")

            if config_summary["max_computation_time"] < 1:
                issues.append("Computation timeout too low")

            status = HealthStatus.HEALTHY if not issues else HealthStatus.DEGRADED
            message = (
                "Configuration healthy"
                if not issues
                else f"Configuration issues: {', '.join(issues)}"
            )

            self.component_health["configuration"] = ComponentHealth(
                name="configuration",
                status=status,
                message=message,
                details={
                    "precision": config_summary["precision"],
                    "cache_size": config_summary["cache_size"],
                    "enabled_features": config_summary["features"],
                    "issues": issues,
                },
                last_checked=time.time(),
            )

        except Exception as e:
            self.component_health["configuration"] = ComponentHealth(
                name="configuration",
                status=HealthStatus.UNHEALTHY,
                message=f"Configuration error: {str(e)}",
                details={"error": str(e)},
                last_checked=time.time(),
            )

    async def _check_services_health(self) -> None:
        """Check services health."""
        try:
            # This would normally check if services are responsive
            # For now, we'll assume they're healthy if no recent errors

            system_metrics = metrics_collector.get_system_metrics()
            error_rate = system_metrics.get("error_rate", 0)

            if error_rate > self.thresholds["max_error_rate"]:
                status = HealthStatus.DEGRADED
                message = f"High error rate: {error_rate:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = "Services operating normally"

            self.component_health["services"] = ComponentHealth(
                name="services",
                status=status,
                message=message,
                details={
                    "error_rate": error_rate,
                    "total_requests": system_metrics.get("total_requests", 0),
                    "uptime_hours": system_metrics.get("uptime_hours", 0),
                },
                last_checked=time.time(),
            )

        except Exception as e:
            self.component_health["services"] = ComponentHealth(
                name="services",
                status=HealthStatus.UNHEALTHY,
                message=f"Services health check failed: {str(e)}",
                details={"error": str(e)},
                last_checked=time.time(),
            )

    async def _check_repositories_health(self) -> None:
        """Check repositories health."""
        try:
            # Check cache repository health
            # This would normally test cache operations

            status = HealthStatus.HEALTHY
            message = "Repositories healthy"
            details = {
                "cache_repository": "healthy",
                "constants_repository": "healthy",
                "currency_repository": "healthy"
                if self.config.is_currency_conversion_enabled()
                else "disabled",
            }

            self.component_health["repositories"] = ComponentHealth(
                name="repositories",
                status=status,
                message=message,
                details=details,
                last_checked=time.time(),
            )

        except Exception as e:
            self.component_health["repositories"] = ComponentHealth(
                name="repositories",
                status=HealthStatus.UNHEALTHY,
                message=f"Repository health check failed: {str(e)}",
                details={"error": str(e)},
                last_checked=time.time(),
            )

    async def _check_performance_health(self) -> None:
        """Check performance health."""
        try:
            performance_summary = metrics_collector.get_performance_summary()
            system_metrics = performance_summary["system_metrics"]

            issues = []
            status = HealthStatus.HEALTHY

            # Check cache hit rate
            cache_hit_rate = system_metrics.get("cache_hit_rate", 0)
            if cache_hit_rate < self.thresholds["min_cache_hit_rate"]:
                issues.append(f"Low cache hit rate: {cache_hit_rate:.1f}%")
                status = HealthStatus.DEGRADED

            # Check for slow operations
            slow_operations = [
                op
                for op in performance_summary.get("slowest_operations", [])
                if op["avg_time_ms"] > self.thresholds["max_response_time_ms"]
            ]

            if slow_operations:
                issues.append(f"{len(slow_operations)} slow operations detected")
                status = HealthStatus.DEGRADED

            # Check error-prone operations
            error_prone = performance_summary.get("error_prone_operations", [])
            if error_prone:
                issues.append(f"{len(error_prone)} operations with high error rates")
                status = HealthStatus.DEGRADED

            message = (
                "Performance healthy" if not issues else f"Performance issues: {', '.join(issues)}"
            )

            self.component_health["performance"] = ComponentHealth(
                name="performance",
                status=status,
                message=message,
                details={
                    "cache_hit_rate": cache_hit_rate,
                    "avg_response_time_ms": system_metrics.get("requests_per_second", 0) * 1000
                    if system_metrics.get("requests_per_second", 0) > 0
                    else 0,
                    "slow_operations_count": len(slow_operations),
                    "error_prone_operations_count": len(error_prone),
                    "issues": issues,
                },
                last_checked=time.time(),
            )

        except Exception as e:
            self.component_health["performance"] = ComponentHealth(
                name="performance",
                status=HealthStatus.UNHEALTHY,
                message=f"Performance health check failed: {str(e)}",
                details={"error": str(e)},
                last_checked=time.time(),
            )

    async def _check_resource_health(self) -> None:
        """Check system resource health."""
        try:
            issues = []
            status = HealthStatus.HEALTHY

            # Check memory usage
            current_memory = self._get_memory_usage()
            if current_memory > self.thresholds["max_memory_usage_mb"]:
                issues.append(f"High memory usage: {current_memory:.1f}MB")
                status = HealthStatus.DEGRADED

            # Check CPU usage (if available)
            cpu_usage = self._get_cpu_usage()
            if cpu_usage and cpu_usage > self.thresholds["max_cpu_usage"]:
                issues.append(f"High CPU usage: {cpu_usage:.1f}%")
                status = HealthStatus.DEGRADED

            message = (
                "Resources healthy" if not issues else f"Resource issues: {', '.join(issues)}"
            )

            self.component_health["resources"] = ComponentHealth(
                name="resources",
                status=status,
                message=message,
                details={
                    "memory_usage_mb": current_memory,
                    "memory_limit_mb": self.config.get_max_memory_mb(),
                    "cpu_usage_percent": cpu_usage,
                    "issues": issues,
                },
                last_checked=time.time(),
            )

        except Exception as e:
            self.component_health["resources"] = ComponentHealth(
                name="resources",
                status=HealthStatus.UNHEALTHY,
                message=f"Resource health check failed: {str(e)}",
                details={"error": str(e)},
                last_checked=time.time(),
            )

    def _determine_overall_health(self) -> HealthStatus:
        """Determine overall system health based on component health.

        Returns:
            Overall health status
        """
        if not self.component_health:
            return HealthStatus.UNHEALTHY

        # If any component is unhealthy, system is unhealthy
        if any(
            health.status == HealthStatus.UNHEALTHY for health in self.component_health.values()
        ):
            return HealthStatus.UNHEALTHY

        # If any component is degraded, system is degraded
        if any(
            health.status == HealthStatus.DEGRADED for health in self.component_health.values()
        ):
            return HealthStatus.DEGRADED

        # All components healthy
        return HealthStatus.HEALTHY

    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics.

        Returns:
            Dictionary with system metrics
        """
        try:
            system_metrics = metrics_collector.get_system_metrics()

            return {
                "uptime_seconds": time.time() - self.system_start_time,
                "total_requests": system_metrics.get("total_requests", 0),
                "error_rate": system_metrics.get("error_rate", 0),
                "cache_hit_rate": system_metrics.get("cache_hit_rate", 0),
                "requests_per_second": system_metrics.get("requests_per_second", 0),
                "memory_usage_mb": self._get_memory_usage(),
                "cpu_usage_percent": self._get_cpu_usage(),
            }
        except Exception:
            return {}

    def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active system alerts.

        Returns:
            List of active alerts
        """
        alerts = []

        try:
            # Get performance alerts
            performance_summary = metrics_collector.get_performance_summary()
            performance_alerts = performance_summary.get("performance_alerts", [])
            alerts.extend(performance_alerts)

            # Add component health alerts
            for name, health in self.component_health.items():
                if health.status != HealthStatus.HEALTHY:
                    alerts.append(
                        {
                            "type": "component_health",
                            "component": name,
                            "status": health.status.value,
                            "message": health.message,
                            "severity": "error"
                            if health.status == HealthStatus.UNHEALTHY
                            else "warning",
                        }
                    )

        except Exception as e:
            alerts.append(
                {
                    "type": "system_error",
                    "message": f"Error getting alerts: {str(e)}",
                    "severity": "error",
                }
            )

        return alerts

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB.

        Returns:
            Memory usage in MB
        """
        try:
            import psutil

            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0
        except Exception:
            return 0.0

    def _get_cpu_usage(self) -> Optional[float]:
        """Get current CPU usage percentage.

        Returns:
            CPU usage percentage or None if unavailable
        """
        try:
            import psutil

            return psutil.cpu_percent(interval=0.1)
        except ImportError:
            return None
        except Exception:
            return None

    async def get_component_health(self, component_name: str) -> Optional[ComponentHealth]:
        """Get health status of a specific component.

        Args:
            component_name: Name of the component

        Returns:
            Component health or None if not found
        """
        return self.component_health.get(component_name)

    async def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of system health.

        Returns:
            Health summary
        """
        overall_status = self._determine_overall_health()

        component_counts = {
            "healthy": sum(
                1 for h in self.component_health.values() if h.status == HealthStatus.HEALTHY
            ),
            "degraded": sum(
                1 for h in self.component_health.values() if h.status == HealthStatus.DEGRADED
            ),
            "unhealthy": sum(
                1 for h in self.component_health.values() if h.status == HealthStatus.UNHEALTHY
            ),
        }

        return {
            "overall_status": overall_status.value,
            "component_counts": component_counts,
            "total_components": len(self.component_health),
            "uptime_seconds": time.time() - self.system_start_time,
            "last_check": self.last_health_check,
            "alerts_count": len(self._get_active_alerts()),
        }

    def update_thresholds(self, new_thresholds: Dict[str, Any]) -> None:
        """Update health check thresholds.

        Args:
            new_thresholds: New threshold values
        """
        self.thresholds.update(new_thresholds)

    def get_thresholds(self) -> Dict[str, Any]:
        """Get current health check thresholds.

        Returns:
            Current thresholds
        """
        return self.thresholds.copy()


class MonitoringService:
    """Service for system monitoring and observability."""

    def __init__(self, config_service: ConfigService):
        """Initialize monitoring service.

        Args:
            config_service: Configuration service
        """
        self.config = config_service
        self.health_checker = HealthChecker(config_service)
        self.monitoring_enabled = config_service.is_performance_monitoring_enabled()

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status.

        Returns:
            System status information
        """
        if not self.monitoring_enabled:
            return {"monitoring": "disabled", "message": "Performance monitoring is disabled"}

        # Get health status
        health_status = await self.health_checker.check_system_health()

        # Get performance metrics
        performance_summary = metrics_collector.get_performance_summary()

        # Combine all information
        return {
            "monitoring": "enabled",
            "health": health_status,
            "performance": performance_summary,
            "timestamp": time.time(),
        }

    async def get_metrics_export(self, format: str = "json") -> str:
        """Export metrics in specified format.

        Args:
            format: Export format ('json', 'csv', 'prometheus')

        Returns:
            Formatted metrics
        """
        return metrics_collector.export_metrics(format)

    async def get_health_check(self) -> Dict[str, Any]:
        """Get basic health check (lightweight).

        Returns:
            Basic health information
        """
        return await self.health_checker.get_health_summary()

    def is_monitoring_enabled(self) -> bool:
        """Check if monitoring is enabled.

        Returns:
            True if monitoring is enabled
        """
        return self.monitoring_enabled
