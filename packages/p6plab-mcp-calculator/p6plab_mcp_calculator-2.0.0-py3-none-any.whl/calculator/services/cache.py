"""Cache service for intelligent caching with TTL and memory management."""

import hashlib
import time
from typing import Any, Callable, Dict, Optional

from loguru import logger

from ..core.monitoring.metrics import metrics_collector
from ..repositories.cache import CacheRepository


class CacheService:
    """Service for managing computation caching with intelligent strategies."""

    def __init__(self, cache_repository: CacheRepository, config=None):
        """Initialize cache service.

        Args:
            cache_repository: Cache repository instance
            config: Configuration service
        """
        self.cache_repo = cache_repository
        self.config = config
        self.cache_stats = {"hits": 0, "misses": 0, "sets": 0, "evictions": 0, "errors": 0}

    async def get_or_compute(
        self,
        key: str,
        compute_func: Callable,
        ttl: Optional[int] = None,
        force_refresh: bool = False,
        cache_metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Get cached result or compute and cache.

        Args:
            key: Cache key
            compute_func: Function to compute result if not cached
            ttl: Time to live in seconds
            force_refresh: Force recomputation even if cached
            cache_metadata: Additional metadata for caching decision

        Returns:
            Cached or computed result
        """
        start_time = time.time()

        try:
            # Check if caching is enabled
            if not self._is_caching_enabled():
                logger.debug(f"Caching disabled, computing directly for key: {key}")
                return await self._execute_compute_func(compute_func)

            # Check cache first (unless force refresh)
            if not force_refresh:
                cached_result = await self.cache_repo.get(key)
                if cached_result is not None:
                    self.cache_stats["hits"] += 1
                    execution_time = time.time() - start_time

                    # Record metrics
                    metrics_collector.record_operation(
                        operation_name=f"cache_get_{self._extract_operation_from_key(key)}",
                        execution_time=execution_time,
                        cached=True,
                        metadata={"cache_key": key},
                    )

                    logger.debug(f"Cache hit for key: {key}")
                    return cached_result

            # Cache miss or force refresh - compute result
            self.cache_stats["misses"] += 1
            logger.debug(f"Cache miss for key: {key}, computing result")

            result = await self._execute_compute_func(compute_func)

            # Cache the result
            await self._cache_result(key, result, ttl, cache_metadata)

            execution_time = time.time() - start_time

            # Record metrics
            metrics_collector.record_operation(
                operation_name=f"cache_compute_{self._extract_operation_from_key(key)}",
                execution_time=execution_time,
                cached=False,
                metadata={"cache_key": key, "force_refresh": force_refresh},
            )

            return result

        except Exception as e:
            self.cache_stats["errors"] += 1
            logger.error(f"Cache service error for key {key}: {str(e)}")

            # Fall back to direct computation
            try:
                return await self._execute_compute_func(compute_func)
            except Exception as compute_error:
                logger.error(f"Compute function also failed for key {key}: {str(compute_error)}")
                raise compute_error

    async def _execute_compute_func(self, compute_func: Callable) -> Any:
        """Execute compute function safely.

        Args:
            compute_func: Function to execute

        Returns:
            Function result
        """
        if callable(compute_func):
            if callable(compute_func):
                # Check if it's an async function
                import asyncio

                if asyncio.iscoroutinefunction(compute_func):
                    return await compute_func()
                else:
                    return compute_func()
            else:
                return compute_func
        else:
            return compute_func

    async def _cache_result(
        self, key: str, result: Any, ttl: Optional[int], metadata: Optional[Dict[str, Any]]
    ) -> None:
        """Cache computation result with intelligent caching decisions.

        Args:
            key: Cache key
            result: Result to cache
            ttl: Time to live
            metadata: Additional metadata
        """
        try:
            # Determine if result should be cached
            if not self._should_cache_result(result, metadata):
                logger.debug(f"Result not cached for key {key} due to caching policy")
                return

            # Determine TTL
            effective_ttl = self._determine_ttl(key, result, ttl, metadata)

            # Cache the result
            success = await self.cache_repo.set(key, result, effective_ttl)

            if success:
                self.cache_stats["sets"] += 1
                logger.debug(f"Cached result for key: {key} with TTL: {effective_ttl}s")
            else:
                logger.warning(f"Failed to cache result for key: {key}")

        except Exception as e:
            logger.error(f"Error caching result for key {key}: {str(e)}")
            # Don't raise - caching failure shouldn't break the operation

    def _should_cache_result(self, result: Any, metadata: Optional[Dict[str, Any]]) -> bool:
        """Determine if result should be cached based on intelligent policies.

        Args:
            result: Result to evaluate
            metadata: Additional metadata

        Returns:
            True if result should be cached
        """
        # Don't cache None results
        if result is None:
            return False

        # Don't cache error results
        if isinstance(result, dict) and result.get("success") is False:
            return False

        # Don't cache very large results (configurable threshold)
        max_cache_size = self._get_max_cacheable_size()
        try:
            import sys

            result_size = sys.getsizeof(result)
            if result_size > max_cache_size:
                logger.debug(
                    f"Result too large to cache: {result_size} bytes > {max_cache_size} bytes"
                )
                return False
        except Exception:
            # If we can't determine size, cache it anyway
            pass

        # Check metadata-based policies
        if metadata:
            # Don't cache if explicitly marked as non-cacheable
            if metadata.get("cacheable") is False:
                return False

            # Don't cache time-sensitive results
            if metadata.get("time_sensitive") is True:
                return False

        return True

    def _determine_ttl(
        self,
        key: str,
        result: Any,
        requested_ttl: Optional[int],
        metadata: Optional[Dict[str, Any]],
    ) -> int:
        """Determine appropriate TTL for caching.

        Args:
            key: Cache key
            result: Result being cached
            requested_ttl: Requested TTL
            metadata: Additional metadata

        Returns:
            Effective TTL in seconds
        """
        # Use requested TTL if provided
        if requested_ttl is not None:
            return requested_ttl

        # Use metadata TTL if provided
        if metadata and "ttl" in metadata:
            return metadata["ttl"]

        # Use operation-specific TTL based on key pattern
        operation_ttls = {
            "arithmetic": 3600,  # 1 hour for arithmetic operations
            "matrix": 1800,  # 30 minutes for matrix operations
            "statistics": 1800,  # 30 minutes for statistics
            "calculus": 7200,  # 2 hours for calculus (more expensive)
            "constants": 86400,  # 24 hours for constants
            "currency": 900,  # 15 minutes for currency (more volatile)
        }

        for operation, ttl in operation_ttls.items():
            if operation in key.lower():
                return ttl

        # Default TTL from configuration
        return self._get_default_ttl()

    def _extract_operation_from_key(self, key: str) -> str:
        """Extract operation name from cache key.

        Args:
            key: Cache key

        Returns:
            Operation name
        """
        # Simple extraction - assumes key format includes operation name
        parts = key.split(":")
        if len(parts) > 0:
            return parts[0]
        return "unknown"

    def _is_caching_enabled(self) -> bool:
        """Check if caching is enabled.

        Returns:
            True if caching is enabled
        """
        if self.config:
            return self.config.is_caching_enabled()
        return True  # Default to enabled

    def _get_default_ttl(self) -> int:
        """Get default TTL from configuration.

        Returns:
            Default TTL in seconds
        """
        if self.config:
            return self.config.get_cache_ttl()
        return 3600  # Default 1 hour

    def _get_max_cacheable_size(self) -> int:
        """Get maximum cacheable result size.

        Returns:
            Maximum size in bytes
        """
        # Default to 1MB max cacheable size
        return 1024 * 1024

    async def invalidate(self, key: str) -> bool:
        """Invalidate a specific cache entry.

        Args:
            key: Cache key to invalidate

        Returns:
            True if key was invalidated
        """
        try:
            result = await self.cache_repo.delete(key)
            if result:
                logger.debug(f"Invalidated cache key: {key}")
            return result
        except Exception as e:
            logger.error(f"Error invalidating cache key {key}: {str(e)}")
            return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching a pattern.

        Args:
            pattern: Pattern to match

        Returns:
            Number of entries invalidated
        """
        try:
            count = await self.cache_repo.invalidate_pattern(pattern)
            logger.info(f"Invalidated {count} cache entries matching pattern: {pattern}")
            return count
        except Exception as e:
            logger.error(f"Error invalidating cache pattern {pattern}: {str(e)}")
            return 0

    async def clear_cache(self) -> int:
        """Clear all cache entries.

        Returns:
            Number of entries cleared
        """
        try:
            count = await self.cache_repo.clear()
            logger.info(f"Cleared {count} cache entries")
            self.cache_stats["evictions"] += count
            return count
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return 0

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        try:
            repo_stats = await self.cache_repo.get_stats()

            # Combine service stats with repository stats
            combined_stats = {
                "service_stats": self.cache_stats.copy(),
                "repository_stats": repo_stats,
                "hit_rate": self._calculate_hit_rate(),
                "miss_rate": self._calculate_miss_rate(),
                "error_rate": self._calculate_error_rate(),
            }

            return combined_stats

        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {"error": str(e)}

    def _calculate_hit_rate(self) -> float:
        """Calculate cache hit rate.

        Returns:
            Hit rate as percentage
        """
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        if total_requests == 0:
            return 0.0
        return (self.cache_stats["hits"] / total_requests) * 100

    def _calculate_miss_rate(self) -> float:
        """Calculate cache miss rate.

        Returns:
            Miss rate as percentage
        """
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        if total_requests == 0:
            return 0.0
        return (self.cache_stats["misses"] / total_requests) * 100

    def _calculate_error_rate(self) -> float:
        """Calculate cache error rate.

        Returns:
            Error rate as percentage
        """
        total_operations = sum(self.cache_stats.values())
        if total_operations == 0:
            return 0.0
        return (self.cache_stats["errors"] / total_operations) * 100

    def generate_cache_key(
        self, operation: str, params: Dict[str, Any], include_config: bool = False
    ) -> str:
        """Generate a cache key for an operation and parameters.

        Args:
            operation: Operation name
            params: Operation parameters
            include_config: Whether to include configuration in key

        Returns:
            Generated cache key
        """
        # Create a deterministic string from parameters
        param_str = self._serialize_params(params)

        # Include configuration if requested
        config_str = ""
        if include_config and self.config:
            config_str = f"_cfg_{self.config.get_precision()}"

        # Create hash for consistent key length
        combined_str = f"{operation}:{param_str}{config_str}"
        key_hash = hashlib.md5(combined_str.encode(), usedforsecurity=False).hexdigest()[:16]

        return f"{operation}:{key_hash}"

    def _serialize_params(self, params: Dict[str, Any]) -> str:
        """Serialize parameters for cache key generation.

        Args:
            params: Parameters to serialize

        Returns:
            Serialized parameter string
        """
        try:
            import json

            # Sort keys for consistent ordering
            return json.dumps(params, sort_keys=True, default=str)
        except Exception:
            # Fallback to string representation
            return str(sorted(params.items()))

    async def warm_cache(self, operations: list) -> Dict[str, Any]:
        """Warm cache with common operations.

        Args:
            operations: List of operations to pre-compute

        Returns:
            Dictionary with warming results
        """
        results = {"warmed": 0, "failed": 0, "operations": []}

        for operation_config in operations:
            try:
                operation_name = operation_config["operation"]
                params = operation_config["params"]
                compute_func = operation_config["compute_func"]

                key = self.generate_cache_key(operation_name, params)

                # Check if already cached
                if await self.cache_repo.exists(key):
                    logger.debug(f"Cache already warm for operation: {operation_name}")
                    continue

                # Compute and cache
                await self.get_or_compute(key, compute_func)

                results["warmed"] += 1
                results["operations"].append(
                    {"operation": operation_name, "status": "warmed", "key": key}
                )

                logger.debug(f"Warmed cache for operation: {operation_name}")

            except Exception as e:
                results["failed"] += 1
                results["operations"].append(
                    {
                        "operation": operation_config.get("operation", "unknown"),
                        "status": "failed",
                        "error": str(e),
                    }
                )

                logger.error(f"Failed to warm cache for operation: {str(e)}")

        logger.info(
            f"Cache warming completed: {results['warmed']} warmed, {results['failed']} failed"
        )
        return results
