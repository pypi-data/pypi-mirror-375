"""Unit tests for ConstantsRepository."""

import math

import pytest

from calculator.repositories.constants import ConstantsRepository


class TestConstantsRepository:
    """Test cases for ConstantsRepository."""

    @pytest.fixture
    def constants_repo(self):
        """Create ConstantsRepository instance for testing."""
        return ConstantsRepository()

    @pytest.mark.asyncio
    async def test_get_mathematical_constants(self, constants_repo):
        """Test retrieval of mathematical constants."""
        # Test pi
        pi_value = await constants_repo.get("pi")
        assert abs(pi_value - math.pi) < 1e-15

        # Test e
        e_value = await constants_repo.get("e")
        assert abs(e_value - math.e) < 1e-15

        # Test tau
        tau_value = await constants_repo.get("tau")
        assert abs(tau_value - (2 * math.pi)) < 1e-15

    @pytest.mark.asyncio
    async def test_get_physical_constants(self, constants_repo):
        """Test retrieval of physical constants."""
        # Test speed of light
        c_value = await constants_repo.get("c")
        assert c_value == 299792458

        # Test Planck constant
        h_value = await constants_repo.get("h")
        assert h_value == 6.62607015e-34

        # Test Boltzmann constant
        k_value = await constants_repo.get("k")
        assert k_value == 1.380649e-23

    @pytest.mark.asyncio
    async def test_get_conversion_factors(self, constants_repo):
        """Test retrieval of conversion factors."""
        # Test degree to radian conversion
        deg_to_rad = await constants_repo.get("deg_to_rad")
        assert abs(deg_to_rad - (math.pi / 180)) < 1e-15

        # Test inch to cm conversion
        inch_to_cm = await constants_repo.get("inch_to_cm")
        assert inch_to_cm == 2.54

    @pytest.mark.asyncio
    async def test_case_insensitive_access(self, constants_repo):
        """Test case-insensitive constant access."""
        pi_lower = await constants_repo.get("pi")
        pi_upper = await constants_repo.get("PI")
        pi_mixed = await constants_repo.get("Pi")

        assert pi_lower == pi_upper == pi_mixed

    @pytest.mark.asyncio
    async def test_aliases(self, constants_repo):
        """Test constant aliases."""
        # Test π alias for pi
        pi_symbol = await constants_repo.get("π")
        pi_name = await constants_repo.get("pi")
        assert pi_symbol == pi_name

        # Test euler alias for e
        euler = await constants_repo.get("euler")
        e_value = await constants_repo.get("e")
        assert euler == e_value

    @pytest.mark.asyncio
    async def test_nonexistent_constant(self, constants_repo):
        """Test retrieval of non-existent constants."""
        result = await constants_repo.get("nonexistent_constant")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_custom_constant(self, constants_repo):
        """Test setting custom constants."""
        success = await constants_repo.set("my_constant", 42.0)
        assert success is True

        # Retrieve custom constant
        value = await constants_repo.get("custom_my_constant")
        assert value == 42.0

    @pytest.mark.asyncio
    async def test_cannot_override_builtin(self, constants_repo):
        """Test that built-in constants cannot be overridden."""
        success = await constants_repo.set("pi", 3.0)
        assert success is False

        # Pi should still be the correct value
        pi_value = await constants_repo.get("pi")
        assert abs(pi_value - math.pi) < 1e-15

    @pytest.mark.asyncio
    async def test_delete_custom_constant(self, constants_repo):
        """Test deletion of custom constants."""
        # Set a custom constant
        await constants_repo.set("temp_constant", 123.0)

        # Delete it
        success = await constants_repo.delete("temp_constant")
        assert success is True

        # Should no longer exist
        value = await constants_repo.get("custom_temp_constant")
        assert value is None

    @pytest.mark.asyncio
    async def test_exists_check(self, constants_repo):
        """Test constant existence checking."""
        # Built-in constant should exist
        assert await constants_repo.exists("pi") is True

        # Non-existent constant should not exist
        assert await constants_repo.exists("nonexistent") is False

        # Custom constant
        await constants_repo.set("test_exists", 1.0)
        assert await constants_repo.exists("test_exists") is True

    @pytest.mark.asyncio
    async def test_get_all_constants(self, constants_repo):
        """Test retrieval of all constants."""
        all_constants = await constants_repo.get_all_constants()

        assert isinstance(all_constants, dict)
        assert "pi" in all_constants
        assert "e" in all_constants
        assert "c" in all_constants
        assert len(all_constants) > 20  # Should have many constants

    @pytest.mark.asyncio
    async def test_get_mathematical_constants_only(self, constants_repo):
        """Test retrieval of mathematical constants only."""
        math_constants = await constants_repo.get_mathematical_constants()

        assert isinstance(math_constants, dict)
        assert "pi" in math_constants
        assert "e" in math_constants
        assert "c" not in math_constants  # Physical constant, not mathematical

    @pytest.mark.asyncio
    async def test_search_constants(self, constants_repo):
        """Test constant search functionality."""
        # Search for constants containing "pi"
        pi_constants = await constants_repo.search_constants("pi")

        assert isinstance(pi_constants, dict)
        assert "pi" in pi_constants
        # Should not contain unrelated constants
        assert "planck" not in [k.lower() for k in pi_constants.keys()]

    @pytest.mark.asyncio
    async def test_get_constant_info(self, constants_repo):
        """Test detailed constant information retrieval."""
        pi_info = await constants_repo.get_constant_info("pi")

        assert isinstance(pi_info, dict)
        assert "name" in pi_info
        assert "value" in pi_info
        assert "type" in pi_info
        assert pi_info["value"] == math.pi

    @pytest.mark.asyncio
    async def test_get_constant_method_alias(self, constants_repo):
        """Test the get_constant method alias."""
        pi_value = await constants_repo.get_constant("pi")
        assert abs(pi_value - math.pi) < 1e-15
