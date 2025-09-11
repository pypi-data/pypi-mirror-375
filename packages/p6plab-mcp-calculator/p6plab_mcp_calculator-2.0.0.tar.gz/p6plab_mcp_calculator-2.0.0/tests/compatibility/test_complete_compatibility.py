"""Comprehensive backward compatibility tests."""

import os
import warnings
from unittest.mock import patch

import pytest

from calculator.server.compatibility import (
    LegacyEnvironmentMapper,
    LegacyServerInterface,
    create_server,
    main,
)
from calculator.services.config import ConfigService


class TestLegacyEnvironmentMapping:
    """Test legacy environment variable mapping."""

    def test_legacy_env_mapping_complete(self):
        """Test that all legacy environment variables are mapped correctly."""
        legacy_vars = {
            "CALCULATOR_PRECISION": "12",
            "CALCULATOR_CACHE_SIZE": "2000",
            "CALCULATOR_MAX_COMPUTATION_TIME": "45",
            "CALCULATOR_MAX_MEMORY_MB": "1024",
            "CALCULATOR_ENABLE_CURRENCY_CONVERSION": "true",
            "CALCULATOR_LOG_LEVEL": "DEBUG",
            "CALCULATOR_CACHE_TTL": "7200",
            "CALCULATOR_ENABLE_CACHING": "false",
            "CALCULATOR_ENABLE_PERFORMANCE_MONITORING": "true",
            "CALCULATOR_ENABLE_ADVANCED_CALCULUS": "false",
            "CALCULATOR_ENABLE_MATRIX_OPERATIONS": "true",
        }

        with patch.dict(os.environ, legacy_vars, clear=False):
            # Test mapping
            mapped = LegacyEnvironmentMapper.map_legacy_environment()

            # Verify all legacy variables are mapped
            assert "CALC_PRECISION" in mapped
            assert mapped["CALC_PRECISION"] == "12"

            assert "CALC_PERF_CACHE_SIZE" in mapped
            assert mapped["CALC_PERF_CACHE_SIZE"] == "2000"

            assert "CALC_PERF_MAX_COMPUTATION_TIME_SECONDS" in mapped
            assert mapped["CALC_PERF_MAX_COMPUTATION_TIME_SECONDS"] == "45"

            assert "CALC_PERF_MAX_MEMORY_MB" in mapped
            assert mapped["CALC_PERF_MAX_MEMORY_MB"] == "1024"

            assert "CALC_FEATURE_ENABLE_CURRENCY_CONVERSION" in mapped
            assert mapped["CALC_FEATURE_ENABLE_CURRENCY_CONVERSION"] == "true"

            assert "CALC_LOGGING_LOG_LEVEL" in mapped
            assert mapped["CALC_LOGGING_LOG_LEVEL"] == "DEBUG"

    def test_legacy_env_deprecation_warnings(self):
        """Test that deprecation warnings are issued for legacy environment variables."""
        with patch.dict(os.environ, {"CALCULATOR_PRECISION": "10"}, clear=False):
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")

                LegacyEnvironmentMapper.map_legacy_environment()

                # Check that deprecation warning was issued
                assert len(w) > 0
                assert any("deprecated" in str(warning.message) for warning in w)
                assert any("CALCULATOR_PRECISION" in str(warning.message) for warning in w)

    def test_legacy_env_no_override_new_vars(self):
        """Test that legacy variables don't override new variables."""
        env_vars = {
            "CALCULATOR_PRECISION": "10",  # Legacy
            "CALC_PRECISION": "15",  # New (should take precedence)
        }

        with patch.dict(os.environ, env_vars, clear=False):
            mapped = LegacyEnvironmentMapper.map_legacy_environment()

            # New variable should not be in mapped (already exists)
            assert "CALC_PRECISION" not in mapped

            # Apply mapping
            LegacyEnvironmentMapper.apply_legacy_mapping()

            # New variable should still have its original value
            assert os.environ.get("CALC_PRECISION") == "15"


class TestLegacyServerInterface:
    """Test legacy server interface compatibility."""

    @pytest.fixture
    def legacy_server(self):
        """Create legacy server interface for testing."""
        return LegacyServerInterface()

    def test_legacy_server_creation(self, legacy_server):
        """Test that legacy server can be created."""
        assert legacy_server is not None
        assert hasattr(legacy_server, "config")
        assert hasattr(legacy_server, "arithmetic_service")
        assert hasattr(legacy_server, "matrix_service")
        assert hasattr(legacy_server, "statistics_service")
        assert hasattr(legacy_server, "calculus_service")

    def test_create_server_deprecation_warning(self, legacy_server):
        """Test that create_server issues deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            server = legacy_server.create_server()

            # Check deprecation warning
            assert len(w) > 0
            assert any("deprecated" in str(warning.message) for warning in w)
            assert server is not None

    @pytest.mark.asyncio
    async def test_legacy_calculate_arithmetic(self, legacy_server):
        """Test legacy calculate interface for arithmetic operations."""
        # Test arithmetic operations
        result = await legacy_server.calculate("add", numbers=[1, 2, 3])
        assert result == 6.0

        result = await legacy_server.calculate("subtract", a=10, b=3)
        assert result == 7.0

        result = await legacy_server.calculate("multiply", numbers=[2, 3, 4])
        assert result == 24.0

        result = await legacy_server.calculate("divide", a=10, b=2)
        assert result == 5.0

    @pytest.mark.asyncio
    async def test_legacy_calculate_matrix(self, legacy_server):
        """Test legacy calculate interface for matrix operations."""
        test_matrix_a = [[1, 2], [3, 4]]
        test_matrix_b = [[5, 6], [7, 8]]

        # Test matrix addition
        result = await legacy_server.calculate(
            "matrix_add", matrix_a=test_matrix_a, matrix_b=test_matrix_b
        )
        assert result == [[6, 8], [10, 12]]

        # Test matrix determinant
        result = await legacy_server.calculate("matrix_determinant", matrix=test_matrix_a)
        assert abs(result - (-2.0)) < 1e-10

    @pytest.mark.asyncio
    async def test_legacy_calculate_statistics(self, legacy_server):
        """Test legacy calculate interface for statistics operations."""
        test_data = [1, 2, 3, 4, 5]

        # Test mean
        result = await legacy_server.calculate("mean", data=test_data)
        assert result == 3.0

        # Test median
        result = await legacy_server.calculate("median", data=test_data)
        assert result == 3.0

    @pytest.mark.asyncio
    async def test_legacy_calculate_unknown_operation(self, legacy_server):
        """Test legacy calculate interface with unknown operation."""
        with pytest.raises(Exception):  # Should raise CalculatorError
            await legacy_server.calculate("unknown_operation", param=123)

    def test_legacy_health_status(self, legacy_server):
        """Test legacy health status format."""
        health = legacy_server.get_health_status()

        # Verify expected structure
        assert "status" in health
        assert "services" in health
        assert "repositories" in health
        assert "configuration" in health

        # Verify services
        services = health["services"]
        assert "arithmetic" in services
        assert "matrix" in services
        assert "statistics" in services
        assert "calculus" in services

        # Verify repositories
        repositories = health["repositories"]
        assert "cache" in repositories
        assert "constants" in repositories
        assert "currency" in repositories

        # Verify configuration
        config = health["configuration"]
        assert "precision" in config
        assert "cache_enabled" in config
        assert "performance_monitoring" in config


class TestLegacyImports:
    """Test legacy import compatibility."""

    def test_legacy_basic_module_import(self):
        """Test that legacy basic module can be imported."""
        try:
            import calculator.core.basic as basic

            assert basic is not None
            assert hasattr(basic, "add_numbers")
            assert hasattr(basic, "subtract_numbers")
            assert hasattr(basic, "multiply_numbers")
            assert hasattr(basic, "divide_numbers")
        except ImportError:
            pytest.fail("Legacy basic module import failed")

    def test_legacy_matrix_module_import(self):
        """Test that legacy matrix module can be imported."""
        try:
            import calculator.core.matrix as matrix

            assert matrix is not None
            assert hasattr(matrix, "add_matrices")
            assert hasattr(matrix, "multiply_matrices")
            assert hasattr(matrix, "calculate_determinant")
        except ImportError:
            pytest.fail("Legacy matrix module import failed")

    def test_legacy_statistics_module_import(self):
        """Test that legacy statistics module can be imported."""
        try:
            import calculator.core.statistics as stats

            assert stats is not None
            assert hasattr(stats, "calculate_mean")
            assert hasattr(stats, "calculate_median")
            assert hasattr(stats, "calculate_std_dev")
        except ImportError:
            pytest.fail("Legacy statistics module import failed")

    def test_legacy_calculus_module_import(self):
        """Test that legacy calculus module can be imported."""
        try:
            import calculator.core.calculus as calculus

            assert calculus is not None
            assert hasattr(calculus, "calculate_derivative")
            assert hasattr(calculus, "calculate_integral")
        except ImportError:
            pytest.fail("Legacy calculus module import failed")

    @pytest.mark.asyncio
    async def test_legacy_function_deprecation_warnings(self):
        """Test that legacy functions issue deprecation warnings."""
        import calculator.core.basic as basic

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # Call legacy function
            result = await basic.add_numbers([1, 2, 3])

            # Check deprecation warning
            assert len(w) > 0
            assert any("deprecated" in str(warning.message) for warning in w)
            assert result == 6.0


class TestLegacyMainFunctions:
    """Test legacy main functions."""

    def test_create_server_function(self):
        """Test legacy create_server function."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            server = create_server()

            # Check deprecation warning
            assert len(w) > 0
            assert any("deprecated" in str(warning.message) for warning in w)
            assert server is not None

    @pytest.mark.asyncio
    async def test_main_function(self):
        """Test legacy main function."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # Mock the run_calculator_server to avoid actually starting server
            with patch("calculator.server.app.run_calculator_server") as mock_run:
                mock_run.return_value = None

                await main()

                # Check deprecation warning
                assert len(w) > 0
                assert any("deprecated" in str(warning.message) for warning in w)

                # Verify that new main function was called
                mock_run.assert_called_once()


class TestConfigurationCompatibility:
    """Test configuration backward compatibility."""

    def test_config_service_with_legacy_env(self):
        """Test ConfigService works with legacy environment variables."""
        legacy_env = {
            "CALCULATOR_PRECISION": "12",
            "CALCULATOR_CACHE_SIZE": "2000",
            "CALCULATOR_MAX_COMPUTATION_TIME": "45",
            "CALCULATOR_ENABLE_CURRENCY_CONVERSION": "true",
        }

        with patch.dict(os.environ, legacy_env, clear=False):
            # Apply legacy mapping
            LegacyEnvironmentMapper.apply_legacy_mapping()

            # Create config service
            config = ConfigService()

            # Verify legacy values are applied
            assert config.get_precision() == 12
            assert config.get_cache_size() == 2000
            assert config.get_max_computation_time() == 45
            assert config.is_currency_conversion_enabled() == True

    def test_config_methods_exist(self):
        """Test that all expected configuration methods exist."""
        config = ConfigService()

        expected_methods = [
            "get_precision",
            "get_cache_size",
            "get_max_computation_time",
            "get_max_memory_mb",
            "get_cache_ttl",
            "is_caching_enabled",
            "is_currency_conversion_enabled",
            "is_advanced_calculus_enabled",
            "is_matrix_operations_enabled",
            "is_performance_monitoring_enabled",
            "get_log_level",
            "get_enabled_tool_groups",
        ]

        for method in expected_methods:
            assert hasattr(config, method), f"Missing configuration method: {method}"
            assert callable(getattr(config, method)), f"Method {method} is not callable"


class TestFullSystemCompatibility:
    """Test full system backward compatibility."""

    @pytest.mark.asyncio
    async def test_end_to_end_legacy_workflow(self):
        """Test complete legacy workflow from server creation to calculation."""
        # Set up legacy environment
        legacy_env = {
            "CALCULATOR_PRECISION": "10",
            "CALCULATOR_CACHE_SIZE": "500",
            "CALCULATOR_LOG_LEVEL": "INFO",
        }

        with patch.dict(os.environ, legacy_env, clear=False):
            with warnings.catch_warnings(record=True):
                warnings.simplefilter("always")

                # Create server using legacy interface
                server_app = create_server()
                assert server_app is not None

                # Create legacy server interface
                legacy_server = LegacyServerInterface()

                # Test calculations
                result = await legacy_server.calculate("add", numbers=[1, 2, 3, 4, 5])
                assert result == 15.0

                # Test health check
                health = legacy_server.get_health_status()
                assert health["status"] == "healthy"

                # Test configuration
                assert legacy_server.config.get_precision() == 10
                assert legacy_server.config.get_cache_size() == 500
                assert legacy_server.config.get_log_level() == "INFO"

    def test_no_breaking_changes_in_public_api(self):
        """Test that no breaking changes exist in public API."""
        # Test that main calculator module can be imported
        import calculator

        # Test that expected attributes exist
        expected_attributes = [
            "__version__",
            "create_calculator_app",
            "run_calculator_server",
            "ArithmeticService",
            "MatrixService",
            "StatisticsService",
            "CalculusService",
            "ConfigService",
            "CalculatorError",
            "create_server",
            "main",  # Legacy functions
        ]

        for attr in expected_attributes:
            assert hasattr(calculator, attr), f"Missing public API attribute: {attr}"

    def test_legacy_module_access(self):
        """Test that legacy module access patterns work."""
        import calculator

        # Test legacy attribute access
        server_module = calculator.server
        assert server_module is not None

        core_module = calculator.core
        assert core_module is not None

        services_module = calculator.services
        assert services_module is not None

        repositories_module = calculator.repositories
        assert repositories_module is not None


class TestMigrationScenarios:
    """Test various migration scenarios."""

    def test_gradual_migration_scenario(self):
        """Test scenario where user gradually migrates from old to new API."""
        # Step 1: User still using legacy environment variables
        legacy_env = {"CALCULATOR_PRECISION": "12"}

        with patch.dict(os.environ, legacy_env, clear=False):
            # Step 2: User creates server using new API but with legacy config
            from calculator import create_calculator_app

            app = create_calculator_app()
            assert app is not None

            # Step 3: Configuration should work with legacy variables
            assert app.config.get_precision() == 12

    def test_mixed_api_usage_scenario(self):
        """Test scenario where user mixes old and new API calls."""
        # User imports both old and new interfaces
        from calculator import create_server
        from calculator.services import ArithmeticService

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")

            # User creates server using legacy method
            legacy_server = create_server()
            assert legacy_server is not None

            # User also uses new service directly
            arithmetic_service = ArithmeticService()
            assert arithmetic_service is not None

    @pytest.mark.asyncio
    async def test_rollback_scenario(self):
        """Test scenario where user needs to rollback to legacy interface."""
        # User switches back to legacy interface
        legacy_server = LegacyServerInterface()

        # All legacy functionality should work
        result = await legacy_server.calculate("add", numbers=[1, 2, 3])
        assert result == 6.0

        health = legacy_server.get_health_status()
        assert health["status"] == "healthy"

        # Configuration should work
        assert legacy_server.config.get_precision() >= 1
