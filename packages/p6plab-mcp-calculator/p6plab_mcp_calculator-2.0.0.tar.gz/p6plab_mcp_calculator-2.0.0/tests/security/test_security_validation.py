"""Tests for security validation functionality."""

import pytest

from calculator.core.errors.exceptions import SecurityError, ValidationError
from calculator.core.security.validation import (
    InputValidator,
    SecurityConfig,
    SecurityValidator,
    validate_operation_input,
)


class TestInputValidator:
    """Test input validation functionality."""

    def test_validate_input_size_normal(self):
        """Test input size validation with normal data."""
        validator = InputValidator()

        # Normal string
        validator.validate_input_size("hello world")

        # Normal list
        validator.validate_input_size([1, 2, 3, 4, 5])

        # Normal dict
        validator.validate_input_size({"a": 1, "b": 2})

    def test_validate_input_size_exceeds_limit(self):
        """Test input size validation with oversized data."""
        validator = InputValidator()

        # Create oversized string
        large_string = "x" * (SecurityConfig.MAX_INPUT_SIZE + 1)

        with pytest.raises(SecurityError) as exc_info:
            validator.validate_input_size(large_string)

        assert "exceeds maximum allowed size" in str(exc_info.value)

    def test_validate_array_length_normal(self):
        """Test array length validation with normal data."""
        validator = InputValidator()

        # Normal array
        validator.validate_array_length([1, 2, 3, 4, 5])

        # Empty array (should be allowed for length validation)
        validator.validate_array_length([])

    def test_validate_array_length_exceeds_limit(self):
        """Test array length validation with oversized array."""
        validator = InputValidator()

        # Create oversized array
        large_array = list(range(SecurityConfig.MAX_ARRAY_LENGTH + 1))

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_array_length(large_array)

        assert "exceeds maximum allowed length" in str(exc_info.value)

    def test_validate_matrix_dimensions_normal(self):
        """Test matrix dimension validation with normal matrix."""
        validator = InputValidator()

        # Normal 2x2 matrix
        matrix = [[1, 2], [3, 4]]
        validator.validate_matrix_dimensions(matrix)

        # Normal 3x3 matrix
        matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        validator.validate_matrix_dimensions(matrix)

    def test_validate_matrix_dimensions_empty(self):
        """Test matrix dimension validation with empty matrix."""
        validator = InputValidator()

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_matrix_dimensions([])

        assert "cannot be empty" in str(exc_info.value)

    def test_validate_matrix_dimensions_irregular(self):
        """Test matrix dimension validation with irregular matrix."""
        validator = InputValidator()

        # Irregular matrix (different row lengths)
        irregular_matrix = [[1, 2, 3], [4, 5]]

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_matrix_dimensions(irregular_matrix)

        assert "expected" in str(exc_info.value)

    def test_validate_matrix_dimensions_oversized(self):
        """Test matrix dimension validation with oversized matrix."""
        validator = InputValidator()

        # Create oversized matrix
        size = SecurityConfig.MAX_MATRIX_SIZE + 1
        large_matrix = [[1] * size for _ in range(size)]

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_matrix_dimensions(large_matrix)

        assert "exceed maximum allowed size" in str(exc_info.value)

    def test_validate_expression_safety_safe(self):
        """Test expression safety validation with safe expressions."""
        validator = InputValidator()

        # Safe mathematical expressions
        safe_expressions = ["x + y", "2 * x^2 + 3 * x + 1", "sin(x) + cos(y)", "log(x) + exp(y)"]

        for expr in safe_expressions:
            validator.validate_expression_safety(expr)

    def test_validate_expression_safety_unsafe(self):
        """Test expression safety validation with unsafe expressions."""
        validator = InputValidator()

        # Unsafe expressions
        unsafe_expressions = [
            "eval('malicious code')",
            "import os",
            "__import__('os')",
            "exec('bad code')",
            "open('/etc/passwd')",
        ]

        for expr in unsafe_expressions:
            with pytest.raises(SecurityError):
                validator.validate_expression_safety(expr)

    def test_validate_numerical_limits_factorial(self):
        """Test numerical limits validation for factorial."""
        validator = InputValidator()

        # Valid factorial inputs
        validator.validate_numerical_limits(5, "factorial")
        validator.validate_numerical_limits(100, "factorial")

        # Invalid factorial inputs
        with pytest.raises(ValidationError):
            validator.validate_numerical_limits(-1, "factorial")

        with pytest.raises(ValidationError):
            validator.validate_numerical_limits(
                SecurityConfig.MAX_FACTORIAL_INPUT + 1, "factorial"
            )

    def test_validate_numerical_limits_power(self):
        """Test numerical limits validation for power operations."""
        validator = InputValidator()

        # Valid power inputs
        validator.validate_numerical_limits(10, "power")
        validator.validate_numerical_limits(-10, "power")

        # Invalid power inputs
        with pytest.raises(ValidationError):
            validator.validate_numerical_limits(SecurityConfig.MAX_POWER_EXPONENT + 1, "power")

    def test_sanitize_numerical_input_valid(self):
        """Test numerical input sanitization with valid inputs."""
        validator = InputValidator()

        # Integer strings
        assert validator.sanitize_numerical_input("123") == 123
        assert validator.sanitize_numerical_input("-456") == -456

        # Float strings
        assert validator.sanitize_numerical_input("123.45") == 123.45
        assert validator.sanitize_numerical_input("-67.89") == -67.89

        # Scientific notation
        assert validator.sanitize_numerical_input("1.23e4") == 12300.0

        # Existing numbers
        assert validator.sanitize_numerical_input(42) == 42
        assert validator.sanitize_numerical_input(3.14) == 3.14

    def test_sanitize_numerical_input_invalid(self):
        """Test numerical input sanitization with invalid inputs."""
        validator = InputValidator()

        # Invalid strings
        with pytest.raises(ValidationError):
            validator.sanitize_numerical_input("not_a_number")

        with pytest.raises(ValidationError):
            validator.sanitize_numerical_input("")

        # Invalid types
        with pytest.raises(ValidationError):
            validator.sanitize_numerical_input([1, 2, 3])

        with pytest.raises(ValidationError):
            validator.sanitize_numerical_input({"key": "value"})


class TestSecurityValidator:
    """Test security validator functionality."""

    def test_validate_arithmetic_input_valid(self):
        """Test arithmetic input validation with valid data."""
        validator = SecurityValidator()

        # Valid arithmetic data
        data = {"numbers": [1, 2, 3, 4, 5], "a": 10, "b": 5}

        result = validator.validate_operation_input("add", data)

        assert "numbers" in result
        assert result["numbers"] == [1, 2, 3, 4, 5]
        assert result["a"] == 10
        assert result["b"] == 5

    def test_validate_arithmetic_input_string_numbers(self):
        """Test arithmetic input validation with string numbers."""
        validator = SecurityValidator()

        # String numbers that should be converted
        data = {"numbers": ["1", "2", "3"], "a": "10.5", "b": "-5"}

        result = validator.validate_operation_input("add", data)

        assert result["numbers"] == [1, 2, 3]
        assert result["a"] == 10.5
        assert result["b"] == -5

    def test_validate_matrix_input_valid(self):
        """Test matrix input validation with valid data."""
        validator = SecurityValidator()

        # Valid matrix data
        data = {"matrix_a": [[1, 2], [3, 4]], "matrix_b": [[5, 6], [7, 8]]}

        result = validator.validate_operation_input("matrix_add", data)

        assert "matrix_a" in result
        assert "matrix_b" in result
        assert result["matrix_a"] == [[1, 2], [3, 4]]
        assert result["matrix_b"] == [[5, 6], [7, 8]]

    def test_validate_statistics_input_valid(self):
        """Test statistics input validation with valid data."""
        validator = SecurityValidator()

        # Valid statistics data
        data = {"data": [1, 2, 3, 4, 5], "x_data": [1, 2, 3], "y_data": [4, 5, 6]}

        result = validator.validate_operation_input("mean", data)

        assert result["data"] == [1, 2, 3, 4, 5]
        assert result["x_data"] == [1, 2, 3]
        assert result["y_data"] == [4, 5, 6]

    def test_validate_calculus_input_valid(self):
        """Test calculus input validation with valid data."""
        validator = SecurityValidator()

        # Valid calculus data
        data = {
            "expression": "x^2 + 2*x + 1",
            "variable": "x",
            "lower_limit": 0,
            "upper_limit": 10,
        }

        result = validator.validate_operation_input("derivative", data)

        assert result["expression"] == "x^2 + 2*x + 1"
        assert result["variable"] == "x"
        assert result["lower_limit"] == 0
        assert result["upper_limit"] == 10

    def test_validate_calculus_input_unsafe_expression(self):
        """Test calculus input validation with unsafe expression."""
        validator = SecurityValidator()

        # Unsafe expression
        data = {"expression": 'eval("malicious code")', "variable": "x"}

        with pytest.raises(SecurityError):
            validator.validate_operation_input("derivative", data)

    def test_validate_oversized_input(self):
        """Test validation with oversized input."""
        validator = SecurityValidator()

        # Create oversized data
        large_array = list(range(SecurityConfig.MAX_ARRAY_LENGTH + 1))
        data = {"numbers": large_array}

        with pytest.raises(SecurityError):
            validator.validate_operation_input("add", data)

    def test_validate_operation_input_function(self):
        """Test the convenience function for operation input validation."""
        # Valid data
        data = {"numbers": [1, 2, 3]}
        result = validate_operation_input("add", data)

        assert result["numbers"] == [1, 2, 3]

        # Invalid data
        large_array = list(range(SecurityConfig.MAX_ARRAY_LENGTH + 1))
        data = {"numbers": large_array}

        with pytest.raises(SecurityError):
            validate_operation_input("add", data)


class TestSecurityConfig:
    """Test security configuration."""

    def test_security_config_constants(self):
        """Test that security configuration constants are reasonable."""
        assert SecurityConfig.MAX_INPUT_SIZE > 0
        assert SecurityConfig.MAX_ARRAY_LENGTH > 0
        assert SecurityConfig.MAX_MATRIX_SIZE > 0
        assert SecurityConfig.MAX_STRING_LENGTH > 0
        assert SecurityConfig.MAX_FACTORIAL_INPUT > 0
        assert SecurityConfig.MAX_POWER_EXPONENT > 0
        assert SecurityConfig.MAX_ITERATION_COUNT > 0
        assert SecurityConfig.MAX_MEMORY_PER_OPERATION > 0
        assert SecurityConfig.MAX_CACHE_ENTRIES > 0
        assert SecurityConfig.MAX_REQUESTS_PER_MINUTE > 0
        assert SecurityConfig.MAX_CONCURRENT_OPERATIONS > 0

    def test_forbidden_patterns(self):
        """Test that forbidden patterns are comprehensive."""
        patterns = SecurityConfig.FORBIDDEN_PATTERNS

        # Should include dangerous patterns
        pattern_strings = [p for p in patterns]

        assert any("eval" in p for p in pattern_strings)
        assert any("exec" in p for p in pattern_strings)
        assert any("import" in p for p in pattern_strings)
        assert any("open" in p for p in pattern_strings)


@pytest.mark.asyncio
class TestSecurityIntegration:
    """Test security validation integration."""

    async def test_validation_decorator_success(self):
        """Test validation decorator with successful validation."""
        from calculator.core.security.validation import validate_input_decorator

        @validate_input_decorator("add")
        async def test_operation(operation, data):
            return sum(data["numbers"])

        # Valid data
        result = await test_operation("add", {"numbers": [1, 2, 3]})
        assert result == 6

    async def test_validation_decorator_failure(self):
        """Test validation decorator with validation failure."""
        from calculator.core.security.validation import validate_input_decorator

        @validate_input_decorator("add")
        async def test_operation(operation, data):
            return sum(data["numbers"])

        # Invalid data (oversized array)
        large_array = list(range(SecurityConfig.MAX_ARRAY_LENGTH + 1))

        with pytest.raises(SecurityError):
            await test_operation("add", {"numbers": large_array})
