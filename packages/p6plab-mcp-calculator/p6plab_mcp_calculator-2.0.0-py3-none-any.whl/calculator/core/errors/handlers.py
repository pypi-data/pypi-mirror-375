"""Error handling decorators and recovery services."""

import asyncio
import time
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

from loguru import logger

from .exceptions import (
    ComputationError,
    ConfigurationError,
    TimeoutError,
    ValidationError,
)


def handle_operation_errors(operation_name: str):
    """Decorator for standardized error handling.

    This decorator wraps mathematical operations to provide consistent
    error handling, logging, and response formatting.

    Args:
        operation_name: Name of the operation for logging and responses
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000

                return {
                    "success": True,
                    "result": result,
                    "execution_time_ms": execution_time,
                    "operation": operation_name,
                }

            except ValidationError as e:
                logger.warning(f"Validation error in {operation_name}: {e.message}")
                return {
                    "success": False,
                    "error": "validation_error",
                    "message": e.message,
                    "operation": operation_name,
                    "field": e.field,
                    "suggestions": _get_validation_suggestions(e),
                }

            except ComputationError as e:
                logger.error(f"Computation error in {operation_name}: {e.message}")
                return {
                    "success": False,
                    "error": "computation_error",
                    "message": e.message,
                    "operation": operation_name,
                    "context": e.context,
                }

            except TimeoutError as e:
                logger.error(f"Timeout error in {operation_name}: {e.message}")
                return {
                    "success": False,
                    "error": "timeout_error",
                    "message": e.message,
                    "operation": operation_name,
                    "timeout_seconds": e.timeout_seconds,
                }

            except ConfigurationError as e:
                logger.error(f"Configuration error in {operation_name}: {e.message}")
                return {
                    "success": False,
                    "error": "configuration_error",
                    "message": e.message,
                    "operation": operation_name,
                    "config_key": e.config_key,
                }

            except Exception as e:
                logger.error(f"Unexpected error in {operation_name}: {str(e)}")
                return {
                    "success": False,
                    "error": "internal_error",
                    "message": "An unexpected error occurred",
                    "operation": operation_name,
                }

        return wrapper

    return decorator


def _get_validation_suggestions(error: ValidationError) -> List[str]:
    """Get suggestions for fixing validation errors.

    Args:
        error: The validation error

    Returns:
        List of suggestions for fixing the error
    """
    suggestions = []

    if error.field:
        if "number" in error.message.lower():
            suggestions.append(f"Ensure {error.field} is a valid number")
        elif "matrix" in error.message.lower():
            suggestions.append(f"Ensure {error.field} is a valid matrix (list of lists)")
        elif "positive" in error.message.lower():
            suggestions.append(f"Ensure {error.field} is a positive number")
        elif "range" in error.message.lower():
            suggestions.append(f"Check that {error.field} is within the valid range")

    if not suggestions:
        suggestions.append("Please check the input format and try again")

    return suggestions


class ErrorRecoveryService:
    """Service for handling error recovery and fallbacks.

    This service provides mechanisms for attempting fallback strategies
    when primary operations fail, improving system resilience.
    """

    def __init__(self, config=None):
        """Initialize error recovery service.

        Args:
            config: Configuration service instance
        """
        self.config = config
        self.fallback_strategies = {}
        self.error_history = {}
        self.recovery_stats = {"total_errors": 0, "recovered_errors": 0, "failed_recoveries": 0}

    async def execute_with_fallback(
        self, primary_func: Callable, fallback_funcs: List[Callable], operation_name: str
    ) -> Any:
        """Execute operation with fallback strategies.

        Args:
            primary_func: Primary function to execute
            fallback_funcs: List of fallback functions to try if primary fails
            operation_name: Name of the operation for logging

        Returns:
            Result from successful function execution

        Raises:
            ComputationError: If all methods fail
        """
        errors = []

        # Try primary function
        try:
            return await primary_func()
        except Exception as e:
            errors.append(f"Primary: {str(e)}")
            logger.warning(f"Primary method failed for {operation_name}: {e}")

        # Try fallback functions
        for i, fallback_func in enumerate(fallback_funcs):
            try:
                result = await fallback_func()
                logger.info(f"Fallback {i + 1} succeeded for {operation_name}")
                return result
            except Exception as e:
                errors.append(f"Fallback {i + 1}: {str(e)}")
                logger.warning(f"Fallback {i + 1} failed for {operation_name}: {e}")

        # All methods failed
        raise ComputationError(
            f"All methods failed for {operation_name}",
            operation=operation_name,
            context={"errors": errors},
        )

    def register_fallback_strategy(self, operation: str, fallback_func: Callable) -> None:
        """Register a fallback strategy for an operation.

        Args:
            operation: Name of the operation
            fallback_func: Fallback function to register
        """
        if operation not in self.fallback_strategies:
            self.fallback_strategies[operation] = []
        self.fallback_strategies[operation].append(fallback_func)

    def get_fallback_strategies(self, operation: str) -> List[Callable]:
        """Get registered fallback strategies for an operation.

        Args:
            operation: Name of the operation

        Returns:
            List of fallback functions
        """
        return self.fallback_strategies.get(operation, [])

    async def execute_with_circuit_breaker(
        self,
        operation_name: str,
        primary_func: Callable,
        fallback_funcs: Optional[List[Callable]] = None,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
    ) -> Any:
        """Execute operation with circuit breaker pattern.

        Args:
            operation_name: Name of the operation
            primary_func: Primary function to execute
            fallback_funcs: List of fallback functions
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds before attempting recovery

        Returns:
            Result from successful function execution
        """
        circuit_key = f"circuit_{operation_name}"

        # Check circuit breaker state
        if self._is_circuit_open(circuit_key, failure_threshold, recovery_timeout):
            logger.warning(f"Circuit breaker open for {operation_name}, using fallback")
            if fallback_funcs:
                return await self._execute_fallback_chain(fallback_funcs, operation_name)
            else:
                raise ComputationError(
                    f"Circuit breaker open for {operation_name} and no fallbacks available",
                    operation=operation_name,
                )

        try:
            # Execute primary function
            result = await primary_func()

            # Reset circuit breaker on success
            self._reset_circuit_breaker(circuit_key)

            return result

        except Exception as e:
            # Record failure
            self._record_circuit_failure(circuit_key)
            self.recovery_stats["total_errors"] += 1

            # Try fallbacks if available
            if fallback_funcs:
                try:
                    result = await self._execute_fallback_chain(fallback_funcs, operation_name)
                    self.recovery_stats["recovered_errors"] += 1
                    return result
                except Exception as fallback_error:
                    self.recovery_stats["failed_recoveries"] += 1
                    logger.error(f"All fallbacks failed for {operation_name}: {fallback_error}")
                    raise e
            else:
                self.recovery_stats["failed_recoveries"] += 1
                raise e

    async def _execute_fallback_chain(
        self, fallback_funcs: List[Callable], operation_name: str
    ) -> Any:
        """Execute chain of fallback functions.

        Args:
            fallback_funcs: List of fallback functions to try
            operation_name: Name of the operation

        Returns:
            Result from successful fallback
        """
        errors = []

        for i, fallback_func in enumerate(fallback_funcs):
            try:
                result = await fallback_func()
                logger.info(f"Fallback {i + 1} succeeded for {operation_name}")
                return result
            except Exception as e:
                errors.append(f"Fallback {i + 1}: {str(e)}")
                logger.warning(f"Fallback {i + 1} failed for {operation_name}: {e}")

        # All fallbacks failed
        raise ComputationError(
            f"All fallbacks failed for {operation_name}",
            operation=operation_name,
            context={"fallback_errors": errors},
        )

    def _is_circuit_open(
        self, circuit_key: str, failure_threshold: int, recovery_timeout: int
    ) -> bool:
        """Check if circuit breaker is open.

        Args:
            circuit_key: Circuit breaker key
            failure_threshold: Failure threshold
            recovery_timeout: Recovery timeout in seconds

        Returns:
            True if circuit is open
        """
        if circuit_key not in self.error_history:
            return False

        circuit_data = self.error_history[circuit_key]
        current_time = time.time()

        # Check if in recovery period
        if circuit_data.get("circuit_open_time"):
            if current_time - circuit_data["circuit_open_time"] > recovery_timeout:
                # Recovery period over, allow one test request
                circuit_data["circuit_open_time"] = None
                circuit_data["state"] = "half_open"
                return False
            else:
                return True

        # Check failure count
        recent_failures = [
            failure_time
            for failure_time in circuit_data.get("failure_times", [])
            if current_time - failure_time < recovery_timeout
        ]

        return len(recent_failures) >= failure_threshold

    def _record_circuit_failure(self, circuit_key: str) -> None:
        """Record a circuit breaker failure.

        Args:
            circuit_key: Circuit breaker key
        """
        current_time = time.time()

        if circuit_key not in self.error_history:
            self.error_history[circuit_key] = {"failure_times": [], "state": "closed"}

        circuit_data = self.error_history[circuit_key]
        circuit_data["failure_times"].append(current_time)

        # Keep only recent failures (last hour)
        circuit_data["failure_times"] = [
            t for t in circuit_data["failure_times"] if current_time - t < 3600
        ]

        # Open circuit if threshold exceeded
        if len(circuit_data["failure_times"]) >= 5:  # Default threshold
            circuit_data["circuit_open_time"] = current_time
            circuit_data["state"] = "open"
            logger.warning(f"Circuit breaker opened for {circuit_key}")

    def _reset_circuit_breaker(self, circuit_key: str) -> None:
        """Reset circuit breaker after successful operation.

        Args:
            circuit_key: Circuit breaker key
        """
        if circuit_key in self.error_history:
            self.error_history[circuit_key] = {"failure_times": [], "state": "closed"}

    async def execute_with_retry(
        self,
        operation_func: Callable,
        operation_name: str,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        backoff_multiplier: float = 2.0,
        retry_on_exceptions: tuple = (ComputationError, TimeoutError),
    ) -> Any:
        """Execute operation with retry logic.

        Args:
            operation_func: Function to execute
            operation_name: Name of the operation
            max_retries: Maximum number of retries
            retry_delay: Initial delay between retries
            backoff_multiplier: Multiplier for exponential backoff
            retry_on_exceptions: Exceptions that should trigger retry

        Returns:
            Result from successful execution
        """
        last_exception = None
        current_delay = retry_delay

        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(
                        f"Retrying {operation_name}, attempt {attempt + 1}/{max_retries + 1}"
                    )
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff_multiplier

                result = await operation_func()

                if attempt > 0:
                    logger.info(f"Retry succeeded for {operation_name} on attempt {attempt + 1}")
                    self.recovery_stats["recovered_errors"] += 1

                return result

            except Exception as e:
                last_exception = e

                # Check if this exception should trigger a retry
                if not isinstance(e, retry_on_exceptions):
                    logger.debug(
                        f"Exception {type(e).__name__} not in retry list for {operation_name}"
                    )
                    break

                if attempt < max_retries:
                    logger.warning(f"Attempt {attempt + 1} failed for {operation_name}: {str(e)}")
                else:
                    logger.error(f"All {max_retries + 1} attempts failed for {operation_name}")

        # All retries exhausted
        self.recovery_stats["total_errors"] += 1
        self.recovery_stats["failed_recoveries"] += 1

        raise ComputationError(
            f"Operation {operation_name} failed after {max_retries + 1} attempts",
            operation=operation_name,
            context={"last_error": str(last_exception), "attempts": max_retries + 1},
        )

    async def execute_with_timeout_and_fallback(
        self,
        operation_func: Callable,
        operation_name: str,
        timeout_seconds: float,
        fallback_func: Optional[Callable] = None,
    ) -> Any:
        """Execute operation with timeout and optional fallback.

        Args:
            operation_func: Function to execute
            operation_name: Name of the operation
            timeout_seconds: Timeout in seconds
            fallback_func: Optional fallback function

        Returns:
            Result from successful execution
        """
        try:
            result = await asyncio.wait_for(operation_func(), timeout=timeout_seconds)
            return result

        except asyncio.TimeoutError:
            logger.warning(f"Operation {operation_name} timed out after {timeout_seconds}s")

            if fallback_func:
                try:
                    logger.info(f"Executing fallback for timed out operation {operation_name}")
                    result = await fallback_func()
                    self.recovery_stats["recovered_errors"] += 1
                    return result
                except Exception as fallback_error:
                    self.recovery_stats["failed_recoveries"] += 1
                    raise TimeoutError(
                        f"Operation {operation_name} timed out and fallback failed",
                        operation=operation_name,
                        timeout_seconds=timeout_seconds,
                        context={"fallback_error": str(fallback_error)},
                    )
            else:
                self.recovery_stats["failed_recoveries"] += 1
                raise TimeoutError(
                    f"Operation {operation_name} timed out",
                    operation=operation_name,
                    timeout_seconds=timeout_seconds,
                )

    def get_recovery_stats(self) -> Dict[str, Any]:
        """Get error recovery statistics.

        Returns:
            Dictionary with recovery statistics
        """
        total_errors = self.recovery_stats["total_errors"]
        recovery_rate = (
            (self.recovery_stats["recovered_errors"] / total_errors * 100)
            if total_errors > 0
            else 0.0
        )

        return {
            "total_errors": total_errors,
            "recovered_errors": self.recovery_stats["recovered_errors"],
            "failed_recoveries": self.recovery_stats["failed_recoveries"],
            "recovery_rate_percent": recovery_rate,
            "circuit_breakers": {
                key: {
                    "state": data.get("state", "closed"),
                    "failure_count": len(data.get("failure_times", [])),
                    "circuit_open_time": data.get("circuit_open_time"),
                }
                for key, data in self.error_history.items()
            },
        }

    def reset_recovery_stats(self) -> None:
        """Reset recovery statistics."""
        self.recovery_stats = {"total_errors": 0, "recovered_errors": 0, "failed_recoveries": 0}
        self.error_history.clear()

    def get_circuit_breaker_status(self, operation_name: str) -> Dict[str, Any]:
        """Get circuit breaker status for an operation.

        Args:
            operation_name: Name of the operation

        Returns:
            Circuit breaker status
        """
        circuit_key = f"circuit_{operation_name}"

        if circuit_key not in self.error_history:
            return {"state": "closed", "failure_count": 0, "circuit_open_time": None}

        circuit_data = self.error_history[circuit_key]
        return {
            "state": circuit_data.get("state", "closed"),
            "failure_count": len(circuit_data.get("failure_times", [])),
            "circuit_open_time": circuit_data.get("circuit_open_time"),
        }


def create_resilient_operation(
    operation_name: str,
    primary_func: Callable,
    fallback_funcs: Optional[List[Callable]] = None,
    max_retries: int = 2,
    timeout_seconds: float = 30.0,
    enable_circuit_breaker: bool = True,
):
    """Create a resilient operation with comprehensive error handling.

    Args:
        operation_name: Name of the operation
        primary_func: Primary function to execute
        fallback_funcs: Optional fallback functions
        max_retries: Maximum retry attempts
        timeout_seconds: Operation timeout
        enable_circuit_breaker: Whether to enable circuit breaker

    Returns:
        Decorated function with resilience patterns
    """
    recovery_service = ErrorRecoveryService()

    async def resilient_wrapper(*args, **kwargs):
        """Wrapper function with resilience patterns."""

        # Create bound function
        bound_func = lambda: primary_func(*args, **kwargs)

        if enable_circuit_breaker and fallback_funcs:
            # Use circuit breaker with fallbacks
            return await recovery_service.execute_with_circuit_breaker(
                operation_name=operation_name,
                primary_func=bound_func,
                fallback_funcs=[lambda: f(*args, **kwargs) for f in fallback_funcs],
            )
        elif max_retries > 0:
            # Use retry logic
            return await recovery_service.execute_with_retry(
                operation_func=bound_func, operation_name=operation_name, max_retries=max_retries
            )
        else:
            # Use timeout with optional fallback
            fallback_func = None
            if fallback_funcs:
                fallback_func = lambda: fallback_funcs[0](*args, **kwargs)

            return await recovery_service.execute_with_timeout_and_fallback(
                operation_func=bound_func,
                operation_name=operation_name,
                timeout_seconds=timeout_seconds,
                fallback_func=fallback_func,
            )

    return resilient_wrapper
