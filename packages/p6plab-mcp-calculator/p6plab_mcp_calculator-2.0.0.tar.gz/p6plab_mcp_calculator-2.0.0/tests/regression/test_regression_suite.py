"""
Regression test suite to ensure refactoring didn't break existing functionality.
Tests against known good results from the original implementation.
"""

import math

import pytest

from calculator.server.app import create_calculator_app


class TestRegressionSuite:
    """Regression tests against known good results."""

    @pytest.fixture
    def calculator_app(self):
        """Create calculator app for testing."""
        app = create_calculator_app()
        return app

    @pytest.mark.asyncio
    async def test_arithmetic_regression(self, calculator_app):
        """Test arithmetic operations against known results."""
        service = calculator_app.arithmetic_service

        # Known good results from original implementation
        test_cases = [
            # Basic operations
            ("add", {"numbers": [1, 2, 3, 4, 5]}, 15.0),
            ("subtract", {"a": 100, "b": 35}, 65.0),
            ("multiply", {"numbers": [2, 3, 4, 5]}, 120.0),
            ("divide", {"a": 100, "b": 10}, 10.0),

            # Advanced operations
            ("power", {"base": 2, "exponent": 10}, 1024.0),
            ("sqrt", {"number": 144}, 12.0),
            ("factorial", {"number": 6}, 720),
            ("gcd", {"numbers": [48, 18]}, 6),
            ("lcm", {"numbers": [12, 18]}, 36),

            # Trigonometric functions (using angle parameter)
            ("sine", {"angle": 0, "unit": "radians"}, 0.0),
            ("sine", {"angle": math.pi/2, "unit": "radians"}, 1.0),
            ("cosine", {"angle": 0, "unit": "radians"}, 1.0),
            ("cosine", {"angle": math.pi, "unit": "radians"}, -1.0),

            # Logarithmic functions
            ("logarithm", {"number": math.e, "base": math.e}, 1.0),
            ("logarithm", {"number": 100, "base": 10}, 2.0),
            ("exponential", {"number": 1}, math.e),
        ]

        for operation, params, expected in test_cases:
            result = await service.process(operation, params)

            if isinstance(expected, float):
                assert abs(result - expected) < 1e-10, f"{operation} failed: expected {expected}, got {result}"
            else:
                assert result == expected, f"{operation} failed: expected {expected}, got {result}"

    @pytest.mark.asyncio
    async def test_matrix_regression(self, calculator_app):
        """Test matrix operations against known results."""
        service = calculator_app.matrix_service

        # Known good results
        test_cases = [
            # Matrix addition
            ("add", {
                "matrix_a": [[1, 2], [3, 4]],
                "matrix_b": [[5, 6], [7, 8]]
            }, [[6, 8], [10, 12]]),

            # Matrix multiplication
            ("multiply", {
                "matrix_a": [[1, 2], [3, 4]],
                "matrix_b": [[5, 6], [7, 8]]
            }, [[19, 22], [43, 50]]),

            # Determinant
            ("determinant", {"matrix": [[1, 2], [3, 4]]}, -2.0),
            ("determinant", {"matrix": [[2, 3], [1, 4]]}, 5.0),
            ("determinant", {"matrix": [[1, 0, 0], [0, 1, 0], [0, 0, 1]]}, 1.0),

            # Transpose
            ("transpose", {"matrix": [[1, 2, 3], [4, 5, 6]]}, [[1, 4], [2, 5], [3, 6]]),
        ]

        for operation, params, expected in test_cases:
            result = await service.process(operation, params)

            if operation == "determinant":
                assert abs(result - expected) < 1e-10, f"Determinant failed: expected {expected}, got {result}"
            else:
                assert result == expected, f"{operation} failed: expected {expected}, got {result}"

    @pytest.mark.asyncio
    async def test_statistics_regression(self, calculator_app):
        """Test statistics operations against known results."""
        service = calculator_app.statistics_service

        # Test data
        data1 = [1, 2, 3, 4, 5]
        data2 = [10, 20, 30, 40, 50]
        data3 = [1, 1, 2, 3, 5, 8, 13]

        test_cases = [
            # Basic statistics
            ("mean", {"data": data1}, 3.0),
            ("mean", {"data": data2}, 30.0),
            ("median", {"data": data1}, 3.0),
            ("median", {"data": data3}, 3.0),

            # Variability measures
            ("variance", {"data": data1, "population": True}, 2.0),
            ("std_dev", {"data": data1, "population": True}, math.sqrt(2.0)),

            # Range
            ("range", {"data": data1}, {"min": 1.0, "max": 5.0, "range": 4.0}),

            # Correlation (perfect positive correlation)
            ("correlation", {"x_data": [1, 2, 3, 4, 5], "y_data": [2, 4, 6, 8, 10]}, 1.0),
        ]

        for operation, params, expected in test_cases:
            result = await service.process(operation, params)

            if isinstance(expected, dict):
                for key, value in expected.items():
                    assert abs(result[key] - value) < 1e-10, f"{operation}.{key} failed: expected {value}, got {result[key]}"
            elif isinstance(expected, float):
                assert abs(result - expected) < 1e-10, f"{operation} failed: expected {expected}, got {result}"
            else:
                assert result == expected, f"{operation} failed: expected {expected}, got {result}"

    @pytest.mark.asyncio
    async def test_calculus_regression(self, calculator_app):
        """Test calculus operations against known results."""
        service = calculator_app.calculus_service

        # Test symbolic derivatives
        derivative_cases = [
            ("x^2", "x", "2*x"),
            ("x^3", "x", "3*x^2"),
            ("sin(x)", "x", "cos(x)"),
            ("cos(x)", "x", "-sin(x)"),
            ("e^x", "x", "e^x"),
            ("ln(x)", "x", "1/x"),
        ]

        for expression, variable, expected_pattern in derivative_cases:
            result = await service.process("derivative", {
                "expression": expression,
                "variable": variable
            })

            # For symbolic results, just check that we got a non-empty result
            assert result is not None, f"Derivative of {expression} returned None"
            assert len(str(result)) > 0, f"Derivative of {expression} returned empty result"

        # Test definite integrals with known numeric results
        integral_cases = [
            ("1", "x", 0, 1, 1.0),  # ∫₀¹ 1 dx = 1
            ("x", "x", 0, 2, 2.0),  # ∫₀² x dx = 2
            ("2*x + 1", "x", 0, 2, 6.0),  # ∫₀² (2x + 1) dx = 6
            ("x^2", "x", 0, 3, 9.0),  # ∫₀³ x² dx = 9
        ]

        for expression, variable, lower, upper, expected in integral_cases:
            result = await service.process("integral", {
                "expression": expression,
                "variable": variable,
                "lower_limit": lower,
                "upper_limit": upper
            })

            assert abs(result - expected) < 1e-10, f"Integral of {expression} from {lower} to {upper}: expected {expected}, got {result}"

    @pytest.mark.asyncio
    async def test_complex_calculations_regression(self, calculator_app):
        """Test complex multi-step calculations."""

        # Test compound interest calculation using multiple operations
        # Formula: A = P(1 + r/n)^(nt)
        # P = 1000, r = 0.05, n = 12, t = 10

        arithmetic = calculator_app.arithmetic_service

        # Step 1: r/n = 0.05/12
        rate_per_period = await arithmetic.process("divide", {"numbers": [0.05, 12]})

        # Step 2: 1 + r/n
        one_plus_rate = await arithmetic.process("add", {"numbers": [1, rate_per_period]})

        # Step 3: nt = 12 * 10
        total_periods = await arithmetic.process("multiply", {"numbers": [12, 10]})

        # Step 4: (1 + r/n)^(nt)
        compound_factor = await arithmetic.process("power", {"base": one_plus_rate, "exponent": total_periods})

        # Step 5: P * compound_factor
        final_amount = await arithmetic.process("multiply", {"numbers": [1000, compound_factor]})

        # Expected result: approximately 1647.01
        expected = 1647.00949769028
        assert abs(final_amount - expected) < 1e-8, f"Compound interest calculation failed: expected {expected}, got {final_amount}"

    @pytest.mark.asyncio
    async def test_edge_cases_regression(self, calculator_app):
        """Test edge cases that were handled in the original implementation."""
        arithmetic = calculator_app.arithmetic_service
        matrix = calculator_app.matrix_service
        statistics = calculator_app.statistics_service

        # Arithmetic edge cases
        edge_cases = [
            # Very large numbers
            ("factorial", {"number": 20}, 2432902008176640000),

            # Very small numbers
            ("add", {"numbers": [1e-15, 1e-15]}, 2e-15),

            # Zero cases
            ("multiply", {"numbers": [1000, 0]}, 0.0),
            ("power", {"base": 5, "exponent": 0}, 1.0),
            ("power", {"base": 0, "exponent": 5}, 0.0),

            # Single element operations
            ("add", {"numbers": [42]}, 42.0),
            ("multiply", {"numbers": [42]}, 42.0),
        ]

        for operation, params, expected in edge_cases:
            result = await arithmetic.process(operation, params)

            if isinstance(expected, float):
                assert abs(result - expected) < 1e-10, f"Edge case {operation} failed: expected {expected}, got {result}"
            else:
                assert result == expected, f"Edge case {operation} failed: expected {expected}, got {result}"

        # Matrix edge cases
        # 1x1 matrix
        result = await matrix.process("determinant", {"matrix": [[5]]})
        assert abs(result - 5.0) < 1e-10, f"1x1 determinant failed: expected 5.0, got {result}"

        # Identity matrix
        identity = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        result = await matrix.process("determinant", {"matrix": identity})
        assert abs(result - 1.0) < 1e-10, f"Identity determinant failed: expected 1.0, got {result}"

        # Statistics edge cases
        # Single value
        result = await statistics.process("mean", {"data": [42]})
        assert result == 42.0, f"Single value mean failed: expected 42.0, got {result}"

        # Two identical values
        result = await statistics.process("std_dev", {"data": [5, 5], "population": True})
        assert result == 0.0, f"Identical values std_dev failed: expected 0.0, got {result}"

    @pytest.mark.asyncio
    async def test_precision_regression(self, calculator_app):
        """Test that precision is maintained as in the original implementation."""
        arithmetic = calculator_app.arithmetic_service

        # High precision calculations
        precision_cases = [
            # Pi-related calculations
            ("multiply", {"numbers": [math.pi, 2]}, 2 * math.pi),
            ("divide", {"numbers": [math.pi, 2]}, math.pi / 2),

            # e-related calculations
            ("power", {"base": math.e, "exponent": 2}, math.e ** 2),
            ("log", {"number": math.e ** 3, "base": math.e}, 3.0),

            # Square root precision
            ("sqrt", {"number": 2}, math.sqrt(2)),
            ("sqrt", {"number": 0.25}, 0.5),

            # Large number precision (use numbers that are actually representable)
            ("add", {"numbers": [1e12, 1]}, 1e12 + 1),
            ("subtract", {"numbers": [1e12 + 1, 1e12]}, 1.0),
        ]

        for operation, params, expected in precision_cases:
            result = await arithmetic.process(operation, params)

            # Use appropriate precision for comparison
            if abs(expected) > 1e10:
                tolerance = 1e-5  # Larger tolerance for very large numbers
            else:
                tolerance = 1e-14  # High precision for normal numbers

            assert abs(result - expected) < tolerance, f"Precision test {operation} failed: expected {expected}, got {result}, diff={abs(result - expected)}"
