"""Arithmetic operation handlers."""

from pydantic import BaseModel, Field

from ...services.arithmetic import ArithmeticService
from ..factory import ToolRegistrationFactory


class BasicArithmeticRequest(BaseModel):
    """Request model for basic arithmetic operations."""

    numbers: list = Field(..., description="List of numbers for the operation")


class TwoNumberRequest(BaseModel):
    """Request model for two-number operations."""

    a: float = Field(..., description="First number")
    b: float = Field(..., description="Second number")


class PowerRequest(BaseModel):
    """Request model for power operations."""

    base: float = Field(..., description="Base number")
    exponent: float = Field(..., description="Exponent")


class SingleNumberRequest(BaseModel):
    """Request model for single number operations."""

    number: float = Field(..., description="Input number")


class FactorialRequest(BaseModel):
    """Request model for factorial operation."""

    number: int = Field(..., ge=0, le=170, description="Non-negative integer for factorial")


class RoundRequest(BaseModel):
    """Request model for rounding operation."""

    number: float = Field(..., description="Number to round")
    decimals: int = Field(default=0, ge=0, le=15, description="Number of decimal places")


class LogarithmRequest(BaseModel):
    """Request model for logarithm operation."""

    number: float = Field(..., gt=0, description="Positive number for logarithm")
    base: float = Field(default=2.718281828459045, gt=0, description="Logarithm base (default: e)")


class TrigonometricRequest(BaseModel):
    """Request model for trigonometric operations."""

    angle: float = Field(..., description="Angle value")
    unit: str = Field(default="radians", description="Angle unit (radians or degrees)")


def register_arithmetic_handlers(
    factory: ToolRegistrationFactory, service: ArithmeticService
) -> None:
    """Register arithmetic operation handlers.

    Args:
        factory: Tool registration factory
        service: Arithmetic service instance
    """

    # Basic arithmetic operations
    factory.register_service_tools(
        service_name="arithmetic",
        service_instance=service,
        tool_definitions=[
            {
                "name": "add",
                "operation": "add",
                "description": "Add two or more numbers",
                "input_schema": BasicArithmeticRequest,
                "tool_group": "basic",
                "examples": [
                    {"numbers": [2, 3, 4], "result": 9},
                    {"numbers": [1.5, 2.5], "result": 4.0},
                ],
                "tags": ["arithmetic", "basic"],
            },
            {
                "name": "subtract",
                "operation": "subtract",
                "description": "Subtract two numbers (a - b)",
                "input_schema": TwoNumberRequest,
                "tool_group": "basic",
                "examples": [{"a": 10, "b": 3, "result": 7}, {"a": 5.5, "b": 2.2, "result": 3.3}],
                "tags": ["arithmetic", "basic"],
            },
            {
                "name": "multiply",
                "operation": "multiply",
                "description": "Multiply two or more numbers",
                "input_schema": BasicArithmeticRequest,
                "tool_group": "basic",
                "examples": [
                    {"numbers": [2, 3, 4], "result": 24},
                    {"numbers": [1.5, 2], "result": 3.0},
                ],
                "tags": ["arithmetic", "basic"],
            },
            {
                "name": "divide",
                "operation": "divide",
                "description": "Divide two numbers (a / b)",
                "input_schema": TwoNumberRequest,
                "tool_group": "basic",
                "examples": [
                    {"a": 10, "b": 2, "result": 5.0},
                    {"a": 7, "b": 3, "result": 2.333333333333333},
                ],
                "tags": ["arithmetic", "basic"],
            },
            {
                "name": "power",
                "operation": "power",
                "description": "Raise a number to a power (base^exponent)",
                "input_schema": PowerRequest,
                "tool_group": "basic",
                "examples": [
                    {"base": 2, "exponent": 3, "result": 8.0},
                    {"base": 9, "exponent": 0.5, "result": 3.0},
                ],
                "tags": ["arithmetic", "basic"],
            },
            {
                "name": "sqrt",
                "operation": "sqrt",
                "description": "Calculate square root of a number",
                "input_schema": SingleNumberRequest,
                "tool_group": "basic",
                "examples": [
                    {"number": 16, "result": 4.0},
                    {"number": 2, "result": 1.4142135623730951},
                ],
                "tags": ["arithmetic", "basic"],
            },
            {
                "name": "factorial",
                "operation": "factorial",
                "description": "Calculate factorial of a non-negative integer",
                "input_schema": FactorialRequest,
                "tool_group": "basic",
                "examples": [{"number": 5, "result": 120}, {"number": 0, "result": 1}],
                "tags": ["arithmetic", "basic"],
            },
            {
                "name": "gcd",
                "operation": "gcd",
                "description": "Calculate greatest common divisor of numbers",
                "input_schema": BasicArithmeticRequest,
                "tool_group": "advanced",
                "examples": [
                    {"numbers": [12, 18], "result": 6},
                    {"numbers": [48, 18, 24], "result": 6},
                ],
                "tags": ["arithmetic", "number_theory"],
            },
            {
                "name": "lcm",
                "operation": "lcm",
                "description": "Calculate least common multiple of numbers",
                "input_schema": BasicArithmeticRequest,
                "tool_group": "advanced",
                "examples": [
                    {"numbers": [4, 6], "result": 12},
                    {"numbers": [3, 4, 5], "result": 60},
                ],
                "tags": ["arithmetic", "number_theory"],
            },
            {
                "name": "modulo",
                "operation": "modulo",
                "description": "Calculate modulo operation (a mod b)",
                "input_schema": TwoNumberRequest,
                "tool_group": "basic",
                "examples": [{"a": 10, "b": 3, "result": 1.0}, {"a": 17, "b": 5, "result": 2.0}],
                "tags": ["arithmetic", "basic"],
            },
            {
                "name": "absolute",
                "operation": "absolute",
                "description": "Calculate absolute value of a number",
                "input_schema": SingleNumberRequest,
                "tool_group": "basic",
                "examples": [{"number": -5, "result": 5.0}, {"number": 3.14, "result": 3.14}],
                "tags": ["arithmetic", "basic"],
            },
            {
                "name": "round",
                "operation": "round_number",
                "description": "Round a number to specified decimal places",
                "input_schema": RoundRequest,
                "tool_group": "basic",
                "examples": [
                    {"number": 3.14159, "decimals": 2, "result": 3.14},
                    {"number": 123.456, "decimals": 0, "result": 123.0},
                ],
                "tags": ["arithmetic", "basic"],
            },
            {
                "name": "floor",
                "operation": "floor",
                "description": "Calculate floor (largest integer ≤ number)",
                "input_schema": SingleNumberRequest,
                "tool_group": "basic",
                "examples": [{"number": 3.7, "result": 3}, {"number": -2.3, "result": -3}],
                "tags": ["arithmetic", "basic"],
            },
            {
                "name": "ceil",
                "operation": "ceil",
                "description": "Calculate ceiling (smallest integer ≥ number)",
                "input_schema": SingleNumberRequest,
                "tool_group": "basic",
                "examples": [{"number": 3.2, "result": 4}, {"number": -2.7, "result": -2}],
                "tags": ["arithmetic", "basic"],
            },
            {
                "name": "log",
                "operation": "logarithm",
                "description": "Calculate logarithm of a number",
                "input_schema": LogarithmRequest,
                "tool_group": "advanced",
                "examples": [
                    {"number": 8, "base": 2, "result": 3.0},
                    {"number": 100, "base": 10, "result": 2.0},
                ],
                "tags": ["arithmetic", "logarithmic"],
            },
            {
                "name": "exp",
                "operation": "exponential",
                "description": "Calculate exponential (e^x)",
                "input_schema": SingleNumberRequest,
                "tool_group": "advanced",
                "examples": [
                    {"number": 1, "result": 2.718281828459045},
                    {"number": 0, "result": 1.0},
                ],
                "tags": ["arithmetic", "exponential"],
            },
            {
                "name": "sin",
                "operation": "sine",
                "description": "Calculate sine of an angle",
                "input_schema": TrigonometricRequest,
                "tool_group": "trigonometry",
                "examples": [
                    {"angle": 1.5708, "unit": "radians", "result": 1.0},
                    {"angle": 90, "unit": "degrees", "result": 1.0},
                ],
                "tags": ["trigonometry", "sine"],
            },
            {
                "name": "cos",
                "operation": "cosine",
                "description": "Calculate cosine of an angle",
                "input_schema": TrigonometricRequest,
                "tool_group": "trigonometry",
                "examples": [
                    {"angle": 0, "unit": "radians", "result": 1.0},
                    {"angle": 90, "unit": "degrees", "result": 0.0},
                ],
                "tags": ["trigonometry", "cosine"],
            },
            {
                "name": "tan",
                "operation": "tangent",
                "description": "Calculate tangent of an angle",
                "input_schema": TrigonometricRequest,
                "tool_group": "trigonometry",
                "examples": [
                    {"angle": 0.7854, "unit": "radians", "result": 1.0},
                    {"angle": 45, "unit": "degrees", "result": 1.0},
                ],
                "tags": ["trigonometry", "tangent"],
            },
            {
                "name": "asin",
                "operation": "arcsine",
                "description": "Calculate arcsine (inverse sine)",
                "input_schema": TrigonometricRequest,
                "tool_group": "trigonometry",
                "examples": [
                    {"angle": 1, "unit": "radians", "result": 1.5708},
                    {"angle": 0.5, "unit": "degrees", "result": 30.0},
                ],
                "tags": ["trigonometry", "inverse"],
            },
            {
                "name": "acos",
                "operation": "arccosine",
                "description": "Calculate arccosine (inverse cosine)",
                "input_schema": TrigonometricRequest,
                "tool_group": "trigonometry",
                "examples": [
                    {"angle": 0, "unit": "radians", "result": 1.5708},
                    {"angle": 0.5, "unit": "degrees", "result": 60.0},
                ],
                "tags": ["trigonometry", "inverse"],
            },
            {
                "name": "atan",
                "operation": "arctangent",
                "description": "Calculate arctangent (inverse tangent)",
                "input_schema": TrigonometricRequest,
                "tool_group": "trigonometry",
                "examples": [
                    {"angle": 1, "unit": "radians", "result": 0.7854},
                    {"angle": 1, "unit": "degrees", "result": 45.0},
                ],
                "tags": ["trigonometry", "inverse"],
            },
            {
                "name": "sinh",
                "operation": "hyperbolic_sine",
                "description": "Calculate hyperbolic sine",
                "input_schema": SingleNumberRequest,
                "tool_group": "hyperbolic",
                "examples": [
                    {"number": 0, "result": 0.0},
                    {"number": 1, "result": 1.1752011936438014},
                ],
                "tags": ["hyperbolic", "sine"],
            },
            {
                "name": "cosh",
                "operation": "hyperbolic_cosine",
                "description": "Calculate hyperbolic cosine",
                "input_schema": SingleNumberRequest,
                "tool_group": "hyperbolic",
                "examples": [
                    {"number": 0, "result": 1.0},
                    {"number": 1, "result": 1.5430806348152437},
                ],
                "tags": ["hyperbolic", "cosine"],
            },
            {
                "name": "tanh",
                "operation": "hyperbolic_tangent",
                "description": "Calculate hyperbolic tangent",
                "input_schema": SingleNumberRequest,
                "tool_group": "hyperbolic",
                "examples": [
                    {"number": 0, "result": 0.0},
                    {"number": 1, "result": 0.7615941559557649},
                ],
                "tags": ["hyperbolic", "tangent"],
            },
        ],
        tool_group="arithmetic",
    )
