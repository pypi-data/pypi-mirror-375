"""Optimization strategies for different types of optimization problems."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

import numpy as np
from scipy import optimize

from ..core.errors.exceptions import ComputationError


class OptimizationStrategy(ABC):
    """Abstract base class for optimization strategies."""

    @abstractmethod
    def can_handle(self, problem_type: str, **kwargs) -> bool:
        """Check if strategy can handle the optimization problem.

        Args:
            problem_type: Type of optimization problem
            **kwargs: Problem parameters

        Returns:
            True if strategy can handle the problem
        """
        pass

    @abstractmethod
    def optimize(self, objective: Callable, **kwargs) -> Dict[str, Any]:
        """Perform optimization.

        Args:
            objective: Objective function to optimize
            **kwargs: Optimization parameters

        Returns:
            Dictionary with optimization results
        """
        pass

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """Get information about the strategy."""
        pass

    def get_priority(self) -> int:
        """Get priority of this strategy (lower = higher priority)."""
        return 100


class ScalarBrentStrategy(OptimizationStrategy):
    """Brent's method for scalar optimization."""

    def can_handle(self, problem_type: str, **kwargs) -> bool:
        """Check if Brent's method can handle the problem."""
        if problem_type not in ["scalar_minimize", "scalar_maximize"]:
            return False

        # Works best with or without bounds
        return True

    def optimize(self, objective: Callable, **kwargs) -> Dict[str, Any]:
        """Optimize using Brent's method."""
        bounds = kwargs.get("bounds")
        tolerance = kwargs.get("tolerance", 1e-8)
        maximize = kwargs.get("maximize", False)

        try:
            # For maximization, minimize the negative function
            if maximize:
                opt_func = lambda x: -objective(x)
            else:
                opt_func = objective

            if bounds:
                result = optimize.minimize_scalar(
                    opt_func, bounds=bounds, method="bounded", options={"xatol": tolerance}
                )
            else:
                result = optimize.minimize_scalar(
                    opt_func, method="brent", options={"xtol": tolerance}
                )

            optimal_value = objective(result.x)

            return {
                "optimal_x": float(result.x),
                "optimal_value": float(optimal_value),
                "success": result.success,
                "iterations": getattr(result, "nit", None),
                "function_evaluations": result.nfev,
                "method": "Brent's method",
                "bounds": bounds,
                "maximization": maximize,
                "tolerance": tolerance,
                "message": getattr(result, "message", "Optimization completed"),
            }

        except Exception as e:
            raise ComputationError(f"Brent's optimization failed: {str(e)}")

    def get_info(self) -> Dict[str, Any]:
        """Get Brent's method information."""
        return {
            "name": "Brent's Method",
            "description": "Robust scalar optimization combining parabolic interpolation and golden section",
            "problem_types": ["scalar_minimize", "scalar_maximize"],
            "convergence_rate": "Superlinear",
            "advantages": [
                "No derivatives needed",
                "Robust convergence",
                "Works with or without bounds",
            ],
            "disadvantages": ["Only for single-variable functions"],
            "parameters": ["bounds (optional)", "tolerance", "maximize"],
        }

    def get_priority(self) -> int:
        """High priority for scalar problems."""
        return 10


class GoldenSectionStrategy(OptimizationStrategy):
    """Golden section search for bounded scalar optimization."""

    def can_handle(self, problem_type: str, **kwargs) -> bool:
        """Check if golden section can handle the problem."""
        if problem_type not in ["scalar_minimize", "scalar_maximize"]:
            return False

        # Requires bounds
        bounds = kwargs.get("bounds")
        return bounds is not None and len(bounds) == 2

    def optimize(self, objective: Callable, **kwargs) -> Dict[str, Any]:
        """Optimize using golden section search."""
        bounds = kwargs.get("bounds")
        tolerance = kwargs.get("tolerance", 1e-8)
        maximize = kwargs.get("maximize", False)

        try:
            # For maximization, minimize the negative function
            if maximize:
                opt_func = lambda x: -objective(x)
            else:
                opt_func = objective

            result = optimize.minimize_scalar(
                opt_func, bounds=bounds, method="golden", options={"xtol": tolerance}
            )

            optimal_value = objective(result.x)

            return {
                "optimal_x": float(result.x),
                "optimal_value": float(optimal_value),
                "success": result.success,
                "iterations": getattr(result, "nit", None),
                "function_evaluations": result.nfev,
                "method": "Golden section search",
                "bounds": bounds,
                "maximization": maximize,
                "tolerance": tolerance,
            }

        except Exception as e:
            raise ComputationError(f"Golden section search failed: {str(e)}")

    def get_info(self) -> Dict[str, Any]:
        """Get golden section information."""
        return {
            "name": "Golden Section Search",
            "description": "Optimization using golden ratio to systematically narrow search interval",
            "problem_types": ["scalar_minimize", "scalar_maximize"],
            "convergence_rate": "Linear",
            "advantages": ["Simple and reliable", "Guaranteed convergence for unimodal functions"],
            "disadvantages": ["Requires bounds", "Slower than Brent's method"],
            "parameters": ["bounds (required)", "tolerance", "maximize"],
        }

    def get_priority(self) -> int:
        """Medium priority for bounded problems."""
        return 30


class NelderMeadStrategy(OptimizationStrategy):
    """Nelder-Mead simplex method for multivariable optimization."""

    def can_handle(self, problem_type: str, **kwargs) -> bool:
        """Check if Nelder-Mead can handle the problem."""
        if problem_type not in ["minimize", "maximize", "multivariable"]:
            return False

        # Requires initial guess
        initial_guess = kwargs.get("initial_guess")
        return initial_guess is not None

    def optimize(self, objective: Callable, **kwargs) -> Dict[str, Any]:
        """Optimize using Nelder-Mead method."""
        initial_guess = kwargs.get("initial_guess")
        tolerance = kwargs.get("tolerance", 1e-8)
        max_iter = kwargs.get("max_iter", 1000)
        maximize = kwargs.get("maximize", False)

        try:
            # Ensure initial_guess is array-like
            if not hasattr(initial_guess, "__iter__"):
                initial_guess = [initial_guess]

            x0 = np.array(initial_guess)

            # For maximization, minimize the negative function
            if maximize:
                opt_func = lambda x: -objective(x)
            else:
                opt_func = objective

            result = optimize.minimize(
                opt_func,
                x0,
                method="Nelder-Mead",
                options={"xatol": tolerance, "fatol": tolerance, "maxiter": max_iter},
            )

            optimal_value = objective(result.x)

            return {
                "optimal_x": result.x.tolist() if len(result.x) > 1 else float(result.x[0]),
                "optimal_value": float(optimal_value),
                "success": result.success,
                "iterations": result.nit,
                "function_evaluations": result.nfev,
                "method": "Nelder-Mead simplex",
                "initial_guess": initial_guess,
                "maximization": maximize,
                "tolerance": tolerance,
                "message": result.message,
            }

        except Exception as e:
            raise ComputationError(f"Nelder-Mead optimization failed: {str(e)}")

    def get_info(self) -> Dict[str, Any]:
        """Get Nelder-Mead information."""
        return {
            "name": "Nelder-Mead Simplex",
            "description": "Derivative-free optimization using simplex transformations",
            "problem_types": ["minimize", "maximize", "multivariable"],
            "convergence_rate": "Linear",
            "advantages": ["No derivatives needed", "Handles multivariable functions", "Robust"],
            "disadvantages": ["Slow convergence", "May converge to local optima"],
            "parameters": ["initial_guess (required)", "tolerance", "max_iter", "maximize"],
        }

    def get_priority(self) -> int:
        """Medium priority for multivariable problems."""
        return 40


class BFGSStrategy(OptimizationStrategy):
    """BFGS quasi-Newton method for smooth multivariable optimization."""

    def can_handle(self, problem_type: str, **kwargs) -> bool:
        """Check if BFGS can handle the problem."""
        if problem_type not in ["minimize", "maximize", "multivariable"]:
            return False

        # Requires initial guess and works best with smooth functions
        initial_guess = kwargs.get("initial_guess")
        return initial_guess is not None

    def optimize(self, objective: Callable, **kwargs) -> Dict[str, Any]:
        """Optimize using BFGS method."""
        initial_guess = kwargs.get("initial_guess")
        tolerance = kwargs.get("tolerance", 1e-8)
        max_iter = kwargs.get("max_iter", 1000)
        maximize = kwargs.get("maximize", False)
        gradient = kwargs.get("gradient")

        try:
            if not hasattr(initial_guess, "__iter__"):
                initial_guess = [initial_guess]

            x0 = np.array(initial_guess)

            # For maximization, minimize the negative function
            if maximize:
                opt_func = lambda x: -objective(x)
                if gradient:
                    grad_func = lambda x: -gradient(x)
                else:
                    grad_func = None
            else:
                opt_func = objective
                grad_func = gradient

            result = optimize.minimize(
                opt_func,
                x0,
                method="BFGS",
                jac=grad_func,
                options={"gtol": tolerance, "maxiter": max_iter},
            )

            optimal_value = objective(result.x)

            return {
                "optimal_x": result.x.tolist() if len(result.x) > 1 else float(result.x[0]),
                "optimal_value": float(optimal_value),
                "success": result.success,
                "iterations": result.nit,
                "function_evaluations": result.nfev,
                "gradient_evaluations": getattr(result, "njev", None),
                "method": "BFGS",
                "initial_guess": initial_guess,
                "maximization": maximize,
                "tolerance": tolerance,
                "used_analytical_gradient": gradient is not None,
                "message": result.message,
            }

        except Exception as e:
            raise ComputationError(f"BFGS optimization failed: {str(e)}")

    def get_info(self) -> Dict[str, Any]:
        """Get BFGS information."""
        return {
            "name": "BFGS (Broyden-Fletcher-Goldfarb-Shanno)",
            "description": "Quasi-Newton method using gradient information",
            "problem_types": ["minimize", "maximize", "multivariable"],
            "convergence_rate": "Superlinear",
            "advantages": [
                "Fast convergence",
                "Good for smooth functions",
                "Uses gradient information",
            ],
            "disadvantages": ["Requires smooth functions", "May fail on non-convex problems"],
            "parameters": [
                "initial_guess (required)",
                "gradient (optional)",
                "tolerance",
                "max_iter",
                "maximize",
            ],
        }

    def get_priority(self) -> int:
        """High priority for smooth multivariable problems."""
        return 20


class ConstrainedOptimizationStrategy(OptimizationStrategy):
    """Strategy for constrained optimization problems."""

    def can_handle(self, problem_type: str, **kwargs) -> bool:
        """Check if constrained optimization can handle the problem."""
        if problem_type not in ["constrained_minimize", "constrained_maximize"]:
            return False

        # Requires initial guess and constraints
        initial_guess = kwargs.get("initial_guess")
        constraints = kwargs.get("constraints")
        bounds = kwargs.get("bounds")

        return initial_guess is not None and (constraints is not None or bounds is not None)

    def optimize(self, objective: Callable, **kwargs) -> Dict[str, Any]:
        """Optimize with constraints using SLSQP method."""
        initial_guess = kwargs.get("initial_guess")
        constraints = kwargs.get("constraints", [])
        bounds = kwargs.get("bounds")
        tolerance = kwargs.get("tolerance", 1e-8)
        max_iter = kwargs.get("max_iter", 1000)
        maximize = kwargs.get("maximize", False)

        try:
            if not hasattr(initial_guess, "__iter__"):
                initial_guess = [initial_guess]

            x0 = np.array(initial_guess)

            # For maximization, minimize the negative function
            if maximize:
                opt_func = lambda x: -objective(x)
            else:
                opt_func = objective

            # Convert constraints to scipy format if needed
            scipy_constraints = []
            if constraints:
                for constraint in constraints:
                    if isinstance(constraint, dict):
                        scipy_constraints.append(constraint)
                    elif callable(constraint):
                        # Assume equality constraint
                        scipy_constraints.append({"type": "eq", "fun": constraint})

            result = optimize.minimize(
                opt_func,
                x0,
                method="SLSQP",
                bounds=bounds,
                constraints=scipy_constraints,
                options={"ftol": tolerance, "maxiter": max_iter},
            )

            optimal_value = objective(result.x)

            return {
                "optimal_x": result.x.tolist() if len(result.x) > 1 else float(result.x[0]),
                "optimal_value": float(optimal_value),
                "success": result.success,
                "iterations": result.nit,
                "function_evaluations": result.nfev,
                "method": "SLSQP (Sequential Least Squares Programming)",
                "initial_guess": initial_guess,
                "maximization": maximize,
                "tolerance": tolerance,
                "bounds": bounds,
                "num_constraints": len(scipy_constraints),
                "message": result.message,
            }

        except Exception as e:
            raise ComputationError(f"Constrained optimization failed: {str(e)}")

    def get_info(self) -> Dict[str, Any]:
        """Get constrained optimization information."""
        return {
            "name": "SLSQP (Sequential Least Squares Programming)",
            "description": "Optimization with equality and inequality constraints",
            "problem_types": ["constrained_minimize", "constrained_maximize"],
            "convergence_rate": "Superlinear",
            "advantages": ["Handles constraints", "Robust for constrained problems"],
            "disadvantages": [
                "Slower than unconstrained methods",
                "Requires feasible initial guess",
            ],
            "parameters": [
                "initial_guess (required)",
                "constraints",
                "bounds",
                "tolerance",
                "max_iter",
                "maximize",
            ],
        }

    def get_priority(self) -> int:
        """High priority for constrained problems."""
        return 15


class DifferentialEvolutionStrategy(OptimizationStrategy):
    """Differential Evolution for global optimization."""

    def can_handle(self, problem_type: str, **kwargs) -> bool:
        """Check if Differential Evolution can handle the problem."""
        if problem_type not in ["global_minimize", "global_maximize", "minimize", "maximize"]:
            return False

        # Requires bounds
        bounds = kwargs.get("bounds")
        return bounds is not None

    def optimize(self, objective: Callable, **kwargs) -> Dict[str, Any]:
        """Optimize using Differential Evolution."""
        bounds = kwargs.get("bounds")
        tolerance = kwargs.get("tolerance", 1e-8)
        max_iter = kwargs.get("max_iter", 1000)
        population_size = kwargs.get("population_size", 15)
        maximize = kwargs.get("maximize", False)
        seed = kwargs.get("seed")

        try:
            # For maximization, minimize the negative function
            if maximize:
                opt_func = lambda x: -objective(x)
            else:
                opt_func = objective

            result = optimize.differential_evolution(
                opt_func,
                bounds,
                maxiter=max_iter,
                tol=tolerance,
                popsize=population_size,
                seed=seed,
            )

            optimal_value = objective(result.x)

            return {
                "optimal_x": result.x.tolist() if len(result.x) > 1 else float(result.x[0]),
                "optimal_value": float(optimal_value),
                "success": result.success,
                "iterations": result.nit,
                "function_evaluations": result.nfev,
                "method": "Differential Evolution",
                "bounds": bounds,
                "maximization": maximize,
                "tolerance": tolerance,
                "population_size": population_size,
                "message": result.message,
            }

        except Exception as e:
            raise ComputationError(f"Differential Evolution failed: {str(e)}")

    def get_info(self) -> Dict[str, Any]:
        """Get Differential Evolution information."""
        return {
            "name": "Differential Evolution",
            "description": "Global optimization using evolutionary algorithm",
            "problem_types": ["global_minimize", "global_maximize", "minimize", "maximize"],
            "convergence_rate": "Variable (population-based)",
            "advantages": [
                "Global optimization",
                "Handles non-smooth functions",
                "No derivatives needed",
            ],
            "disadvantages": ["Slow convergence", "Requires bounds", "Stochastic results"],
            "parameters": [
                "bounds (required)",
                "tolerance",
                "max_iter",
                "population_size",
                "maximize",
                "seed",
            ],
        }

    def get_priority(self) -> int:
        """Lower priority due to slow convergence."""
        return 70


class OptimizationContext:
    """Context for selecting and executing optimization strategies."""

    def __init__(self):
        """Initialize context with available strategies."""
        self.strategies = [
            ScalarBrentStrategy(),
            ConstrainedOptimizationStrategy(),
            BFGSStrategy(),
            GoldenSectionStrategy(),
            NelderMeadStrategy(),
            DifferentialEvolutionStrategy(),
        ]

        # Sort by priority
        self.strategies.sort(key=lambda s: s.get_priority())

    def optimize(
        self, objective: Callable, problem_type: str = "minimize", **kwargs
    ) -> Dict[str, Any]:
        """Optimize function using best available strategy.

        Args:
            objective: Objective function to optimize
            problem_type: Type of optimization problem
            **kwargs: Optimization parameters

        Returns:
            Dictionary with optimization results
        """
        # Try strategies in priority order
        for strategy in self.strategies:
            if strategy.can_handle(problem_type, **kwargs):
                try:
                    result = strategy.optimize(objective, **kwargs)
                    result["strategy_info"] = strategy.get_info()
                    result["problem_type"] = problem_type
                    return result
                except ComputationError:
                    continue

        raise ComputationError(
            f"No suitable optimization strategy found for problem type: {problem_type}"
        )

    def get_suitable_strategies(self, problem_type: str, **kwargs) -> List[Dict[str, Any]]:
        """Get list of strategies suitable for the problem.

        Args:
            problem_type: Type of optimization problem
            **kwargs: Problem parameters

        Returns:
            List of suitable strategy information
        """
        suitable = []
        for strategy in self.strategies:
            if strategy.can_handle(problem_type, **kwargs):
                info = strategy.get_info()
                info["priority"] = strategy.get_priority()
                suitable.append(info)

        return suitable

    def recommend_strategy(self, problem_type: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Recommend best strategy for the problem.

        Args:
            problem_type: Type of optimization problem
            **kwargs: Problem parameters

        Returns:
            Information about recommended strategy
        """
        for strategy in self.strategies:
            if strategy.can_handle(problem_type, **kwargs):
                info = strategy.get_info()
                info["priority"] = strategy.get_priority()
                return info

        return None

    def analyze_problem(self, objective: Callable, **kwargs) -> Dict[str, Any]:
        """Analyze optimization problem and provide recommendations.

        Args:
            objective: Objective function
            **kwargs: Problem parameters

        Returns:
            Dictionary with problem analysis and recommendations
        """
        analysis = {"parameters": kwargs, "problem_characteristics": {}, "recommendations": []}

        # Analyze problem characteristics
        initial_guess = kwargs.get("initial_guess")
        bounds = kwargs.get("bounds")
        constraints = kwargs.get("constraints")

        if initial_guess is not None:
            if hasattr(initial_guess, "__iter__") and len(initial_guess) > 1:
                analysis["problem_characteristics"]["multivariable"] = True
                analysis["problem_characteristics"]["dimension"] = len(initial_guess)
            else:
                analysis["problem_characteristics"]["multivariable"] = False
                analysis["problem_characteristics"]["dimension"] = 1

        analysis["problem_characteristics"]["bounded"] = bounds is not None
        analysis["problem_characteristics"]["constrained"] = constraints is not None

        # Determine problem type
        if constraints:
            problem_type = "constrained_minimize"
        elif bounds and not initial_guess:
            problem_type = "global_minimize"
        elif analysis["problem_characteristics"].get("multivariable", False):
            problem_type = "minimize"
        else:
            problem_type = "scalar_minimize"

        analysis["recommended_problem_type"] = problem_type

        # Get suitable strategies
        suitable_strategies = self.get_suitable_strategies(problem_type, **kwargs)
        analysis["suitable_strategies"] = suitable_strategies

        # Provide recommendations
        if suitable_strategies:
            best_strategy = suitable_strategies[0]  # Already sorted by priority
            analysis["recommendations"].append(f"Recommended: {best_strategy['name']}")
            analysis["recommendations"].extend(best_strategy["advantages"])

        return analysis
