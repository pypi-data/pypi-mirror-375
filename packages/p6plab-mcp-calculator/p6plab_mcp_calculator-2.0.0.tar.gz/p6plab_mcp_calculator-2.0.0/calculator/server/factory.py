"""Tool registration factory for MCP tools."""

import asyncio
from typing import Any, Callable, Dict, List, Optional, Type

from fastmcp import FastMCP
from loguru import logger
from pydantic import BaseModel

from ..core.base.operation import BaseOperation
from ..core.errors.exceptions import ComputationError, ValidationError
from ..core.errors.handlers import handle_operation_errors
from ..services.config import ConfigService


class ToolRegistrationFactory:
    """Factory for registering MCP tools with standardized patterns."""

    def __init__(self, server: FastMCP, config_service: ConfigService):
        """Initialize tool registration factory.

        Args:
            server: FastMCP server instance
            config_service: Configuration service
        """
        self.server = server
        self.config = config_service
        self.registered_tools = {}
        self.tool_groups = {}
        self.registration_stats = {
            "total_registered": 0,
            "enabled_tools": 0,
            "disabled_tools": 0,
            "groups": {},
        }

    def register_operation_tool(
        self,
        name: str,
        operation_class: Type[BaseOperation],
        description: str,
        input_schema: Type[BaseModel],
        tool_group: str = "basic",
        examples: Optional[List[Dict[str, Any]]] = None,
        tags: Optional[List[str]] = None,
    ) -> None:
        """Register a mathematical operation as an MCP tool.

        Args:
            name: Tool name
            operation_class: Operation class to instantiate
            description: Tool description
            input_schema: Pydantic model for input validation
            tool_group: Tool group for filtering
            examples: Example usage
            tags: Tool tags for categorization
        """
        # Check if tool group is enabled
        if not self._is_tool_enabled(tool_group, name):
            logger.debug(f"Tool {name} disabled by configuration")
            self.registration_stats["disabled_tools"] += 1
            return

        # Create the tool handler with error handling
        @handle_operation_errors(name)
        async def tool_handler(params: input_schema) -> Dict[str, Any]:
            try:
                # Create operation instance
                operation = operation_class(
                    config=self.config, cache=getattr(self, "cache_service", None)
                )

                # Validate input
                if not operation.validate_input(params):
                    raise ValidationError(f"Invalid input for operation {name}")

                # Execute operation
                result = await operation.execute(params)

                # Format result consistently
                return operation.format_result(
                    result,
                    {
                        "tool_name": name,
                        "tool_group": tool_group,
                        "operation_class": operation_class.__name__,
                    },
                )

            except Exception as e:
                logger.error(f"Error in tool {name}: {str(e)}")
                return self._handle_tool_error(e, name, params)

        # Register with FastMCP
        self.server.tool(name=name, description=description)(tool_handler)

        # Store tool metadata
        self.registered_tools[name] = {
            "handler": tool_handler,
            "operation_class": operation_class,
            "description": description,
            "input_schema": input_schema,
            "tool_group": tool_group,
            "examples": examples or [],
            "tags": tags or [],
            "enabled": True,
        }

        # Update group tracking
        if tool_group not in self.tool_groups:
            self.tool_groups[tool_group] = []
        self.tool_groups[tool_group].append(name)

        # Update statistics
        self.registration_stats["total_registered"] += 1
        self.registration_stats["enabled_tools"] += 1
        if tool_group not in self.registration_stats["groups"]:
            self.registration_stats["groups"][tool_group] = 0
        self.registration_stats["groups"][tool_group] += 1

        logger.debug(f"Registered tool: {name} in group {tool_group}")

    def register_service_tools(
        self,
        service_name: str,
        service_instance: Any,
        tool_definitions: List[Dict[str, Any]],
        tool_group: str = "basic",
    ) -> None:
        """Register multiple tools from a service.

        Args:
            service_name: Name of the service
            service_instance: Service instance
            tool_definitions: List of tool definition dictionaries
            tool_group: Default tool group
        """
        for tool_def in tool_definitions:
            name = tool_def["name"]
            operation = tool_def["operation"]
            description = tool_def["description"]
            input_schema = tool_def["input_schema"]
            group = tool_def.get("tool_group", tool_group)
            examples = tool_def.get("examples")
            tags = tool_def.get("tags", [service_name])

            # Check if tool is enabled
            if not self._is_tool_enabled(group, name):
                logger.debug(f"Service tool {name} disabled by configuration")
                self.registration_stats["disabled_tools"] += 1
                continue

            # Create handler that delegates to service
            def create_service_handler(op_name=operation):
                @handle_operation_errors(name)
                async def service_handler(params: input_schema) -> Dict[str, Any]:
                    try:
                        # Call service method
                        result = await service_instance.process(op_name, params.dict())

                        return {
                            "success": True,
                            "result": result,
                            "service": service_name,
                            "operation": op_name,
                            "tool_name": name,
                        }

                    except Exception as e:
                        logger.error(f"Error in service tool {name}: {str(e)}")
                        return self._handle_tool_error(e, name, params)

                return service_handler

            handler = create_service_handler()

            # Register with FastMCP
            self.server.tool(name=name, description=description)(handler)

            # Store tool metadata
            self.registered_tools[name] = {
                "handler": handler,
                "service": service_name,
                "operation": operation,
                "description": description,
                "input_schema": input_schema,
                "tool_group": group,
                "examples": examples or [],
                "tags": tags,
                "enabled": True,
            }

            # Update group tracking
            if group not in self.tool_groups:
                self.tool_groups[group] = []
            self.tool_groups[group].append(name)

            # Update statistics
            self.registration_stats["total_registered"] += 1
            self.registration_stats["enabled_tools"] += 1
            if group not in self.registration_stats["groups"]:
                self.registration_stats["groups"][group] = 0
            self.registration_stats["groups"][group] += 1

            logger.debug(f"Registered service tool: {name} from {service_name}")

    def register_function_tool(
        self,
        name: str,
        func: Callable,
        description: str,
        input_schema: Type[BaseModel],
        tool_group: str = "basic",
        examples: Optional[List[Dict[str, Any]]] = None,
        tags: Optional[List[str]] = None,
    ) -> None:
        """Register a function as an MCP tool.

        Args:
            name: Tool name
            func: Function to wrap
            description: Tool description
            input_schema: Input validation schema
            tool_group: Tool group
            examples: Usage examples
            tags: Tool tags
        """
        # Check if tool is enabled
        if not self._is_tool_enabled(tool_group, name):
            logger.debug(f"Function tool {name} disabled by configuration")
            self.registration_stats["disabled_tools"] += 1
            return

        # Create handler
        @handle_operation_errors(name)
        async def function_handler(params: input_schema) -> Dict[str, Any]:
            try:
                # Call function with parameters
                if asyncio.iscoroutinefunction(func):
                    result = await func(**params.dict())
                else:
                    result = func(**params.dict())

                return {
                    "success": True,
                    "result": result,
                    "function": func.__name__,
                    "tool_name": name,
                }

            except Exception as e:
                logger.error(f"Error in function tool {name}: {str(e)}")
                return self._handle_tool_error(e, name, params)

        # Register with FastMCP
        self.server.tool(name=name, description=description)(function_handler)

        # Store metadata
        self.registered_tools[name] = {
            "handler": function_handler,
            "function": func,
            "description": description,
            "input_schema": input_schema,
            "tool_group": tool_group,
            "examples": examples or [],
            "tags": tags or [],
            "enabled": True,
        }

        # Update tracking
        if tool_group not in self.tool_groups:
            self.tool_groups[tool_group] = []
        self.tool_groups[tool_group].append(name)

        # Update statistics
        self.registration_stats["total_registered"] += 1
        self.registration_stats["enabled_tools"] += 1
        if tool_group not in self.registration_stats["groups"]:
            self.registration_stats["groups"][tool_group] = 0
        self.registration_stats["groups"][tool_group] += 1

        logger.debug(f"Registered function tool: {name}")

    def register_batch_tools(self, tool_batch: List[Dict[str, Any]]) -> None:
        """Register multiple tools from a batch definition.

        Args:
            tool_batch: List of tool definitions
        """
        for tool_def in tool_batch:
            registration_type = tool_def.get("type", "operation")

            if registration_type == "operation":
                self.register_operation_tool(**tool_def)
            elif registration_type == "function":
                self.register_function_tool(**tool_def)
            elif registration_type == "service":
                self.register_service_tools(**tool_def)
            else:
                logger.warning(f"Unknown tool registration type: {registration_type}")

    def _is_tool_enabled(self, tool_group: str, tool_name: str = None) -> bool:
        """Check if a tool or tool group is enabled.

        Args:
            tool_group: Tool group name
            tool_name: Specific tool name (optional)

        Returns:
            True if tool is enabled
        """
        # Check if specific tool is disabled
        if tool_name and self.config.is_tool_disabled(tool_name):
            return False

        # Check if tool group is enabled
        return self.config.is_tool_group_enabled(tool_group)

    def _handle_tool_error(self, error: Exception, tool_name: str, params: Any) -> Dict[str, Any]:
        """Handle tool execution errors consistently.

        Args:
            error: Exception that occurred
            tool_name: Name of the tool
            params: Tool parameters

        Returns:
            Standardized error response
        """
        error_type = type(error).__name__

        if isinstance(error, ValidationError):
            return {
                "success": False,
                "error": "validation_error",
                "message": str(error),
                "tool_name": tool_name,
                "error_type": error_type,
            }
        elif isinstance(error, ComputationError):
            return {
                "success": False,
                "error": "computation_error",
                "message": str(error),
                "tool_name": tool_name,
                "error_type": error_type,
            }
        else:
            return {
                "success": False,
                "error": "internal_error",
                "message": "An unexpected error occurred",
                "tool_name": tool_name,
                "error_type": error_type,
            }

    def get_registered_tools(self) -> Dict[str, Any]:
        """Get information about all registered tools.

        Returns:
            Dictionary with tool information
        """
        return {
            "tools": {
                name: {
                    "description": info["description"],
                    "tool_group": info["tool_group"],
                    "tags": info["tags"],
                    "enabled": info["enabled"],
                    "examples": info["examples"],
                }
                for name, info in self.registered_tools.items()
            },
            "groups": self.tool_groups,
            "statistics": self.registration_stats,
        }

    def get_tools_by_group(self, group: str) -> List[str]:
        """Get tools in a specific group.

        Args:
            group: Tool group name

        Returns:
            List of tool names in the group
        """
        return self.tool_groups.get(group, [])

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool information or None if not found
        """
        if tool_name not in self.registered_tools:
            return None

        info = self.registered_tools[tool_name].copy()
        # Remove handler reference for serialization
        info.pop("handler", None)
        return info

    def get_registration_stats(self) -> Dict[str, Any]:
        """Get tool registration statistics.

        Returns:
            Dictionary with registration statistics
        """
        return self.registration_stats.copy()

    def enable_tool(self, tool_name: str) -> bool:
        """Enable a specific tool.

        Args:
            tool_name: Name of the tool to enable

        Returns:
            True if tool was enabled
        """
        if tool_name in self.registered_tools:
            self.registered_tools[tool_name]["enabled"] = True
            return True
        return False

    def disable_tool(self, tool_name: str) -> bool:
        """Disable a specific tool.

        Args:
            tool_name: Name of the tool to disable

        Returns:
            True if tool was disabled
        """
        if tool_name in self.registered_tools:
            self.registered_tools[tool_name]["enabled"] = False
            return True
        return False

    def enable_tool_group(self, group: str) -> int:
        """Enable all tools in a group.

        Args:
            group: Tool group name

        Returns:
            Number of tools enabled
        """
        count = 0
        for tool_name in self.tool_groups.get(group, []):
            if self.enable_tool(tool_name):
                count += 1
        return count

    def disable_tool_group(self, group: str) -> int:
        """Disable all tools in a group.

        Args:
            group: Tool group name

        Returns:
            Number of tools disabled
        """
        count = 0
        for tool_name in self.tool_groups.get(group, []):
            if self.disable_tool(tool_name):
                count += 1
        return count

    def validate_tool_definitions(self, tool_definitions: List[Dict[str, Any]]) -> List[str]:
        """Validate tool definitions before registration.

        Args:
            tool_definitions: List of tool definitions to validate

        Returns:
            List of validation errors (empty if all valid)
        """
        errors = []

        for i, tool_def in enumerate(tool_definitions):
            # Check required fields
            required_fields = ["name", "description"]
            for field in required_fields:
                if field not in tool_def:
                    errors.append(f"Tool {i}: Missing required field '{field}'")

            # Check tool name uniqueness
            if "name" in tool_def and tool_def["name"] in self.registered_tools:
                errors.append(f"Tool {i}: Name '{tool_def['name']}' already registered")

            # Validate tool type
            tool_type = tool_def.get("type", "operation")
            if tool_type not in ["operation", "function", "service"]:
                errors.append(f"Tool {i}: Invalid type '{tool_type}'")

            # Type-specific validation
            if tool_type == "operation":
                if "operation_class" not in tool_def:
                    errors.append(f"Tool {i}: Missing 'operation_class' for operation tool")
                if "input_schema" not in tool_def:
                    errors.append(f"Tool {i}: Missing 'input_schema' for operation tool")

            elif tool_type == "function":
                if "func" not in tool_def:
                    errors.append(f"Tool {i}: Missing 'func' for function tool")
                if "input_schema" not in tool_def:
                    errors.append(f"Tool {i}: Missing 'input_schema' for function tool")

            elif tool_type == "service":
                if "service_instance" not in tool_def:
                    errors.append(f"Tool {i}: Missing 'service_instance' for service tool")
                if "tool_definitions" not in tool_def:
                    errors.append(f"Tool {i}: Missing 'tool_definitions' for service tool")

        return errors

    def generate_tool_documentation(self) -> Dict[str, Any]:
        """Generate documentation for all registered tools.

        Returns:
            Dictionary with tool documentation
        """
        documentation = {
            "overview": {
                "total_tools": self.registration_stats["total_registered"],
                "enabled_tools": self.registration_stats["enabled_tools"],
                "tool_groups": list(self.tool_groups.keys()),
            },
            "groups": {},
            "tools": {},
        }

        # Group documentation
        for group, tools in self.tool_groups.items():
            documentation["groups"][group] = {
                "tool_count": len(tools),
                "tools": tools,
                "description": f"Tools in the {group} category",
            }

        # Individual tool documentation
        for name, info in self.registered_tools.items():
            documentation["tools"][name] = {
                "name": name,
                "description": info["description"],
                "group": info["tool_group"],
                "tags": info["tags"],
                "examples": info["examples"],
                "enabled": info["enabled"],
                "input_schema": info["input_schema"].__name__
                if hasattr(info["input_schema"], "__name__")
                else str(info["input_schema"]),
            }

        return documentation
