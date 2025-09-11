"""Currency repository with fallback mechanisms."""

import asyncio
import time
from typing import Any, Dict, Optional

from .base import BaseRepository


class CurrencyRepository(BaseRepository):
    """Repository for currency exchange rates with fallback mechanisms.

    This repository manages currency exchange rates with multiple fallback
    strategies when external APIs are unavailable.
    """

    def __init__(self, cache_ttl: int = 3600):
        """Initialize currency repository.

        Args:
            cache_ttl: Cache time-to-live in seconds
        """
        self.cache_ttl = cache_ttl
        self._rates_cache: Dict[str, Any] = {}
        self._cache_metadata: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

        # Fallback exchange rates (approximate values for common currencies)
        self._fallback_rates = {
            "USD": 1.0,  # Base currency
            "EUR": 0.85,
            "GBP": 0.73,
            "JPY": 110.0,
            "CAD": 1.25,
            "AUD": 1.35,
            "CHF": 0.92,
            "CNY": 6.45,
            "INR": 74.5,
            "BRL": 5.2,
            "RUB": 73.0,
            "KRW": 1180.0,
            "MXN": 20.1,
            "SGD": 1.35,
            "HKD": 7.8,
            "NOK": 8.6,
            "SEK": 8.9,
            "DKK": 6.3,
            "PLN": 3.9,
            "CZK": 21.5,
            "HUF": 295.0,
            "TRY": 8.5,
            "ZAR": 14.8,
            "NZD": 1.42,
            "THB": 31.5,
            "MYR": 4.15,
            "PHP": 50.2,
            "IDR": 14250.0,
            "VND": 23100.0,
        }

        # Last updated timestamp for fallback rates
        self._fallback_updated = time.time()

    async def get(self, key: str) -> Optional[Any]:
        """Get exchange rate by currency pair.

        Args:
            key: Currency pair in format "FROM_TO" (e.g., "USD_EUR")

        Returns:
            Exchange rate or None if not found
        """
        async with self._lock:
            # Check cache first
            if key in self._rates_cache:
                metadata = self._cache_metadata[key]
                if time.time() < metadata["expires_at"]:
                    metadata["last_accessed"] = time.time()
                    metadata["access_count"] += 1
                    return self._rates_cache[key]
                else:
                    # Expired, remove from cache
                    del self._rates_cache[key]
                    del self._cache_metadata[key]

            # Try to get fresh rate (would normally call external API here)
            rate = await self._get_fresh_rate(key)
            if rate is not None:
                await self._cache_rate(key, rate)
                return rate

            # Fall back to cached rate even if expired
            return await self._get_fallback_rate(key)

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set exchange rate manually.

        Args:
            key: Currency pair
            value: Exchange rate
            ttl: Time to live (uses default if None)

        Returns:
            True if rate was set
        """
        try:
            async with self._lock:
                await self._cache_rate(key, value, ttl)
                return True
        except Exception:
            return False

    async def delete(self, key: str) -> bool:
        """Delete cached exchange rate.

        Args:
            key: Currency pair to delete

        Returns:
            True if rate was deleted
        """
        async with self._lock:
            if key in self._rates_cache:
                del self._rates_cache[key]
                del self._cache_metadata[key]
                return True
            return False

    async def exists(self, key: str) -> bool:
        """Check if exchange rate exists (in cache or fallback).

        Args:
            key: Currency pair to check

        Returns:
            True if rate exists
        """
        # Check cache
        if key in self._rates_cache:
            return True

        # Check if we can provide fallback rate
        return await self._can_provide_fallback_rate(key)

    async def _get_fresh_rate(self, currency_pair: str) -> Optional[float]:
        """Get fresh exchange rate from external API.

        Args:
            currency_pair: Currency pair in format "FROM_TO"

        Returns:
            Exchange rate or None if unavailable
        """
        # In a real implementation, this would call an external API
        # For now, we'll simulate API unavailability and rely on fallbacks
        return None

    async def _get_fallback_rate(self, currency_pair: str) -> Optional[float]:
        """Get fallback exchange rate.

        Args:
            currency_pair: Currency pair in format "FROM_TO"

        Returns:
            Fallback exchange rate or None
        """
        try:
            from_currency, to_currency = currency_pair.split("_")

            if from_currency == to_currency:
                return 1.0

            # Get rates relative to USD
            from_rate = self._fallback_rates.get(from_currency)
            to_rate = self._fallback_rates.get(to_currency)

            if from_rate is None or to_rate is None:
                return None

            # Calculate cross rate
            if from_currency == "USD":
                rate = to_rate
            elif to_currency == "USD":
                rate = 1.0 / from_rate
            else:
                rate = to_rate / from_rate

            return rate

        except (ValueError, KeyError):
            return None

    async def _can_provide_fallback_rate(self, currency_pair: str) -> bool:
        """Check if we can provide a fallback rate for the currency pair.

        Args:
            currency_pair: Currency pair to check

        Returns:
            True if fallback rate is available
        """
        try:
            from_currency, to_currency = currency_pair.split("_")
            return from_currency in self._fallback_rates and to_currency in self._fallback_rates
        except ValueError:
            return False

    async def _cache_rate(self, key: str, rate: float, ttl: Optional[int] = None) -> None:
        """Cache an exchange rate.

        Args:
            key: Currency pair
            rate: Exchange rate
            ttl: Time to live (uses default if None)
        """
        ttl = ttl or self.cache_ttl
        current_time = time.time()

        self._rates_cache[key] = rate
        self._cache_metadata[key] = {
            "created_at": current_time,
            "expires_at": current_time + ttl,
            "last_accessed": current_time,
            "access_count": 1,
            "source": "api",  # or 'fallback' or 'manual'
        }

    async def get_supported_currencies(self) -> list:
        """Get list of supported currencies.

        Returns:
            List of supported currency codes
        """
        return list(self._fallback_rates.keys())

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary containing cache statistics
        """
        async with self._lock:
            current_time = time.time()
            expired_count = 0
            total_access_count = 0

            for metadata in self._cache_metadata.values():
                if current_time > metadata["expires_at"]:
                    expired_count += 1
                total_access_count += metadata["access_count"]

            return {
                "total_cached_rates": len(self._rates_cache),
                "expired_rates": expired_count,
                "total_access_count": total_access_count,
                "fallback_rates_count": len(self._fallback_rates),
                "fallback_last_updated": self._fallback_updated,
            }

    async def clear_cache(self) -> int:
        """Clear all cached rates.

        Returns:
            Number of rates cleared
        """
        async with self._lock:
            count = len(self._rates_cache)
            self._rates_cache.clear()
            self._cache_metadata.clear()
            return count

    async def update_fallback_rates(self, rates: Dict[str, float]) -> bool:
        """Update fallback exchange rates.

        Args:
            rates: Dictionary of currency codes to exchange rates (relative to USD)

        Returns:
            True if rates were updated
        """
        try:
            async with self._lock:
                self._fallback_rates.update(rates)
                self._fallback_updated = time.time()
                return True
        except Exception:
            return False

    async def get_rate_with_metadata(self, currency_pair: str) -> Optional[Dict[str, Any]]:
        """Get exchange rate with metadata.

        Args:
            currency_pair: Currency pair in format "FROM_TO"

        Returns:
            Dictionary with rate and metadata or None
        """
        rate = await self.get(currency_pair)
        if rate is None:
            return None

        metadata = self._cache_metadata.get(currency_pair, {})

        return {
            "rate": rate,
            "currency_pair": currency_pair,
            "cached": currency_pair in self._rates_cache,
            "source": metadata.get("source", "fallback"),
            "created_at": metadata.get("created_at"),
            "expires_at": metadata.get("expires_at"),
            "access_count": metadata.get("access_count", 0),
        }


class MockCurrencyRepository(BaseRepository):
    """Mock currency repository for when currency conversion is disabled."""

    async def get(self, key: str) -> Optional[Any]:
        """Mock get method that returns None."""
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Mock set method that returns False."""
        return False

    async def delete(self, key: str) -> bool:
        """Mock delete method that returns False."""
        return False

    async def exists(self, key: str) -> bool:
        """Mock exists method that returns False."""
        return False

    async def get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """Mock get_exchange_rate method that returns None."""
        return None
