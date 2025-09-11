"""Custom exception hierarchy for calculator operations."""

from typing import Any, Dict, Optional


class CalculatorError(Exception):
    """Base exception for calculator operations.

    All calculator-specific exceptions inherit from this base class
    to provide consistent error handling and context information.
    """

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Initialize calculator error.

        Args:
            message: Human-readable error message
            operation: Name of the operation that failed
            context: Additional context information
        """
        self.message = message
        self.operation = operation
        self.context = context or {}
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format.

        Returns:
            Dictionary representation of the error
        """
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "operation": self.operation,
            "context": self.context,
        }


class ValidationError(CalculatorError):
    """Raised when input validation fails.

    This exception is raised when user input does not meet the
    requirements for a mathematical operation.
    """

    def __init__(
        self, message: str, field: Optional[str] = None, value: Optional[Any] = None, **kwargs
    ):
        """Initialize validation error.

        Args:
            message: Error message
            field: Name of the field that failed validation
            value: The invalid value
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)
        self.field = field
        self.value = value
        if field:
            self.context["field"] = field
        if value is not None:
            self.context["value"] = str(value)


class ComputationError(CalculatorError):
    """Raised when mathematical computation fails.

    This exception is raised when a mathematical operation cannot
    be completed due to mathematical constraints or computational issues.
    """

    def __init__(self, message: str, computation_type: Optional[str] = None, **kwargs):
        """Initialize computation error.

        Args:
            message: Error message
            computation_type: Type of computation that failed
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)
        self.computation_type = computation_type
        if computation_type:
            self.context["computation_type"] = computation_type


class TimeoutError(CalculatorError):
    """Raised when operation exceeds time limit.

    This exception is raised when a mathematical operation takes
    longer than the configured maximum computation time.
    """

    def __init__(self, message: str, timeout_seconds: Optional[float] = None, **kwargs):
        """Initialize timeout error.

        Args:
            message: Error message
            timeout_seconds: The timeout limit that was exceeded
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)
        self.timeout_seconds = timeout_seconds
        if timeout_seconds:
            self.context["timeout_seconds"] = timeout_seconds


class ConfigurationError(CalculatorError):
    """Raised when configuration is invalid or missing.

    This exception is raised when the calculator configuration
    contains invalid values or required settings are missing.
    """

    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        """Initialize configuration error.

        Args:
            message: Error message
            config_key: The configuration key that caused the error
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)
        self.config_key = config_key
        if config_key:
            self.context["config_key"] = config_key


class CacheError(CalculatorError):
    """Raised when cache operations fail.

    This exception is raised when caching operations encounter
    errors that prevent normal operation.
    """

    def __init__(self, message: str, cache_operation: Optional[str] = None, **kwargs):
        """Initialize cache error.

        Args:
            message: Error message
            cache_operation: The cache operation that failed (get, set, delete, etc.)
            **kwargs: Additional arguments for base class
        """
        super().__init__(message, **kwargs)
        self.cache_operation = cache_operation
        if cache_operation:
            self.context["cache_operation"] = cache_operation


class SecurityError(CalculatorError):
    """Raised when security validation fails.

    This exception is raised when security checks detect potentially
    dangerous operations or input that violates security policies.
    """

    def __init__(self, message: str, security_check: Optional[str] = None, details: Optional[Dict[str, Any]] = None, **kwargs):
        """Initialize security error.

        Args:
            message: Error message
            security_check: The security check that failed
            details: Additional details about the security violation
            **kwargs: Additional arguments for base class
        """
        # Merge details into context
        context = kwargs.get('context', {})
        if details:
            context.update(details)
        kwargs['context'] = context
        
        super().__init__(message, **kwargs)
        self.security_check = security_check
        if security_check:
            self.context["security_check"] = security_check
