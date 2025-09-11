"""Structured logging configuration."""

import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from loguru import logger


class StructuredFormatter:
    """Custom formatter for structured logging."""

    def __init__(self, include_correlation_id: bool = True):
        """Initialize structured formatter.

        Args:
            include_correlation_id: Whether to include correlation IDs
        """
        self.include_correlation_id = include_correlation_id

    def format(self, record) -> str:
        """Format log record as structured JSON.

        Args:
            record: Log record

        Returns:
            Formatted log string
        """
        # Extract basic information
        log_entry = {
            "timestamp": datetime.fromtimestamp(record["time"].timestamp()).isoformat(),
            "level": record["level"].name,
            "logger": record["name"],
            "message": record["message"],
            "module": record["module"],
            "function": record["function"],
            "line": record["line"],
        }

        # Add correlation ID if available
        if self.include_correlation_id and "correlation_id" in record["extra"]:
            log_entry["correlation_id"] = record["extra"]["correlation_id"]

        # Add any extra fields
        for key, value in record["extra"].items():
            if key not in log_entry:
                log_entry[key] = value

        # Add exception information if present
        if record["exception"]:
            log_entry["exception"] = {
                "type": record["exception"].type.__name__,
                "value": str(record["exception"].value),
                "traceback": record["exception"].traceback,
            }

        return json.dumps(log_entry, default=str)


def setup_structured_logging(
    log_level: str = "INFO",
    log_format: str = "structured",
    enable_correlation_ids: bool = True,
    log_file: Optional[str] = None,
) -> None:
    """Set up structured logging configuration.

    Args:
        log_level: Logging level
        log_format: Log format ('structured' or 'simple')
        enable_correlation_ids: Whether to enable correlation ID tracking
        log_file: Optional log file path
    """
    # Remove default handler
    logger.remove()

    if log_format == "structured":
        # Structured JSON logging
        formatter = StructuredFormatter(include_correlation_id=enable_correlation_ids)

        # Console handler
        logger.add(
            sys.stdout, level=log_level, format=formatter.format, colorize=False, serialize=False
        )

        # File handler if specified
        if log_file:
            logger.add(
                log_file,
                level=log_level,
                format=formatter.format,
                rotation="10 MB",
                retention="7 days",
                compression="gz",
                serialize=False,
            )

    else:
        # Simple human-readable logging
        format_string = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )

        if enable_correlation_ids:
            format_string = (
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "[{extra[correlation_id]}] | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>"
            )

        # Console handler
        logger.add(sys.stdout, level=log_level, format=format_string, colorize=True)

        # File handler if specified
        if log_file:
            logger.add(
                log_file,
                level=log_level,
                format=format_string,
                rotation="10 MB",
                retention="7 days",
                compression="gz",
                colorize=False,
            )

    # Configure logger for specific modules
    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "level": log_level,
                "format": formatter.format if log_format == "structured" else format_string,
            }
        ]
    )


class CorrelationIdFilter:
    """Filter to add correlation IDs to log records."""

    def __init__(self):
        """Initialize correlation ID filter."""
        self.correlation_ids = {}

    def set_correlation_id(self, correlation_id: str) -> None:
        """Set correlation ID for current context.

        Args:
            correlation_id: Correlation ID to set
        """
        import threading

        thread_id = threading.get_ident()
        self.correlation_ids[thread_id] = correlation_id

    def get_correlation_id(self) -> Optional[str]:
        """Get correlation ID for current context.

        Returns:
            Correlation ID or None
        """
        import threading

        thread_id = threading.get_ident()
        return self.correlation_ids.get(thread_id)

    def clear_correlation_id(self) -> None:
        """Clear correlation ID for current context."""
        import threading

        thread_id = threading.get_ident()
        self.correlation_ids.pop(thread_id, None)

    def filter(self, record) -> bool:
        """Filter log record to add correlation ID.

        Args:
            record: Log record

        Returns:
            True to include record
        """
        correlation_id = self.get_correlation_id()
        if correlation_id:
            record["extra"]["correlation_id"] = correlation_id
        return True


class PerformanceLogger:
    """Logger for performance-related events."""

    def __init__(self, logger_name: str = "performance"):
        """Initialize performance logger.

        Args:
            logger_name: Name of the logger
        """
        self.logger = logger.bind(component="performance")

    def log_operation_start(self, operation: str, correlation_id: str, **kwargs) -> None:
        """Log operation start.

        Args:
            operation: Operation name
            correlation_id: Correlation ID
            **kwargs: Additional parameters
        """
        self.logger.bind(
            correlation_id=correlation_id,
            operation=operation,
            event_type="operation_start",
            **kwargs,
        ).info(f"Starting operation: {operation}")

    def log_operation_complete(
        self,
        operation: str,
        correlation_id: str,
        execution_time: float,
        cached: bool = False,
        **kwargs,
    ) -> None:
        """Log operation completion.

        Args:
            operation: Operation name
            correlation_id: Correlation ID
            execution_time: Execution time in seconds
            cached: Whether result was cached
            **kwargs: Additional parameters
        """
        self.logger.bind(
            correlation_id=correlation_id,
            operation=operation,
            event_type="operation_complete",
            execution_time_ms=execution_time * 1000,
            cached=cached,
            **kwargs,
        ).info(f"Completed operation: {operation} in {execution_time:.3f}s")

    def log_operation_error(
        self,
        operation: str,
        correlation_id: str,
        error: Exception,
        execution_time: float,
        **kwargs,
    ) -> None:
        """Log operation error.

        Args:
            operation: Operation name
            correlation_id: Correlation ID
            error: Exception that occurred
            execution_time: Execution time before error
            **kwargs: Additional parameters
        """
        self.logger.bind(
            correlation_id=correlation_id,
            operation=operation,
            event_type="operation_error",
            error_type=type(error).__name__,
            error_message=str(error),
            execution_time_ms=execution_time * 1000,
            **kwargs,
        ).error(f"Operation failed: {operation} - {str(error)}")

    def log_cache_event(
        self, operation: str, correlation_id: str, event_type: str, cache_key: str, **kwargs
    ) -> None:
        """Log cache-related event.

        Args:
            operation: Operation name
            correlation_id: Correlation ID
            event_type: Type of cache event (hit, miss, set, evict)
            cache_key: Cache key
            **kwargs: Additional parameters
        """
        self.logger.bind(
            correlation_id=correlation_id,
            operation=operation,
            event_type=f"cache_{event_type}",
            cache_key=cache_key,
            **kwargs,
        ).debug(f"Cache {event_type}: {cache_key}")

    def log_performance_alert(
        self, alert_type: str, operation: str, threshold: float, actual_value: float, **kwargs
    ) -> None:
        """Log performance alert.

        Args:
            alert_type: Type of alert
            operation: Operation name
            threshold: Threshold value
            actual_value: Actual value that triggered alert
            **kwargs: Additional parameters
        """
        self.logger.bind(
            event_type="performance_alert",
            alert_type=alert_type,
            operation=operation,
            threshold=threshold,
            actual_value=actual_value,
            **kwargs,
        ).warning(f"Performance alert: {alert_type} for {operation}")


class AuditLogger:
    """Logger for audit events."""

    def __init__(self, logger_name: str = "audit"):
        """Initialize audit logger.

        Args:
            logger_name: Name of the logger
        """
        self.logger = logger.bind(component="audit")

    def log_configuration_change(
        self, setting: str, old_value: Any, new_value: Any, user: str = "system"
    ) -> None:
        """Log configuration change.

        Args:
            setting: Configuration setting name
            old_value: Previous value
            new_value: New value
            user: User who made the change
        """
        self.logger.bind(
            event_type="configuration_change",
            setting=setting,
            old_value=str(old_value),
            new_value=str(new_value),
            user=user,
        ).info(f"Configuration changed: {setting}")

    def log_tool_registration(
        self, tool_name: str, tool_group: str, enabled: bool, user: str = "system"
    ) -> None:
        """Log tool registration event.

        Args:
            tool_name: Name of the tool
            tool_group: Tool group
            enabled: Whether tool is enabled
            user: User who registered the tool
        """
        self.logger.bind(
            event_type="tool_registration",
            tool_name=tool_name,
            tool_group=tool_group,
            enabled=enabled,
            user=user,
        ).info(f"Tool {'registered' if enabled else 'disabled'}: {tool_name}")

    def log_security_event(
        self, event_type: str, details: Dict[str, Any], severity: str = "info"
    ) -> None:
        """Log security-related event.

        Args:
            event_type: Type of security event
            details: Event details
            severity: Event severity
        """
        log_method = getattr(self.logger, severity.lower(), self.logger.info)

        log_method(
            self.logger.bind(
                event_type="security_event", security_event_type=event_type, **details
            ),
            f"Security event: {event_type}",
        )


# Global logger instances
correlation_filter = CorrelationIdFilter()
performance_logger = PerformanceLogger()
audit_logger = AuditLogger()


def get_logger_with_correlation(correlation_id: str):
    """Get logger with correlation ID bound.

    Args:
        correlation_id: Correlation ID

    Returns:
        Logger with correlation ID
    """
    return logger.bind(correlation_id=correlation_id)


def configure_logging_from_config(config_service) -> None:
    """Configure logging from configuration service.

    Args:
        config_service: Configuration service instance
    """
    log_level = config_service.get_log_level()
    log_format = config_service.get_config_value("logging.log_format", "structured")
    enable_correlation_ids = config_service.get_config_value(
        "logging.enable_correlation_ids", True
    )

    # Set up logging
    setup_structured_logging(
        log_level=log_level, log_format=log_format, enable_correlation_ids=enable_correlation_ids
    )

    logger.info(
        "Logging configured",
        level=log_level,
        format=log_format,
        correlation_ids=enable_correlation_ids,
    )
