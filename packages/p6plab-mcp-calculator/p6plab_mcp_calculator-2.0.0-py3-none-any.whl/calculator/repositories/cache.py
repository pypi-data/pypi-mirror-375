"""Cache repository with TTL and LRU eviction."""

import asyncio
import time
from collections import OrderedDict
from typing import Any, Dict, Optional

from ..core.errors.exceptions import CacheError
from .base import BaseRepository


class CacheRepository(BaseRepository):
    """Repository for caching computed results with TTL and LRU eviction.

    This repository provides an in-memory cache with automatic expiration
    and least-recently-used eviction when the cache reaches capacity.
    """

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """Initialize cache repository.

        Args:
            max_size: Maximum number of cache entries
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, Any] = OrderedDict()
        self.metadata: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        async with self._lock:
            if key not in self.cache:
                return None

            metadata = self.metadata[key]
            current_time = time.time()

            # Check if expired
            if current_time > metadata["expires_at"]:
                await self._delete_internal(key)
                return None

            # Update access metadata
            metadata["last_accessed"] = current_time
            metadata["access_count"] += 1

            # Move to end (most recently used)
            self.cache.move_to_end(key)

            return self.cache[key]

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cached value with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default if None)

        Returns:
            True if caching succeeded
        """
        try:
            async with self._lock:
                # Evict if at capacity and key doesn't exist
                if len(self.cache) >= self.max_size and key not in self.cache:
                    await self._evict_lru()

                ttl = ttl or self.default_ttl
                current_time = time.time()

                self.cache[key] = value
                self.metadata[key] = {
                    "created_at": current_time,
                    "expires_at": current_time + ttl,
                    "last_accessed": current_time,
                    "access_count": 1,
                    "ttl": ttl,
                }

                # Move to end (most recently used)
                self.cache.move_to_end(key)

                return True

        except Exception as e:
            raise CacheError(f"Failed to set cache key {key}: {str(e)}", cache_operation="set")

    async def delete(self, key: str) -> bool:
        """Delete cached value.

        Args:
            key: Cache key to delete

        Returns:
            True if key was deleted
        """
        async with self._lock:
            return await self._delete_internal(key)

    async def _delete_internal(self, key: str) -> bool:
        """Internal delete method (assumes lock is held).

        Args:
            key: Cache key to delete

        Returns:
            True if key was deleted
        """
        if key in self.cache:
            del self.cache[key]
            del self.metadata[key]
            return True
        return False

    async def exists(self, key: str) -> bool:
        """Check if key exists and is not expired.

        Args:
            key: Cache key to check

        Returns:
            True if key exists and is not expired
        """
        async with self._lock:
            if key not in self.cache:
                return False

            metadata = self.metadata[key]
            current_time = time.time()

            # Check if expired
            if current_time > metadata["expires_at"]:
                await self._delete_internal(key)
                return False

            return True

    async def clear(self) -> int:
        """Clear all cached entries.

        Returns:
            Number of entries cleared
        """
        async with self._lock:
            count = len(self.cache)
            self.cache.clear()
            self.metadata.clear()
            return count

    async def _evict_lru(self) -> bool:
        """Evict least recently used entry.

        Returns:
            True if an entry was evicted
        """
        if not self.cache:
            return False

        # Get least recently used key (first in OrderedDict)
        lru_key = next(iter(self.cache))
        await self._delete_internal(lru_key)
        return True

    async def cleanup_expired(self) -> int:
        """Remove all expired entries.

        Returns:
            Number of entries removed
        """
        async with self._lock:
            current_time = time.time()
            expired_keys = []

            for key, metadata in self.metadata.items():
                if current_time > metadata["expires_at"]:
                    expired_keys.append(key)

            for key in expired_keys:
                await self._delete_internal(key)

            return len(expired_keys)

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary containing cache statistics
        """
        async with self._lock:
            current_time = time.time()
            expired_count = 0
            total_access_count = 0

            for metadata in self.metadata.values():
                if current_time > metadata["expires_at"]:
                    expired_count += 1
                total_access_count += metadata["access_count"]

            return {
                "total_entries": len(self.cache),
                "max_size": self.max_size,
                "expired_entries": expired_count,
                "utilization": len(self.cache) / self.max_size if self.max_size > 0 else 0,
                "total_access_count": total_access_count,
                "average_access_count": total_access_count / len(self.cache) if self.cache else 0,
            }

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching a pattern.

        Args:
            pattern: Pattern to match (simple string contains matching)

        Returns:
            Number of entries invalidated
        """
        async with self._lock:
            matching_keys = [key for key in self.cache.keys() if pattern in key]

            for key in matching_keys:
                await self._delete_internal(key)

            return len(matching_keys)

    async def extend_ttl(self, key: str, additional_seconds: int) -> bool:
        """Extend the TTL of a cached entry.

        Args:
            key: Cache key
            additional_seconds: Additional seconds to add to TTL

        Returns:
            True if TTL was extended
        """
        async with self._lock:
            if key not in self.metadata:
                return False

            metadata = self.metadata[key]
            current_time = time.time()

            # Check if already expired
            if current_time > metadata["expires_at"]:
                await self._delete_internal(key)
                return False

            # Extend TTL
            metadata["expires_at"] += additional_seconds
            return True
