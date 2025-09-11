"""Scientific Calculator MCP Server - Refactored Architecture.

This module provides a comprehensive mathematical computation server with
modular architecture, enhanced performance, and backward compatibility.
"""

# Version information
__version__ = "2.0.0"
__author__ = "Calculator Development Team"
__description__ = "Scientific Calculator MCP Server with Modular Architecture"

# Import main server components
from .core.config import CalculatorConfig

# Import core components
from .core.errors import CalculatorError, ComputationError, ValidationError

# Import repositories
from .repositories import CacheRepository, ConstantsRepository, CurrencyRepository
from .server import CalculatorApp, create_calculator_app, run_calculator_server

# Legacy compatibility imports
from .server.compatibility import create_server, main

# Import services for direct use
from .services import (
    ArithmeticService,
    CalculusService,
    ConfigService,
    MatrixService,
    StatisticsService,
)

# Export main API
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__description__",
    # Main server components
    "create_calculator_app",
    "run_calculator_server",
    "CalculatorApp",
    # Services
    "ArithmeticService",
    "MatrixService",
    "StatisticsService",
    "CalculusService",
    "ConfigService",
    # Core components
    "CalculatorError",
    "ValidationError",
    "ComputationError",
    "CalculatorConfig",
    # Repositories
    "CacheRepository",
    "ConstantsRepository",
    "CurrencyRepository",
    # Legacy compatibility
    "create_server",
    "main",
]


# Ensure backward compatibility for legacy imports
def __getattr__(name):
    """Handle legacy attribute access."""
    if name == "server":
        # Legacy access to server module
        from . import server

        return server
    elif name == "core":
        # Legacy access to core module
        from . import core

        return core
    elif name == "services":
        # Legacy access to services module
        from . import services

        return services
    elif name == "repositories":
        # Legacy access to repositories module
        from . import repositories

        return repositories

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
