"""Pydantic configuration models for all settings."""

from typing import List, Optional, Set

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class PerformanceConfig(BaseSettings):
    """Performance-related configuration."""

    max_computation_time: int = Field(
        default=30, ge=1, le=300, description="Maximum computation time in seconds"
    )
    max_memory_mb: int = Field(
        default=512, ge=64, le=4096, description="Maximum memory usage in MB"
    )
    cache_ttl_seconds: int = Field(
        default=3600, ge=60, le=86400, description="Cache TTL in seconds"
    )
    max_cache_size: int = Field(default=1000, ge=10, le=10000, description="Maximum cache entries")

    class Config:
        env_prefix = "CALC_PERF_"


class FeatureConfig(BaseSettings):
    """Feature toggle configuration."""

    enable_currency_conversion: bool = Field(
        default=False, description="Enable currency conversion features"
    )
    enable_advanced_calculus: bool = Field(
        default=True, description="Enable advanced calculus operations"
    )
    enable_matrix_operations: bool = Field(default=True, description="Enable matrix operations")
    enable_caching: bool = Field(default=True, description="Enable result caching")
    enable_performance_monitoring: bool = Field(
        default=True, description="Enable performance monitoring"
    )

    class Config:
        env_prefix = "CALC_FEATURE_"


class SecurityConfig(BaseSettings):
    """Security-related configuration."""

    max_input_size: int = Field(
        default=10000, ge=100, le=100000, description="Maximum input size in characters"
    )
    allowed_operations: Set[str] = Field(
        default_factory=set, description="Allowed operations (empty = all allowed)"
    )
    rate_limit_per_minute: int = Field(
        default=1000, ge=1, le=10000, description="Rate limit per minute"
    )

    class Config:
        env_prefix = "CALC_SECURITY_"


class LoggingConfig(BaseSettings):
    """Logging configuration."""

    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="structured", description="Log format (structured or simple)")
    enable_correlation_ids: bool = Field(
        default=True, description="Enable correlation IDs for request tracing"
    )

    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()

    class Config:
        env_prefix = "CALC_LOG_"


class ExternalAPIConfig(BaseSettings):
    """External API configuration."""

    currency_api_key: Optional[str] = Field(default=None, description="Currency API key")
    currency_fallback_enabled: bool = Field(
        default=True, description="Enable currency fallback mechanisms"
    )
    currency_cache_ttl: int = Field(
        default=3600, ge=300, le=86400, description="Currency cache TTL in seconds"
    )

    class Config:
        env_prefix = "CALC_API_"


class ToolConfig(BaseSettings):
    """Tool filtering and grouping configuration."""

    enabled_tool_groups: List[str] = Field(
        default=["basic", "advanced", "matrix", "statistics", "calculus", "complex", "units", "solver", "financial", "currency", "constants"],
        description="Enabled tool groups",
    )
    disabled_tools: List[str] = Field(
        default_factory=list, description="Specifically disabled tools"
    )

    class Config:
        env_prefix = "CALC_TOOLS_"


class CalculatorConfig(BaseSettings):
    """Main configuration model combining all settings."""

    # Legacy environment variables for backward compatibility
    precision: int = Field(default=15, ge=1, le=50, description="Calculation precision")
    cache_size: int = Field(default=1000, ge=10, le=10000, description="Cache size (legacy)")

    # Sub-configurations
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    features: FeatureConfig = Field(default_factory=FeatureConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    external_apis: ExternalAPIConfig = Field(default_factory=ExternalAPIConfig)
    tools: ToolConfig = Field(default_factory=ToolConfig)

    class Config:
        env_prefix = "CALC_"
        case_sensitive = False

    def __init__(self, **kwargs):
        """Initialize configuration with sub-configs."""
        super().__init__(**kwargs)

        # Initialize sub-configurations
        self.performance = PerformanceConfig()
        self.features = FeatureConfig()
        self.security = SecurityConfig()
        self.logging = LoggingConfig()
        self.external_apis = ExternalAPIConfig()
        self.tools = ToolConfig()

    @validator("precision")
    def validate_precision(cls, v):
        """Validate precision value."""
        if v < 1 or v > 50:
            raise ValueError("Precision must be between 1 and 50")
        return v

    def get_legacy_env_mapping(self) -> dict:
        """Get mapping of legacy environment variables to new config."""
        return {
            "CALCULATOR_PRECISION": "precision",
            "CALCULATOR_CACHE_SIZE": "cache_size",
            "CALCULATOR_MAX_COMPUTATION_TIME": "performance.max_computation_time",
            "CALCULATOR_MAX_MEMORY_MB": "performance.max_memory_mb",
            "CALCULATOR_ENABLE_CURRENCY_CONVERSION": "features.enable_currency_conversion",
            "CALCULATOR_LOG_LEVEL": "logging.log_level",
        }

    def is_tool_group_enabled(self, group: str) -> bool:
        """Check if a tool group is enabled."""
        return group in self.tools.enabled_tool_groups

    def is_tool_disabled(self, tool_name: str) -> bool:
        """Check if a specific tool is disabled."""
        return tool_name in self.tools.disabled_tools
