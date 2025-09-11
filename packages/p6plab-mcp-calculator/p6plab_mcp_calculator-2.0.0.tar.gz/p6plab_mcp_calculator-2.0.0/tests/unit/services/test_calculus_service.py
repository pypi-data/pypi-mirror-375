"""Unit tests for CalculusService."""

import pytest

from calculator.services.calculus import CalculusService


class TestCalculusService:
    """Test cases for CalculusService."""

    @pytest.fixture
    def calculus_service(self):
        """Create CalculusService instance for testing."""
        return CalculusService()

    @pytest.mark.asyncio
    async def test_symbolic_derivative(self, calculus_service):
        """Test symbolic derivative calculation."""
        result = await calculus_service.process("derivative", {
            "expression": "x^2",
            "variable": "x"
        })

        assert isinstance(result, dict)
        assert "derivative" in result
        # Should contain "2*x" in some form

    @pytest.mark.asyncio
    async def test_partial_derivative(self, calculus_service):
        """Test partial derivative calculation."""
        result = await calculus_service.process("derivatives.partial", {
            "expression": "x^2 + y^2",
            "variable": "x"
        })

        assert isinstance(result, dict)
        assert "partial_derivative" in result

    @pytest.mark.asyncio
    async def test_definite_integral(self, calculus_service):
        """Test definite integral calculation."""
        result = await calculus_service.process("integral", {
            "expression": "2*x + 1",
            "variable": "x",
            "lower_limit": 0,
            "upper_limit": 2
        })

        # Should return 6.0 for definite integral
        assert result == 6.0

    @pytest.mark.asyncio
    async def test_indefinite_integral(self, calculus_service):
        """Test indefinite integral calculation."""
        result = await calculus_service.process("integrals.symbolic", {
            "expression": "2*x + 1",
            "variable": "x"
        })

        assert isinstance(result, dict)
        assert "integral" in result

    @pytest.mark.asyncio
    async def test_limit_calculation(self, calculus_service):
        """Test limit calculation."""
        result = await calculus_service.process("limit", {
            "expression": "sin(x)/x",
            "variable": "x",
            "approach_value": "0"
        })

        assert isinstance(result, dict)
        assert "limit" in result

    @pytest.mark.asyncio
    async def test_taylor_series(self, calculus_service):
        """Test Taylor series expansion."""
        result = await calculus_service.process("taylor_series", {
            "expression": "sin(x)",
            "variable": "x",
            "center": 0,
            "order": 5
        })

        assert isinstance(result, dict)
        assert "taylor_series" in result

    @pytest.mark.asyncio
    async def test_numerical_derivative(self, calculus_service):
        """Test numerical derivative calculation."""
        result = await calculus_service.process("derivatives.numerical", {
            "expression": "x^2",
            "variable": "x",
            "point": 2.0
        })

        assert isinstance(result, dict)
        assert "numerical_derivative" in result
        # At x=2, derivative of x^2 should be 4
        assert abs(result["numerical_derivative"] - 4.0) < 0.1

    @pytest.mark.asyncio
    async def test_numerical_integral(self, calculus_service):
        """Test numerical integration."""
        result = await calculus_service.process("integrals.numerical", {
            "expression": "x^2",
            "variable": "x",
            "lower_bound": 0,
            "upper_bound": 1
        })

        assert isinstance(result, dict)
        assert "numerical_integral" in result
        # Integral of x^2 from 0 to 1 should be 1/3
        assert abs(result["numerical_integral"] - 1/3) < 0.01

    @pytest.mark.asyncio
    async def test_invalid_expression(self, calculus_service):
        """Test error handling for invalid expressions."""
        with pytest.raises(Exception):
            await calculus_service.process("derivative", {
                "expression": "invalid_expression_+++",
                "variable": "x"
            })

    @pytest.mark.asyncio
    async def test_missing_variable(self, calculus_service):
        """Test error handling for missing variable."""
        with pytest.raises(Exception):
            await calculus_service.process("derivative", {
                "expression": "x^2"
                # Missing variable parameter
            })

    @pytest.mark.asyncio
    async def test_invalid_operation(self, calculus_service):
        """Test error handling for invalid operations."""
        with pytest.raises(Exception):
            await calculus_service.process("invalid_operation", {
                "expression": "x^2",
                "variable": "x"
            })

    @pytest.mark.asyncio
    async def test_complex_expression(self, calculus_service):
        """Test handling of complex mathematical expressions."""
        result = await calculus_service.process("derivative", {
            "expression": "sin(x) * cos(x) + exp(x)",
            "variable": "x"
        })

        assert isinstance(result, dict)
        assert "derivative" in result

    @pytest.mark.asyncio
    async def test_multivariate_function(self, calculus_service):
        """Test handling of multivariate functions."""
        result = await calculus_service.process("derivatives.partial", {
            "expression": "x^2 * y + sin(x*y)",
            "variable": "x"
        })

        assert isinstance(result, dict)
        assert "partial_derivative" in result
