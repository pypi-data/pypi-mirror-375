"""Configuration service for dependency injection."""

from typing import Any, Optional

from calculator.core.config.loader import config_loader
from calculator.core.config.settings import CalculatorConfig


class ConfigService:
    """Configuration service providing centralized access to settings.

    This service acts as a facade for the configuration system,
    providing easy access to configuration values throughout the application.
    """

    def __init__(self, config: Optional[CalculatorConfig] = None):
        """Initialize configuration service.

        Args:
            config: Optional configuration instance (will load from environment if not provided)
        """
        if config is None:
            self._config = config_loader.load_config()
        else:
            self._config = config

    @property
    def config(self) -> CalculatorConfig:
        """Get the configuration instance."""
        return self._config

    def get_precision(self) -> int:
        """Get calculation precision."""
        return self._config.precision

    def get_cache_size(self) -> int:
        """Get cache size."""
        return self._config.cache_size

    def get_max_computation_time(self) -> int:
        """Get maximum computation time in seconds."""
        return self._config.performance.max_computation_time

    def get_max_memory_mb(self) -> int:
        """Get maximum memory usage in MB."""
        return self._config.performance.max_memory_mb

    def get_cache_ttl(self) -> int:
        """Get cache TTL in seconds."""
        return self._config.performance.cache_ttl_seconds

    def is_caching_enabled(self) -> bool:
        """Check if caching is enabled."""
        return self._config.features.enable_caching

    def is_currency_conversion_enabled(self) -> bool:
        """Check if currency conversion is enabled."""
        return self._config.features.enable_currency_conversion

    def is_advanced_calculus_enabled(self) -> bool:
        """Check if advanced calculus is enabled."""
        return self._config.features.enable_advanced_calculus

    def is_matrix_operations_enabled(self) -> bool:
        """Check if matrix operations are enabled."""
        return self._config.features.enable_matrix_operations

    def is_performance_monitoring_enabled(self) -> bool:
        """Check if performance monitoring is enabled."""
        return self._config.features.enable_performance_monitoring

    def get_log_level(self) -> str:
        """Get logging level."""
        return self._config.logging.log_level

    def get_enabled_tool_groups(self) -> list:
        """Get list of enabled tool groups."""
        return self._config.tools.enabled_tool_groups

    def is_tool_group_enabled(self, group: str) -> bool:
        """Check if a tool group is enabled.

        Args:
            group: Tool group name

        Returns:
            True if the tool group is enabled
        """
        # Use the same logic as get_enabled_tool_groups to ensure consistency
        enabled_groups = self.get_enabled_tool_groups()
        return group in enabled_groups

    def is_tool_disabled(self, tool_name: str) -> bool:
        """Check if a specific tool is disabled.

        Args:
            tool_name: Name of the tool

        Returns:
            True if the tool is disabled
        """
        return self._config.is_tool_disabled(tool_name)

    def get_currency_api_key(self) -> Optional[str]:
        """Get currency API key."""
        return self._config.external_apis.currency_api_key

    def is_currency_fallback_enabled(self) -> bool:
        """Check if currency fallback is enabled."""
        return self._config.external_apis.currency_fallback_enabled

    def get_max_input_size(self) -> int:
        """Get maximum input size."""
        return self._config.security.max_input_size

    def get_rate_limit_per_minute(self) -> int:
        """Get rate limit per minute."""
        return self._config.security.rate_limit_per_minute

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key with dot notation support.

        Args:
            key: Configuration key (supports dot notation like 'performance.max_memory_mb')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        try:
            parts = key.split(".")
            current = self._config

            for part in parts:
                current = getattr(current, part)

            return current
        except AttributeError:
            return default

    def reload_config(self) -> None:
        """Reload configuration from environment variables."""
        self._config = config_loader.reload_config()

    def validate_config(self) -> bool:
        """Validate the current configuration.

        Returns:
            True if configuration is valid

        Raises:
            ConfigurationError: If configuration is invalid
        """
        return config_loader.validate_configuration(self._config)

    def get_config_summary(self) -> dict:
        """Get a summary of the current configuration.

        Returns:
            Dictionary containing configuration summary
        """
        return {
            "precision": self.get_precision(),
            "cache_size": self.get_cache_size(),
            "max_computation_time": self.get_max_computation_time(),
            "max_memory_mb": self.get_max_memory_mb(),
            "cache_ttl": self.get_cache_ttl(),
            "features": {
                "caching": self.is_caching_enabled(),
                "currency_conversion": self.is_currency_conversion_enabled(),
                "advanced_calculus": self.is_advanced_calculus_enabled(),
                "matrix_operations": self.is_matrix_operations_enabled(),
                "performance_monitoring": self.is_performance_monitoring_enabled(),
            },
            "tool_groups": self.get_enabled_tool_groups(),
            "log_level": self.get_log_level(),
        }
    def get_enabled_tool_groups(self) -> list[str]:
        """Get list of enabled tool groups from configuration.
        
        This method checks both the static configuration and environment variables
        to determine which tool groups should be enabled.
        
        Returns:
            List of enabled tool group names
        """
        from calculator.core.tool_groups import ToolGroupConfig, ToolGroupRegistry
        
        # Create tool group configuration and load from environment
        registry = ToolGroupRegistry()
        tool_config = ToolGroupConfig(registry)
        tool_config.load_from_environment()
        
        # If only basic group is enabled (default), use static configuration
        enabled_groups = [group.value for group in tool_config.enabled_groups]
        if len(enabled_groups) == 1 and "basic" in enabled_groups:
            # Fall back to static configuration
            return self._config.tools.enabled_tool_groups
        
        return enabled_groups