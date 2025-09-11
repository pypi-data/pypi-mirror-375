"""Error handling system for the calculator."""

from .exceptions import (
    CacheError,
    CalculatorError,
    ComputationError,
    ConfigurationError,
    TimeoutError,
    ValidationError,
)
from .handlers import ErrorRecoveryService, handle_operation_errors

__all__ = [
    "CalculatorError",
    "ValidationError",
    "ComputationError",
    "TimeoutError",
    "ConfigurationError",
    "CacheError",
    "handle_operation_errors",
    "ErrorRecoveryService",
]
