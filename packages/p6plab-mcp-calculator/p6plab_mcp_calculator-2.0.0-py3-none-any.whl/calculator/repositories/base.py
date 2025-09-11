"""Abstract base class for all repositories."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseRepository(ABC):
    """Abstract base class for all repositories.

    Repositories handle data access and storage operations,
    providing a consistent interface for different storage backends.
    """

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve data by key.

        Args:
            key: Key to retrieve data for

        Returns:
            Data associated with the key, or None if not found
        """
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store data with optional TTL.

        Args:
            key: Key to store data under
            value: Data to store
            ttl: Time to live in seconds (optional)

        Returns:
            True if storage succeeded
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete data by key.

        Args:
            key: Key to delete

        Returns:
            True if deletion succeeded
        """
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists.

        Args:
            key: Key to check

        Returns:
            True if key exists
        """
        pass

    async def get_or_default(self, key: str, default: Any = None) -> Any:
        """Get value or return default if not found.

        Args:
            key: Key to retrieve
            default: Default value to return if key not found

        Returns:
            Value associated with key or default
        """
        result = await self.get(key)
        return result if result is not None else default
