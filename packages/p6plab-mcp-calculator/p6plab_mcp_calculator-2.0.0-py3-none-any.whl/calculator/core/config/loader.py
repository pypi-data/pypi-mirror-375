"""Configuration loader with environment variable support."""

import os
from typing import Any, Dict, Optional

from loguru import logger

from ..errors.exceptions import ConfigurationError
from .settings import CalculatorConfig


class ConfigLoader:
    """Configuration loader with validation and environment variable support."""

    def __init__(self):
        """Initialize configuration loader."""
        self._config: Optional[CalculatorConfig] = None
        self._legacy_mappings = {}

    def load_config(self, config_dict: Optional[Dict[str, Any]] = None) -> CalculatorConfig:
        """Load configuration from environment variables and optional dictionary.

        Args:
            config_dict: Optional configuration dictionary to override defaults

        Returns:
            Validated configuration instance

        Raises:
            ConfigurationError: If configuration is invalid
        """
        try:
            # Start with environment variables
            config_data = self._load_from_environment()

            # Override with provided dictionary
            if config_dict:
                config_data.update(config_dict)

            # Create and validate configuration
            self._config = CalculatorConfig(**config_data)

            # Handle legacy environment variables
            self._handle_legacy_environment_variables()

            logger.info("Configuration loaded successfully")
            self._log_configuration_summary()

            return self._config

        except Exception as e:
            error_msg = f"Failed to load configuration: {str(e)}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg, context={"original_error": str(e)})

    def get_config(self) -> CalculatorConfig:
        """Get the current configuration.

        Returns:
            Current configuration instance

        Raises:
            ConfigurationError: If configuration hasn't been loaded
        """
        if self._config is None:
            raise ConfigurationError("Configuration not loaded. Call load_config() first.")
        return self._config

    def reload_config(self) -> CalculatorConfig:
        """Reload configuration from environment variables.

        Returns:
            Reloaded configuration instance
        """
        logger.info("Reloading configuration...")
        self._config = None
        return self.load_config()

    def _load_from_environment(self) -> Dict[str, Any]:
        """Load configuration values from environment variables.

        Returns:
            Dictionary of configuration values
        """
        config_data = {}

        # Load main configuration values
        env_mappings = {
            "CALC_PRECISION": ("precision", int),
            "CALC_CACHE_SIZE": ("cache_size", int),
        }

        for env_var, (config_key, type_func) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    config_data[config_key] = type_func(value)
                except ValueError as e:
                    logger.warning(f"Invalid value for {env_var}: {value}. Error: {e}")

        return config_data

    def _handle_legacy_environment_variables(self) -> None:
        """Handle legacy environment variables for backward compatibility."""
        if not self._config:
            return

        legacy_mappings = self._config.get_legacy_env_mapping()

        for legacy_env, config_path in legacy_mappings.items():
            value = os.getenv(legacy_env)
            if value is not None:
                try:
                    self._set_nested_config_value(config_path, value)
                    logger.debug(
                        f"Applied legacy environment variable {legacy_env} -> {config_path}"
                    )
                except Exception as e:
                    logger.warning(
                        f"Failed to apply legacy environment variable {legacy_env}: {e}"
                    )

    def _set_nested_config_value(self, config_path: str, value: str) -> None:
        """Set a nested configuration value using dot notation.

        Args:
            config_path: Dot-separated path to the configuration value
            value: String value to set (will be converted to appropriate type)
        """
        if not self._config:
            return

        parts = config_path.split(".")
        current = self._config

        # Navigate to the parent object
        for part in parts[:-1]:
            current = getattr(current, part)

        # Set the final value with type conversion
        final_key = parts[-1]
        current_value = getattr(current, final_key)

        # Convert value to the same type as the current value
        if isinstance(current_value, bool):
            converted_value = value.lower() in ("true", "1", "yes", "on")
        elif isinstance(current_value, int):
            converted_value = int(value)
        elif isinstance(current_value, float):
            converted_value = float(value)
        else:
            converted_value = value

        setattr(current, final_key, converted_value)

    def _log_configuration_summary(self) -> None:
        """Log a summary of the loaded configuration."""
        if not self._config:
            return

        logger.info("Configuration Summary:")
        logger.info(f"  Precision: {self._config.precision}")
        logger.info(f"  Cache Size: {self._config.cache_size}")
        logger.info(f"  Max Computation Time: {self._config.performance.max_computation_time}s")
        logger.info(f"  Max Memory: {self._config.performance.max_memory_mb}MB")
        logger.info(
            f"  Currency Conversion: {'enabled' if self._config.features.enable_currency_conversion else 'disabled'}"
        )
        logger.info(
            f"  Caching: {'enabled' if self._config.features.enable_caching else 'disabled'}"
        )
        logger.info(f"  Tool Groups: {', '.join(self._config.tools.enabled_tool_groups)}")
        logger.info(f"  Log Level: {self._config.logging.log_level}")

    def validate_configuration(self, config: CalculatorConfig) -> bool:
        """Validate configuration values.

        Args:
            config: Configuration to validate

        Returns:
            True if configuration is valid

        Raises:
            ConfigurationError: If configuration is invalid
        """
        errors = []

        # Validate performance settings
        if config.performance.max_computation_time <= 0:
            errors.append("max_computation_time must be positive")

        if config.performance.max_memory_mb < 64:
            errors.append("max_memory_mb must be at least 64MB")

        if config.performance.cache_ttl_seconds < 60:
            errors.append("cache_ttl_seconds must be at least 60 seconds")

        # Validate precision
        if config.precision < 1 or config.precision > 50:
            errors.append("precision must be between 1 and 50")

        # Validate tool groups
        valid_tool_groups = {
            "basic",
            "advanced",
            "matrix",
            "statistics",
            "calculus",
            "complex",
            "units",
            "solver",
            "financial",
            "currency",
            "constants",
        }
        invalid_groups = set(config.tools.enabled_tool_groups) - valid_tool_groups
        if invalid_groups:
            errors.append(f"Invalid tool groups: {invalid_groups}")

        if errors:
            error_msg = "Configuration validation failed: " + "; ".join(errors)
            raise ConfigurationError(error_msg, context={"validation_errors": errors})

        return True


# Global configuration loader instance
config_loader = ConfigLoader()
