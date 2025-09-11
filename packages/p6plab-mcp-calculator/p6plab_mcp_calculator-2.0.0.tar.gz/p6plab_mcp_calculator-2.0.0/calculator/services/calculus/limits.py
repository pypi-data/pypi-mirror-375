"""Limits service for calculating mathematical limits."""

from typing import Any, Dict, Union

import sympy as sp
from sympy.parsing.sympy_parser import parse_expr

from ...core.errors.exceptions import ComputationError, ValidationError
from ..base import BaseService


class LimitsService(BaseService):
    """Service for limit calculations."""

    def __init__(self, config=None, cache=None):
        """Initialize limits service."""
        super().__init__(config, cache)

    async def process(self, operation: str, params: Dict[str, Any]) -> Any:
        """Process limit operation.

        Args:
            operation: Name of the limit operation
            params: Parameters for the operation

        Returns:
            Result of the limit operation
        """
        operation_map = {
            "limit": self.calculate_limit,
            "left_limit": self.left_limit,
            "right_limit": self.right_limit,
            "limit_at_infinity": self.limit_at_infinity,
            "multivariable_limit": self.multivariable_limit,
            "sequential_limit": self.sequential_limit,
        }

        if operation not in operation_map:
            raise ValidationError(f"Unknown limit operation: {operation}")

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

            if not variable.replace("_", "").isalnum():
                raise ValueError(
                    "Variable name must contain only letters, numbers, and underscores"
                )

            return sp.Symbol(variable)

        except Exception as e:
            raise ValidationError(f"Invalid variable '{variable}': {e}")

    def _parse_approach_value(
        self, approach_value: Union[float, int, str]
    ) -> Union[float, sp.Basic]:
        """Parse approach value, handling infinity and symbolic values."""
        try:
            if isinstance(approach_value, str):
                if approach_value.lower() in ["inf", "infinity", "+inf", "+infinity"]:
                    return sp.oo
                elif approach_value.lower() in ["-inf", "-infinity"]:
                    return -sp.oo
                else:
                    # Try to parse as symbolic expression
                    return parse_expr(approach_value)
            else:
                return float(approach_value)
        except Exception as e:
            raise ValidationError(f"Invalid approach value '{approach_value}': {e}")

    async def calculate_limit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate limit of an expression.

        Args:
            params: Dictionary containing 'expression', 'variable', 'approach_value', 'direction'

        Returns:
            Dictionary with limit result and metadata
        """
        expression = params.get("expression")
        variable = params.get("variable")
        approach_value = params.get("approach_value")
        direction = params.get("direction", "both")

        if not expression:
            raise ValidationError("Expression is required for limit calculation")

        if not variable:
            raise ValidationError("Variable is required for limit calculation")

        if approach_value is None:
            raise ValidationError("Approach value is required for limit calculation")

        if direction not in ["both", "left", "right", "+", "-"]:
            raise ValidationError("Direction must be 'both', 'left', 'right', '+', or '-'")

        try:
            # Parse expression and variable
            expr = self._validate_expression(expression)
            var = self._validate_variable(variable)
            approach_val = self._parse_approach_value(approach_value)

            # Calculate limit based on direction
            if direction in ["both"]:
                limit_result = sp.limit(expr, var, approach_val)
            elif direction in ["left", "-"]:
                limit_result = sp.limit(expr, var, approach_val, "-")
            elif direction in ["right", "+"]:
                limit_result = sp.limit(expr, var, approach_val, "+")

            # Check if limit exists
            limit_exists = limit_result != sp.nan and not limit_result.has(sp.AccumBounds)

            # Get string representation
            limit_str = str(limit_result)

            # Check for special cases
            is_infinite = limit_result in [sp.oo, -sp.oo]
            is_indeterminate = limit_result == sp.nan

            # Try to evaluate numerically if possible
            numerical_value = None
            if limit_exists and not is_infinite:
                try:
                    numerical_value = float(limit_result.evalf())
                except:
                    pass

            # Calculate one-sided limits for comparison if direction is 'both'
            left_limit = None
            right_limit = None

            if direction == "both":
                try:
                    left_limit = sp.limit(expr, var, approach_val, "-")
                    right_limit = sp.limit(expr, var, approach_val, "+")

                    # Check if one-sided limits agree
                    limits_agree = left_limit == right_limit
                except:
                    limits_agree = None
            else:
                limits_agree = None

            return {
                "limit": limit_str,
                "numerical_value": numerical_value,
                "exists": limit_exists,
                "infinite": is_infinite,
                "indeterminate": is_indeterminate,
                "expression": expression,
                "variable": variable,
                "approach_value": str(approach_val),
                "direction": direction,
                "left_limit": str(left_limit) if left_limit is not None else None,
                "right_limit": str(right_limit) if right_limit is not None else None,
                "limits_agree": limits_agree,
                "latex": sp.latex(limit_result),
            }

        except Exception as e:
            raise ComputationError(f"Limit calculation failed: {str(e)}")

    async def left_limit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate left-hand limit.

        Args:
            params: Dictionary containing limit parameters

        Returns:
            Dictionary with left limit result
        """
        params["direction"] = "left"
        return await self.calculate_limit(params)

    async def right_limit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate right-hand limit.

        Args:
            params: Dictionary containing limit parameters

        Returns:
            Dictionary with right limit result
        """
        params["direction"] = "right"
        return await self.calculate_limit(params)

    async def limit_at_infinity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate limit as variable approaches infinity.

        Args:
            params: Dictionary containing 'expression', 'variable', 'infinity_type'

        Returns:
            Dictionary with limit at infinity result
        """
        expression = params.get("expression")
        variable = params.get("variable")
        infinity_type = params.get("infinity_type", "positive")

        if infinity_type not in ["positive", "negative", "both"]:
            raise ValidationError("Infinity type must be 'positive', 'negative', or 'both'")

        try:
            results = {}

            if infinity_type in ["positive", "both"]:
                positive_result = await self.calculate_limit(
                    {
                        "expression": expression,
                        "variable": variable,
                        "approach_value": "inf",
                        "direction": "both",
                    }
                )
                results["positive_infinity"] = positive_result

            if infinity_type in ["negative", "both"]:
                negative_result = await self.calculate_limit(
                    {
                        "expression": expression,
                        "variable": variable,
                        "approach_value": "-inf",
                        "direction": "both",
                    }
                )
                results["negative_infinity"] = negative_result

            # Determine horizontal asymptotes
            horizontal_asymptotes = []

            if "positive_infinity" in results:
                pos_limit = results["positive_infinity"]["limit"]
                if (
                    pos_limit not in ["oo", "-oo", "nan"]
                    and results["positive_infinity"]["exists"]
                ):
                    horizontal_asymptotes.append(f"y = {pos_limit}")

            if "negative_infinity" in results:
                neg_limit = results["negative_infinity"]["limit"]
                if (
                    neg_limit not in ["oo", "-oo", "nan"]
                    and results["negative_infinity"]["exists"]
                ):
                    if f"y = {neg_limit}" not in horizontal_asymptotes:
                        horizontal_asymptotes.append(f"y = {neg_limit}")

            return {
                "limits_at_infinity": results,
                "horizontal_asymptotes": horizontal_asymptotes,
                "expression": expression,
                "variable": variable,
                "infinity_type": infinity_type,
            }

        except Exception as e:
            raise ComputationError(f"Limit at infinity calculation failed: {str(e)}")

    async def multivariable_limit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate multivariable limit.

        Args:
            params: Dictionary containing 'expression', 'variables', 'approach_point'

        Returns:
            Dictionary with multivariable limit result
        """
        expression = params.get("expression")
        variables = params.get("variables")
        approach_point = params.get("approach_point")

        if not expression:
            raise ValidationError("Expression is required for multivariable limit")

        if not variables or not isinstance(variables, list):
            raise ValidationError("Variables list is required for multivariable limit")

        if not approach_point or not isinstance(approach_point, list):
            raise ValidationError("Approach point is required for multivariable limit")

        if len(variables) != len(approach_point):
            raise ValidationError("Variables and approach point must have same length")

        try:
            # Parse expression
            expr = self._validate_expression(expression)

            # Parse variables and approach point
            var_symbols = []
            approach_values = []

            for i, var in enumerate(variables):
                var_symbol = self._validate_variable(var)
                var_symbols.append(var_symbol)
                approach_val = self._parse_approach_value(approach_point[i])
                approach_values.append(approach_val)

            # For multivariable limits, we'll substitute variables one by one
            # This is a simplified approach - true multivariable limits are more complex
            current_expr = expr
            substitution_order = []

            for i, (var_symbol, approach_val) in enumerate(zip(var_symbols, approach_values)):
                try:
                    # Calculate limit with respect to this variable
                    limit_result = sp.limit(current_expr, var_symbol, approach_val)
                    current_expr = limit_result

                    substitution_order.append(
                        {
                            "variable": variables[i],
                            "approach_value": str(approach_val),
                            "intermediate_result": str(limit_result),
                        }
                    )

                except Exception as e:
                    # If limit calculation fails, try direct substitution
                    try:
                        current_expr = current_expr.subs(var_symbol, approach_val)
                        substitution_order.append(
                            {
                                "variable": variables[i],
                                "approach_value": str(approach_val),
                                "intermediate_result": str(current_expr),
                                "method": "substitution",
                            }
                        )
                    except:
                        raise ComputationError(f"Failed to process variable {variables[i]}: {e}")

            # Final result
            final_result = current_expr

            # Check if result exists and is finite
            limit_exists = final_result != sp.nan and not final_result.has(sp.AccumBounds)
            is_infinite = final_result in [sp.oo, -sp.oo]

            # Try numerical evaluation
            numerical_value = None
            if limit_exists and not is_infinite:
                try:
                    numerical_value = float(final_result.evalf())
                except:
                    pass

            return {
                "multivariable_limit": str(final_result),
                "numerical_value": numerical_value,
                "exists": limit_exists,
                "infinite": is_infinite,
                "expression": expression,
                "variables": variables,
                "approach_point": [str(val) for val in approach_values],
                "substitution_order": substitution_order,
                "latex": sp.latex(final_result),
                "note": "This is a sequential limit calculation. True multivariable limits may differ.",
            }

        except Exception as e:
            raise ComputationError(f"Multivariable limit calculation failed: {str(e)}")

    async def sequential_limit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate limit of a sequence.

        Args:
            params: Dictionary containing 'sequence_expression', 'variable' (usually 'n')

        Returns:
            Dictionary with sequential limit result
        """
        sequence_expression = params.get("sequence_expression")
        variable = params.get("variable", "n")

        if not sequence_expression:
            raise ValidationError("Sequence expression is required for sequential limit")

        try:
            # Calculate limit as n approaches infinity
            result = await self.calculate_limit(
                {
                    "expression": sequence_expression,
                    "variable": variable,
                    "approach_value": "inf",
                    "direction": "both",
                }
            )

            # Determine convergence
            limit_value = result["limit"]
            converges = result["exists"] and not result["infinite"]

            # Calculate first few terms for context
            expr = self._validate_expression(sequence_expression)
            var = self._validate_variable(variable)

            first_terms = []
            for n in range(1, 11):  # First 10 terms
                try:
                    term_value = float(expr.subs(var, n))
                    first_terms.append({"n": n, "value": term_value})
                except:
                    break

            return {
                "sequential_limit": limit_value,
                "converges": converges,
                "diverges": not converges,
                "sequence_expression": sequence_expression,
                "variable": variable,
                "first_terms": first_terms,
                "numerical_value": result.get("numerical_value"),
                "latex": result.get("latex"),
            }

        except Exception as e:
            raise ComputationError(f"Sequential limit calculation failed: {str(e)}")
