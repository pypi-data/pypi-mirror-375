"""Abstract base class for all services."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseService(ABC):
    """Abstract base class for all services.

    Services contain the business logic for mathematical operations and
    coordinate between repositories, strategies, and other components.
    """

    def __init__(self, config=None, cache=None):
        """Initialize the service with configuration and cache.

        Args:
            config: Configuration service instance
            cache: Cache repository instance
        """
        self.config = config
        self.cache = cache

    @abstractmethod
    async def process(self, operation: str, params: Dict[str, Any]) -> Any:
        """Process a service operation.

        Args:
            operation: Name of the operation to perform
            params: Parameters for the operation

        Returns:
            Result of the operation

        Raises:
            ValidationError: If parameters are invalid
            ComputationError: If the operation fails
        """
        pass

    async def get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Get a cached result if available.

        Args:
            cache_key: Key to look up in cache

        Returns:
            Cached result or None if not found/expired
        """
        if not self.cache:
            return None
        return await self.cache.get(cache_key)

    async def cache_result(self, cache_key: str, result: Any, ttl: Optional[int] = None) -> bool:
        """Cache a computation result.

        Args:
            cache_key: Key to store the result under
            result: Result to cache
            ttl: Time to live in seconds (optional)

        Returns:
            True if caching succeeded
        """
        if not self.cache:
            return False
        return await self.cache.set(cache_key, result, ttl)

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        if not self.config:
            return default
        return getattr(self.config, key, default)
