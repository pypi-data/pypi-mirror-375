"""Calculator server module with backward compatibility."""

# Import new architecture components
from .app import CalculatorApp, create_calculator_app, run_calculator_server

# Import compatibility layer
# Ensure legacy imports work
from .compatibility import (
    LegacyEnvironmentMapper,
    LegacyImportCompatibility,
    LegacyServerInterface,
    create_server,  # Legacy function
    main,  # Legacy main function
)
from .factory import ToolRegistrationFactory
from .middleware import MiddlewareStack

LegacyImportCompatibility.setup_legacy_imports()

# MCP server instance for deployment testing (lazy initialization)
def get_mcp_server():
    """Get MCP server instance for testing purposes."""
    try:
        from calculator.server.app import create_server
        server = create_server()
        return server.get_server()
    except Exception as e:
        # Return None if server creation fails during import
        return None

# For backward compatibility, provide mcp as a function call
mcp = get_mcp_server

# Export main components
__all__ = [
    # New architecture
    "create_calculator_app",
    "run_calculator_server",
    "CalculatorApp",
    "ToolRegistrationFactory",
    "MiddlewareStack",
    # Legacy compatibility
    "create_server",
    "main",
    "LegacyServerInterface",
    "LegacyEnvironmentMapper",
    # MCP server instance
    "mcp",
]

# Legacy compatibility: make main available at module level
main = main
