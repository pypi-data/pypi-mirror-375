"""Integrals service for symbolic and numerical integration."""

from typing import Any, Dict, Tuple, Union

import numpy as np
import sympy as sp
from scipy import integrate as scipy_integrate
from sympy.parsing.sympy_parser import parse_expr

from ...core.errors.exceptions import ComputationError, ValidationError
from ..base import BaseService


class IntegralsService(BaseService):
    """Service for integration calculations."""

    def __init__(self, config=None, cache=None):
        """Initialize integrals service."""
        super().__init__(config, cache)

    async def process(self, operation: str, params: Dict[str, Any]) -> Any:
        """Process integration operation.

        Args:
            operation: Name of the integration operation
            params: Parameters for the operation

        Returns:
            Result of the integration operation
        """
        operation_map = {
            "symbolic": self.symbolic_integral,
            "definite": self.definite_integral,
            "numerical": self.numerical_integral,
            "improper": self.improper_integral,
            "multiple": self.multiple_integral,
            "line": self.line_integral,
            "surface": self.surface_integral,
        }

        if operation not in operation_map:
            raise ValidationError(f"Unknown integration operation: {operation}")

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

    def _validate_numeric_bounds(
        self, lower: Union[float, int, str], upper: Union[float, int, str]
    ) -> Tuple[Union[float, Any], Union[float, Any]]:
        """Validate and convert integration bounds."""
        try:
            # Handle symbolic bounds
            if isinstance(lower, str):
                if lower.lower() in ["-inf", "-infinity"]:
                    lower_bound = -sp.oo
                elif lower.lower() in ["inf", "infinity"]:
                    lower_bound = sp.oo
                else:
                    lower_bound = float(lower)
            else:
                lower_bound = float(lower)

            if isinstance(upper, str):
                if upper.lower() in ["-inf", "-infinity"]:
                    upper_bound = -sp.oo
                elif upper.lower() in ["inf", "infinity"]:
                    upper_bound = sp.oo
                else:
                    upper_bound = float(upper)
            else:
                upper_bound = float(upper)

            return lower_bound, upper_bound

        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid integration bounds: {e}")

    async def symbolic_integral(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate symbolic integral (indefinite or definite).

        Args:
            params: Dictionary containing 'expression', 'variable', and optional bounds

        Returns:
            Dictionary with integral result and metadata
        """
        expression = params.get("expression")
        variable = params.get("variable")
        lower_bound = params.get("lower_bound")
        upper_bound = params.get("upper_bound")

        if not expression:
            raise ValidationError("Expression is required for integration")

        if not variable:
            raise ValidationError("Variable is required for integration")

        try:
            # Parse expression and variable
            expr = self._validate_expression(expression)
            var = self._validate_variable(variable)

            # Check if variable exists in expression
            if var not in expr.free_symbols:
                # If variable doesn't appear, integral is expression * variable
                if lower_bound is not None and upper_bound is not None:
                    lower_val, upper_val = self._validate_numeric_bounds(lower_bound, upper_bound)
                    if sp.oo in [lower_val, upper_val] or -sp.oo in [lower_val, upper_val]:
                        result = sp.oo if expr > 0 else -sp.oo if expr < 0 else 0
                    else:
                        result = expr * (upper_val - lower_val)
                else:
                    result = expr * var

                # Add numerical value for definite integrals
                numerical_value = None
                if lower_bound is not None and upper_bound is not None:
                    try:
                        numerical_value = float(result.evalf()) if result.is_real else complex(result.evalf())
                    except:
                        numerical_value = None

                return {
                    "integral": str(result),
                    "numerical_value": numerical_value,
                    "original_expression": expression,
                    "variable": variable,
                    "definite": lower_bound is not None and upper_bound is not None,
                    "bounds": [lower_bound, upper_bound] if lower_bound is not None else None,
                    "latex": sp.latex(result),
                }

            # Calculate integral
            if lower_bound is not None and upper_bound is not None:
                # Definite integral
                lower_val, upper_val = self._validate_numeric_bounds(lower_bound, upper_bound)

                try:
                    integral_result = sp.integrate(expr, (var, lower_val, upper_val))

                    # Try to evaluate numerically if result contains unevaluated integrals
                    if integral_result.has(sp.Integral):
                        numerical_result = float(integral_result.evalf())
                        return {
                            "integral": str(integral_result),
                            "numerical_value": numerical_result,
                            "original_expression": expression,
                            "variable": variable,
                            "definite": True,
                            "bounds": [lower_bound, upper_bound],
                            "latex": sp.latex(integral_result),
                            "convergent": not (
                                sp.oo in [integral_result] or -sp.oo in [integral_result]
                            ),
                        }
                    else:
                        # Evaluate the result
                        evaluated = integral_result.evalf()

                        return {
                            "integral": str(integral_result),
                            "numerical_value": float(evaluated)
                            if evaluated.is_real
                            else complex(evaluated),
                            "original_expression": expression,
                            "variable": variable,
                            "definite": True,
                            "bounds": [lower_bound, upper_bound],
                            "latex": sp.latex(integral_result),
                            "convergent": integral_result.is_finite,
                        }

                except Exception:
                    # Fall back to numerical integration for definite integrals
                    return await self.numerical_integral(
                        {
                            "expression": expression,
                            "variable": variable,
                            "lower_bound": lower_bound,
                            "upper_bound": upper_bound,
                            "fallback_from_symbolic": True,
                        }
                    )
            else:
                # Indefinite integral
                integral_result = sp.integrate(expr, var)

                # Add constant of integration
                C = sp.Symbol("C")
                result_with_constant = integral_result + C

                return {
                    "integral": str(result_with_constant),
                    "without_constant": str(integral_result),
                    "original_expression": expression,
                    "variable": variable,
                    "definite": False,
                    "latex": sp.latex(result_with_constant),
                }

        except Exception as e:
            raise ComputationError(f"Symbolic integration failed: {str(e)}")

    async def definite_integral(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate definite integral with bounds.

        Args:
            params: Dictionary containing 'expression', 'variable', 'lower_bound', 'upper_bound'

        Returns:
            Dictionary with definite integral result
        """
        expression = params.get("expression")
        variable = params.get("variable")

        # Support both parameter naming conventions
        lower_bound = params.get("lower_bound") or params.get("lower_limit")
        upper_bound = params.get("upper_bound") or params.get("upper_limit")

        if lower_bound is None or upper_bound is None:
            raise ValidationError(
                "Both lower_bound/lower_limit and upper_bound/upper_limit are required for definite integral"
            )

        # Use symbolic integral with bounds
        return await self.symbolic_integral(
            {
                "expression": expression,
                "variable": variable,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
            }
        )

    async def numerical_integral(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate numerical integral using scipy.

        Args:
            params: Dictionary containing integration parameters

        Returns:
            Dictionary with numerical integral result
        """
        expression = params.get("expression")
        variable = params.get("variable")
        lower_bound = params.get("lower_bound")
        upper_bound = params.get("upper_bound")
        method = params.get("method", "quad")
        tolerance = params.get("tolerance", 1e-8)
        fallback_from_symbolic = params.get("fallback_from_symbolic", False)

        if not expression:
            raise ValidationError("Expression is required for numerical integration")

        if not variable:
            raise ValidationError("Variable is required for numerical integration")

        if lower_bound is None or upper_bound is None:
            raise ValidationError("Both bounds are required for numerical integration")

        try:
            # Parse expression and create numerical function
            expr = self._validate_expression(expression)
            var = self._validate_variable(variable)

            # Create numerical function
            func = sp.lambdify(var, expr, "numpy")

            # Convert bounds to float (handle infinity)
            if isinstance(lower_bound, str) and lower_bound.lower() in ["-inf", "-infinity"]:
                lower_val = -np.inf
            elif isinstance(lower_bound, str) and lower_bound.lower() in ["inf", "infinity"]:
                lower_val = np.inf
            else:
                lower_val = float(lower_bound)

            if isinstance(upper_bound, str) and upper_bound.lower() in ["-inf", "-infinity"]:
                upper_val = -np.inf
            elif isinstance(upper_bound, str) and upper_bound.lower() in ["inf", "infinity"]:
                upper_val = np.inf
            else:
                upper_val = float(upper_bound)

            # Choose integration method
            if method == "quad":
                result, error = scipy_integrate.quad(func, lower_val, upper_val, epsabs=tolerance)
            elif method == "romberg":
                if np.isinf(lower_val) or np.isinf(upper_val):
                    raise ValidationError("Romberg method cannot handle infinite bounds")
                result = scipy_integrate.romberg(func, lower_val, upper_val, tol=tolerance)
                error = None
            elif method == "simpson":
                if np.isinf(lower_val) or np.isinf(upper_val):
                    raise ValidationError("Simpson's method cannot handle infinite bounds")
                # Create points for Simpson's rule
                n_points = params.get("n_points", 1001)  # Must be odd
                if n_points % 2 == 0:
                    n_points += 1
                x = np.linspace(lower_val, upper_val, n_points)
                y = func(x)
                result = scipy_integrate.simpson(y, x)
                error = None
            else:
                raise ValidationError(f"Unknown integration method: {method}")

            return {
                "numerical_integral": result,
                "error_estimate": error,
                "method": method,
                "tolerance": tolerance,
                "bounds": [lower_bound, upper_bound],
                "expression": expression,
                "variable": variable,
                "fallback_from_symbolic": fallback_from_symbolic,
            }

        except Exception as e:
            raise ComputationError(f"Numerical integration failed: {str(e)}")

    async def improper_integral(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate improper integral with infinite bounds or discontinuities.

        Args:
            params: Dictionary containing integration parameters

        Returns:
            Dictionary with improper integral result
        """
        expression = params.get("expression")
        variable = params.get("variable")
        lower_bound = params.get("lower_bound")
        upper_bound = params.get("upper_bound")

        if not expression:
            raise ValidationError("Expression is required for improper integral")

        if not variable:
            raise ValidationError("Variable is required for improper integral")

        # Check if bounds are infinite
        has_infinite_bounds = False
        if isinstance(lower_bound, str) and lower_bound.lower() in [
            "-inf",
            "-infinity",
            "inf",
            "infinity",
        ]:
            has_infinite_bounds = True
        if isinstance(upper_bound, str) and upper_bound.lower() in [
            "-inf",
            "-infinity",
            "inf",
            "infinity",
        ]:
            has_infinite_bounds = True

        if not has_infinite_bounds:
            raise ValidationError("Improper integrals require at least one infinite bound")

        try:
            # Try symbolic integration first
            symbolic_result = await self.symbolic_integral(
                {
                    "expression": expression,
                    "variable": variable,
                    "lower_bound": lower_bound,
                    "upper_bound": upper_bound,
                }
            )

            # Check convergence
            integral_value = symbolic_result.get("numerical_value")
            convergent = True

            if integral_value is not None:
                if np.isinf(integral_value) or np.isnan(integral_value):
                    convergent = False

            # Also try numerical integration
            try:
                numerical_result = await self.numerical_integral(
                    {
                        "expression": expression,
                        "variable": variable,
                        "lower_bound": lower_bound,
                        "upper_bound": upper_bound,
                        "method": "quad",
                    }
                )

                return {
                    "improper_integral": symbolic_result.get("integral"),
                    "symbolic_value": integral_value,
                    "numerical_value": numerical_result.get("numerical_integral"),
                    "numerical_error": numerical_result.get("error_estimate"),
                    "convergent": convergent
                    and not np.isinf(numerical_result.get("numerical_integral", 0)),
                    "bounds": [lower_bound, upper_bound],
                    "expression": expression,
                    "variable": variable,
                    "latex": symbolic_result.get("latex"),
                }

            except Exception:
                # Return symbolic result only
                return {
                    "improper_integral": symbolic_result.get("integral"),
                    "symbolic_value": integral_value,
                    "convergent": convergent,
                    "bounds": [lower_bound, upper_bound],
                    "expression": expression,
                    "variable": variable,
                    "latex": symbolic_result.get("latex"),
                }

        except Exception as e:
            raise ComputationError(f"Improper integral calculation failed: {str(e)}")

    async def multiple_integral(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate multiple integral (double, triple, etc.).

        Args:
            params: Dictionary containing integration parameters for multiple variables

        Returns:
            Dictionary with multiple integral result
        """
        expression = params.get("expression")
        integrations = params.get("integrations")  # List of {variable, lower_bound, upper_bound}

        if not expression:
            raise ValidationError("Expression is required for multiple integral")

        if not integrations or not isinstance(integrations, list):
            raise ValidationError("Integrations list is required for multiple integral")

        if len(integrations) < 2:
            raise ValidationError("At least 2 integrations are required for multiple integral")

        try:
            # Parse expression
            expr = self._validate_expression(expression)

            # Build integration sequence (innermost to outermost)
            current_expr = expr
            integration_order = []

            for integration in integrations:
                variable = integration.get("variable")
                lower_bound = integration.get("lower_bound")
                upper_bound = integration.get("upper_bound")

                if not variable:
                    raise ValidationError("Variable is required for each integration")

                var = self._validate_variable(variable)
                integration_order.append(
                    {
                        "variable": variable,
                        "symbol": var,
                        "lower_bound": lower_bound,
                        "upper_bound": upper_bound,
                    }
                )

            # Perform nested integration
            for integration in integration_order:
                var = integration["symbol"]
                lower_bound = integration["lower_bound"]
                upper_bound = integration["upper_bound"]

                if lower_bound is not None and upper_bound is not None:
                    # Definite integration
                    lower_val, upper_val = self._validate_numeric_bounds(lower_bound, upper_bound)
                    current_expr = sp.integrate(current_expr, (var, lower_val, upper_val))
                else:
                    # Indefinite integration
                    current_expr = sp.integrate(current_expr, var)

            # Evaluate result
            try:
                numerical_value = (
                    float(current_expr.evalf())
                    if current_expr.is_real
                    else complex(current_expr.evalf())
                )
            except:
                numerical_value = None

            return {
                "multiple_integral": str(current_expr),
                "numerical_value": numerical_value,
                "integration_order": [integ["variable"] for integ in integration_order],
                "expression": expression,
                "latex": sp.latex(current_expr),
            }

        except Exception as e:
            raise ComputationError(f"Multiple integral calculation failed: {str(e)}")

    async def line_integral(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate line integral along a parametric curve.

        Args:
            params: Dictionary containing vector field, parametric curve, and parameter bounds

        Returns:
            Dictionary with line integral result
        """
        vector_field = params.get("vector_field")  # List of component expressions
        parametric_curve = params.get("parametric_curve")  # List of parametric equations
        parameter = params.get("parameter", "t")
        lower_bound = params.get("lower_bound")
        upper_bound = params.get("upper_bound")

        if not vector_field or not isinstance(vector_field, list):
            raise ValidationError("Vector field components are required for line integral")

        if not parametric_curve or not isinstance(parametric_curve, list):
            raise ValidationError("Parametric curve equations are required for line integral")

        if len(vector_field) != len(parametric_curve):
            raise ValidationError("Vector field and parametric curve must have same dimension")

        if lower_bound is None or upper_bound is None:
            raise ValidationError("Parameter bounds are required for line integral")

        try:
            # Parse components
            t = self._validate_variable(parameter)

            # Parse vector field components
            F_components = []
            for component in vector_field:
                F_components.append(self._validate_expression(component))

            # Parse parametric curve
            curve_components = []
            for component in parametric_curve:
                curve_components.append(self._validate_expression(component))

            # Calculate derivatives of curve components
            curve_derivatives = []
            for component in curve_components:
                derivative = sp.diff(component, t)
                curve_derivatives.append(derivative)

            # Substitute parametric equations into vector field
            # Assume vector field is in terms of x, y, z (or x, y for 2D)
            if len(curve_components) == 2:
                x, y = sp.symbols("x y")
                substitutions = {x: curve_components[0], y: curve_components[1]}
            elif len(curve_components) == 3:
                x, y, z = sp.symbols("x y z")
                substitutions = {
                    x: curve_components[0],
                    y: curve_components[1],
                    z: curve_components[2],
                }
            else:
                raise ValidationError("Line integrals support 2D or 3D curves only")

            # Substitute and calculate dot product
            integrand_terms = []
            for i, F_comp in enumerate(F_components):
                F_substituted = F_comp.subs(substitutions)
                term = F_substituted * curve_derivatives[i]
                integrand_terms.append(term)

            integrand = sum(integrand_terms)

            # Integrate over parameter
            lower_val, upper_val = self._validate_numeric_bounds(lower_bound, upper_bound)
            result = sp.integrate(integrand, (t, lower_val, upper_val))

            # Evaluate numerically
            try:
                numerical_value = float(result.evalf())
            except:
                numerical_value = None

            return {
                "line_integral": str(result),
                "numerical_value": numerical_value,
                "integrand": str(integrand),
                "vector_field": vector_field,
                "parametric_curve": parametric_curve,
                "parameter": parameter,
                "bounds": [lower_bound, upper_bound],
                "latex": sp.latex(result),
            }

        except Exception as e:
            raise ComputationError(f"Line integral calculation failed: {str(e)}")

    async def surface_integral(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate surface integral over a parametric surface.

        Args:
            params: Dictionary containing scalar field, parametric surface, and parameter bounds

        Returns:
            Dictionary with surface integral result
        """
        scalar_field = params.get("scalar_field")
        parametric_surface = params.get("parametric_surface")  # List of 3 parametric equations
        parameters = params.get("parameters", ["u", "v"])
        u_bounds = params.get("u_bounds")  # [lower, upper]
        v_bounds = params.get("v_bounds")  # [lower, upper]

        if not scalar_field:
            raise ValidationError("Scalar field is required for surface integral")

        if not parametric_surface or len(parametric_surface) != 3:
            raise ValidationError("Parametric surface must have 3 components (x, y, z)")

        if not u_bounds or not v_bounds:
            raise ValidationError("Parameter bounds are required for surface integral")

        if len(parameters) != 2:
            raise ValidationError("Exactly 2 parameters are required for surface integral")

        try:
            # Parse parameters
            u, v = [self._validate_variable(param) for param in parameters]

            # Parse scalar field and surface
            f = self._validate_expression(scalar_field)
            surface_components = [self._validate_expression(comp) for comp in parametric_surface]

            # Calculate partial derivatives of surface
            r_u = [sp.diff(comp, u) for comp in surface_components]
            r_v = [sp.diff(comp, v) for comp in surface_components]

            # Calculate cross product r_u × r_v
            cross_product = [
                r_u[1] * r_v[2] - r_u[2] * r_v[1],  # i component
                r_u[2] * r_v[0] - r_u[0] * r_v[2],  # j component
                r_u[0] * r_v[1] - r_u[1] * r_v[0],  # k component
            ]

            # Calculate magnitude of cross product
            magnitude = sp.sqrt(sum(comp**2 for comp in cross_product))

            # Substitute surface equations into scalar field
            x, y, z = sp.symbols("x y z")
            substitutions = {
                x: surface_components[0],
                y: surface_components[1],
                z: surface_components[2],
            }
            f_substituted = f.subs(substitutions)

            # Create integrand
            integrand = f_substituted * magnitude

            # Integrate over both parameters
            u_lower, u_upper = self._validate_numeric_bounds(u_bounds[0], u_bounds[1])
            v_lower, v_upper = self._validate_numeric_bounds(v_bounds[0], v_bounds[1])

            result = sp.integrate(integrand, (u, u_lower, u_upper), (v, v_lower, v_upper))

            # Evaluate numerically
            try:
                numerical_value = float(result.evalf())
            except:
                numerical_value = None

            return {
                "surface_integral": str(result),
                "numerical_value": numerical_value,
                "integrand": str(integrand),
                "scalar_field": scalar_field,
                "parametric_surface": parametric_surface,
                "parameters": parameters,
                "u_bounds": u_bounds,
                "v_bounds": v_bounds,
                "latex": sp.latex(result),
            }

        except Exception as e:
            raise ComputationError(f"Surface integral calculation failed: {str(e)}")
