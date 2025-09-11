"""Security auditing for calculator operations."""

import hashlib
import json
import time
from dataclasses import asdict, dataclass
from enum import Enum
from functools import wraps
from typing import Any, Dict, List, Optional, Union

from loguru import logger

from ..errors.exceptions import SecurityError


class AuditEventType(Enum):
    """Types of audit events."""

    OPERATION_START = "operation_start"
    OPERATION_SUCCESS = "operation_success"
    OPERATION_ERROR = "operation_error"
    SECURITY_VIOLATION = "security_violation"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INPUT_VALIDATION_FAILED = "input_validation_failed"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    CONFIGURATION_CHANGE = "configuration_change"
    AUTHENTICATION_ATTEMPT = "authentication_attempt"
    AUTHORIZATION_FAILURE = "authorization_failure"


class RiskLevel(Enum):
    """Risk levels for audit events."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Audit event data structure."""

    event_id: str
    timestamp: float
    event_type: AuditEventType
    risk_level: RiskLevel
    client_id: str
    operation: str
    success: bool
    duration_ms: Optional[float] = None
    input_hash: Optional[str] = None
    output_hash: Optional[str] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert audit event to dictionary."""
        data = asdict(self)
        data["event_type"] = self.event_type.value
        data["risk_level"] = self.risk_level.value
        return data

    def to_json(self) -> str:
        """Convert audit event to JSON string."""
        return json.dumps(self.to_dict(), default=str)


class SecurityAuditor:
    """Security auditor for calculator operations."""

    def __init__(self, max_events: int = 10000):
        """Initialize security auditor.

        Args:
            max_events: Maximum number of events to keep in memory
        """
        self.max_events = max_events
        self.events: List[AuditEvent] = []
        self.event_counter = 0

        # Risk analysis
        self.risk_patterns = {
            "high_frequency_errors": {"threshold": 10, "window": 60},
            "large_input_attempts": {"threshold": 5, "window": 300},
            "suspicious_expressions": {"threshold": 3, "window": 300},
            "rate_limit_violations": {"threshold": 5, "window": 300},
        }

        # Statistics
        self.stats = {
            "total_events": 0,
            "events_by_type": {},
            "events_by_risk": {},
            "clients_tracked": set(),
            "suspicious_clients": set(),
        }

    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        self.event_counter += 1
        return f"audit_{int(time.time())}_{self.event_counter}"

    def _hash_data(self, data: Any) -> str:
        """Generate hash of data for audit trail."""
        try:
            data_str = json.dumps(data, sort_keys=True, default=str)
            return hashlib.sha256(data_str.encode()).hexdigest()[:16]
        except Exception:
            return "hash_error"

    def _determine_risk_level(
        self, event_type: AuditEventType, metadata: Dict[str, Any]
    ) -> RiskLevel:
        """Determine risk level for event."""
        if event_type in [AuditEventType.SECURITY_VIOLATION, AuditEventType.AUTHORIZATION_FAILURE]:
            return RiskLevel.CRITICAL
        elif event_type in [
            AuditEventType.RATE_LIMIT_EXCEEDED,
            AuditEventType.SUSPICIOUS_ACTIVITY,
        ]:
            return RiskLevel.HIGH
        elif event_type in [
            AuditEventType.INPUT_VALIDATION_FAILED,
            AuditEventType.OPERATION_ERROR,
        ]:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def record_event(
        self,
        event_type: AuditEventType,
        client_id: str,
        operation: str,
        success: bool,
        duration_ms: Optional[float] = None,
        input_data: Optional[Any] = None,
        output_data: Optional[Any] = None,
        error: Optional[Exception] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        """Record an audit event.

        Args:
            event_type: Type of event
            client_id: Client identifier
            operation: Operation name
            success: Whether operation succeeded
            duration_ms: Operation duration in milliseconds
            input_data: Input data (will be hashed)
            output_data: Output data (will be hashed)
            error: Exception if operation failed
            metadata: Additional metadata

        Returns:
            Created audit event
        """
        metadata = metadata or {}

        # Create event
        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=time.time(),
            event_type=event_type,
            risk_level=self._determine_risk_level(event_type, metadata),
            client_id=client_id,
            operation=operation,
            success=success,
            duration_ms=duration_ms,
            input_hash=self._hash_data(input_data) if input_data is not None else None,
            output_hash=self._hash_data(output_data) if output_data is not None else None,
            error_type=type(error).__name__ if error else None,
            error_message=str(error) if error else None,
            metadata=metadata,
        )

        # Add to events list
        self.events.append(event)

        # Maintain max events limit
        if len(self.events) > self.max_events:
            self.events.pop(0)

        # Update statistics
        self._update_stats(event)

        # Log event
        self._log_event(event)

        # Check for suspicious patterns
        self._check_suspicious_patterns(event)

        return event

    def _update_stats(self, event: AuditEvent) -> None:
        """Update audit statistics."""
        self.stats["total_events"] += 1

        # Update by type
        event_type = event.event_type.value
        self.stats["events_by_type"][event_type] = (
            self.stats["events_by_type"].get(event_type, 0) + 1
        )

        # Update by risk
        risk_level = event.risk_level.value
        self.stats["events_by_risk"][risk_level] = (
            self.stats["events_by_risk"].get(risk_level, 0) + 1
        )

        # Track clients
        self.stats["clients_tracked"].add(event.client_id)

        # Track suspicious clients
        if event.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            self.stats["suspicious_clients"].add(event.client_id)

    def _log_event(self, event: AuditEvent) -> None:
        """Log audit event."""
        log_data = {
            "audit_event_id": event.event_id,
            "event_type": event.event_type.value,
            "risk_level": event.risk_level.value,
            "client_id": event.client_id,
            "operation": event.operation,
            "success": event.success,
            "duration_ms": event.duration_ms,
        }

        if event.error_type:
            log_data["error_type"] = event.error_type
            log_data["error_message"] = event.error_message

        if event.metadata:
            log_data.update(event.metadata)

        # Log with appropriate level based on risk
        if event.risk_level == RiskLevel.CRITICAL:
            logger.critical("Security audit event", **log_data)
        elif event.risk_level == RiskLevel.HIGH:
            logger.error("Security audit event", **log_data)
        elif event.risk_level == RiskLevel.MEDIUM:
            logger.warning("Security audit event", **log_data)
        else:
            logger.info("Security audit event", **log_data)

    def _check_suspicious_patterns(self, event: AuditEvent) -> None:
        """Check for suspicious activity patterns."""
        current_time = event.timestamp
        client_id = event.client_id

        # Get recent events for this client
        recent_events = [
            e
            for e in self.events[-100:]  # Check last 100 events
            if e.client_id == client_id and current_time - e.timestamp <= 300  # Last 5 minutes
        ]

        # Check patterns
        self._check_high_frequency_errors(recent_events, client_id)
        self._check_large_input_attempts(recent_events, client_id)
        self._check_suspicious_expressions(recent_events, client_id)
        self._check_rate_limit_violations(recent_events, client_id)

    def _check_high_frequency_errors(
        self, recent_events: List[AuditEvent], client_id: str
    ) -> None:
        """Check for high frequency of errors."""
        pattern = self.risk_patterns["high_frequency_errors"]
        error_events = [e for e in recent_events if not e.success]

        if len(error_events) >= pattern["threshold"]:
            self.record_event(
                AuditEventType.SUSPICIOUS_ACTIVITY,
                client_id,
                "pattern_detection",
                False,
                metadata={
                    "pattern": "high_frequency_errors",
                    "error_count": len(error_events),
                    "threshold": pattern["threshold"],
                    "window_seconds": pattern["window"],
                },
            )

    def _check_large_input_attempts(self, recent_events: List[AuditEvent], client_id: str) -> None:
        """Check for attempts with unusually large inputs."""
        pattern = self.risk_patterns["large_input_attempts"]
        large_input_events = [
            e
            for e in recent_events
            if e.metadata and e.metadata.get("input_size_bytes", 0) > 10000
        ]

        if len(large_input_events) >= pattern["threshold"]:
            self.record_event(
                AuditEventType.SUSPICIOUS_ACTIVITY,
                client_id,
                "pattern_detection",
                False,
                metadata={
                    "pattern": "large_input_attempts",
                    "large_input_count": len(large_input_events),
                    "threshold": pattern["threshold"],
                },
            )

    def _check_suspicious_expressions(
        self, recent_events: List[AuditEvent], client_id: str
    ) -> None:
        """Check for suspicious mathematical expressions."""
        pattern = self.risk_patterns["suspicious_expressions"]
        suspicious_events = [
            e
            for e in recent_events
            if e.event_type == AuditEventType.INPUT_VALIDATION_FAILED
            and e.metadata
            and "expression" in e.metadata.get("operation", "")
        ]

        if len(suspicious_events) >= pattern["threshold"]:
            self.record_event(
                AuditEventType.SUSPICIOUS_ACTIVITY,
                client_id,
                "pattern_detection",
                False,
                metadata={
                    "pattern": "suspicious_expressions",
                    "suspicious_count": len(suspicious_events),
                    "threshold": pattern["threshold"],
                },
            )

    def _check_rate_limit_violations(
        self, recent_events: List[AuditEvent], client_id: str
    ) -> None:
        """Check for repeated rate limit violations."""
        pattern = self.risk_patterns["rate_limit_violations"]
        rate_limit_events = [
            e for e in recent_events if e.event_type == AuditEventType.RATE_LIMIT_EXCEEDED
        ]

        if len(rate_limit_events) >= pattern["threshold"]:
            self.record_event(
                AuditEventType.SUSPICIOUS_ACTIVITY,
                client_id,
                "pattern_detection",
                False,
                metadata={
                    "pattern": "rate_limit_violations",
                    "violation_count": len(rate_limit_events),
                    "threshold": pattern["threshold"],
                },
            )

    def get_events(
        self,
        client_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        risk_level: Optional[RiskLevel] = None,
        limit: int = 100,
    ) -> List[AuditEvent]:
        """Get audit events with optional filtering.

        Args:
            client_id: Filter by client ID
            event_type: Filter by event type
            risk_level: Filter by risk level
            limit: Maximum number of events to return

        Returns:
            List of matching audit events
        """
        events = self.events

        # Apply filters
        if client_id:
            events = [e for e in events if e.client_id == client_id]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        if risk_level:
            events = [e for e in events if e.risk_level == risk_level]

        # Sort by timestamp (newest first) and limit
        events = sorted(events, key=lambda e: e.timestamp, reverse=True)
        return events[:limit]

    def get_client_summary(self, client_id: str) -> Dict[str, Any]:
        """Get security summary for a specific client.

        Args:
            client_id: Client identifier

        Returns:
            Client security summary
        """
        client_events = [e for e in self.events if e.client_id == client_id]

        if not client_events:
            return {"client_id": client_id, "no_events": True}

        # Calculate statistics
        total_events = len(client_events)
        successful_events = len([e for e in client_events if e.success])
        failed_events = total_events - successful_events

        # Risk distribution
        risk_distribution = {}
        for risk_level in RiskLevel:
            count = len([e for e in client_events if e.risk_level == risk_level])
            risk_distribution[risk_level.value] = count

        # Recent activity (last hour)
        recent_cutoff = time.time() - 3600
        recent_events = [e for e in client_events if e.timestamp > recent_cutoff]

        # Suspicious activity
        suspicious_events = [
            e for e in client_events if e.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        ]

        return {
            "client_id": client_id,
            "total_events": total_events,
            "successful_events": successful_events,
            "failed_events": failed_events,
            "success_rate": successful_events / total_events if total_events > 0 else 0,
            "risk_distribution": risk_distribution,
            "recent_events_count": len(recent_events),
            "suspicious_events_count": len(suspicious_events),
            "is_suspicious": client_id in self.stats["suspicious_clients"],
            "first_seen": min(e.timestamp for e in client_events),
            "last_seen": max(e.timestamp for e in client_events),
        }

    def get_security_report(self) -> Dict[str, Any]:
        """Get comprehensive security report.

        Returns:
            Security report dictionary
        """
        current_time = time.time()

        # Recent activity (last hour)
        recent_events = [e for e in self.events if current_time - e.timestamp <= 3600]

        # High-risk events (last 24 hours)
        high_risk_events = [
            e
            for e in self.events
            if current_time - e.timestamp <= 86400
            and e.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        ]

        # Top clients by activity
        client_activity = {}
        for event in recent_events:
            client_activity[event.client_id] = client_activity.get(event.client_id, 0) + 1

        top_clients = sorted(client_activity.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "report_timestamp": current_time,
            "total_events": self.stats["total_events"],
            "events_by_type": dict(self.stats["events_by_type"]),
            "events_by_risk": dict(self.stats["events_by_risk"]),
            "total_clients": len(self.stats["clients_tracked"]),
            "suspicious_clients": len(self.stats["suspicious_clients"]),
            "recent_events_count": len(recent_events),
            "high_risk_events_count": len(high_risk_events),
            "top_active_clients": top_clients,
            "suspicious_client_list": list(self.stats["suspicious_clients"]),
        }

    def export_events(self, format: str = "json") -> Union[str, List[Dict[str, Any]]]:
        """Export audit events.

        Args:
            format: Export format ('json' or 'dict')

        Returns:
            Exported events
        """
        if format == "json":
            return json.dumps([event.to_dict() for event in self.events], default=str, indent=2)
        else:
            return [event.to_dict() for event in self.events]

    def clear_events(self, older_than_hours: Optional[int] = None) -> int:
        """Clear audit events.

        Args:
            older_than_hours: Only clear events older than specified hours

        Returns:
            Number of events cleared
        """
        if older_than_hours is None:
            # Clear all events
            cleared_count = len(self.events)
            self.events.clear()
            return cleared_count
        else:
            # Clear old events
            cutoff_time = time.time() - (older_than_hours * 3600)
            old_events = [e for e in self.events if e.timestamp < cutoff_time]
            self.events = [e for e in self.events if e.timestamp >= cutoff_time]
            return len(old_events)


# Global security auditor instance
security_auditor = SecurityAuditor()


def audit_operation(operation_name: str, client_id: str = "default"):
    """Decorator to audit operation execution.

    Args:
        operation_name: Name of the operation
        client_id: Client identifier
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            input_data = kwargs.get("data") or (args[1] if len(args) > 1 else None)

            # Record operation start
            security_auditor.record_event(
                AuditEventType.OPERATION_START,
                client_id,
                operation_name,
                True,
                input_data=input_data,
            )

            try:
                # Execute operation
                result = await func(*args, **kwargs)

                # Record success
                duration_ms = (time.time() - start_time) * 1000
                security_auditor.record_event(
                    AuditEventType.OPERATION_SUCCESS,
                    client_id,
                    operation_name,
                    True,
                    duration_ms=duration_ms,
                    input_data=input_data,
                    output_data=result,
                )

                return result

            except Exception as error:
                # Record error
                duration_ms = (time.time() - start_time) * 1000

                # Determine event type based on error
                if isinstance(error, SecurityError):
                    event_type = AuditEventType.SECURITY_VIOLATION
                else:
                    event_type = AuditEventType.OPERATION_ERROR

                security_auditor.record_event(
                    event_type,
                    client_id,
                    operation_name,
                    False,
                    duration_ms=duration_ms,
                    input_data=input_data,
                    error=error,
                )

                raise

        return wrapper

    return decorator
