"""Scientific Calculator MCP Server - Refactored Architecture.

This is the main entry point for the refactored Scientific Calculator MCP Server.
It uses the new modular architecture with services, repositories, and strategies.
"""

import sys

from loguru import logger

from calculator.core.monitoring.logging import configure_logging_from_config

# Import the new server architecture
from calculator.server.app import create_server
from calculator.services.config import ConfigService


def main():
    """Main entry point for the Scientific Calculator MCP Server."""
    try:
        # Initialize configuration first
        config_service = ConfigService()

        # Configure logging based on configuration
        configure_logging_from_config(config_service)

        logger.info("Starting Scientific Calculator MCP Server (Refactored)")
        logger.info("=" * 60)

        # Create and initialize the server
        calculator_server = create_server()

        # Get the FastMCP server instance
        mcp_server = calculator_server.get_server()

        logger.info("Scientific Calculator MCP Server is ready!")
        logger.info("Server initialized with modular architecture")
        logger.info("=" * 60)

        # Return the server for FastMCP to run
        return mcp_server

    except Exception as e:
        logger.error(f"Failed to start Scientific Calculator MCP Server: {e}")
        logger.exception("Startup error details:")
        sys.exit(1)


# For backward compatibility with the original server.py
if __name__ == "__main__":
    server = main()
    # If running directly, the server would be started by FastMCP framework
else:
    # When imported as a module, return the server
    mcp = main()
