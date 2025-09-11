"""Numerical method strategies for optimization and root finding."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

from scipy import optimize

from ..core.errors.exceptions import ComputationError


class NumericalStrategy(ABC):
    """Abstract base class for numerical strategies."""

    @abstractmethod
    def can_handle(self, problem_type: str, **kwargs) -> bool:
        """Check if strategy can handle the problem.

        Args:
            problem_type: Type of problem ('root_finding', 'optimization', etc.)
            **kwargs: Additional problem parameters

        Returns:
            True if strategy can handle the problem
        """
        pass

    @abstractmethod
    def execute(self, func: Callable, **kwargs) -> Dict[str, Any]:
        """Execute the numerical method.

        Args:
            func: Function to operate on
            **kwargs: Method-specific parameters

        Returns:
            Dictionary with results and metadata
        """
        pass

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """Get information about the strategy."""
        pass

    def get_priority(self) -> int:
        """Get priority of this strategy (lower = higher priority)."""
        return 100


class BrentRootFindingStrategy(NumericalStrategy):
    """Brent's method for root finding."""

    def can_handle(self, problem_type: str, **kwargs) -> bool:
        """Check if Brent's method can handle the problem."""
        if problem_type != "root_finding":
            return False

        # Requires bounds and function values with opposite signs
        bounds = kwargs.get("bounds")
        func = kwargs.get("func")

        if not bounds or len(bounds) != 2:
            return False

        if func:
            try:
                fa, fb = func(bounds[0]), func(bounds[1])
                return fa * fb < 0  # Opposite signs
            except:
                return False

        return True

    def execute(self, func: Callable, **kwargs) -> Dict[str, Any]:
        """Execute Brent's method."""
        bounds = kwargs.get("bounds")
        tolerance = kwargs.get("tolerance", 1e-8)
        max_iter = kwargs.get("max_iter", 100)

        try:
            result = optimize.brentq(
                func, bounds[0], bounds[1], xtol=tolerance, maxiter=max_iter, full_output=True
            )

            root, info = result[0], result[1]

            return {
                "root": float(root),
                "function_value": float(func(root)),
                "iterations": info.iterations,
                "function_calls": info.function_calls,
                "converged": info.converged,
                "bounds_used": bounds,
                "tolerance": tolerance,
                "method": "Brent's method",
            }

        except Exception as e:
            raise ComputationError(f"Brent's method failed: {str(e)}")

    def get_info(self) -> Dict[str, Any]:
        """Get Brent's method information."""
        return {
            "name": "Brent's Method",
            "description": "Robust root finding combining bisection, secant, and inverse quadratic interpolation",
            "convergence_rate": "Superlinear",
            "requirements": "Function values at bounds must have opposite signs",
            "advantages": ["Guaranteed convergence", "Fast convergence", "Robust"],
            "disadvantages": ["Requires bracketing interval"],
        }

    def get_priority(self) -> int:
        """Brent's method has high priority when applicable."""
        return 10


class NewtonRootFindingStrategy(NumericalStrategy):
    """Newton's method for root finding."""

    def can_handle(self, problem_type: str, **kwargs) -> bool:
        """Check if Newton's method can handle the problem."""
        if problem_type != "root_finding":
            return False

        # Requires initial guess
        return kwargs.get("initial_guess") is not None

    def execute(self, func: Callable, **kwargs) -> Dict[str, Any]:
        """Execute Newton's method."""
        initial_guess = kwargs.get("initial_guess")
        tolerance = kwargs.get("tolerance", 1e-8)
        max_iter = kwargs.get("max_iter", 50)
        derivative = kwargs.get("derivative")

        try:
            if derivative:
                # Use provided derivative
                result = optimize.newton(
                    func,
                    initial_guess,
                    fprime=derivative,
                    tol=tolerance,
                    maxiter=max_iter,
                    full_output=True,
                )
            else:
                # Use numerical derivative
                result = optimize.newton(
                    func, initial_guess, tol=tolerance, maxiter=max_iter, full_output=True
                )

            root, info = result[0], result[1]

            return {
                "root": float(root),
                "function_value": float(func(root)),
                "iterations": info.iterations,
                "converged": info.converged,
                "initial_guess": initial_guess,
                "tolerance": tolerance,
                "method": "Newton's method",
                "used_analytical_derivative": derivative is not None,
            }

        except Exception as e:
            raise ComputationError(f"Newton's method failed: {str(e)}")

    def get_info(self) -> Dict[str, Any]:
        """Get Newton's method information."""
        return {
            "name": "Newton's Method",
            "description": "Fast root finding using function and derivative values",
            "convergence_rate": "Quadratic (when close to root)",
            "requirements": "Initial guess, derivative (or numerical approximation)",
            "advantages": ["Very fast convergence near root", "Simple implementation"],
            "disadvantages": [
                "May not converge",
                "Sensitive to initial guess",
                "Requires derivative",
            ],
        }

    def get_priority(self) -> int:
        """Newton's method has medium priority."""
        return 30


class SecantRootFindingStrategy(NumericalStrategy):
    """Secant method for root finding."""

    def can_handle(self, problem_type: str, **kwargs) -> bool:
        """Check if secant method can handle the problem."""
        if problem_type != "root_finding":
            return False

        # Requires two initial guesses
        initial_guess = kwargs.get("initial_guess")
        return initial_guess is not None and len(initial_guess) >= 2

    def execute(self, func: Callable, **kwargs) -> Dict[str, Any]:
        """Execute secant method."""
        initial_guess = kwargs.get("initial_guess")
        tolerance = kwargs.get("tolerance", 1e-8)
        max_iter = kwargs.get("max_iter", 50)

        try:
            x0, x1 = initial_guess[0], initial_guess[1]

            result = optimize.newton(
                func, x0, x1=x1, tol=tolerance, maxiter=max_iter, full_output=True
            )

            root, info = result[0], result[1]

            return {
                "root": float(root),
                "function_value": float(func(root)),
                "iterations": info.iterations,
                "converged": info.converged,
                "initial_guesses": [x0, x1],
                "tolerance": tolerance,
                "method": "Secant method",
            }

        except Exception as e:
            raise ComputationError(f"Secant method failed: {str(e)}")

    def get_info(self) -> Dict[str, Any]:
        """Get secant method information."""
        return {
            "name": "Secant Method",
            "description": "Root finding using secant line approximation (no derivative needed)",
            "convergence_rate": "Superlinear (φ ≈ 1.618)",
            "requirements": "Two initial guesses",
            "advantages": ["No derivative needed", "Good convergence rate"],
            "disadvantages": ["May not converge", "Slower than Newton's method"],
        }

    def get_priority(self) -> int:
        """Secant method has medium priority."""
        return 40


class BisectionRootFindingStrategy(NumericalStrategy):
    """Bisection method for root finding."""

    def can_handle(self, problem_type: str, **kwargs) -> bool:
        """Check if bisection method can handle the problem."""
        if problem_type != "root_finding":
            return False

        # Requires bounds with opposite signs
        bounds = kwargs.get("bounds")
        func = kwargs.get("func")

        if not bounds or len(bounds) != 2:
            return False

        if func:
            try:
                fa, fb = func(bounds[0]), func(bounds[1])
                return fa * fb < 0
            except:
                return False

        return True

    def execute(self, func: Callable, **kwargs) -> Dict[str, Any]:
        """Execute bisection method."""
        bounds = kwargs.get("bounds")
        tolerance = kwargs.get("tolerance", 1e-8)
        max_iter = kwargs.get("max_iter", 100)

        try:
            result = optimize.bisect(
                func, bounds[0], bounds[1], xtol=tolerance, maxiter=max_iter, full_output=True
            )

            root, info = result[0], result[1]

            return {
                "root": float(root),
                "function_value": float(func(root)),
                "iterations": info.iterations,
                "function_calls": info.function_calls,
                "converged": info.converged,
                "bounds_used": bounds,
                "tolerance": tolerance,
                "method": "Bisection method",
            }

        except Exception as e:
            raise ComputationError(f"Bisection method failed: {str(e)}")

    def get_info(self) -> Dict[str, Any]:
        """Get bisection method information."""
        return {
            "name": "Bisection Method",
            "description": "Reliable but slow root finding by repeatedly halving interval",
            "convergence_rate": "Linear",
            "requirements": "Function values at bounds must have opposite signs",
            "advantages": ["Always converges", "Simple and robust"],
            "disadvantages": ["Slow convergence", "Requires bracketing interval"],
        }

    def get_priority(self) -> int:
        """Bisection has low priority (fallback method)."""
        return 80


class BrentOptimizationStrategy(NumericalStrategy):
    """Brent's method for scalar optimization."""

    def can_handle(self, problem_type: str, **kwargs) -> bool:
        """Check if Brent's optimization can handle the problem."""
        return problem_type == "optimization"

    def execute(self, func: Callable, **kwargs) -> Dict[str, Any]:
        """Execute Brent's optimization."""
        bounds = kwargs.get("bounds")
        tolerance = kwargs.get("tolerance", 1e-8)

        try:
            if bounds:
                result = optimize.minimize_scalar(
                    func, bounds=bounds, method="bounded", options={"xatol": tolerance}
                )
            else:
                result = optimize.minimize_scalar(
                    func, method="brent", options={"xtol": tolerance}
                )

            return {
                "optimal_x": float(result.x),
                "optimal_value": float(result.fun),
                "success": result.success,
                "iterations": result.nit if hasattr(result, "nit") else None,
                "function_calls": result.nfev,
                "method": "Brent's method",
                "bounds": bounds,
                "tolerance": tolerance,
            }

        except Exception as e:
            raise ComputationError(f"Brent's optimization failed: {str(e)}")

    def get_info(self) -> Dict[str, Any]:
        """Get Brent's optimization information."""
        return {
            "name": "Brent's Optimization",
            "description": "Robust scalar optimization using parabolic interpolation and golden section",
            "convergence_rate": "Superlinear",
            "requirements": "Scalar function (single variable)",
            "advantages": ["No derivative needed", "Robust convergence"],
            "disadvantages": ["Only for scalar functions"],
        }

    def get_priority(self) -> int:
        """Brent's optimization has high priority."""
        return 20


class GoldenSectionStrategy(NumericalStrategy):
    """Golden section search for optimization."""

    def can_handle(self, problem_type: str, **kwargs) -> bool:
        """Check if golden section can handle the problem."""
        if problem_type != "optimization":
            return False

        # Requires bounds
        bounds = kwargs.get("bounds")
        return bounds is not None and len(bounds) == 2

    def execute(self, func: Callable, **kwargs) -> Dict[str, Any]:
        """Execute golden section search."""
        bounds = kwargs.get("bounds")
        tolerance = kwargs.get("tolerance", 1e-8)

        try:
            result = optimize.minimize_scalar(
                func, bounds=bounds, method="golden", options={"xtol": tolerance}
            )

            return {
                "optimal_x": float(result.x),
                "optimal_value": float(result.fun),
                "success": result.success,
                "iterations": result.nit if hasattr(result, "nit") else None,
                "function_calls": result.nfev,
                "method": "Golden section search",
                "bounds": bounds,
                "tolerance": tolerance,
            }

        except Exception as e:
            raise ComputationError(f"Golden section search failed: {str(e)}")

    def get_info(self) -> Dict[str, Any]:
        """Get golden section information."""
        return {
            "name": "Golden Section Search",
            "description": "Optimization using golden ratio to narrow search interval",
            "convergence_rate": "Linear",
            "requirements": "Bounded interval, unimodal function",
            "advantages": ["Simple implementation", "Guaranteed convergence"],
            "disadvantages": ["Slow convergence", "Requires bounds"],
        }

    def get_priority(self) -> int:
        """Golden section has medium-low priority."""
        return 60


class NelderMeadStrategy(NumericalStrategy):
    """Nelder-Mead simplex method for multivariable optimization."""

    def can_handle(self, problem_type: str, **kwargs) -> bool:
        """Check if Nelder-Mead can handle the problem."""
        if problem_type != "optimization":
            return False

        # Good for multivariable problems
        initial_guess = kwargs.get("initial_guess")
        return initial_guess is not None

    def execute(self, func: Callable, **kwargs) -> Dict[str, Any]:
        """Execute Nelder-Mead optimization."""
        initial_guess = kwargs.get("initial_guess")
        tolerance = kwargs.get("tolerance", 1e-8)
        max_iter = kwargs.get("max_iter", 1000)

        try:
            # Ensure initial_guess is a list/array
            if not hasattr(initial_guess, "__iter__"):
                initial_guess = [initial_guess]

            result = optimize.minimize(
                func,
                initial_guess,
                method="Nelder-Mead",
                options={"xatol": tolerance, "fatol": tolerance, "maxiter": max_iter},
            )

            return {
                "optimal_x": result.x.tolist()
                if hasattr(result.x, "tolist")
                else [float(result.x)],
                "optimal_value": float(result.fun),
                "success": result.success,
                "iterations": result.nit,
                "function_calls": result.nfev,
                "method": "Nelder-Mead simplex",
                "initial_guess": initial_guess,
                "tolerance": tolerance,
            }

        except Exception as e:
            raise ComputationError(f"Nelder-Mead optimization failed: {str(e)}")

    def get_info(self) -> Dict[str, Any]:
        """Get Nelder-Mead information."""
        return {
            "name": "Nelder-Mead Simplex",
            "description": "Derivative-free optimization using simplex transformations",
            "convergence_rate": "Linear",
            "requirements": "Initial guess (works for multivariable functions)",
            "advantages": ["No derivatives needed", "Handles multivariable functions", "Robust"],
            "disadvantages": ["Slow convergence", "May get stuck in local minima"],
        }

    def get_priority(self) -> int:
        """Nelder-Mead has medium priority."""
        return 50


class NumericalMethodContext:
    """Context for selecting and executing numerical methods."""

    def __init__(self):
        """Initialize context with available strategies."""
        self.root_finding_strategies = [
            BrentRootFindingStrategy(),
            NewtonRootFindingStrategy(),
            SecantRootFindingStrategy(),
            BisectionRootFindingStrategy(),
        ]

        self.optimization_strategies = [
            BrentOptimizationStrategy(),
            GoldenSectionStrategy(),
            NelderMeadStrategy(),
        ]

        # Sort by priority
        self.root_finding_strategies.sort(key=lambda s: s.get_priority())
        self.optimization_strategies.sort(key=lambda s: s.get_priority())

    def find_root(self, func: Callable, **kwargs) -> Dict[str, Any]:
        """Find root using best available strategy.

        Args:
            func: Function to find root of
            **kwargs: Method parameters

        Returns:
            Dictionary with root finding results
        """
        kwargs["func"] = func

        for strategy in self.root_finding_strategies:
            if strategy.can_handle("root_finding", **kwargs):
                try:
                    result = strategy.execute(func, **kwargs)
                    result["strategy_info"] = strategy.get_info()
                    return result
                except ComputationError:
                    continue

        raise ComputationError("No suitable root finding strategy found")

    def optimize(self, func: Callable, **kwargs) -> Dict[str, Any]:
        """Optimize function using best available strategy.

        Args:
            func: Function to optimize
            **kwargs: Method parameters

        Returns:
            Dictionary with optimization results
        """
        for strategy in self.optimization_strategies:
            if strategy.can_handle("optimization", **kwargs):
                try:
                    result = strategy.execute(func, **kwargs)
                    result["strategy_info"] = strategy.get_info()
                    return result
                except ComputationError:
                    continue

        raise ComputationError("No suitable optimization strategy found")

    def get_available_strategies(self, problem_type: str) -> List[Dict[str, Any]]:
        """Get list of available strategies for a problem type.

        Args:
            problem_type: Type of problem ('root_finding' or 'optimization')

        Returns:
            List of strategy information
        """
        if problem_type == "root_finding":
            strategies = self.root_finding_strategies
        elif problem_type == "optimization":
            strategies = self.optimization_strategies
        else:
            return []

        return [strategy.get_info() for strategy in strategies]

    def recommend_strategy(self, problem_type: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Recommend best strategy for given problem parameters.

        Args:
            problem_type: Type of problem
            **kwargs: Problem parameters

        Returns:
            Information about recommended strategy
        """
        if problem_type == "root_finding":
            strategies = self.root_finding_strategies
        elif problem_type == "optimization":
            strategies = self.optimization_strategies
        else:
            return None

        for strategy in strategies:
            if strategy.can_handle(problem_type, **kwargs):
                info = strategy.get_info()
                info["priority"] = strategy.get_priority()
                return info

        return None
