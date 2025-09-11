"""Middleware for request/response processing."""

import time
import uuid
from functools import wraps
from typing import Any, Callable, Dict

from loguru import logger

from ..core.errors.exceptions import ComputationError, TimeoutError, ValidationError
from ..services.config import ConfigService


class RequestMiddleware:
    """Middleware for processing MCP requests."""

    def __init__(self, config_service: ConfigService):
        """Initialize request middleware.

        Args:
            config_service: Configuration service
        """
        self.config = config_service
        self.request_count = 0
        self.active_requests = {}

    def request_logging(self, func: Callable) -> Callable:
        """Middleware for request logging with correlation IDs.

        Args:
            func: Function to wrap

        Returns:
            Wrapped function with logging
        """

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate correlation ID
            correlation_id = str(uuid.uuid4())[:8]
            self.request_count += 1

            # Extract request info
            request_info = {
                "correlation_id": correlation_id,
                "request_number": self.request_count,
                "function": func.__name__,
                "timestamp": time.time(),
            }

            # Log request start
            if self.config.is_performance_monitoring_enabled():
                logger.info(
                    f"[{correlation_id}] Request {self.request_count}: {func.__name__} started"
                )

            # Track active request
            self.active_requests[correlation_id] = request_info

            try:
                start_time = time.time()
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time

                # Add metadata to result
                if isinstance(result, dict):
                    result["_metadata"] = {
                        "correlation_id": correlation_id,
                        "execution_time_ms": execution_time * 1000,
                        "request_number": self.request_count,
                    }

                # Log successful completion
                if self.config.is_performance_monitoring_enabled():
                    logger.info(f"[{correlation_id}] Request completed in {execution_time:.3f}s")

                return result

            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"[{correlation_id}] Request failed after {execution_time:.3f}s: {str(e)}"
                )
                raise

            finally:
                # Remove from active requests
                self.active_requests.pop(correlation_id, None)

        return wrapper

    def performance_monitoring(self, func: Callable) -> Callable:
        """Middleware for performance monitoring.

        Args:
            func: Function to wrap

        Returns:
            Wrapped function with performance monitoring
        """

        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not self.config.is_performance_monitoring_enabled():
                return await func(*args, **kwargs)

            start_time = time.time()
            start_memory = self._get_memory_usage()

            try:
                result = await func(*args, **kwargs)

                # Calculate metrics
                execution_time = time.time() - start_time
                end_memory = self._get_memory_usage()
                memory_delta = end_memory - start_memory

                # Add performance metrics to result
                if isinstance(result, dict):
                    if "_metadata" not in result:
                        result["_metadata"] = {}

                    result["_metadata"].update(
                        {
                            "performance": {
                                "execution_time_ms": execution_time * 1000,
                                "memory_usage_mb": end_memory,
                                "memory_delta_mb": memory_delta,
                            }
                        }
                    )

                # Log performance metrics
                logger.debug(
                    f"Performance: {func.__name__} - {execution_time:.3f}s, {memory_delta:.2f}MB"
                )

                return result

            except Exception:
                execution_time = time.time() - start_time
                logger.warning(f"Performance: {func.__name__} failed after {execution_time:.3f}s")
                raise

        return wrapper

    def timeout_protection(self, func: Callable) -> Callable:
        """Middleware for timeout protection.

        Args:
            func: Function to wrap

        Returns:
            Wrapped function with timeout protection
        """

        @wraps(func)
        async def wrapper(*args, **kwargs):
            import asyncio

            timeout = self.config.get_max_computation_time()

            try:
                result = await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
                return result

            except asyncio.TimeoutError:
                logger.error(f"Function {func.__name__} timed out after {timeout}s")
                raise TimeoutError(
                    f"Operation timed out after {timeout} seconds",
                    operation=func.__name__,
                    timeout_seconds=timeout,
                )

        return wrapper

    def input_validation(self, func: Callable) -> Callable:
        """Middleware for input validation and sanitization.

        Args:
            func: Function to wrap

        Returns:
            Wrapped function with input validation
        """

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Validate input size
            max_input_size = self.config.get_max_input_size()

            # Check all string arguments
            for arg in args:
                if isinstance(arg, str) and len(arg) > max_input_size:
                    raise ValidationError(
                        f"Input size exceeds maximum of {max_input_size} characters"
                    )

            for key, value in kwargs.items():
                if isinstance(value, str) and len(value) > max_input_size:
                    raise ValidationError(
                        f"Input '{key}' size exceeds maximum of {max_input_size} characters"
                    )

            # Sanitize inputs (remove potentially dangerous characters)
            sanitized_kwargs = {}
            for key, value in kwargs.items():
                if isinstance(value, str):
                    # Basic sanitization - remove null bytes and control characters
                    sanitized_value = "".join(
                        char for char in value if ord(char) >= 32 or char in "\t\n\r"
                    )
                    sanitized_kwargs[key] = sanitized_value
                else:
                    sanitized_kwargs[key] = value

            return await func(*args, **sanitized_kwargs)

        return wrapper

    def rate_limiting(self, func: Callable) -> Callable:
        """Middleware for rate limiting.

        Args:
            func: Function to wrap

        Returns:
            Wrapped function with rate limiting
        """

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Simple rate limiting based on request count
            rate_limit = self.config.get_rate_limit_per_minute()

            # Check if we're within rate limit (simplified implementation)
            current_time = time.time()
            minute_ago = current_time - 60

            # Count recent requests
            recent_requests = sum(
                1
                for req_info in self.active_requests.values()
                if req_info["timestamp"] > minute_ago
            )

            if recent_requests >= rate_limit:
                logger.warning(f"Rate limit exceeded: {recent_requests} requests in last minute")
                raise ValidationError(
                    f"Rate limit exceeded: maximum {rate_limit} requests per minute"
                )

            return await func(*args, **kwargs)

        return wrapper

    def error_handling(self, func: Callable) -> Callable:
        """Middleware for standardized error handling.

        Args:
            func: Function to wrap

        Returns:
            Wrapped function with error handling
        """

        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)

            except ValidationError as e:
                logger.warning(f"Validation error in {func.__name__}: {e.message}")
                return {
                    "success": False,
                    "error": "validation_error",
                    "message": e.message,
                    "operation": func.__name__,
                }

            except ComputationError as e:
                logger.error(f"Computation error in {func.__name__}: {e.message}")
                return {
                    "success": False,
                    "error": "computation_error",
                    "message": e.message,
                    "operation": func.__name__,
                    "context": e.context,
                }

            except TimeoutError as e:
                logger.error(f"Timeout error in {func.__name__}: {e.message}")
                return {
                    "success": False,
                    "error": "timeout_error",
                    "message": e.message,
                    "operation": func.__name__,
                    "timeout_seconds": e.timeout_seconds,
                }

            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
                return {
                    "success": False,
                    "error": "internal_error",
                    "message": "An unexpected error occurred",
                    "operation": func.__name__,
                }

        return wrapper

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
            # psutil not available, return 0
            return 0.0
        except Exception:
            return 0.0

    def get_active_requests(self) -> Dict[str, Any]:
        """Get information about active requests.

        Returns:
            Dictionary with active request information
        """
        return {
            "count": len(self.active_requests),
            "requests": list(self.active_requests.values()),
        }

    def get_request_stats(self) -> Dict[str, Any]:
        """Get request statistics.

        Returns:
            Dictionary with request statistics
        """
        return {
            "total_requests": self.request_count,
            "active_requests": len(self.active_requests),
            "average_requests_per_minute": self._calculate_request_rate(),
        }

    def _calculate_request_rate(self) -> float:
        """Calculate average requests per minute.

        Returns:
            Average requests per minute
        """
        if not self.active_requests:
            return 0.0

        current_time = time.time()
        minute_ago = current_time - 60

        recent_requests = sum(
            1 for req_info in self.active_requests.values() if req_info["timestamp"] > minute_ago
        )

        return recent_requests


class ResponseMiddleware:
    """Middleware for processing MCP responses."""

    def __init__(self, config_service: ConfigService):
        """Initialize response middleware.

        Args:
            config_service: Configuration service
        """
        self.config = config_service

    def response_formatting(self, func: Callable) -> Callable:
        """Middleware for consistent response formatting.

        Args:
            func: Function to wrap

        Returns:
            Wrapped function with response formatting
        """

        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)

            # Ensure consistent response format
            if not isinstance(result, dict):
                result = {"result": result}

            # Add standard fields if not present
            if "success" not in result:
                result["success"] = True

            if "timestamp" not in result:
                result["timestamp"] = time.time()

            # Add version information
            result["calculator_version"] = "2.0.0"  # Version from config

            return result

        return wrapper

    def response_compression(self, func: Callable) -> Callable:
        """Middleware for response compression (if needed).

        Args:
            func: Function to wrap

        Returns:
            Wrapped function with response compression
        """

        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)

            # For large responses, we could implement compression here
            # For now, just return the result as-is

            return result

        return wrapper

    def response_caching_headers(self, func: Callable) -> Callable:
        """Middleware for adding caching information to responses.

        Args:
            func: Function to wrap

        Returns:
            Wrapped function with caching headers
        """

        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)

            if isinstance(result, dict) and self.config.is_caching_enabled():
                # Add caching metadata
                if "_metadata" not in result:
                    result["_metadata"] = {}

                result["_metadata"]["caching"] = {
                    "cacheable": True,
                    "ttl_seconds": self.config.get_cache_ttl(),
                }

            return result

        return wrapper


class MiddlewareStack:
    """Stack for combining multiple middleware functions."""

    def __init__(self, config_service: ConfigService):
        """Initialize middleware stack.

        Args:
            config_service: Configuration service
        """
        self.request_middleware = RequestMiddleware(config_service)
        self.response_middleware = ResponseMiddleware(config_service)
        self.config = config_service

    def create_full_middleware(self, func: Callable) -> Callable:
        """Create full middleware stack for a function.

        Args:
            func: Function to wrap

        Returns:
            Function wrapped with all middleware
        """
        # Apply middleware in order (innermost first)
        wrapped = func

        # Response middleware (applied first, executed last)
        wrapped = self.response_middleware.response_caching_headers(wrapped)
        wrapped = self.response_middleware.response_formatting(wrapped)
        wrapped = self.response_middleware.response_compression(wrapped)

        # Request middleware (applied last, executed first)
        wrapped = self.request_middleware.error_handling(wrapped)
        wrapped = self.request_middleware.timeout_protection(wrapped)
        wrapped = self.request_middleware.performance_monitoring(wrapped)
        wrapped = self.request_middleware.input_validation(wrapped)
        wrapped = self.request_middleware.rate_limiting(wrapped)
        wrapped = self.request_middleware.request_logging(wrapped)

        return wrapped

    def create_lightweight_middleware(self, func: Callable) -> Callable:
        """Create lightweight middleware stack (essential only).

        Args:
            func: Function to wrap

        Returns:
            Function wrapped with essential middleware
        """
        wrapped = func

        # Essential middleware only
        wrapped = self.response_middleware.response_formatting(wrapped)
        wrapped = self.request_middleware.error_handling(wrapped)
        wrapped = self.request_middleware.input_validation(wrapped)
        wrapped = self.request_middleware.request_logging(wrapped)

        return wrapped

    def get_middleware_stats(self) -> Dict[str, Any]:
        """Get middleware statistics.

        Returns:
            Dictionary with middleware statistics
        """
        return {
            "request_stats": self.request_middleware.get_request_stats(),
            "active_requests": self.request_middleware.get_active_requests(),
            "config": {
                "performance_monitoring": self.config.is_performance_monitoring_enabled(),
                "caching": self.config.is_caching_enabled(),
                "max_computation_time": self.config.get_max_computation_time(),
                "rate_limit": self.config.get_rate_limit_per_minute(),
            },
        }
