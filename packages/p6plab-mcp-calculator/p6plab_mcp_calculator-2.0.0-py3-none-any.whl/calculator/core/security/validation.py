"""Security validation utilities for calculator operations."""

import math
import re
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Union

from ..errors.exceptions import SecurityError, ValidationError


class SecurityConfig:
    """Security configuration constants."""

    # Input size limits
    MAX_INPUT_SIZE = 50000  # Maximum size of input data in bytes
    MAX_ARRAY_LENGTH = 10000  # Maximum length of arrays/lists
    MAX_MATRIX_SIZE = 1000  # Maximum matrix dimension (1000x1000)
    MAX_STRING_LENGTH = 1000  # Maximum string length

    # Computation limits
    MAX_FACTORIAL_INPUT = 1000  # Maximum input for factorial
    MAX_POWER_EXPONENT = 1000  # Maximum exponent for power operations
    MAX_ITERATION_COUNT = 100000  # Maximum iterations for algorithms

    # Memory limits
    MAX_MEMORY_PER_OPERATION = 100 * 1024 * 1024  # 100MB per operation
    MAX_CACHE_ENTRIES = 10000  # Maximum cache entries

    # Rate limiting
    MAX_REQUESTS_PER_MINUTE = 2000  # Maximum requests per minute per client
    MAX_CONCURRENT_OPERATIONS = 50  # Maximum concurrent operations

    # Expression validation
    ALLOWED_EXPRESSION_CHARS = re.compile(r"^[a-zA-Z0-9+\-*/().,\s\^_]+$")
    FORBIDDEN_PATTERNS = [
        r"__.*__",  # Python dunder methods
        r"eval\s*\(",  # eval function calls
        r"exec\s*\(",  # exec function calls
        r"import\s+",  # import statements
        r"from\s+.*\s+import",  # from-import statements
        r"open\s*\(",  # file operations
        r"file\s*\(",  # file operations
        r"input\s*\(",  # input operations
        r"raw_input\s*\(",  # raw input operations
    ]


class InputValidator:
    """Validates and sanitizes input data for security."""

    @staticmethod
    def validate_input_size(data: Any) -> None:
        """Validate that input data size is within limits.

        Args:
            data: Input data to validate

        Raises:
            SecurityError: If input size exceeds limits
        """
        try:
            # Calculate approximate size
            if isinstance(data, str):
                size = len(data.encode("utf-8"))
            elif isinstance(data, (list, tuple)):
                size = sum(len(str(item).encode("utf-8")) for item in data)
            elif isinstance(data, dict):
                size = sum(
                    len(str(k).encode("utf-8")) + len(str(v).encode("utf-8"))
                    for k, v in data.items()
                )
            else:
                size = len(str(data).encode("utf-8"))

            if size > SecurityConfig.MAX_INPUT_SIZE:
                raise SecurityError(
                    f"Input size {size} bytes exceeds maximum allowed size "
                    f"{SecurityConfig.MAX_INPUT_SIZE} bytes"
                )

        except Exception as e:
            if isinstance(e, SecurityError):
                raise
            raise SecurityError(f"Failed to validate input size: {str(e)}")

    @staticmethod
    def validate_array_length(data: List[Any], max_length: Optional[int] = None) -> None:
        """Validate array length is within limits.

        Args:
            data: Array to validate
            max_length: Optional custom maximum length

        Raises:
            ValidationError: If array length exceeds limits
        """
        max_len = max_length or SecurityConfig.MAX_ARRAY_LENGTH

        if len(data) > max_len:
            raise ValidationError(
                f"Array length {len(data)} exceeds maximum allowed length {max_len}",
                field="array_length",
            )

    @staticmethod
    def validate_matrix_dimensions(matrix: List[List[Any]]) -> None:
        """Validate matrix dimensions are within limits.

        Args:
            matrix: Matrix to validate

        Raises:
            ValidationError: If matrix dimensions exceed limits
        """
        if not matrix:
            raise ValidationError("Matrix cannot be empty", field="matrix")

        rows = len(matrix)
        cols = len(matrix[0]) if matrix else 0

        if rows > SecurityConfig.MAX_MATRIX_SIZE:
            raise ValidationError(
                f"Matrix rows {rows} exceed maximum allowed size {SecurityConfig.MAX_MATRIX_SIZE}",
                field="matrix_rows",
            )

        if cols > SecurityConfig.MAX_MATRIX_SIZE:
            raise ValidationError(
                f"Matrix columns {cols} exceed maximum allowed size {SecurityConfig.MAX_MATRIX_SIZE}",
                field="matrix_cols",
            )

        # Validate all rows have same length
        for i, row in enumerate(matrix):
            if len(row) != cols:
                raise ValidationError(
                    f"Matrix row {i} has length {len(row)}, expected {cols}",
                    field="matrix_structure",
                )

    @staticmethod
    def validate_string_length(text: str, max_length: Optional[int] = None) -> None:
        """Validate string length is within limits.

        Args:
            text: String to validate
            max_length: Optional custom maximum length

        Raises:
            ValidationError: If string length exceeds limits
        """
        max_len = max_length or SecurityConfig.MAX_STRING_LENGTH

        if len(text) > max_len:
            raise ValidationError(
                f"String length {len(text)} exceeds maximum allowed length {max_len}",
                field="string_length",
            )

    @staticmethod
    def validate_expression_safety(expression: str) -> None:
        """Validate that mathematical expression is safe to evaluate.

        Args:
            expression: Mathematical expression to validate

        Raises:
            SecurityError: If expression contains unsafe patterns
        """
        # Check for allowed characters
        if not SecurityConfig.ALLOWED_EXPRESSION_CHARS.match(expression):
            raise SecurityError(
                "Expression contains forbidden characters",
                details={"expression": expression[:100]},  # Limit logged expression length
            )

        # Check for forbidden patterns
        for pattern in SecurityConfig.FORBIDDEN_PATTERNS:
            if re.search(pattern, expression, re.IGNORECASE):
                raise SecurityError(
                    f"Expression contains forbidden pattern: {pattern}",
                    details={"pattern": pattern},
                )

    @staticmethod
    def validate_numerical_limits(value: Union[int, float], operation: str) -> None:
        """Validate numerical values are within safe limits for operations.

        Args:
            value: Numerical value to validate
            operation: Operation being performed

        Raises:
            ValidationError: If value exceeds safe limits
        """
        if operation == "factorial":
            if value < 0:
                raise ValidationError(
                    "Factorial input must be non-negative", field="factorial_input"
                )
            if value > SecurityConfig.MAX_FACTORIAL_INPUT:
                raise ValidationError(
                    f"Factorial input {value} exceeds maximum allowed value "
                    f"{SecurityConfig.MAX_FACTORIAL_INPUT}",
                    field="factorial_input",
                )

        elif operation == "power":
            if abs(value) > SecurityConfig.MAX_POWER_EXPONENT:
                raise ValidationError(
                    f"Power exponent {value} exceeds maximum allowed value "
                    f"{SecurityConfig.MAX_POWER_EXPONENT}",
                    field="power_exponent",
                )

        # Check for infinity and NaN
        if isinstance(value, float):
            if math.isinf(value):
                raise ValidationError("Infinite values are not allowed", field="numerical_value")
            if math.isnan(value):
                raise ValidationError("NaN values are not allowed", field="numerical_value")

    @staticmethod
    def sanitize_numerical_input(value: Any) -> Union[int, float, Decimal]:
        """Sanitize and convert numerical input to safe format.

        Args:
            value: Input value to sanitize

        Returns:
            Sanitized numerical value

        Raises:
            ValidationError: If value cannot be safely converted
        """
        try:
            # Handle string inputs
            if isinstance(value, str):
                value = value.strip()

                # Check for empty string
                if not value:
                    raise ValidationError("Empty string cannot be converted to number")

                # Try to convert to number
                try:
                    # Try integer first
                    if "." not in value and "e" not in value.lower():
                        return int(value)
                    else:
                        return float(value)
                except ValueError:
                    # Try Decimal for high precision
                    return Decimal(value)

            # Handle existing numbers
            elif isinstance(value, (int, float, Decimal)):
                # Validate limits
                if isinstance(value, float):
                    if math.isinf(value) or math.isnan(value):
                        raise ValidationError("Invalid numerical value (inf/nan)")

                return value

            else:
                raise ValidationError(f"Cannot convert {type(value)} to number")

        except (ValueError, InvalidOperation) as e:
            raise ValidationError(f"Invalid numerical input: {str(e)}")


class SecurityValidator:
    """Main security validator class."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize security validator.

        Args:
            config: Optional security configuration overrides
        """
        self.config = config or {}
        self.input_validator = InputValidator()

    def validate_operation_input(self, operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input data for a specific operation.

        Args:
            operation: Operation name
            data: Input data dictionary

        Returns:
            Validated and sanitized data

        Raises:
            ValidationError: If validation fails
            SecurityError: If security check fails
        """
        # Validate overall input size
        self.input_validator.validate_input_size(data)

        # Operation-specific validation
        if operation in ["add", "subtract", "multiply"]:
            return self._validate_arithmetic_input(data)
        elif operation.startswith("matrix_"):
            return self._validate_matrix_input(data)
        elif operation in ["mean", "median", "std_dev", "variance"]:
            return self._validate_statistics_input(data)
        elif operation in ["derivative", "integral"]:
            return self._validate_calculus_input(data)
        else:
            return self._validate_generic_input(data)

    def _validate_arithmetic_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate arithmetic operation input."""
        validated_data = {}

        for key, value in data.items():
            if key == "numbers" and isinstance(value, list):
                self.input_validator.validate_array_length(value)
                validated_data[key] = [
                    self.input_validator.sanitize_numerical_input(num) for num in value
                ]
            elif key in ["a", "b", "base", "exponent", "number"]:
                if key == "exponent":
                    self.input_validator.validate_numerical_limits(value, "power")
                elif key == "number" and "factorial" in str(data):
                    self.input_validator.validate_numerical_limits(value, "factorial")

                validated_data[key] = self.input_validator.sanitize_numerical_input(value)
            else:
                validated_data[key] = value

        return validated_data

    def _validate_matrix_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate matrix operation input."""
        validated_data = {}

        for key, value in data.items():
            if key in ["matrix", "matrix_a", "matrix_b"] and isinstance(value, list):
                self.input_validator.validate_matrix_dimensions(value)

                # Validate and sanitize matrix elements
                validated_matrix = []
                for row in value:
                    validated_row = [
                        self.input_validator.sanitize_numerical_input(elem) for elem in row
                    ]
                    validated_matrix.append(validated_row)

                validated_data[key] = validated_matrix
            elif key == "vector_b" and isinstance(value, list):
                self.input_validator.validate_array_length(value)
                validated_data[key] = [
                    self.input_validator.sanitize_numerical_input(elem) for elem in value
                ]
            else:
                validated_data[key] = value

        return validated_data

    def _validate_statistics_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate statistics operation input."""
        validated_data = {}

        for key, value in data.items():
            if key in ["data", "x_data", "y_data"] and isinstance(value, list):
                self.input_validator.validate_array_length(value)
                validated_data[key] = [
                    self.input_validator.sanitize_numerical_input(num) for num in value
                ]
            elif key == "groups" and isinstance(value, list):
                # Validate grouped data
                for i, group in enumerate(value):
                    if not isinstance(group, list):
                        raise ValidationError(f"Group {i} must be a list")
                    self.input_validator.validate_array_length(group)

                validated_groups = []
                for group in value:
                    validated_group = [
                        self.input_validator.sanitize_numerical_input(num) for num in group
                    ]
                    validated_groups.append(validated_group)

                validated_data[key] = validated_groups
            else:
                validated_data[key] = value

        return validated_data

    def _validate_calculus_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate calculus operation input."""
        validated_data = {}

        for key, value in data.items():
            if key == "expression" and isinstance(value, str):
                self.input_validator.validate_string_length(value)
                self.input_validator.validate_expression_safety(value)
                validated_data[key] = value.strip()
            elif key in ["lower_limit", "upper_limit", "point"]:
                validated_data[key] = self.input_validator.sanitize_numerical_input(value)
            else:
                validated_data[key] = value

        return validated_data

    def _validate_generic_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate generic operation input."""
        validated_data = {}

        for key, value in data.items():
            if isinstance(value, list):
                self.input_validator.validate_array_length(value)
                # Try to sanitize numerical lists
                try:
                    validated_data[key] = [
                        self.input_validator.sanitize_numerical_input(item) for item in value
                    ]
                except ValidationError:
                    # If not all numerical, keep original
                    validated_data[key] = value
            elif isinstance(value, str):
                self.input_validator.validate_string_length(value)
                validated_data[key] = value.strip()
            elif isinstance(value, (int, float)):
                validated_data[key] = self.input_validator.sanitize_numerical_input(value)
            else:
                validated_data[key] = value

        return validated_data


# Global security validator instance
security_validator = SecurityValidator()


def validate_operation_input(operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to validate operation input.

    Args:
        operation: Operation name
        data: Input data

    Returns:
        Validated and sanitized data
    """
    return security_validator.validate_operation_input(operation, data)


def validate_input_decorator(operation_name: str):
    """Decorator to automatically validate operation input.

    Args:
        operation_name: Name of the operation for validation
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Find data parameter
            if "data" in kwargs:
                kwargs["data"] = validate_operation_input(operation_name, kwargs["data"])
            elif len(args) > 1 and isinstance(args[1], dict):
                # Assume second argument is data
                args = list(args)
                args[1] = validate_operation_input(operation_name, args[1])
                args = tuple(args)

            return await func(*args, **kwargs)

        return wrapper

    return decorator
