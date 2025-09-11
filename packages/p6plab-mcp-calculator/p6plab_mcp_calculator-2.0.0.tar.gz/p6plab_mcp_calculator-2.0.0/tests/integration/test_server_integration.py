"""Integration tests for server components."""

from unittest.mock import Mock

import pytest

from calculator.repositories.cache import CacheRepository
from calculator.server.app import CalculatorServer
from calculator.services.config import ConfigService


class TestServerIntegration:
    """Integration tests for server components."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration service."""
        config = Mock(spec=ConfigService)
        config.get_cache_size.return_value = 100
        config.get_cache_ttl.return_value = 3600
        config.is_currency_conversion_enabled.return_value = False
        config.is_matrix_operations_enabled.return_value = True
        config.is_advanced_calculus_enabled.return_value = True
        config.is_caching_enabled.return_value = True
        config.is_performance_monitoring_enabled.return_value = True
        config.get_config_summary.return_value = {
            "precision": 15,
            "cache_size": 100,
            "max_computation_time": 30,
            "max_memory_mb": 512,
            "features": {
                "caching": True,
                "currency_conversion": False,
                "advanced_calculus": True,
                "matrix_operations": True,
                "performance_monitoring": True,
            },
            "tool_groups": ["basic", "advanced", "matrix", "statistics", "calculus"],
            "log_level": "INFO",
        }
        config.is_tool_group_enabled.return_value = True
        config.is_tool_disabled.return_value = False
        config.get_enabled_tool_groups.return_value = ["basic", "advanced", "matrix", "statistics", "calculus"]
        return config

    @pytest.fixture
    def server(self, mock_config):
        """Create server instance for testing."""
        server = CalculatorServer()
        server.config_service = mock_config
        return server

    def test_server_initialization(self, server):
        """Test server initialization."""
        # Test that server can be created
        assert server is not None
        assert server.mcp is not None
        assert server.services == {}
        assert server.repositories == {}

    def test_setup_repositories(self, server):
        """Test repository setup."""
        server._setup_repositories()

        # Check that repositories are created
        assert "cache" in server.repositories
        assert isinstance(server.repositories["cache"], CacheRepository)
        assert "constants" in server.repositories

    def test_setup_services(self, server):
        """Test service setup."""
        # Setup repositories first
        server._setup_repositories()

        # Setup services
        server._setup_services()

        # Check that services are created
        assert "arithmetic" in server.services
        assert "matrix" in server.services
        assert "statistics" in server.services
        assert "calculus" in server.services

    def test_setup_middleware_and_factory(self, server):
        """Test middleware and factory setup."""
        server._setup_middleware_and_factory()

        # Check that middleware and factory are created
        assert server.middleware is not None
        assert server.factory is not None

    def test_get_health_status(self, server):
        """Test health status retrieval."""
        # Setup basic components
        server._setup_repositories()
        server._setup_services()
        server._setup_middleware_and_factory()

        health_status = server.get_health_status()

        assert health_status["status"] == "healthy"
        assert "services" in health_status
        assert "repositories" in health_status
        assert health_status["configuration"] == "loaded"


class TestServiceIntegration:
    """Integration tests for service interactions."""

    @pytest.fixture
    def cache_repo(self):
        """Create cache repository for testing."""
        return CacheRepository(max_size=10, default_ttl=60)

    @pytest.fixture
    def config_service(self):
        """Create config service for testing."""
        return ConfigService()

    @pytest.mark.asyncio
    async def test_arithmetic_service_with_cache(self, cache_repo, config_service):
        """Test arithmetic service with caching."""
        from calculator.services.arithmetic import ArithmeticService

        service = ArithmeticService(config=config_service, cache=cache_repo)

        # Test operation
        result1 = await service.process("add", {"numbers": [2, 3, 4]})
        assert result1 == 9.0

        # Test same operation (should use cache if implemented)
        result2 = await service.process("add", {"numbers": [2, 3, 4]})
        assert result2 == 9.0

    @pytest.mark.asyncio
    async def test_matrix_service_with_cache(self, cache_repo, config_service):
        """Test matrix service with caching."""
        from calculator.services.matrix import MatrixService

        service = MatrixService(config=config_service, cache=cache_repo)

        # Test matrix addition
        result = await service.process(
            "add", {"matrix_a": [[1, 2], [3, 4]], "matrix_b": [[5, 6], [7, 8]]}
        )

        expected = [[6, 8], [10, 12]]
        assert result == expected

    @pytest.mark.asyncio
    async def test_statistics_service_with_cache(self, cache_repo, config_service):
        """Test statistics service with caching."""
        from calculator.services.statistics import StatisticsService

        service = StatisticsService(config=config_service, cache=cache_repo)

        # Test mean calculation
        result = await service.process("mean", {"data": [1, 2, 3, 4, 5]})
        assert result == 3.0


class TestEndToEndIntegration:
    """End-to-end integration tests."""

    @pytest.mark.asyncio
    async def test_complete_server_workflow(self):
        """Test complete server initialization and operation workflow."""
        try:
            # This would test the complete workflow but requires more setup
            # For now, we'll test that the server can be created
            from calculator.server.app import CalculatorServer

            server = CalculatorServer()
            assert server is not None

            # Test that we can get health status even without full initialization
            health = server.get_health_status()
            assert "status" in health

        except Exception as e:
            pytest.fail(f"Complete server workflow test failed: {e}")

    @pytest.mark.asyncio
    async def test_tool_registration_workflow(self):
        """Test tool registration workflow."""
        from fastmcp import FastMCP

        from calculator.server.factory import ToolRegistrationFactory
        from calculator.services.config import ConfigService

        # Create mock server and config
        mock_server = Mock(spec=FastMCP)
        mock_server.tool = Mock(return_value=lambda f: f)  # Mock decorator

        config_service = ConfigService()

        # Create factory
        factory = ToolRegistrationFactory(mock_server, config_service)

        # Test that factory can be created and has expected attributes
        assert factory.server == mock_server
        assert factory.config == config_service
        assert factory.registered_tools == {}
        assert factory.tool_groups == {}

    @pytest.mark.asyncio
    async def test_error_handling_integration(self):
        """Test error handling across components."""
        from calculator.core.errors.exceptions import ComputationError, ValidationError
        from calculator.services.arithmetic import ArithmeticService

        service = ArithmeticService()

        # Test validation error
        with pytest.raises(ValidationError):
            await service.process("add", {"numbers": []})

        # Test computation error
        with pytest.raises(ComputationError):
            await service.process("divide", {"a": 10, "b": 0})

        # Test unknown operation
        with pytest.raises(ValidationError):
            await service.process("unknown_op", {"param": "value"})
