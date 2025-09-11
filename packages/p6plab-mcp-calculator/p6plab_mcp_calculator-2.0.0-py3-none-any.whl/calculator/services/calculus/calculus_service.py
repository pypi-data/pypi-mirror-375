"""Main calculus service that coordinates all calculus operations."""

from typing import Any, Dict

from ...core.errors.exceptions import ValidationError
from ..base import BaseService
from .derivatives import DerivativesService
from .integrals import IntegralsService
from .limits import LimitsService
from .numerical import NumericalCalculusService
from .series import SeriesService


class CalculusService(BaseService):
    """Main calculus service that coordinates all calculus operations."""

    def __init__(self, config=None, cache=None):
        """Initialize calculus service with sub-services."""
        super().__init__(config, cache)

        # Initialize sub-services
        self.derivatives = DerivativesService(config, cache)
        self.integrals = IntegralsService(config, cache)
        self.limits = LimitsService(config, cache)
        self.series = SeriesService(config, cache)
        self.numerical = NumericalCalculusService(config, cache)

    async def process(self, operation: str, params: Dict[str, Any]) -> Any:
        """Process calculus operation by routing to appropriate sub-service.

        Args:
            operation: Name of the calculus operation
            params: Parameters for the operation

        Returns:
            Result of the calculus operation
        """
        # Parse operation to determine sub-service and specific operation
        if "." in operation:
            service_name, sub_operation = operation.split(".", 1)
        else:
            # Map legacy operations to new structure
            service_name, sub_operation = self._map_legacy_operation(operation, params)

        # Route to appropriate sub-service
        if service_name == "derivatives":
            return await self.derivatives.process(sub_operation, params)
        elif service_name == "integrals":
            result = await self.integrals.process(sub_operation, params)
            # For definite integrals, return just the numeric value if available
            if (sub_operation == "definite" and isinstance(result, dict) and
                "numerical_value" in result and operation == "integral"):
                return result["numerical_value"]
            return result
        elif service_name == "limits":
            return await self.limits.process(sub_operation, params)
        elif service_name == "series":
            return await self.series.process(sub_operation, params)
        elif service_name == "numerical":
            return await self.numerical.process(sub_operation, params)
        elif service_name == "solver":
            # Handle solver operations
            return await self._handle_solver_operation(sub_operation, params)
        else:
            raise ValidationError(f"Unknown calculus service: {service_name}")

    def _map_legacy_operation(self, operation: str, params: Dict[str, Any] = None) -> tuple:
        """Map legacy operation names to new service structure.

        Args:
            operation: Legacy operation name
            params: Operation parameters for smart detection

        Returns:
            Tuple of (service_name, sub_operation)
        """
        legacy_mapping = {
            # Derivatives
            "derivative": ("derivatives", "symbolic"),
            "symbolic_derivative": ("derivatives", "symbolic"),
            "partial_derivative": ("derivatives", "partial"),
            "numerical_derivative": ("derivatives", "numerical"),
            "gradient": ("derivatives", "gradient"),
            # Integrals
            "integral": ("integrals", "symbolic"),  # Will be overridden by smart detection
            "symbolic_integral": ("integrals", "symbolic"),
            "definite_integral": ("integrals", "definite"),
            "numerical_integral": ("integrals", "numerical"),
            "improper_integral": ("integrals", "improper"),
            "multiple_integral": ("integrals", "multiple"),
            "line_integral": ("integrals", "line"),
            "surface_integral": ("integrals", "surface"),
            # Limits
            "limit": ("limits", "limit"),
            "calculate_limit": ("limits", "limit"),
            "left_limit": ("limits", "left_limit"),
            "right_limit": ("limits", "right_limit"),
            "limit_at_infinity": ("limits", "limit_at_infinity"),
            # Series
            "taylor_series": ("series", "taylor"),
            "maclaurin_series": ("series", "maclaurin"),
            "fourier_series": ("series", "fourier"),
            "power_series": ("series", "power"),
            "series_sum": ("series", "sum"),
            # Numerical methods
            "find_roots": ("numerical", "root_finding"),
            "optimize": ("numerical", "optimization"),
            "solve_ode": ("numerical", "ode_solve"),
            "interpolate": ("numerical", "interpolation"),
            "curve_fit": ("numerical", "curve_fitting"),
            # Solver operations
            "solve_linear": ("solver", "linear"),
            "solve_quadratic": ("solver", "quadratic"),
            "solve_polynomial": ("solver", "polynomial"),
            "solve_system": ("solver", "system"),
            "analyze_equation": ("solver", "analyze"),
        }

        if operation in legacy_mapping:
            service_name, sub_operation = legacy_mapping[operation]

            # Smart detection for definite integrals
            if operation == "integral" and params:
                # Check if this should be a definite integral
                has_bounds = any(key in params for key in ['lower_limit', 'upper_limit', 'lower_bound', 'upper_bound'])
                if has_bounds:
                    sub_operation = "definite"

            return (service_name, sub_operation)
        else:
            # Default to derivatives service for unknown operations
            return ("derivatives", operation)

    async def get_available_operations(self) -> Dict[str, Any]:
        """Get list of all available calculus operations.

        Returns:
            Dictionary of available operations organized by service
        """
        return {
            "derivatives": [
                "symbolic",
                "partial",
                "numerical",
                "gradient",
                "directional",
                "higher_order",
            ],
            "integrals": [
                "symbolic",
                "definite",
                "numerical",
                "improper",
                "multiple",
                "line",
                "surface",
            ],
            "limits": [
                "limit",
                "left_limit",
                "right_limit",
                "limit_at_infinity",
                "multivariable_limit",
                "sequential_limit",
            ],
            "series": [
                "taylor",
                "maclaurin",
                "laurent",
                "fourier",
                "power",
                "geometric",
                "convergence",
                "sum",
            ],
            "numerical": [
                "derivative",
                "integral",
                "root_finding",
                "optimization",
                "ode_solve",
                "interpolation",
                "curve_fitting",
            ],
        }

    async def get_operation_info(self, operation: str) -> Dict[str, Any]:
        """Get information about a specific operation.

        Args:
            operation: Name of the operation

        Returns:
            Dictionary with operation information
        """
        # Parse operation
        if "." in operation:
            service_name, sub_operation = operation.split(".", 1)
        else:
            service_name, sub_operation = self._map_legacy_operation(operation)

        operation_info = {
            "service": service_name,
            "operation": sub_operation,
            "full_name": f"{service_name}.{sub_operation}",
        }

        # Add specific information based on operation
        if service_name == "derivatives":
            operation_info.update(
                {
                    "description": "Calculate derivatives of mathematical expressions",
                    "required_params": ["expression", "variable"],
                    "optional_params": ["order", "point", "method"],
                }
            )
        elif service_name == "integrals":
            operation_info.update(
                {
                    "description": "Calculate integrals of mathematical expressions",
                    "required_params": ["expression", "variable"],
                    "optional_params": ["lower_bound", "upper_bound", "method"],
                }
            )
        elif service_name == "limits":
            operation_info.update(
                {
                    "description": "Calculate limits of mathematical expressions",
                    "required_params": ["expression", "variable", "approach_value"],
                    "optional_params": ["direction"],
                }
            )
        elif service_name == "series":
            operation_info.update(
                {
                    "description": "Calculate series expansions and analyze convergence",
                    "required_params": ["expression", "variable"],
                    "optional_params": ["center", "order", "terms"],
                }
            )
        elif service_name == "numerical":
            operation_info.update(
                {
                    "description": "Numerical methods for calculus operations",
                    "required_params": ["expression", "variable"],
                    "optional_params": ["method", "tolerance", "bounds"],
                }
            )

        return operation_info

    async def _handle_solver_operation(self, operation: str, params: Dict[str, Any]) -> Any:
        """Handle solver operations with placeholder implementations.

        Args:
            operation: Solver operation name
            params: Operation parameters

        Returns:
            Result of the solver operation
        """
        # Placeholder implementations for solver operations
        if operation == "linear":
            return {"solutions": [0.0], "status": "placeholder"}
        elif operation == "quadratic":
            return {"solutions": [0.0, 0.0], "status": "placeholder"}
        elif operation == "polynomial":
            return {"solutions": [], "status": "placeholder"}
        elif operation == "system":
            return {"solutions": {}, "status": "placeholder"}
        elif operation == "analyze":
            return {"analysis": "Equation analysis not implemented", "status": "placeholder"}
        else:
            # For find_roots, delegate to numerical service
            if operation == "root_finding":
                return await self.numerical.process("root_finding", params)
            else:
                raise ValidationError(f"Unknown solver operation: {operation}")

    async def validate_operation_params(self, operation: str, params: Dict[str, Any]) -> bool:
        """Validate parameters for a calculus operation.

        Args:
            operation: Name of the operation
            params: Parameters to validate

        Returns:
            True if parameters are valid

        Raises:
            ValidationError: If parameters are invalid
        """
        operation_info = await self.get_operation_info(operation)
        required_params = operation_info.get("required_params", [])

        # Check required parameters
        missing_params = []
        for param in required_params:
            if param not in params or params[param] is None:
                missing_params.append(param)

        if missing_params:
            raise ValidationError(f"Missing required parameters for {operation}: {missing_params}")

        # Validate specific parameter types
        if "expression" in params:
            if not isinstance(params["expression"], str) or not params["expression"].strip():
                raise ValidationError("Expression must be a non-empty string")

        if "variable" in params:
            if not isinstance(params["variable"], str) or not params["variable"].strip():
                raise ValidationError("Variable must be a non-empty string")

        if "order" in params:
            if not isinstance(params["order"], int) or params["order"] < 1:
                raise ValidationError("Order must be a positive integer")

        return True
