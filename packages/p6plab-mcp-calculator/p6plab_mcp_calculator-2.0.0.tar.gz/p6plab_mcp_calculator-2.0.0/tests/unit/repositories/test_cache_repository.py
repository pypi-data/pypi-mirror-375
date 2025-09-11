"""Unit tests for cache repository."""

import asyncio

import pytest

from calculator.repositories.cache import CacheRepository


class TestCacheRepository:
    """Test cases for CacheRepository."""

    @pytest.fixture
    def cache_repo(self):
        """Create cache repository for testing."""
        return CacheRepository(max_size=5, default_ttl=1)

    @pytest.mark.asyncio
    async def test_set_and_get(self, cache_repo):
        """Test basic set and get operations."""
        # Set a value
        result = await cache_repo.set("test_key", "test_value")
        assert result is True

        # Get the value
        value = await cache_repo.get("test_key")
        assert value == "test_value"

    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self, cache_repo):
        """Test getting a non-existent key."""
        value = await cache_repo.get("nonexistent")
        assert value is None

    @pytest.mark.asyncio
    async def test_ttl_expiration(self, cache_repo):
        """Test TTL expiration."""
        # Set with short TTL
        await cache_repo.set("expire_key", "expire_value", ttl=0.1)

        # Should exist immediately
        value = await cache_repo.get("expire_key")
        assert value == "expire_value"

        # Wait for expiration
        await asyncio.sleep(0.2)

        # Should be expired
        value = await cache_repo.get("expire_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_lru_eviction(self, cache_repo):
        """Test LRU eviction when cache is full."""
        # Fill cache to capacity
        for i in range(5):
            await cache_repo.set(f"key_{i}", f"value_{i}")

        # Add one more item (should evict oldest)
        await cache_repo.set("new_key", "new_value")

        # First key should be evicted
        value = await cache_repo.get("key_0")
        assert value is None

        # New key should exist
        value = await cache_repo.get("new_key")
        assert value == "new_value"

    @pytest.mark.asyncio
    async def test_exists(self, cache_repo):
        """Test exists method."""
        # Non-existent key
        exists = await cache_repo.exists("test_key")
        assert exists is False

        # Set a key
        await cache_repo.set("test_key", "test_value")
        exists = await cache_repo.exists("test_key")
        assert exists is True

    @pytest.mark.asyncio
    async def test_delete(self, cache_repo):
        """Test delete operation."""
        # Set a value
        await cache_repo.set("delete_key", "delete_value")

        # Verify it exists
        value = await cache_repo.get("delete_key")
        assert value == "delete_value"

        # Delete it
        result = await cache_repo.delete("delete_key")
        assert result is True

        # Verify it's gone
        value = await cache_repo.get("delete_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_clear(self, cache_repo):
        """Test clear operation."""
        # Add some items
        await cache_repo.set("key1", "value1")
        await cache_repo.set("key2", "value2")

        # Clear cache
        count = await cache_repo.clear()
        assert count == 2

        # Verify items are gone
        value1 = await cache_repo.get("key1")
        value2 = await cache_repo.get("key2")
        assert value1 is None
        assert value2 is None

    @pytest.mark.asyncio
    async def test_cleanup_expired(self, cache_repo):
        """Test cleanup of expired entries."""
        # Add items with different TTLs
        await cache_repo.set("short_ttl", "value1", ttl=0.1)
        await cache_repo.set("long_ttl", "value2", ttl=10)

        # Wait for short TTL to expire
        await asyncio.sleep(0.2)

        # Cleanup expired
        count = await cache_repo.cleanup_expired()
        assert count == 1

        # Verify only expired item is gone
        value1 = await cache_repo.get("short_ttl")
        value2 = await cache_repo.get("long_ttl")
        assert value1 is None
        assert value2 == "value2"

    @pytest.mark.asyncio
    async def test_get_stats(self, cache_repo):
        """Test cache statistics."""
        # Add some items
        await cache_repo.set("key1", "value1")
        await cache_repo.set("key2", "value2")

        # Access one item multiple times
        await cache_repo.get("key1")
        await cache_repo.get("key1")

        stats = await cache_repo.get_stats()
        assert stats["total_entries"] == 2
        assert stats["max_size"] == 5
        assert stats["total_access_count"] >= 2

    @pytest.mark.asyncio
    async def test_invalidate_pattern(self, cache_repo):
        """Test pattern-based invalidation."""
        # Add items with different patterns
        await cache_repo.set("user_123", "user_data")
        await cache_repo.set("user_456", "user_data")
        await cache_repo.set("product_789", "product_data")

        # Invalidate user pattern
        count = await cache_repo.invalidate_pattern("user_")
        assert count == 2

        # Verify user items are gone, product remains
        user1 = await cache_repo.get("user_123")
        user2 = await cache_repo.get("user_456")
        product = await cache_repo.get("product_789")

        assert user1 is None
        assert user2 is None
        assert product == "product_data"
