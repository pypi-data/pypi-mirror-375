"""Unit tests for ArithmeticService."""

import math

import pytest

from calculator.core.errors.exceptions import ComputationError, ValidationError
from calculator.services.arithmetic import ArithmeticService


class TestArithmeticService:
    """Test cases for ArithmeticService."""

    @pytest.fixture
    def service(self):
        """Create arithmetic service for testing."""
        return ArithmeticService()

    @pytest.mark.asyncio
    async def test_add_basic(self, service):
        """Test basic addition."""
        result = await service.process("add", {"numbers": [2, 3, 4]})
        assert result == 9.0

    @pytest.mark.asyncio
    async def test_add_empty_list(self, service):
        """Test addition with empty list."""
        with pytest.raises(ValidationError):
            await service.process("add", {"numbers": []})

    @pytest.mark.asyncio
    async def test_subtract_basic(self, service):
        """Test basic subtraction."""
        result = await service.process("subtract", {"a": 10, "b": 3})
        assert result == 7.0

    @pytest.mark.asyncio
    async def test_subtract_missing_params(self, service):
        """Test subtraction with missing parameters."""
        with pytest.raises(ValidationError):
            await service.process("subtract", {"a": 10})

    @pytest.mark.asyncio
    async def test_multiply_basic(self, service):
        """Test basic multiplication."""
        result = await service.process("multiply", {"numbers": [2, 3, 4]})
        assert result == 24.0

    @pytest.mark.asyncio
    async def test_divide_basic(self, service):
        """Test basic division."""
        result = await service.process("divide", {"a": 10, "b": 2})
        assert result == 5.0

    @pytest.mark.asyncio
    async def test_divide_by_zero(self, service):
        """Test division by zero."""
        with pytest.raises(ComputationError):
            await service.process("divide", {"a": 10, "b": 0})

    @pytest.mark.asyncio
    async def test_power_basic(self, service):
        """Test power operation."""
        result = await service.process("power", {"base": 2, "exponent": 3})
        assert result == 8.0

    @pytest.mark.asyncio
    async def test_power_zero_negative(self, service):
        """Test power with zero base and negative exponent."""
        with pytest.raises(ComputationError):
            await service.process("power", {"base": 0, "exponent": -1})

    @pytest.mark.asyncio
    async def test_sqrt_basic(self, service):
        """Test square root."""
        result = await service.process("sqrt", {"number": 16})
        assert result == 4.0

    @pytest.mark.asyncio
    async def test_sqrt_negative(self, service):
        """Test square root of negative number."""
        with pytest.raises(ComputationError):
            await service.process("sqrt", {"number": -4})

    @pytest.mark.asyncio
    async def test_factorial_basic(self, service):
        """Test factorial."""
        result = await service.process("factorial", {"number": 5})
        assert result == 120

    @pytest.mark.asyncio
    async def test_factorial_zero(self, service):
        """Test factorial of zero."""
        result = await service.process("factorial", {"number": 0})
        assert result == 1

    @pytest.mark.asyncio
    async def test_factorial_negative(self, service):
        """Test factorial of negative number."""
        with pytest.raises(ValidationError):
            await service.process("factorial", {"number": -1})

    @pytest.mark.asyncio
    async def test_factorial_large(self, service):
        """Test factorial of large number."""
        with pytest.raises(ComputationError):
            await service.process("factorial", {"number": 200})

    @pytest.mark.asyncio
    async def test_gcd_basic(self, service):
        """Test GCD calculation."""
        result = await service.process("gcd", {"numbers": [12, 18]})
        assert result == 6

    @pytest.mark.asyncio
    async def test_gcd_multiple_numbers(self, service):
        """Test GCD with multiple numbers."""
        result = await service.process("gcd", {"numbers": [48, 18, 24]})
        assert result == 6

    @pytest.mark.asyncio
    async def test_gcd_insufficient_numbers(self, service):
        """Test GCD with insufficient numbers."""
        with pytest.raises(ValidationError):
            await service.process("gcd", {"numbers": [12]})

    @pytest.mark.asyncio
    async def test_lcm_basic(self, service):
        """Test LCM calculation."""
        result = await service.process("lcm", {"numbers": [4, 6]})
        assert result == 12

    @pytest.mark.asyncio
    async def test_modulo_basic(self, service):
        """Test modulo operation."""
        result = await service.process("modulo", {"a": 10, "b": 3})
        assert result == 1.0

    @pytest.mark.asyncio
    async def test_modulo_by_zero(self, service):
        """Test modulo by zero."""
        with pytest.raises(ComputationError):
            await service.process("modulo", {"a": 10, "b": 0})

    @pytest.mark.asyncio
    async def test_absolute_positive(self, service):
        """Test absolute value of positive number."""
        result = await service.process("absolute", {"number": 5})
        assert result == 5.0

    @pytest.mark.asyncio
    async def test_absolute_negative(self, service):
        """Test absolute value of negative number."""
        result = await service.process("absolute", {"number": -5})
        assert result == 5.0

    @pytest.mark.asyncio
    async def test_round_basic(self, service):
        """Test rounding."""
        result = await service.process("round_number", {"number": 3.14159, "decimals": 2})
        assert result == 3.14

    @pytest.mark.asyncio
    async def test_floor_basic(self, service):
        """Test floor operation."""
        result = await service.process("floor", {"number": 3.7})
        assert result == 3

    @pytest.mark.asyncio
    async def test_ceil_basic(self, service):
        """Test ceiling operation."""
        result = await service.process("ceil", {"number": 3.2})
        assert result == 4

    @pytest.mark.asyncio
    async def test_logarithm_basic(self, service):
        """Test logarithm."""
        result = await service.process("logarithm", {"number": 8, "base": 2})
        assert result == 3.0

    @pytest.mark.asyncio
    async def test_logarithm_negative(self, service):
        """Test logarithm of negative number."""
        with pytest.raises(ComputationError):
            await service.process("logarithm", {"number": -1})

    @pytest.mark.asyncio
    async def test_exponential_basic(self, service):
        """Test exponential function."""
        result = await service.process("exponential", {"number": 0})
        assert result == 1.0

    @pytest.mark.asyncio
    async def test_sine_radians(self, service):
        """Test sine in radians."""
        result = await service.process("sine", {"angle": math.pi / 2, "unit": "radians"})
        assert abs(result - 1.0) < 1e-10

    @pytest.mark.asyncio
    async def test_sine_degrees(self, service):
        """Test sine in degrees."""
        result = await service.process("sine", {"angle": 90, "unit": "degrees"})
        assert abs(result - 1.0) < 1e-10

    @pytest.mark.asyncio
    async def test_cosine_radians(self, service):
        """Test cosine in radians."""
        result = await service.process("cosine", {"angle": 0, "unit": "radians"})
        assert abs(result - 1.0) < 1e-10

    @pytest.mark.asyncio
    async def test_tangent_radians(self, service):
        """Test tangent in radians."""
        result = await service.process("tangent", {"angle": math.pi / 4, "unit": "radians"})
        assert abs(result - 1.0) < 1e-10

    @pytest.mark.asyncio
    async def test_arcsine_basic(self, service):
        """Test arcsine."""
        result = await service.process("asin", {"value": 1})
        assert abs(result - math.pi / 2) < 1e-10

    @pytest.mark.asyncio
    async def test_arcsine_out_of_range(self, service):
        """Test arcsine with out of range value."""
        with pytest.raises(ComputationError):
            await service.process("asin", {"value": 2})

    @pytest.mark.asyncio
    async def test_hyperbolic_sine(self, service):
        """Test hyperbolic sine."""
        result = await service.process("sinh", {"value": 0})
        assert result == 0.0

    @pytest.mark.asyncio
    async def test_hyperbolic_cosine(self, service):
        """Test hyperbolic cosine."""
        result = await service.process("cosh", {"value": 0})
        assert result == 1.0

    @pytest.mark.asyncio
    async def test_hyperbolic_tangent(self, service):
        """Test hyperbolic tangent."""
        result = await service.process("tanh", {"value": 0})
        assert result == 0.0

    @pytest.mark.asyncio
    async def test_unknown_operation(self, service):
        """Test unknown operation."""
        with pytest.raises(ValidationError):
            await service.process("unknown_operation", {"number": 5})
