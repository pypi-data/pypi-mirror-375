"""Rate limiting for calculator operations."""

import asyncio
import time
from collections import defaultdict, deque
from functools import wraps
from typing import Dict, Tuple

from ..errors.exceptions import SecurityError


class RateLimiter:
    """Rate limiter for calculator operations."""

    def __init__(self, max_requests: int = 2000, window_seconds: int = 60):
        """Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds

        # Track requests per client
        self.client_requests: Dict[str, deque] = defaultdict(lambda: deque())

        # Track concurrent operations per client
        self.concurrent_operations: Dict[str, int] = defaultdict(int)
        self.max_concurrent = 50

        # Cleanup task (will be started lazily)
        self._cleanup_task = None

    def _start_cleanup_task(self):
        """Start background cleanup task."""
        try:
            if self._cleanup_task is None or self._cleanup_task.done():
                self._cleanup_task = asyncio.create_task(self._cleanup_old_requests())
        except RuntimeError:
            # No event loop running, cleanup task will be started when needed
            pass

    async def _cleanup_old_requests(self):
        """Clean up old request records periodically."""
        while True:
            try:
                current_time = time.time()
                cutoff_time = current_time - self.window_seconds

                # Clean up old requests
                for client_id in list(self.client_requests.keys()):
                    requests = self.client_requests[client_id]

                    # Remove old requests
                    while requests and requests[0] < cutoff_time:
                        requests.popleft()

                    # Remove empty queues
                    if not requests:
                        del self.client_requests[client_id]

                # Clean up concurrent operation counts for inactive clients
                active_clients = set(self.client_requests.keys())
                for client_id in list(self.concurrent_operations.keys()):
                    if (
                        client_id not in active_clients
                        and self.concurrent_operations[client_id] == 0
                    ):
                        del self.concurrent_operations[client_id]

                # Sleep for cleanup interval
                await asyncio.sleep(60)  # Cleanup every minute

            except asyncio.CancelledError:
                break
            except Exception:
                # Continue cleanup on errors
                await asyncio.sleep(60)

    def check_rate_limit(self, client_id: str) -> Tuple[bool, Dict[str, int]]:
        """Check if client is within rate limits.

        Args:
            client_id: Client identifier

        Returns:
            Tuple of (allowed, rate_limit_info)
        """
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds

        # Get client's request history
        requests = self.client_requests[client_id]

        # Remove old requests
        while requests and requests[0] < cutoff_time:
            requests.popleft()

        # Check rate limit
        current_requests = len(requests)
        allowed = current_requests < self.max_requests

        rate_limit_info = {
            "current_requests": current_requests,
            "max_requests": self.max_requests,
            "window_seconds": self.window_seconds,
            "reset_time": int(current_time + self.window_seconds),
            "remaining_requests": max(0, self.max_requests - current_requests),
        }

        return allowed, rate_limit_info

    def record_request(self, client_id: str) -> None:
        """Record a request for rate limiting.

        Args:
            client_id: Client identifier
        """
        current_time = time.time()
        self.client_requests[client_id].append(current_time)

    def check_concurrent_limit(self, client_id: str) -> Tuple[bool, Dict[str, int]]:
        """Check if client is within concurrent operation limits.

        Args:
            client_id: Client identifier

        Returns:
            Tuple of (allowed, concurrent_info)
        """
        current_concurrent = self.concurrent_operations[client_id]
        allowed = current_concurrent < self.max_concurrent

        concurrent_info = {
            "current_concurrent": current_concurrent,
            "max_concurrent": self.max_concurrent,
            "remaining_concurrent": max(0, self.max_concurrent - current_concurrent),
        }

        return allowed, concurrent_info

    def start_operation(self, client_id: str) -> None:
        """Mark start of concurrent operation.

        Args:
            client_id: Client identifier
        """
        self.concurrent_operations[client_id] += 1

    def end_operation(self, client_id: str) -> None:
        """Mark end of concurrent operation.

        Args:
            client_id: Client identifier
        """
        if self.concurrent_operations[client_id] > 0:
            self.concurrent_operations[client_id] -= 1

    async def acquire(self, client_id: str) -> Dict[str, int]:
        """Acquire rate limit permission for client.

        Args:
            client_id: Client identifier

        Returns:
            Rate limit information

        Raises:
            SecurityError: If rate limit exceeded
        """
        # Check rate limit
        rate_allowed, rate_info = self.check_rate_limit(client_id)
        if not rate_allowed:
            raise SecurityError(
                f"Rate limit exceeded: {rate_info['current_requests']}/{rate_info['max_requests']} "
                f"requests in {rate_info['window_seconds']} seconds",
                details=rate_info,
            )

        # Check concurrent limit
        concurrent_allowed, concurrent_info = self.check_concurrent_limit(client_id)
        if not concurrent_allowed:
            raise SecurityError(
                f"Concurrent operation limit exceeded: {concurrent_info['current_concurrent']}/"
                f"{concurrent_info['max_concurrent']} operations",
                details=concurrent_info,
            )

        # Record request and start operation
        self.record_request(client_id)
        self.start_operation(client_id)

        # Return combined info
        return {**rate_info, **concurrent_info}

    def release(self, client_id: str) -> None:
        """Release concurrent operation slot.

        Args:
            client_id: Client identifier
        """
        self.end_operation(client_id)

    def get_client_stats(self, client_id: str) -> Dict[str, int]:
        """Get statistics for a specific client.

        Args:
            client_id: Client identifier

        Returns:
            Client statistics
        """
        _, rate_info = self.check_rate_limit(client_id)
        _, concurrent_info = self.check_concurrent_limit(client_id)

        return {**rate_info, **concurrent_info}

    def get_global_stats(self) -> Dict[str, int]:
        """Get global rate limiter statistics.

        Returns:
            Global statistics
        """
        total_clients = len(self.client_requests)
        total_requests = sum(len(requests) for requests in self.client_requests.values())
        total_concurrent = sum(self.concurrent_operations.values())

        return {
            "total_clients": total_clients,
            "total_active_requests": total_requests,
            "total_concurrent_operations": total_concurrent,
            "max_requests_per_client": self.max_requests,
            "max_concurrent_per_client": self.max_concurrent,
            "window_seconds": self.window_seconds,
        }

    async def shutdown(self):
        """Shutdown rate limiter and cleanup resources."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit_decorator(client_id_func=None):
    """Decorator to apply rate limiting to operations.

    Args:
        client_id_func: Function to extract client ID from arguments
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract client ID
            if client_id_func:
                client_id = client_id_func(*args, **kwargs)
            else:
                # Default: use 'default' as client ID
                client_id = kwargs.get("client_id", "default")

            # Acquire rate limit
            rate_info = await rate_limiter.acquire(client_id)

            try:
                # Execute operation
                result = await func(*args, **kwargs)
                return result
            finally:
                # Release concurrent slot
                rate_limiter.release(client_id)

        return wrapper

    return decorator


class AdaptiveRateLimiter(RateLimiter):
    """Adaptive rate limiter that adjusts limits based on system load."""

    def __init__(self, base_max_requests: int = 2000, window_seconds: int = 60):
        """Initialize adaptive rate limiter.

        Args:
            base_max_requests: Base maximum requests
            window_seconds: Time window in seconds
        """
        super().__init__(base_max_requests, window_seconds)
        self.base_max_requests = base_max_requests
        self.load_factor = 1.0  # Current load factor (1.0 = normal)

        # Load monitoring
        self.error_count = 0
        self.success_count = 0
        self.last_adjustment = time.time()
        self.adjustment_interval = 30  # Adjust every 30 seconds

    def record_success(self):
        """Record successful operation."""
        self.success_count += 1
        self._maybe_adjust_limits()

    def record_error(self):
        """Record failed operation."""
        self.error_count += 1
        self._maybe_adjust_limits()

    def _maybe_adjust_limits(self):
        """Adjust limits based on error rate."""
        current_time = time.time()
        if current_time - self.last_adjustment < self.adjustment_interval:
            return

        total_operations = self.success_count + self.error_count
        if total_operations < 10:  # Need minimum operations for adjustment
            return

        error_rate = self.error_count / total_operations

        # Adjust load factor based on error rate
        if error_rate > 0.1:  # High error rate (>10%)
            self.load_factor = max(0.5, self.load_factor * 0.8)  # Reduce limits
        elif error_rate < 0.02:  # Low error rate (<2%)
            self.load_factor = min(2.0, self.load_factor * 1.1)  # Increase limits

        # Update max requests based on load factor
        self.max_requests = int(self.base_max_requests * self.load_factor)

        # Reset counters
        self.success_count = 0
        self.error_count = 0
        self.last_adjustment = current_time

    def get_adaptive_stats(self) -> Dict[str, float]:
        """Get adaptive rate limiter statistics.

        Returns:
            Adaptive statistics
        """
        total_operations = self.success_count + self.error_count
        error_rate = self.error_count / total_operations if total_operations > 0 else 0

        return {
            "load_factor": self.load_factor,
            "current_max_requests": self.max_requests,
            "base_max_requests": self.base_max_requests,
            "error_rate": error_rate,
            "total_operations": total_operations,
            "success_count": self.success_count,
            "error_count": self.error_count,
        }


# Adaptive rate limiter instance
adaptive_rate_limiter = AdaptiveRateLimiter()


def adaptive_rate_limit_decorator(client_id_func=None):
    """Decorator to apply adaptive rate limiting to operations.

    Args:
        client_id_func: Function to extract client ID from arguments
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract client ID
            if client_id_func:
                client_id = client_id_func(*args, **kwargs)
            else:
                client_id = kwargs.get("client_id", "default")

            # Acquire rate limit
            rate_info = await adaptive_rate_limiter.acquire(client_id)

            try:
                # Execute operation
                result = await func(*args, **kwargs)
                adaptive_rate_limiter.record_success()
                return result
            except Exception:
                adaptive_rate_limiter.record_error()
                raise
            finally:
                # Release concurrent slot
                adaptive_rate_limiter.release(client_id)

        return wrapper

    return decorator
