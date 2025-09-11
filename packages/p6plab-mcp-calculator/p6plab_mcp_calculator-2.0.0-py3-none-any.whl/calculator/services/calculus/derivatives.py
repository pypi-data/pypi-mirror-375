"""Derivatives service for symbolic and numerical differentiation."""

from typing import Any, Dict

import sympy as sp
from sympy.parsing.sympy_parser import parse_expr

from ...core.errors.exceptions import ComputationError, ValidationError
from ..base import BaseService


class DerivativesService(BaseService):
    """Service for derivative calculations."""

    def __init__(self, config=None, cache=None):
        """Initialize derivatives service."""
        super().__init__(config, cache)

    async def process(self, operation: str, params: Dict[str, Any]) -> Any:
        """Process derivative operation.

        Args:
            operation: Name of the derivative operation
            params: Parameters for the operation

        Returns:
            Result of the derivative operation
        """
        operation_map = {
            "symbolic": self.symbolic_derivative,
            "partial": self.partial_derivative,
            "numerical": self.numerical_derivative,
            "gradient": self.gradient,
            "directional": self.directional_derivative,
            "higher_order": self.higher_order_derivative,
        }

        if operation not in operation_map:
            raise ValidationError(f"Unknown derivative operation: {operation}")

        return await operation_map[operation](params)

    def _validate_expression(self, expression: str) -> sp.Expr:
        """Validate and parse mathematical expression."""
        try:
            cleaned_expr = expression.strip()
            if not cleaned_expr:
                raise ValueError("Expression cannot be empty")

            parsed_expr = parse_expr(cleaned_expr, transformations="all")

            if parsed_expr is None:
                raise ValueError("Failed to parse expression")

            return parsed_expr

        except Exception as e:
            raise ValidationError(f"Invalid mathematical expression '{expression}': {e}")

    def _validate_variable(self, variable: str) -> sp.Symbol:
        """Validate and create a SymPy symbol for a variable."""
        try:
            if not variable or not isinstance(variable, str):
                raise ValueError("Variable must be a non-empty string")

            # Check for valid variable name
            if not variable.replace("_", "").isalnum():
                raise ValueError(
                    "Variable name must contain only letters, numbers, and underscores"
                )

            return sp.Symbol(variable)

        except Exception as e:
            raise ValidationError(f"Invalid variable '{variable}': {e}")

    async def symbolic_derivative(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate symbolic derivative of an expression.

        Args:
            params: Dictionary containing 'expression', 'variable', and optional 'order'

        Returns:
            Dictionary with derivative result and metadata
        """
        expression = params.get("expression")
        variable = params.get("variable")
        order = params.get("order", 1)

        if not expression:
            raise ValidationError("Expression is required for derivative calculation")

        if not variable:
            raise ValidationError("Variable is required for derivative calculation")

        if not isinstance(order, int) or order < 1:
            raise ValidationError("Order must be a positive integer")

        if order > 10:
            raise ValidationError("Order cannot exceed 10 for performance reasons")

        try:
            # Parse expression and variable
            expr = self._validate_expression(expression)
            var = self._validate_variable(variable)

            # Check if variable exists in expression
            if var not in expr.free_symbols:
                return {
                    "derivative": "0",
                    "original_expression": expression,
                    "variable": variable,
                    "order": order,
                    "latex": "0",
                    "simplified": "0",
                }

            # Calculate derivative
            derivative = sp.diff(expr, var, order)

            # Simplify the result
            simplified = sp.simplify(derivative)

            # Convert to LaTeX for display
            latex_result = sp.latex(simplified)

            return {
                "derivative": str(simplified),
                "original_expression": expression,
                "variable": variable,
                "order": order,
                "latex": latex_result,
                "simplified": str(simplified),
            }

        except Exception as e:
            raise ComputationError(f"Derivative calculation failed: {str(e)}")

    async def partial_derivative(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate partial derivative of a multi-variable expression.

        Args:
            params: Dictionary containing 'expression', 'variable', and optional 'order'

        Returns:
            Dictionary with partial derivative result
        """
        expression = params.get("expression")
        variable = params.get("variable")
        order = params.get("order", 1)

        if not expression:
            raise ValidationError("Expression is required for partial derivative calculation")

        if not variable:
            raise ValidationError("Variable is required for partial derivative calculation")

        if not isinstance(order, int) or order < 1:
            raise ValidationError("Order must be a positive integer")

        try:
            # Parse expression and variable
            expr = self._validate_expression(expression)
            var = self._validate_variable(variable)

            # Get all variables in the expression
            all_variables = list(expr.free_symbols)

            if len(all_variables) < 2:
                raise ValidationError(
                    "Expression must contain at least 2 variables for partial derivatives"
                )

            if var not in all_variables:
                return {
                    "partial_derivative": "0",
                    "original_expression": expression,
                    "variable": variable,
                    "order": order,
                    "all_variables": [str(v) for v in all_variables],
                    "latex": "0",
                }

            # Calculate partial derivative
            partial_deriv = sp.diff(expr, var, order)

            # Simplify the result
            simplified = sp.simplify(partial_deriv)

            # Convert to LaTeX
            latex_result = sp.latex(simplified)

            return {
                "partial_derivative": str(simplified),
                "original_expression": expression,
                "variable": variable,
                "order": order,
                "all_variables": [str(v) for v in all_variables],
                "latex": latex_result,
            }

        except Exception as e:
            raise ComputationError(f"Partial derivative calculation failed: {str(e)}")

    async def numerical_derivative(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate numerical derivative at a specific point.

        Args:
            params: Dictionary containing 'expression', 'variable', 'point', 'method', 'step_size'

        Returns:
            Dictionary with numerical derivative result
        """
        expression = params.get("expression")
        variable = params.get("variable")
        point = params.get("point")
        method = params.get("method", "central")
        step_size = params.get("step_size", 1e-6)

        if not expression:
            raise ValidationError("Expression is required for numerical derivative")

        if not variable:
            raise ValidationError("Variable is required for numerical derivative")

        if point is None:
            raise ValidationError("Point is required for numerical derivative")

        if method not in ["forward", "backward", "central"]:
            raise ValidationError("Method must be 'forward', 'backward', or 'central'")

        if step_size <= 0:
            raise ValidationError("Step size must be positive")

        try:
            # Parse expression and variable
            expr = self._validate_expression(expression)
            var = self._validate_variable(variable)
            point_val = float(point)

            # Create a numerical function
            func = sp.lambdify(var, expr, "numpy")

            # Calculate numerical derivative using finite differences
            if method == "forward":
                derivative_val = (func(point_val + step_size) - func(point_val)) / step_size
            elif method == "backward":
                derivative_val = (func(point_val) - func(point_val - step_size)) / step_size
            else:  # central
                derivative_val = (func(point_val + step_size) - func(point_val - step_size)) / (
                    2 * step_size
                )

            # Also calculate symbolic derivative for comparison
            symbolic_deriv = sp.diff(expr, var)
            symbolic_func = sp.lambdify(var, symbolic_deriv, "numpy")
            symbolic_val = float(symbolic_func(point_val))

            # Calculate error
            error = abs(derivative_val - symbolic_val) if not (sp.isnan(symbolic_val) if hasattr(sp, 'isnan') else False) else None

            return {
                "numerical_derivative": float(derivative_val),
                "symbolic_derivative": float(symbolic_val),
                "point": point_val,
                "method": method,
                "step_size": step_size,
                "error": error,
                "expression": expression,
                "variable": variable,
            }

        except Exception as e:
            raise ComputationError(f"Numerical derivative calculation failed: {str(e)}")

    async def gradient(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate gradient (vector of partial derivatives) of a multi-variable function.

        Args:
            params: Dictionary containing 'expression' and 'variables'

        Returns:
            Dictionary with gradient components
        """
        expression = params.get("expression")
        variables = params.get("variables")

        if not expression:
            raise ValidationError("Expression is required for gradient calculation")

        if not variables or not isinstance(variables, list):
            raise ValidationError("Variables list is required for gradient calculation")

        if len(variables) < 2:
            raise ValidationError("At least 2 variables are required for gradient calculation")

        try:
            # Parse expression
            expr = self._validate_expression(expression)

            # Validate variables
            var_symbols = []
            for var in variables:
                var_symbols.append(self._validate_variable(var))

            # Calculate partial derivatives for each variable
            gradient_components = []
            gradient_latex = []

            for i, var_symbol in enumerate(var_symbols):
                partial_deriv = sp.diff(expr, var_symbol)
                simplified = sp.simplify(partial_deriv)

                gradient_components.append(
                    {
                        "variable": variables[i],
                        "partial_derivative": str(simplified),
                        "latex": sp.latex(simplified),
                    }
                )
                gradient_latex.append(sp.latex(simplified))

            return {
                "gradient": gradient_components,
                "expression": expression,
                "variables": variables,
                "gradient_vector": [comp["partial_derivative"] for comp in gradient_components],
                "latex_vector": gradient_latex,
            }

        except Exception as e:
            raise ComputationError(f"Gradient calculation failed: {str(e)}")

    async def directional_derivative(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate directional derivative.

        Args:
            params: Dictionary containing 'expression', 'variables', 'direction', and optional 'point'

        Returns:
            Dictionary with directional derivative result
        """
        expression = params.get("expression")
        variables = params.get("variables")
        direction = params.get("direction")
        point = params.get("point")

        if not expression:
            raise ValidationError("Expression is required for directional derivative")

        if not variables or not isinstance(variables, list):
            raise ValidationError("Variables list is required for directional derivative")

        if not direction or not isinstance(direction, list):
            raise ValidationError("Direction vector is required for directional derivative")

        if len(variables) != len(direction):
            raise ValidationError("Direction vector must have same length as variables list")

        try:
            # First calculate gradient
            gradient_result = await self.gradient(
                {"expression": expression, "variables": variables}
            )

            # Parse direction vector
            direction_vals = [float(d) for d in direction]

            # Calculate magnitude of direction vector
            magnitude = sum(d**2 for d in direction_vals) ** 0.5

            if magnitude == 0:
                raise ValidationError("Direction vector cannot be zero")

            # Normalize direction vector
            unit_direction = [d / magnitude for d in direction_vals]

            # Calculate directional derivative as dot product of gradient and unit direction
            if point:
                # Evaluate gradient at specific point
                point_vals = [float(p) for p in point]
                if len(point_vals) != len(variables):
                    raise ValidationError("Point must have same dimension as variables")

                # Parse expression and substitute point values
                expr = self._validate_expression(expression)
                var_symbols = [self._validate_variable(var) for var in variables]

                # Calculate gradient at point
                gradient_at_point = []
                for var_symbol in var_symbols:
                    partial_deriv = sp.diff(expr, var_symbol)
                    # Substitute point values
                    substitutions = dict(zip(var_symbols, point_vals))
                    value_at_point = float(partial_deriv.subs(substitutions))
                    gradient_at_point.append(value_at_point)

                # Dot product
                directional_deriv = sum(g * u for g, u in zip(gradient_at_point, unit_direction))

                return {
                    "directional_derivative": directional_deriv,
                    "gradient_at_point": gradient_at_point,
                    "unit_direction": unit_direction,
                    "point": point_vals,
                    "expression": expression,
                    "variables": variables,
                }
            else:
                # Symbolic directional derivative
                gradient_exprs = [
                    comp["partial_derivative"] for comp in gradient_result["gradient"]
                ]

                # Create symbolic expression for directional derivative
                directional_expr_terms = []
                for i, grad_expr in enumerate(gradient_exprs):
                    if unit_direction[i] != 0:
                        if unit_direction[i] == 1:
                            directional_expr_terms.append(grad_expr)
                        else:
                            directional_expr_terms.append(f"({unit_direction[i]}) * ({grad_expr})")

                directional_expr = (
                    " + ".join(directional_expr_terms) if directional_expr_terms else "0"
                )

                return {
                    "directional_derivative": directional_expr,
                    "gradient": gradient_result["gradient"],
                    "unit_direction": unit_direction,
                    "expression": expression,
                    "variables": variables,
                }

        except Exception as e:
            raise ComputationError(f"Directional derivative calculation failed: {str(e)}")

    async def higher_order_derivative(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate higher-order derivatives.

        Args:
            params: Dictionary containing 'expression', 'variable', 'order'

        Returns:
            Dictionary with higher-order derivative results
        """
        expression = params.get("expression")
        variable = params.get("variable")
        order = params.get("order", 2)

        if not expression:
            raise ValidationError("Expression is required for higher-order derivative")

        if not variable:
            raise ValidationError("Variable is required for higher-order derivative")

        if not isinstance(order, int) or order < 2:
            raise ValidationError("Order must be an integer >= 2")

        if order > 10:
            raise ValidationError("Order cannot exceed 10 for performance reasons")

        try:
            # Parse expression and variable
            expr = self._validate_expression(expression)
            var = self._validate_variable(variable)

            # Calculate derivatives up to the specified order
            derivatives = []
            current_expr = expr

            for i in range(1, order + 1):
                derivative = sp.diff(current_expr, var)
                simplified = sp.simplify(derivative)

                derivatives.append(
                    {"order": i, "derivative": str(simplified), "latex": sp.latex(simplified)}
                )

                current_expr = derivative

            return {
                "derivatives": derivatives,
                "expression": expression,
                "variable": variable,
                "max_order": order,
                "final_derivative": derivatives[-1]["derivative"] if derivatives else "0",
            }

        except Exception as e:
            raise ComputationError(f"Higher-order derivative calculation failed: {str(e)}")
