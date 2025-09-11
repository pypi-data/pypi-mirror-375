"""Constants repository for mathematical constants."""

import math
from typing import Any, Dict, Optional

from .base import BaseRepository


class ConstantsRepository(BaseRepository):
    """Repository for mathematical constants and predefined values.

    This repository provides access to mathematical constants, conversion factors,
    and other predefined values used throughout the calculator.
    """

    def __init__(self):
        """Initialize constants repository with predefined values."""
        self._constants = {
            # Mathematical constants
            "pi": math.pi,
            "e": math.e,
            "tau": 2 * math.pi,
            "phi": (1 + math.sqrt(5)) / 2,  # Golden ratio
            "euler_gamma": 0.5772156649015329,  # Euler-Mascheroni constant
            "sqrt2": math.sqrt(2),
            "sqrt3": math.sqrt(3),
            "ln2": math.log(2),
            "ln10": math.log(10),
            # Physical constants
            "c": 299792458,  # Speed of light in m/s
            "h": 6.62607015e-34,  # Planck constant in J⋅s
            "k": 1.380649e-23,  # Boltzmann constant in J/K
            "na": 6.02214076e23,  # Avogadro constant in mol⁻¹
            "g": 9.80665,  # Standard gravity in m/s²
            "r": 8.314462618,  # Gas constant in J/(mol⋅K)
            # Conversion factors
            "deg_to_rad": math.pi / 180,
            "rad_to_deg": 180 / math.pi,
            "inch_to_cm": 2.54,
            "foot_to_meter": 0.3048,
            "mile_to_km": 1.609344,
            "pound_to_kg": 0.45359237,
            "fahrenheit_offset": 32,
            "fahrenheit_scale": 5 / 9,
            # Financial constants
            "days_per_year": 365.25,
            "months_per_year": 12,
            "weeks_per_year": 52.1775,
            # Precision constants
            "default_precision": 15,
            "max_precision": 50,
            "min_precision": 1,
            # Computational limits
            "max_iterations": 10000,
            "convergence_tolerance": 1e-10,
            "overflow_threshold": 1e100,
            "underflow_threshold": 1e-100,
        }

        # Add aliases for common constants
        self._aliases = {
            "π": "pi",
            "euler": "e",
            "golden_ratio": "phi",
            "speed_of_light": "c",
            "planck": "h",
            "boltzmann": "k",
            "avogadro": "na",
            "gravity": "g",
            "gas_constant": "r",
        }

    async def get(self, key: str) -> Optional[Any]:
        """Get constant value by key.

        Args:
            key: Constant name (case-insensitive)

        Returns:
            Constant value or None if not found
        """
        key_lower = key.lower()

        # Check direct key
        if key_lower in self._constants:
            return self._constants[key_lower]

        # Check aliases
        if key_lower in self._aliases:
            return self._constants[self._aliases[key_lower]]

        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a custom constant value.

        Args:
            key: Constant name
            value: Constant value
            ttl: Ignored for constants (constants don't expire)

        Returns:
            True if constant was set
        """
        key_lower = key.lower()

        # Don't allow overriding built-in constants
        if key_lower in self._constants:
            return False

        # Add as custom constant with 'custom_' prefix
        custom_key = f"custom_{key_lower}"
        self._constants[custom_key] = value
        return True

    async def delete(self, key: str) -> bool:
        """Delete a custom constant.

        Args:
            key: Constant name

        Returns:
            True if constant was deleted
        """
        key_lower = key.lower()
        custom_key = f"custom_{key_lower}"

        if custom_key in self._constants:
            del self._constants[custom_key]
            return True

        return False

    async def exists(self, key: str) -> bool:
        """Check if constant exists.

        Args:
            key: Constant name

        Returns:
            True if constant exists
        """
        key_lower = key.lower()
        return (
            key_lower in self._constants
            or key_lower in self._aliases
            or f"custom_{key_lower}" in self._constants
        )

    async def get_all_constants(self) -> Dict[str, Any]:
        """Get all available constants.

        Returns:
            Dictionary of all constants
        """
        return self._constants.copy()

    async def get_mathematical_constants(self) -> Dict[str, Any]:
        """Get mathematical constants only.

        Returns:
            Dictionary of mathematical constants
        """
        math_constants = {}
        math_keys = ["pi", "e", "tau", "phi", "euler_gamma", "sqrt2", "sqrt3", "ln2", "ln10"]

        for key in math_keys:
            if key in self._constants:
                math_constants[key] = self._constants[key]

        return math_constants

    async def get_physical_constants(self) -> Dict[str, Any]:
        """Get physical constants only.

        Returns:
            Dictionary of physical constants
        """
        physical_constants = {}
        physical_keys = ["c", "h", "k", "na", "g", "r"]

        for key in physical_keys:
            if key in self._constants:
                physical_constants[key] = self._constants[key]

        return physical_constants

    async def get_conversion_factors(self) -> Dict[str, Any]:
        """Get conversion factors only.

        Returns:
            Dictionary of conversion factors
        """
        conversion_factors = {}
        conversion_keys = [
            "deg_to_rad",
            "rad_to_deg",
            "inch_to_cm",
            "foot_to_meter",
            "mile_to_km",
            "pound_to_kg",
            "fahrenheit_offset",
            "fahrenheit_scale",
        ]

        for key in conversion_keys:
            if key in self._constants:
                conversion_factors[key] = self._constants[key]

        return conversion_factors

    async def search_constants(self, pattern: str) -> Dict[str, Any]:
        """Search for constants matching a pattern.

        Args:
            pattern: Search pattern (case-insensitive substring match)

        Returns:
            Dictionary of matching constants
        """
        pattern_lower = pattern.lower()
        matching_constants = {}

        for key, value in self._constants.items():
            if pattern_lower in key.lower():
                matching_constants[key] = value

        # Also search aliases
        for alias, actual_key in self._aliases.items():
            if pattern_lower in alias.lower():
                matching_constants[alias] = self._constants[actual_key]

        return matching_constants

    async def get_constant_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a constant.

        Args:
            key: Constant name

        Returns:
            Dictionary with constant information or None if not found
        """
        value = await self.get(key)
        if value is None:
            return None

        key_lower = key.lower()

        # Determine constant type and description
        constant_info = {"name": key, "value": value, "type": type(value).__name__}

        # Add descriptions for known constants
        descriptions = {
            "pi": "The ratio of a circle's circumference to its diameter",
            "e": "Euler's number, the base of natural logarithms",
            "tau": "The ratio of a circle's circumference to its radius (2π)",
            "phi": "The golden ratio",
            "c": "Speed of light in vacuum (m/s)",
            "h": "Planck constant (J⋅s)",
            "k": "Boltzmann constant (J/K)",
            "na": "Avogadro constant (mol⁻¹)",
            "g": "Standard acceleration due to gravity (m/s²)",
            "r": "Universal gas constant (J/(mol⋅K))",
        }

        if key_lower in descriptions:
            constant_info["description"] = descriptions[key_lower]
        elif key_lower in self._aliases and self._aliases[key_lower] in descriptions:
            constant_info["description"] = descriptions[self._aliases[key_lower]]

        return constant_info

    async def get_constant(self, key: str) -> Optional[Any]:
        """Get constant value by key (alias for get method).

        Args:
            key: Constant name

        Returns:
            Constant value or None if not found
        """
        return await self.get(key)
