"""Unit tests for configuration system."""

import os
from unittest.mock import patch

import pytest

from calculator.core.config.loader import ConfigLoader
from calculator.core.config.settings import CalculatorConfig
from calculator.services.config import ConfigService


class TestCalculatorConfig:
    """Test cases for CalculatorConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = CalculatorConfig()

        assert config.precision == 15
        assert config.performance.max_computation_time == 30
        assert config.performance.max_memory_mb == 512
        assert config.performance.cache_ttl_seconds == 3600
        assert config.features.enable_currency_conversion is False
        assert config.features.enable_advanced_calculus is True

    def test_environment_variable_override(self):
        """Test configuration override via environment variables."""
        with patch.dict(os.environ, {
            'CALC_PRECISION': '20',
            'CALC_CACHE_SIZE': '2000'
        }):
            config = CalculatorConfig()

            assert config.precision == 20
            assert config.cache_size == 2000
            # Nested config values use their default values since nested env vars aren't supported yet
            assert config.performance.max_computation_time == 30
            assert config.features.enable_currency_conversion is False

    def test_validation_constraints(self):
        """Test configuration validation constraints."""
        # Test precision bounds
        with patch.dict(os.environ, {'CALC_PRECISION': '0'}):
            with pytest.raises(Exception):  # Should fail validation
                CalculatorConfig()

        with patch.dict(os.environ, {'CALC_PRECISION': '100'}):
            with pytest.raises(Exception):  # Should fail validation
                CalculatorConfig()

    def test_tool_groups_configuration(self):
        """Test tool groups configuration."""
        config = CalculatorConfig()

        assert "basic" in config.tools.enabled_tool_groups
        assert "advanced" in config.tools.enabled_tool_groups
        assert "matrix" in config.tools.enabled_tool_groups


class TestConfigLoader:
    """Test cases for ConfigLoader."""

    def test_config_loading(self):
        """Test configuration loading."""
        loader = ConfigLoader()
        config = loader.load_config()

        assert isinstance(config, CalculatorConfig)
        assert config.precision > 0

    def test_config_validation(self):
        """Test configuration validation."""
        loader = ConfigLoader()

        # Should not raise exception for valid config
        config = CalculatorConfig()
        loader.validate_configuration(config)

    def test_environment_mapping(self):
        """Test environment variable mapping."""
        with patch.dict(os.environ, {
            'CALC_PRECISION': '25',
            'CALC_CACHE_SIZE': '2000'
        }):
            loader = ConfigLoader()
            config = loader.load_config()

            assert config.precision == 25
            assert config.cache_size == 2000


class TestConfigService:
    """Test cases for ConfigService."""

    @pytest.fixture
    def config_service(self):
        """Create ConfigService instance for testing."""
        return ConfigService()

    def test_get_precision(self, config_service):
        """Test precision retrieval."""
        precision = config_service.get_precision()
        assert isinstance(precision, int)
        assert precision > 0

    def test_get_cache_size(self, config_service):
        """Test cache size retrieval."""
        cache_size = config_service.get_cache_size()
        assert isinstance(cache_size, int)
        assert cache_size > 0

    def test_get_max_computation_time(self, config_service):
        """Test max computation time retrieval."""
        max_time = config_service.get_max_computation_time()
        assert isinstance(max_time, int)
        assert max_time > 0

    def test_boolean_configurations(self, config_service):
        """Test boolean configuration methods."""
        assert isinstance(config_service.is_caching_enabled(), bool)
        assert isinstance(config_service.is_currency_conversion_enabled(), bool)
        assert isinstance(config_service.is_advanced_calculus_enabled(), bool)
        assert isinstance(config_service.is_matrix_operations_enabled(), bool)
        assert isinstance(config_service.is_performance_monitoring_enabled(), bool)

    def test_get_config_value(self, config_service):
        """Test generic config value retrieval."""
        precision = config_service.get_config_value("precision", 10)
        assert precision >= 10

        # Test default value
        nonexistent = config_service.get_config_value("nonexistent_key", "default")
        assert nonexistent == "default"

    def test_get_config_summary(self, config_service):
        """Test configuration summary."""
        summary = config_service.get_config_summary()

        assert isinstance(summary, dict)
        assert "precision" in summary
        assert "cache_size" in summary
        assert "max_computation_time" in summary
        assert "features" in summary
        assert "tool_groups" in summary

    def test_tool_group_methods(self, config_service):
        """Test tool group configuration methods."""
        enabled_groups = config_service.get_enabled_tool_groups()
        assert isinstance(enabled_groups, list)
        assert len(enabled_groups) > 0

        # Test specific group checks
        assert config_service.is_tool_group_enabled("basic") is True
        assert config_service.is_tool_group_enabled("nonexistent_group") is False
