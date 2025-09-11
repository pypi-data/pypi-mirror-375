"""Backward compatibility layer for the refactored calculator."""

import os
import warnings
from functools import wraps
from types import ModuleType
from typing import Any, Dict, Optional

from ..core.errors.exceptions import CalculatorError
from ..services.arithmetic import ArithmeticService
from ..services.calculus import CalculusService
from ..services.config import ConfigService
from ..services.matrix import MatrixService
from ..services.statistics import StatisticsService


class DeprecationWarning(UserWarning):
    """Custom deprecation warning for calculator components."""
    pass


def deprecated(reason: str, version: str = "2.0.0"):
    """Decorator to mark functions as deprecated.
    
    Args:
        reason: Reason for deprecation and suggested alternative
        version: Version when the deprecation was introduced
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__} is deprecated since version {version}. {reason}",
                DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator


class LegacyEnvironmentMapper:
    """Maps legacy environment variables to new configuration format."""

    LEGACY_ENV_MAPPING = {
        # Legacy -> New format
        'CALCULATOR_PRECISION': 'CALC_PRECISION',
        'CALCULATOR_CACHE_SIZE': 'CALC_PERF_CACHE_SIZE',
        'CALCULATOR_MAX_COMPUTATION_TIME': 'CALC_PERF_MAX_COMPUTATION_TIME_SECONDS',
        'CALCULATOR_MAX_MEMORY_MB': 'CALC_PERF_MAX_MEMORY_MB',
        'CALCULATOR_ENABLE_CURRENCY_CONVERSION': 'CALC_FEATURE_ENABLE_CURRENCY_CONVERSION',
        'CALCULATOR_LOG_LEVEL': 'CALC_LOGGING_LOG_LEVEL',
        'CALCULATOR_CACHE_TTL': 'CALC_PERF_CACHE_TTL_SECONDS',
        'CALCULATOR_ENABLE_CACHING': 'CALC_FEATURE_ENABLE_CACHING',
        'CALCULATOR_ENABLE_PERFORMANCE_MONITORING': 'CALC_FEATURE_ENABLE_PERFORMANCE_MONITORING',
        'CALCULATOR_ENABLE_ADVANCED_CALCULUS': 'CALC_FEATURE_ENABLE_ADVANCED_CALCULUS',
        'CALCULATOR_ENABLE_MATRIX_OPERATIONS': 'CALC_FEATURE_ENABLE_MATRIX_OPERATIONS'
    }

    @classmethod
    def map_legacy_environment(cls) -> Dict[str, str]:
        """Map legacy environment variables to new format.
        
        Returns:
            Dictionary of mapped environment variables
        """
        mapped_env = {}

        for legacy_key, new_key in cls.LEGACY_ENV_MAPPING.items():
            if legacy_key in os.environ:
                # Issue deprecation warning
                warnings.warn(
                    f"Environment variable '{legacy_key}' is deprecated. "
                    f"Use '{new_key}' instead.",
                    DeprecationWarning,
                    stacklevel=3
                )

                # Map to new format if new key doesn't exist
                if new_key not in os.environ:
                    mapped_env[new_key] = os.environ[legacy_key]

        return mapped_env

    @classmethod
    def apply_legacy_mapping(cls) -> None:
        """Apply legacy environment variable mapping."""
        mapped_env = cls.map_legacy_environment()
        os.environ.update(mapped_env)


class LegacyServerInterface:
    """Provides backward compatibility for the old server interface."""

    def __init__(self, config: Optional[ConfigService] = None):
        """Initialize legacy server interface.
        
        Args:
            config: Optional configuration service
        """
        # Apply legacy environment mapping
        LegacyEnvironmentMapper.apply_legacy_mapping()

        self.config = config or ConfigService()

        # Initialize services
        self.arithmetic_service = ArithmeticService(self.config)
        self.matrix_service = MatrixService(self.config)
        self.statistics_service = StatisticsService(self.config)
        self.calculus_service = CalculusService(self.config)

    @deprecated("Use calculator.server.app.create_calculator_app() instead")
    def create_server(self):
        """Create server using legacy interface.
        
        Returns:
            Server application instance
        """
        from .app import create_calculator_app
        return create_calculator_app()

    @deprecated("Use ArithmeticService.process() instead")
    async def calculate(self, operation: str, **kwargs) -> Any:
        """Legacy calculation interface.
        
        Args:
            operation: Operation name
            **kwargs: Operation parameters
            
        Returns:
            Calculation result
        """
        # Route to appropriate service based on operation
        if operation in ['add', 'subtract', 'multiply', 'divide', 'power', 'sqrt',
                        'factorial', 'gcd', 'lcm', 'modulo', 'absolute', 'round_number',
                        'floor', 'ceil', 'logarithm', 'exponential', 'sine', 'cosine',
                        'tangent', 'arcsine', 'arccosine', 'arctangent',
                        'hyperbolic_sine', 'hyperbolic_cosine', 'hyperbolic_tangent']:
            return await self.arithmetic_service.process(operation, kwargs)

        elif operation in ['matrix_add', 'matrix_subtract', 'matrix_multiply',
                          'matrix_transpose', 'matrix_determinant', 'matrix_inverse',
                          'matrix_eigenvalues', 'matrix_eigenvectors', 'matrix_rank',
                          'matrix_trace', 'matrix_norm', 'solve_linear_system']:
            # Remove 'matrix_' prefix for service call
            service_operation = operation.replace('matrix_', '') if operation.startswith('matrix_') else operation
            return await self.matrix_service.process(service_operation, kwargs)

        elif operation in ['mean', 'median', 'mode', 'variance', 'std_dev',
                          'range', 'quartiles', 'percentile', 'correlation',
                          'covariance', 'histogram', 't_test', 'anova']:
            return await self.statistics_service.process(operation, kwargs)

        elif operation in ['derivative', 'integral', 'limit', 'series_expansion',
                          'taylor_series', 'fourier_series', 'numerical_derivative',
                          'numerical_integral', 'solve_ode']:
            return await self.calculus_service.process(operation, kwargs)

        else:
            raise CalculatorError(f"Unknown operation: {operation}")

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status in legacy format.
        
        Returns:
            Health status dictionary
        """
        return {
            'status': 'healthy',
            'services': {
                'arithmetic': 'available',
                'matrix': 'available',
                'statistics': 'available',
                'calculus': 'available'
            },
            'repositories': {
                'cache': 'available',
                'constants': 'available',
                'currency': 'available' if self.config.is_currency_conversion_enabled() else 'disabled'
            },
            'configuration': {
                'precision': self.config.get_precision(),
                'cache_enabled': self.config.is_caching_enabled(),
                'performance_monitoring': self.config.is_performance_monitoring_enabled()
            }
        }


class LegacyImportCompatibility:
    """Provides backward compatibility for import paths."""

    @staticmethod
    def setup_legacy_imports():
        """Setup legacy import compatibility."""
        import sys

        # Create compatibility modules
        legacy_modules = {
            'calculator.core.basic': LegacyBasicModule(),
            'calculator.core.matrix': LegacyMatrixModule(),
            'calculator.core.statistics': LegacyStatisticsModule(),
            'calculator.core.calculus': LegacyCalculusModule()
        }

        for module_name, module_obj in legacy_modules.items():
            sys.modules[module_name] = module_obj


class LegacyBasicModule(ModuleType):
    """Legacy basic operations module."""

    def __init__(self):
        super().__init__('calculator.core.basic')
        self._service = ArithmeticService()

    @deprecated("Use ArithmeticService.process('add', {'numbers': numbers}) instead")
    async def add_numbers(self, numbers):
        return await self._service.process('add', {'numbers': numbers})

    @deprecated("Use ArithmeticService.process('subtract', {'a': a, 'b': b}) instead")
    async def subtract_numbers(self, a, b):
        return await self._service.process('subtract', {'a': a, 'b': b})

    @deprecated("Use ArithmeticService.process('multiply', {'numbers': numbers}) instead")
    async def multiply_numbers(self, numbers):
        return await self._service.process('multiply', {'numbers': numbers})

    @deprecated("Use ArithmeticService.process('divide', {'a': a, 'b': b}) instead")
    async def divide_numbers(self, a, b):
        return await self._service.process('divide', {'a': a, 'b': b})


class LegacyMatrixModule(ModuleType):
    """Legacy matrix operations module."""

    def __init__(self):
        super().__init__('calculator.core.matrix')
        self._service = MatrixService()

    @deprecated("Use MatrixService.process('add', {'matrix_a': a, 'matrix_b': b}) instead")
    async def add_matrices(self, matrix_a, matrix_b):
        return await self._service.process('add', {'matrix_a': matrix_a, 'matrix_b': matrix_b})

    @deprecated("Use MatrixService.process('multiply', {'matrix_a': a, 'matrix_b': b}) instead")
    async def multiply_matrices(self, matrix_a, matrix_b):
        return await self._service.process('multiply', {'matrix_a': matrix_a, 'matrix_b': matrix_b})

    @deprecated("Use MatrixService.process('determinant', {'matrix': matrix}) instead")
    async def calculate_determinant(self, matrix):
        return await self._service.process('determinant', {'matrix': matrix})


class LegacyStatisticsModule(ModuleType):
    """Legacy statistics operations module."""

    def __init__(self):
        super().__init__('calculator.core.statistics')
        self._service = StatisticsService()

    @deprecated("Use StatisticsService.process('mean', {'data': data}) instead")
    async def calculate_mean(self, data):
        return await self._service.process('mean', {'data': data})

    @deprecated("Use StatisticsService.process('median', {'data': data}) instead")
    async def calculate_median(self, data):
        return await self._service.process('median', {'data': data})

    @deprecated("Use StatisticsService.process('std_dev', {'data': data}) instead")
    async def calculate_std_dev(self, data):
        return await self._service.process('std_dev', {'data': data, 'population': False})


class LegacyCalculusModule(ModuleType):
    """Legacy calculus operations module."""

    def __init__(self):
        super().__init__('calculator.core.calculus')
        self._service = CalculusService()

    @deprecated("Use CalculusService.process('derivative', params) instead")
    async def calculate_derivative(self, expression, variable):
        return await self._service.process('derivative', {
            'expression': expression,
            'variable': variable
        })

    @deprecated("Use CalculusService.process('integral', params) instead")
    async def calculate_integral(self, expression, variable, lower_limit=None, upper_limit=None):
        params = {'expression': expression, 'variable': variable}
        if lower_limit is not None:
            params['lower_limit'] = lower_limit
        if upper_limit is not None:
            params['upper_limit'] = upper_limit
        return await self._service.process('integral', params)


# Legacy server creation function
@deprecated("Use calculator.server.app.create_calculator_app() instead")
def create_server(config: Optional[ConfigService] = None):
    """Create server using legacy interface.
    
    Args:
        config: Optional configuration service
        
    Returns:
        Server application instance
    """
    legacy_interface = LegacyServerInterface(config)
    return legacy_interface.create_server()


# Legacy main function
@deprecated("Use calculator.server.app.run_calculator_server() instead")
async def main():
    """Legacy main function."""
    from .app import run_calculator_server
    run_calculator_server()


# Setup legacy imports when module is imported
LegacyImportCompatibility.setup_legacy_imports()
