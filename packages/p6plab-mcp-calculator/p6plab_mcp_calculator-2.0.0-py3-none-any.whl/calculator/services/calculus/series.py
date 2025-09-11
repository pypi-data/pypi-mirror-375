"""Series service for series expansion and analysis."""

from typing import Any, Dict

import sympy as sp
from sympy.parsing.sympy_parser import parse_expr

from ...core.errors.exceptions import ComputationError, ValidationError
from ..base import BaseService


class SeriesService(BaseService):
    """Service for series calculations and expansions."""

    def __init__(self, config=None, cache=None):
        """Initialize series service."""
        super().__init__(config, cache)

    async def process(self, operation: str, params: Dict[str, Any]) -> Any:
        """Process series operation.

        Args:
            operation: Name of the series operation
            params: Parameters for the operation

        Returns:
            Result of the series operation
        """
        operation_map = {
            "taylor": self.taylor_series,
            "maclaurin": self.maclaurin_series,
            "laurent": self.laurent_series,
            "fourier": self.fourier_series,
            "power": self.power_series,
            "geometric": self.geometric_series,
            "convergence": self.test_convergence,
            "sum": self.series_sum,
        }

        if operation not in operation_map:
            raise ValidationError(f"Unknown series operation: {operation}")

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

    async def taylor_series(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Taylor series expansion.

        Args:
            params: Dictionary containing 'expression', 'variable', 'center', 'order'

        Returns:
            Dictionary with Taylor series result
        """
        expression = params.get("expression")
        variable = params.get("variable")
        center = params.get("center", 0)
        order = params.get("order", 5)

        if not expression:
            raise ValidationError("Expression is required for Taylor series")

        if not variable:
            raise ValidationError("Variable is required for Taylor series")

        if not isinstance(order, int) or order < 0:
            raise ValidationError("Order must be a non-negative integer")

        if order > 20:
            raise ValidationError("Order cannot exceed 20 for performance reasons")

        try:
            # Parse expression and variable
            expr = self._validate_expression(expression)
            var = self._validate_variable(variable)

            # Parse center
            if isinstance(center, str):
                center_val = parse_expr(center)
            else:
                center_val = center

            # Calculate Taylor series
            series_expansion = sp.series(expr, var, center_val, n=order + 1)

            # Remove O() term
            series_without_o = series_expansion.removeO()

            # Get individual terms
            terms = []
            series_poly = sp.Poly(series_without_o, var - center_val)

            for i in range(order + 1):
                try:
                    coeff = series_poly.nth(i)
                    if coeff != 0:
                        if i == 0:
                            term_expr = coeff
                        elif i == 1:
                            term_expr = coeff * (var - center_val)
                        else:
                            term_expr = coeff * (var - center_val) ** i

                        terms.append(
                            {
                                "power": i,
                                "coefficient": str(coeff),
                                "term": str(term_expr),
                                "latex": sp.latex(term_expr),
                            }
                        )
                except:
                    # Handle cases where coefficient extraction fails
                    pass

            # Calculate remainder term (Lagrange form)
            try:
                remainder_expr = sp.diff(expr, var, order + 1)
                remainder_term = f"R_{order + 1}(x) = f^({order + 1})(c) * (x - {center})^{order + 1} / {sp.factorial(order + 1)}!"
            except:
                remainder_term = f"R_{order + 1}(x) = O((x - {center})^{order + 1})"

            # Evaluate series at specific points for verification
            test_points = []
            if center_val == 0:  # Maclaurin series
                test_vals = [0.1, 0.5, 1.0]
            else:
                test_vals = [
                    float(center_val) + 0.1,
                    float(center_val) + 0.5,
                    float(center_val) + 1.0,
                ]

            for test_val in test_vals:
                try:
                    original_value = float(expr.subs(var, test_val))
                    series_value = float(series_without_o.subs(var, test_val))
                    error = abs(original_value - series_value)

                    test_points.append(
                        {
                            "x": test_val,
                            "original": original_value,
                            "series": series_value,
                            "error": error,
                        }
                    )
                except:
                    pass

            return {
                "taylor_series": str(series_without_o),
                "terms": terms,
                "expression": expression,
                "variable": variable,
                "center": str(center_val),
                "order": order,
                "remainder_term": remainder_term,
                "test_points": test_points,
                "latex": sp.latex(series_without_o),
            }

        except Exception as e:
            raise ComputationError(f"Taylor series calculation failed: {str(e)}")

    async def maclaurin_series(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Maclaurin series (Taylor series at center=0).

        Args:
            params: Dictionary containing series parameters

        Returns:
            Dictionary with Maclaurin series result
        """
        params["center"] = 0
        result = await self.taylor_series(params)
        result["series_type"] = "Maclaurin"
        return result

    async def laurent_series(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Laurent series expansion.

        Args:
            params: Dictionary containing 'expression', 'variable', 'center', 'order'

        Returns:
            Dictionary with Laurent series result
        """
        expression = params.get("expression")
        variable = params.get("variable")
        center = params.get("center", 0)
        order = params.get("order", 5)

        if not expression:
            raise ValidationError("Expression is required for Laurent series")

        if not variable:
            raise ValidationError("Variable is required for Laurent series")

        try:
            # Parse expression and variable
            expr = self._validate_expression(expression)
            var = self._validate_variable(variable)

            # Parse center
            if isinstance(center, str):
                center_val = parse_expr(center)
            else:
                center_val = center

            # Calculate Laurent series (includes negative powers)
            series_expansion = sp.series(expr, var, center_val, n=order + 1)

            # Extract terms including negative powers
            terms = []
            series_dict = series_expansion.as_leading_term(var).as_coeff_exponent(var)

            # Get all terms from the series
            series_expr = series_expansion.removeO()

            # Try to extract individual terms
            if series_expr.is_Add:
                for term in series_expr.args:
                    terms.append({"term": str(term), "latex": sp.latex(term)})
            else:
                terms.append({"term": str(series_expr), "latex": sp.latex(series_expr)})

            # Check for poles (negative powers)
            has_poles = any("-" in str(term) and "**" in str(term) for term in terms)

            return {
                "laurent_series": str(series_expr),
                "terms": terms,
                "expression": expression,
                "variable": variable,
                "center": str(center_val),
                "order": order,
                "has_poles": has_poles,
                "latex": sp.latex(series_expr),
            }

        except Exception as e:
            raise ComputationError(f"Laurent series calculation failed: {str(e)}")

    async def fourier_series(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Fourier series expansion.

        Args:
            params: Dictionary containing 'expression', 'variable', 'period', 'terms'

        Returns:
            Dictionary with Fourier series result
        """
        expression = params.get("expression")
        variable = params.get("variable", "x")
        period = params.get("period", 2 * sp.pi)
        n_terms = params.get("terms", 5)

        if not expression:
            raise ValidationError("Expression is required for Fourier series")

        try:
            # Parse expression and variable
            expr = self._validate_expression(expression)
            var = self._validate_variable(variable)

            # Calculate Fourier coefficients
            L = period / 2  # Half period

            # a0 coefficient
            a0 = (1 / L) * sp.integrate(expr, (var, -L, L))

            # an and bn coefficients
            fourier_terms = []
            fourier_terms.append(
                {
                    "type": "constant",
                    "coefficient": str(a0 / 2),
                    "term": str(a0 / 2),
                    "latex": sp.latex(a0 / 2),
                }
            )

            series_sum = a0 / 2

            for n in range(1, n_terms + 1):
                # an coefficient
                an_integrand = expr * sp.cos(n * sp.pi * var / L)
                an = (1 / L) * sp.integrate(an_integrand, (var, -L, L))

                # bn coefficient
                bn_integrand = expr * sp.sin(n * sp.pi * var / L)
                bn = (1 / L) * sp.integrate(bn_integrand, (var, -L, L))

                # Add cosine term if an != 0
                if an != 0:
                    cos_term = an * sp.cos(n * sp.pi * var / L)
                    fourier_terms.append(
                        {
                            "type": "cosine",
                            "n": n,
                            "coefficient": str(an),
                            "term": str(cos_term),
                            "latex": sp.latex(cos_term),
                        }
                    )
                    series_sum += cos_term

                # Add sine term if bn != 0
                if bn != 0:
                    sin_term = bn * sp.sin(n * sp.pi * var / L)
                    fourier_terms.append(
                        {
                            "type": "sine",
                            "n": n,
                            "coefficient": str(bn),
                            "term": str(sin_term),
                            "latex": sp.latex(sin_term),
                        }
                    )
                    series_sum += sin_term

            return {
                "fourier_series": str(series_sum),
                "terms": fourier_terms,
                "a0": str(a0),
                "expression": expression,
                "variable": variable,
                "period": str(period),
                "n_terms": n_terms,
                "latex": sp.latex(series_sum),
            }

        except Exception as e:
            raise ComputationError(f"Fourier series calculation failed: {str(e)}")

    async def power_series(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze power series.

        Args:
            params: Dictionary containing 'coefficients', 'variable', 'center'

        Returns:
            Dictionary with power series analysis
        """
        coefficients = params.get("coefficients")
        variable = params.get("variable", "x")
        center = params.get("center", 0)

        if not coefficients or not isinstance(coefficients, list):
            raise ValidationError("Coefficients list is required for power series")

        try:
            # Parse variable and center
            var = self._validate_variable(variable)

            if isinstance(center, str):
                center_val = parse_expr(center)
            else:
                center_val = center

            # Build power series
            series_terms = []
            series_expr = 0

            for n, coeff in enumerate(coefficients):
                if coeff != 0:
                    if n == 0:
                        term = coeff
                    elif n == 1:
                        term = coeff * (var - center_val)
                    else:
                        term = coeff * (var - center_val) ** n

                    series_terms.append(
                        {
                            "power": n,
                            "coefficient": str(coeff),
                            "term": str(term),
                            "latex": sp.latex(term),
                        }
                    )

                    series_expr += term

            # Calculate radius of convergence using ratio test
            radius_of_convergence = None
            try:
                # Ratio test: R = lim |a_n / a_{n+1}|
                non_zero_coeffs = [c for c in coefficients if c != 0]
                if len(non_zero_coeffs) >= 2:
                    ratios = []
                    for i in range(len(non_zero_coeffs) - 1):
                        if non_zero_coeffs[i + 1] != 0:
                            ratio = abs(non_zero_coeffs[i] / non_zero_coeffs[i + 1])
                            ratios.append(ratio)

                    if ratios:
                        # Take the limit of ratios (simplified approach)
                        radius_of_convergence = ratios[-1]  # Last ratio as approximation
            except:
                pass

            # Calculate interval of convergence
            interval_of_convergence = None
            if radius_of_convergence is not None:
                if center_val == 0:
                    interval_of_convergence = (
                        f"(-{radius_of_convergence}, {radius_of_convergence})"
                    )
                else:
                    left = center_val - radius_of_convergence
                    right = center_val + radius_of_convergence
                    interval_of_convergence = f"({left}, {right})"

            return {
                "power_series": str(series_expr),
                "terms": series_terms,
                "coefficients": coefficients,
                "variable": variable,
                "center": str(center_val),
                "radius_of_convergence": radius_of_convergence,
                "interval_of_convergence": interval_of_convergence,
                "latex": sp.latex(series_expr),
            }

        except Exception as e:
            raise ComputationError(f"Power series analysis failed: {str(e)}")

    async def geometric_series(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze geometric series.

        Args:
            params: Dictionary containing 'first_term', 'common_ratio'

        Returns:
            Dictionary with geometric series analysis
        """
        first_term = params.get("first_term")
        common_ratio = params.get("common_ratio")
        n_terms = params.get("n_terms")

        if first_term is None:
            raise ValidationError("First term is required for geometric series")

        if common_ratio is None:
            raise ValidationError("Common ratio is required for geometric series")

        try:
            a = float(first_term)
            r = float(common_ratio)

            # Check convergence
            converges = abs(r) < 1

            # Calculate sum if convergent
            infinite_sum = None
            if converges:
                infinite_sum = a / (1 - r)

            # Calculate partial sum if n_terms specified
            partial_sum = None
            if n_terms is not None:
                n = int(n_terms)
                if r == 1:
                    partial_sum = a * n
                else:
                    partial_sum = a * (1 - r**n) / (1 - r)

            # Generate first few terms
            terms = []
            for i in range(min(10, n_terms if n_terms else 10)):
                term_value = a * (r**i)
                terms.append(
                    {
                        "n": i,
                        "term": term_value,
                        "expression": f"{a} * {r}^{i}" if i > 0 else str(a),
                    }
                )

            return {
                "first_term": a,
                "common_ratio": r,
                "converges": converges,
                "diverges": not converges,
                "infinite_sum": infinite_sum,
                "partial_sum": partial_sum,
                "n_terms": n_terms,
                "terms": terms,
                "series_formula": f"{a} + {a}*{r} + {a}*{r}^2 + {a}*{r}^3 + ...",
            }

        except Exception as e:
            raise ComputationError(f"Geometric series analysis failed: {str(e)}")

    async def test_convergence(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Test series convergence using various tests.

        Args:
            params: Dictionary containing 'series_terms' or 'general_term'

        Returns:
            Dictionary with convergence test results
        """
        series_terms = params.get("series_terms")
        general_term = params.get("general_term")
        variable = params.get("variable", "n")

        if not series_terms and not general_term:
            raise ValidationError("Either series_terms or general_term is required")

        try:
            test_results = {}

            if general_term:
                # Parse general term
                expr = self._validate_expression(general_term)
                var = self._validate_variable(variable)

                # Ratio test
                try:
                    next_term = expr.subs(var, var + 1)
                    ratio = sp.limit(sp.Abs(next_term / expr), var, sp.oo)

                    if ratio < 1:
                        ratio_result = "Convergent"
                    elif ratio > 1:
                        ratio_result = "Divergent"
                    else:
                        ratio_result = "Inconclusive"

                    test_results["ratio_test"] = {"limit": str(ratio), "result": ratio_result}
                except:
                    test_results["ratio_test"] = {"result": "Failed"}

                # Root test
                try:
                    root_limit = sp.limit((sp.Abs(expr)) ** (1 / var), var, sp.oo)

                    if root_limit < 1:
                        root_result = "Convergent"
                    elif root_limit > 1:
                        root_result = "Divergent"
                    else:
                        root_result = "Inconclusive"

                    test_results["root_test"] = {"limit": str(root_limit), "result": root_result}
                except:
                    test_results["root_test"] = {"result": "Failed"}

                # Integral test (for positive decreasing functions)
                try:
                    # Check if function is positive and decreasing
                    derivative = sp.diff(expr, var)

                    # Try to integrate from 1 to infinity
                    integral_result = sp.integrate(expr, (var, 1, sp.oo))

                    if integral_result.is_finite:
                        integral_test_result = "Convergent"
                    else:
                        integral_test_result = "Divergent"

                    test_results["integral_test"] = {
                        "integral": str(integral_result),
                        "result": integral_test_result,
                    }
                except:
                    test_results["integral_test"] = {"result": "Failed"}

            if series_terms:
                # Direct analysis of given terms
                terms = [float(term) for term in series_terms]

                # Check if terms approach zero
                last_terms = terms[-5:] if len(terms) >= 5 else terms
                approaching_zero = all(
                    abs(term) < abs(prev_term)
                    for term, prev_term in zip(last_terms[1:], last_terms[:-1])
                )

                test_results["term_test"] = {
                    "terms_approach_zero": approaching_zero,
                    "last_term": terms[-1] if terms else None,
                }

            return {
                "convergence_tests": test_results,
                "general_term": general_term,
                "series_terms": series_terms,
                "variable": variable,
            }

        except Exception as e:
            raise ComputationError(f"Convergence test failed: {str(e)}")

    async def series_sum(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate sum of a series.

        Args:
            params: Dictionary containing 'general_term', 'variable', 'start', 'end'

        Returns:
            Dictionary with series sum result
        """
        general_term = params.get("general_term")
        variable = params.get("variable", "n")
        start = params.get("start", 1)
        end = params.get("end")  # None for infinite series

        if not general_term:
            raise ValidationError("General term is required for series sum")

        try:
            # Parse general term and variable
            expr = self._validate_expression(general_term)
            var = self._validate_variable(variable)

            # Calculate sum
            if end is None:
                # Infinite series
                try:
                    series_sum = sp.Sum(expr, (var, start, sp.oo))
                    evaluated_sum = series_sum.doit()

                    # Try to get numerical value
                    numerical_value = None
                    if evaluated_sum.is_number:
                        try:
                            numerical_value = float(evaluated_sum.evalf())
                        except:
                            pass

                    return {
                        "series_sum": str(evaluated_sum),
                        "numerical_value": numerical_value,
                        "general_term": general_term,
                        "variable": variable,
                        "start": start,
                        "end": "infinity",
                        "latex": sp.latex(evaluated_sum),
                    }

                except Exception:
                    # If symbolic sum fails, try numerical approximation
                    partial_sum = 0
                    for n in range(start, start + 1000):  # Sum first 1000 terms
                        term_value = float(expr.subs(var, n))
                        partial_sum += term_value

                        # Check for convergence
                        if abs(term_value) < 1e-10:
                            break

                    return {
                        "series_sum": "Numerical approximation",
                        "numerical_value": partial_sum,
                        "general_term": general_term,
                        "variable": variable,
                        "start": start,
                        "end": "infinity",
                        "note": "Approximated using first 1000 terms",
                    }
            else:
                # Finite series
                series_sum = sp.Sum(expr, (var, start, end))
                evaluated_sum = series_sum.doit()

                # Calculate numerical value
                numerical_value = float(evaluated_sum.evalf())

                return {
                    "series_sum": str(evaluated_sum),
                    "numerical_value": numerical_value,
                    "general_term": general_term,
                    "variable": variable,
                    "start": start,
                    "end": end,
                    "latex": sp.latex(evaluated_sum),
                }

        except Exception as e:
            raise ComputationError(f"Series sum calculation failed: {str(e)}")
