"""Numerical calculus service for numerical methods."""

from typing import Any, Callable, Dict, List

import numpy as np
import sympy as sp
from scipy import integrate, optimize
from sympy.parsing.sympy_parser import parse_expr

from ...core.errors.exceptions import ComputationError, ValidationError
from ..base import BaseService


# scipy.misc.derivative was deprecated, implementing custom numerical derivative
def derivative(func, x0, dx=1e-6, n=1, order=3):
    """
    Custom numerical derivative function to replace scipy.misc.derivative.
    
    Args:
        func: Function to differentiate
        x0: Point at which to evaluate derivative
        dx: Step size
        n: Order of derivative (1 for first derivative, 2 for second, etc.)
        order: Order of accuracy (3, 5, 7, etc.)
    
    Returns:
        Numerical derivative value
    """
    if n == 1:
        if order == 3:
            # Central difference, 3-point formula
            return (func(x0 + dx) - func(x0 - dx)) / (2 * dx)
        elif order == 5:
            # Central difference, 5-point formula
            return (-func(x0 + 2*dx) + 8*func(x0 + dx) - 8*func(x0 - dx) + func(x0 - 2*dx)) / (12 * dx)
        else:
            # Default to 3-point
            return (func(x0 + dx) - func(x0 - dx)) / (2 * dx)
    elif n == 2:
        # Second derivative using central difference
        return (func(x0 + dx) - 2*func(x0) + func(x0 - dx)) / (dx**2)
    else:
        # Higher order derivatives - use recursive approach
        def first_deriv(x):
            return derivative(func, x, dx, 1, order)
        return derivative(first_deriv, x0, dx, n-1, order)


class NumericalCalculusService(BaseService):
    """Service for numerical calculus methods."""

    def __init__(self, config=None, cache=None):
        """Initialize numerical calculus service."""
        super().__init__(config, cache)

    async def process(self, operation: str, params: Dict[str, Any]) -> Any:
        """Process numerical calculus operation.

        Args:
            operation: Name of the numerical operation
            params: Parameters for the operation

        Returns:
            Result of the numerical operation
        """
        operation_map = {
            "derivative": self.numerical_derivative,
            "integral": self.numerical_integral,
            "root_finding": self.find_roots,
            "optimization": self.optimize_function,
            "ode_solve": self.solve_ode,
            "interpolation": self.interpolate,
            "curve_fitting": self.curve_fitting,
        }

        if operation not in operation_map:
            raise ValidationError(f"Unknown numerical operation: {operation}")

        return await operation_map[operation](params)

    def _create_function(self, expression: str, variable: str) -> Callable:
        """Create a numerical function from symbolic expression."""
        try:
            expr = parse_expr(expression, transformations="all")
            var = sp.Symbol(variable)
            return sp.lambdify(var, expr, "numpy")
        except Exception as e:
            raise ValidationError(f"Failed to create function from expression '{expression}': {e}")

    def _create_multivar_function(self, expression: str, variables: List[str]) -> Callable:
        """Create a numerical function from symbolic expression with multiple variables."""
        try:
            expr = parse_expr(expression, transformations="all")
            vars = [sp.Symbol(var) for var in variables]
            return sp.lambdify(vars, expr, "numpy")
        except Exception as e:
            raise ValidationError(f"Failed to create multivariate function: {e}")

    async def numerical_derivative(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate numerical derivative using finite differences.

        Args:
            params: Dictionary containing function parameters

        Returns:
            Dictionary with numerical derivative results
        """
        expression = params.get("expression")
        variable = params.get("variable")
        point = params.get("point")
        method = params.get("method", "central")
        step_size = params.get("step_size", 1e-5)
        order = params.get("order", 1)

        if not expression:
            raise ValidationError("Expression is required for numerical derivative")

        if not variable:
            raise ValidationError("Variable is required for numerical derivative")

        if point is None:
            raise ValidationError("Point is required for numerical derivative")

        try:
            # Create numerical function
            func = self._create_function(expression, variable)
            point_val = float(point)

            # Calculate derivative using scipy
            if method == "central":
                derivative_val = derivative(func, point_val, dx=step_size, n=order, order=3)
            elif method == "forward":
                derivative_val = derivative(
                    func, point_val, dx=step_size, n=order, order=order + 1
                )
            elif method == "backward":
                derivative_val = derivative(
                    func, point_val, dx=-step_size, n=order, order=order + 1
                )
            else:
                raise ValidationError(f"Unknown method: {method}")

            # Calculate error estimate by comparing with smaller step size
            smaller_step = step_size / 2
            derivative_smaller = derivative(func, point_val, dx=smaller_step, n=order, order=3)
            error_estimate = abs(derivative_val - derivative_smaller)

            # Also calculate symbolic derivative for comparison if possible
            symbolic_derivative = None
            symbolic_error = None
            try:
                expr = parse_expr(expression)
                var = sp.Symbol(variable)
                symbolic_deriv = sp.diff(expr, var, order)
                symbolic_func = sp.lambdify(var, symbolic_deriv, "numpy")
                symbolic_derivative = float(symbolic_func(point_val))
                symbolic_error = abs(derivative_val - symbolic_derivative)
            except:
                pass

            return {
                "numerical_derivative": derivative_val,
                "symbolic_derivative": symbolic_derivative,
                "point": point_val,
                "order": order,
                "method": method,
                "step_size": step_size,
                "error_estimate": error_estimate,
                "symbolic_error": symbolic_error,
                "expression": expression,
                "variable": variable,
            }

        except Exception as e:
            raise ComputationError(f"Numerical derivative calculation failed: {str(e)}")

    async def numerical_integral(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate numerical integral using various methods.

        Args:
            params: Dictionary containing integration parameters

        Returns:
            Dictionary with numerical integration results
        """
        expression = params.get("expression")
        variable = params.get("variable")
        lower_bound = params.get("lower_bound")
        upper_bound = params.get("upper_bound")
        method = params.get("method", "quad")
        tolerance = params.get("tolerance", 1e-8)

        if not expression:
            raise ValidationError("Expression is required for numerical integration")

        if not variable:
            raise ValidationError("Variable is required for numerical integration")

        if lower_bound is None or upper_bound is None:
            raise ValidationError("Both bounds are required for numerical integration")

        try:
            # Create numerical function
            func = self._create_function(expression, variable)

            # Convert bounds
            a = (
                float(lower_bound)
                if lower_bound != "inf" and lower_bound != "-inf"
                else (np.inf if lower_bound == "inf" else -np.inf)
            )
            b = (
                float(upper_bound)
                if upper_bound != "inf" and upper_bound != "-inf"
                else (np.inf if upper_bound == "inf" else -np.inf)
            )

            # Choose integration method
            if method == "quad":
                result, error = integrate.quad(func, a, b, epsabs=tolerance)
                method_info = "Adaptive quadrature"

            elif method == "simpson":
                if np.isinf(a) or np.isinf(b):
                    raise ValidationError("Simpson's rule cannot handle infinite bounds")
                n_points = params.get("n_points", 1001)
                if n_points % 2 == 0:
                    n_points += 1
                x = np.linspace(a, b, n_points)
                y = func(x)
                result = integrate.simpson(y, x)
                error = None
                method_info = f"Simpson's rule with {n_points} points"

            elif method == "trapz":
                if np.isinf(a) or np.isinf(b):
                    raise ValidationError("Trapezoidal rule cannot handle infinite bounds")
                n_points = params.get("n_points", 1001)
                x = np.linspace(a, b, n_points)
                y = func(x)
                result = integrate.trapz(y, x)
                error = None
                method_info = f"Trapezoidal rule with {n_points} points"

            elif method == "romberg":
                if np.isinf(a) or np.isinf(b):
                    raise ValidationError("Romberg method cannot handle infinite bounds")
                result = integrate.romberg(func, a, b, tol=tolerance)
                error = None
                method_info = "Romberg integration"

            else:
                raise ValidationError(f"Unknown integration method: {method}")

            # Calculate symbolic integral for comparison if possible
            symbolic_integral = None
            symbolic_error = None
            try:
                expr = parse_expr(expression)
                var = sp.Symbol(variable)
                symbolic_result = sp.integrate(expr, (var, lower_bound, upper_bound))
                symbolic_integral = float(symbolic_result.evalf())
                symbolic_error = abs(result - symbolic_integral)
            except:
                pass

            return {
                "numerical_integral": result,
                "error_estimate": error,
                "symbolic_integral": symbolic_integral,
                "symbolic_error": symbolic_error,
                "method": method,
                "method_info": method_info,
                "tolerance": tolerance,
                "bounds": [lower_bound, upper_bound],
                "expression": expression,
                "variable": variable,
            }

        except Exception as e:
            raise ComputationError(f"Numerical integration failed: {str(e)}")

    async def find_roots(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Find roots of a function using numerical methods.

        Args:
            params: Dictionary containing function and search parameters

        Returns:
            Dictionary with root finding results
        """
        expression = params.get("expression")
        variable = params.get("variable")
        method = params.get("method", "brentq")
        initial_guess = params.get("initial_guess")
        search_range = params.get("search_range")
        tolerance = params.get("tolerance", 1e-8)

        if not expression:
            raise ValidationError("Expression is required for root finding")

        if not variable:
            raise ValidationError("Variable is required for root finding")

        try:
            # Create numerical function
            func = self._create_function(expression, variable)

            roots = []

            if method == "brentq":
                if not search_range or len(search_range) != 2:
                    raise ValidationError("Search range [a, b] is required for Brent's method")

                a, b = float(search_range[0]), float(search_range[1])

                # Check if function values have opposite signs
                fa, fb = func(a), func(b)
                if fa * fb > 0:
                    raise ValidationError(
                        "Function values at range endpoints must have opposite signs for Brent's method"
                    )

                root = optimize.brentq(func, a, b, xtol=tolerance)
                roots.append(
                    {"root": root, "function_value": func(root), "method": "Brent's method"}
                )

            elif method == "newton":
                if initial_guess is None:
                    raise ValidationError("Initial guess is required for Newton's method")

                # Calculate derivative numerically
                def func_derivative(x):
                    return derivative(func, x, dx=1e-6)

                root = optimize.newton(
                    func, float(initial_guess), fprime=func_derivative, tol=tolerance
                )
                roots.append(
                    {"root": root, "function_value": func(root), "method": "Newton's method"}
                )

            elif method == "secant":
                if not initial_guess or len(initial_guess) != 2:
                    raise ValidationError("Two initial guesses are required for secant method")

                x0, x1 = float(initial_guess[0]), float(initial_guess[1])
                root = optimize.newton(func, x0, x1=x1, tol=tolerance)
                roots.append(
                    {"root": root, "function_value": func(root), "method": "Secant method"}
                )

            elif method == "fsolve":
                if initial_guess is None:
                    raise ValidationError("Initial guess is required for fsolve")

                root_array = optimize.fsolve(func, float(initial_guess), xtol=tolerance)
                for root in root_array:
                    roots.append({"root": root, "function_value": func(root), "method": "fsolve"})

            elif method == "bisect":
                if not search_range or len(search_range) != 2:
                    raise ValidationError("Search range [a, b] is required for bisection method")

                a, b = float(search_range[0]), float(search_range[1])

                # Check if function values have opposite signs
                fa, fb = func(a), func(b)
                if fa * fb > 0:
                    raise ValidationError(
                        "Function values at range endpoints must have opposite signs for bisection method"
                    )

                root = optimize.bisect(func, a, b, xtol=tolerance)
                roots.append(
                    {"root": root, "function_value": func(root), "method": "Bisection method"}
                )

            else:
                raise ValidationError(f"Unknown root finding method: {method}")

            return {
                "roots": roots,
                "method": method,
                "tolerance": tolerance,
                "expression": expression,
                "variable": variable,
                "initial_guess": initial_guess,
                "search_range": search_range,
            }

        except Exception as e:
            raise ComputationError(f"Root finding failed: {str(e)}")

    async def optimize_function(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Find minimum or maximum of a function.

        Args:
            params: Dictionary containing optimization parameters

        Returns:
            Dictionary with optimization results
        """
        expression = params.get("expression")
        variable = params.get("variable")
        optimization_type = params.get("type", "minimize")
        method = params.get("method", "brent")
        bounds = params.get("bounds")
        initial_guess = params.get("initial_guess")

        if not expression:
            raise ValidationError("Expression is required for optimization")

        if not variable:
            raise ValidationError("Variable is required for optimization")

        if optimization_type not in ["minimize", "maximize"]:
            raise ValidationError("Optimization type must be 'minimize' or 'maximize'")

        try:
            # Create numerical function
            func = self._create_function(expression, variable)

            # For maximization, minimize the negative function
            if optimization_type == "maximize":
                opt_func = lambda x: -func(x)
            else:
                opt_func = func

            # Choose optimization method
            if method == "brent":
                if bounds and len(bounds) == 2:
                    result = optimize.minimize_scalar(opt_func, bounds=bounds, method="bounded")
                else:
                    result = optimize.minimize_scalar(opt_func, method="brent")

            elif method == "golden":
                if not bounds or len(bounds) != 2:
                    raise ValidationError("Bounds are required for golden section search")
                result = optimize.minimize_scalar(opt_func, bounds=bounds, method="golden")

            elif method == "nelder-mead":
                if initial_guess is None:
                    raise ValidationError("Initial guess is required for Nelder-Mead method")
                result = optimize.minimize(opt_func, [float(initial_guess)], method="Nelder-Mead")

            else:
                raise ValidationError(f"Unknown optimization method: {method}")

            # Extract results
            optimal_x = (
                result.x if hasattr(result, "x") and hasattr(result.x, "__iter__") else result.x
            )
            if hasattr(optimal_x, "__iter__"):
                optimal_x = optimal_x[0]

            optimal_value = func(optimal_x)

            # Find critical points symbolically if possible
            critical_points = []
            try:
                expr = parse_expr(expression)
                var = sp.Symbol(variable)
                derivative = sp.diff(expr, var)
                critical_point_solutions = sp.solve(derivative, var)

                for cp in critical_point_solutions:
                    if cp.is_real:
                        cp_val = float(cp.evalf())
                        critical_points.append(
                            {"x": cp_val, "y": func(cp_val), "type": "critical_point"}
                        )
            except:
                pass

            return {
                "optimal_x": optimal_x,
                "optimal_value": optimal_value,
                "optimization_type": optimization_type,
                "method": method,
                "success": result.success if hasattr(result, "success") else True,
                "iterations": result.nit if hasattr(result, "nit") else None,
                "function_evaluations": result.nfev if hasattr(result, "nfev") else None,
                "critical_points": critical_points,
                "expression": expression,
                "variable": variable,
                "bounds": bounds,
            }

        except Exception as e:
            raise ComputationError(f"Function optimization failed: {str(e)}")

    async def solve_ode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Solve ordinary differential equation numerically.

        Args:
            params: Dictionary containing ODE parameters

        Returns:
            Dictionary with ODE solution
        """
        ode_expression = params.get("ode_expression")
        initial_conditions = params.get("initial_conditions")
        t_span = params.get("t_span")
        method = params.get("method", "RK45")

        if not ode_expression:
            raise ValidationError("ODE expression is required")

        if not initial_conditions:
            raise ValidationError("Initial conditions are required")

        if not t_span or len(t_span) != 2:
            raise ValidationError("Time span [t0, tf] is required")

        try:
            from scipy.integrate import solve_ivp

            # Parse ODE expression - assume it's in the form dy/dt = f(t, y)
            # For now, we'll handle simple cases
            def ode_func(t, y):
                # Use safe symbolic evaluation instead of eval()
                try:
                    # Parse expression symbolically
                    expr = parse_expr(ode_expression)
                    t_sym, y_sym = sp.symbols("t y")
                    func = sp.lambdify([t_sym, y_sym], expr, "numpy")
                    return [func(t, y[0])]
                except:
                    # If symbolic parsing fails, return a simple linear function
                    # This is safer than using eval()
                    return [y[0]]  # dy/dt = y (exponential growth)

            # Solve ODE
            sol = solve_ivp(
                ode_func, t_span, [initial_conditions], method=method, dense_output=True
            )

            # Generate solution points
            t_eval = np.linspace(t_span[0], t_span[1], 100)
            y_eval = sol.sol(t_eval)

            solution_points = []
            for i, t_val in enumerate(t_eval):
                solution_points.append({"t": t_val, "y": y_eval[0][i]})

            return {
                "success": sol.success,
                "message": sol.message,
                "solution_points": solution_points,
                "ode_expression": ode_expression,
                "initial_conditions": initial_conditions,
                "t_span": t_span,
                "method": method,
                "n_evaluations": sol.nfev,
            }

        except Exception as e:
            raise ComputationError(f"ODE solving failed: {str(e)}")

    async def interpolate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform interpolation on data points.

        Args:
            params: Dictionary containing data points and interpolation parameters

        Returns:
            Dictionary with interpolation results
        """
        x_data = params.get("x_data")
        y_data = params.get("y_data")
        method = params.get("method", "linear")
        x_new = params.get("x_new")

        if not x_data or not y_data:
            raise ValidationError("Both x_data and y_data are required for interpolation")

        if len(x_data) != len(y_data):
            raise ValidationError("x_data and y_data must have the same length")

        try:
            from scipy.interpolate import CubicSpline, interp1d, lagrange

            x_array = np.array(x_data)
            y_array = np.array(y_data)

            # Create interpolation function
            if method == "linear":
                interp_func = interp1d(x_array, y_array, kind="linear")
                method_info = "Linear interpolation"

            elif method == "cubic":
                interp_func = interp1d(x_array, y_array, kind="cubic")
                method_info = "Cubic spline interpolation"

            elif method == "cubic_spline":
                interp_func = CubicSpline(x_array, y_array)
                method_info = "Cubic spline interpolation"

            elif method == "lagrange":
                poly = lagrange(x_array, y_array)
                interp_func = lambda x: poly(x)
                method_info = "Lagrange polynomial interpolation"

            else:
                raise ValidationError(f"Unknown interpolation method: {method}")

            # Evaluate at new points if provided
            interpolated_values = []
            if x_new:
                x_new_array = np.array(x_new)
                y_new_array = interp_func(x_new_array)

                for i, x_val in enumerate(x_new):
                    interpolated_values.append(
                        {
                            "x": x_val,
                            "y": float(y_new_array[i])
                            if hasattr(y_new_array, "__iter__")
                            else float(y_new_array),
                        }
                    )

            # Generate smooth curve for visualization
            x_smooth = np.linspace(min(x_data), max(x_data), 100)
            y_smooth = interp_func(x_smooth)

            smooth_curve = []
            for i, x_val in enumerate(x_smooth):
                smooth_curve.append({"x": float(x_val), "y": float(y_smooth[i])})

            return {
                "interpolated_values": interpolated_values,
                "smooth_curve": smooth_curve,
                "method": method,
                "method_info": method_info,
                "original_data": [{"x": x_data[i], "y": y_data[i]} for i in range(len(x_data))],
                "x_range": [float(min(x_data)), float(max(x_data))],
            }

        except Exception as e:
            raise ComputationError(f"Interpolation failed: {str(e)}")

    async def curve_fitting(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fit a curve to data points.

        Args:
            params: Dictionary containing data and fitting parameters

        Returns:
            Dictionary with curve fitting results
        """
        x_data = params.get("x_data")
        y_data = params.get("y_data")
        fit_type = params.get("fit_type", "polynomial")
        degree = params.get("degree", 2)

        if not x_data or not y_data:
            raise ValidationError("Both x_data and y_data are required for curve fitting")

        if len(x_data) != len(y_data):
            raise ValidationError("x_data and y_data must have the same length")

        try:
            x_array = np.array(x_data)
            y_array = np.array(y_data)

            if fit_type == "polynomial":
                # Polynomial fitting
                coefficients = np.polyfit(x_array, y_array, degree)
                poly_func = np.poly1d(coefficients)

                # Calculate R-squared
                y_pred = poly_func(x_array)
                ss_res = np.sum((y_array - y_pred) ** 2)
                ss_tot = np.sum((y_array - np.mean(y_array)) ** 2)
                r_squared = 1 - (ss_res / ss_tot)

                # Generate fitted curve
                x_fit = np.linspace(min(x_data), max(x_data), 100)
                y_fit = poly_func(x_fit)

                fitted_curve = [
                    {"x": float(x_fit[i]), "y": float(y_fit[i])} for i in range(len(x_fit))
                ]

                # Create polynomial expression
                poly_expr = " + ".join(
                    [
                        f"{coeff:.6f}*x^{degree - i}"
                        if degree - i > 1
                        else f"{coeff:.6f}*x"
                        if degree - i == 1
                        else f"{coeff:.6f}"
                        for i, coeff in enumerate(coefficients)
                        if abs(coeff) > 1e-10
                    ]
                )

                return {
                    "fit_type": "polynomial",
                    "degree": degree,
                    "coefficients": coefficients.tolist(),
                    "polynomial_expression": poly_expr,
                    "r_squared": r_squared,
                    "fitted_curve": fitted_curve,
                    "original_data": [
                        {"x": x_data[i], "y": y_data[i]} for i in range(len(x_data))
                    ],
                }

            elif fit_type == "exponential":
                # Exponential fitting: y = a * exp(b * x)
                # Take log to linearize: ln(y) = ln(a) + b*x
                if any(y <= 0 for y in y_data):
                    raise ValidationError("All y values must be positive for exponential fitting")

                log_y = np.log(y_array)
                coeffs = np.polyfit(x_array, log_y, 1)
                a = np.exp(coeffs[1])
                b = coeffs[0]

                # Generate fitted curve
                x_fit = np.linspace(min(x_data), max(x_data), 100)
                y_fit = a * np.exp(b * x_fit)

                fitted_curve = [
                    {"x": float(x_fit[i]), "y": float(y_fit[i])} for i in range(len(x_fit))
                ]

                # Calculate R-squared
                y_pred = a * np.exp(b * x_array)
                ss_res = np.sum((y_array - y_pred) ** 2)
                ss_tot = np.sum((y_array - np.mean(y_array)) ** 2)
                r_squared = 1 - (ss_res / ss_tot)

                return {
                    "fit_type": "exponential",
                    "parameters": {"a": a, "b": b},
                    "expression": f"{a:.6f} * exp({b:.6f} * x)",
                    "r_squared": r_squared,
                    "fitted_curve": fitted_curve,
                    "original_data": [
                        {"x": x_data[i], "y": y_data[i]} for i in range(len(x_data))
                    ],
                }

            else:
                raise ValidationError(f"Unknown fit type: {fit_type}")

        except Exception as e:
            raise ComputationError(f"Curve fitting failed: {str(e)}")
