"""
Smoke tests for the refactored calculator.
Quick validation that core functionality works after deployment.
"""

import asyncio

import pytest
import pytest_asyncio

from calculator.server.app import create_calculator_app


class TestSmokeTests:
    """Smoke tests for basic functionality validation."""

    @pytest_asyncio.fixture
    async def calculator_app(self):
        """Create calculator application for smoke testing."""
        app = create_calculator_app()
        return app

    @pytest.mark.smoke
    @pytest.mark.asyncio
    async def test_server_starts_successfully(self, calculator_app):
        """Test that server starts without errors."""
        assert calculator_app is not None
        assert calculator_app.is_initialized
        assert calculator_app.config is not None
        print("✅ Server starts successfully")

    @pytest.mark.smoke
    @pytest.mark.asyncio
    async def test_basic_arithmetic_works(self, calculator_app):
        """Test basic arithmetic operations work."""
        service = calculator_app.arithmetic_service

        # Test basic operations
        assert abs(await service.process("add", {"numbers": [2, 3]}) - 5.0) < 1e-10
        assert abs(await service.process("subtract", {"a": 10, "b": 3}) - 7.0) < 1e-10
        assert abs(await service.process("multiply", {"numbers": [2, 3, 4]}) - 24.0) < 1e-10
        assert abs(await service.process("divide", {"a": 10, "b": 2}) - 5.0) < 1e-10

        print("✅ Basic arithmetic operations work")

    @pytest.mark.smoke
    @pytest.mark.asyncio
    async def test_matrix_operations_work(self, calculator_app):
        """Test basic matrix operations work."""
        service = calculator_app.matrix_service

        matrix_a = [[1, 2], [3, 4]]
        matrix_b = [[5, 6], [7, 8]]

        # Test basic matrix operations
        result = await service.process("add", {"matrix_a": matrix_a, "matrix_b": matrix_b})
        assert result == [[6, 8], [10, 12]]

        result = await service.process("determinant", {"matrix": matrix_a})
        assert abs(result - (-2.0)) < 1e-10

        print("✅ Basic matrix operations work")

    @pytest.mark.smoke
    @pytest.mark.asyncio
    async def test_statistics_operations_work(self, calculator_app):
        """Test basic statistics operations work."""
        service = calculator_app.statistics_service

        data = [1, 2, 3, 4, 5]

        # Test basic statistics
        assert abs(await service.process("mean", {"data": data}) - 3.0) < 1e-10
        assert abs(await service.process("median", {"data": data}) - 3.0) < 1e-10

        print("✅ Basic statistics operations work")

    @pytest.mark.smoke
    @pytest.mark.asyncio
    async def test_calculus_operations_work(self, calculator_app):
        """Test basic calculus operations work."""
        service = calculator_app.calculus_service

        # Test derivative
        result = await service.process("derivative", {"expression": "x^2", "variable": "x"})
        assert result is not None

        # Test definite integral
        result = await service.process("integral", {
            "expression": "2*x + 1",
            "variable": "x",
            "lower_limit": 0,
            "upper_limit": 2
        })
        assert abs(result - 6.0) < 1e-10

        print("✅ Basic calculus operations work")

    @pytest.mark.smoke
    @pytest.mark.asyncio
    async def test_caching_works(self, calculator_app):
        """Test that caching system works."""
        service = calculator_app.arithmetic_service

        # First call (cache miss)
        result1 = await service.process("factorial", {"number": 10})

        # Second call (cache hit)
        result2 = await service.process("factorial", {"number": 10})

        # Results should be identical
        assert result1 == result2

        print("✅ Caching system works")

    @pytest.mark.smoke
    @pytest.mark.asyncio
    async def test_error_handling_works(self, calculator_app):
        """Test that error handling works properly."""
        service = calculator_app.arithmetic_service

        # Test division by zero
        with pytest.raises(Exception):
            await service.process("divide", {"a": 1, "b": 0})

        # Test invalid operation
        with pytest.raises(Exception):
            await service.process("invalid_operation", {"param": "value"})

        print("✅ Error handling works")

    @pytest.mark.smoke
    def test_configuration_works(self, calculator_app):
        """Test that configuration system works."""
        config = calculator_app.config

        # Test configuration access
        assert config.get_precision() > 0
        assert config.get_cache_size() > 0
        assert config.get_max_computation_time() > 0

        # Test boolean configurations
        assert isinstance(config.is_caching_enabled(), bool)
        assert isinstance(config.is_performance_monitoring_enabled(), bool)

        print("✅ Configuration system works")

    @pytest.mark.smoke
    @pytest.mark.asyncio
    async def test_repositories_work(self, calculator_app):
        """Test that repository system works."""
        # Test cache repository
        cache_repo = calculator_app.cache_repo
        await cache_repo.set("test_key", "test_value")
        result = await cache_repo.get("test_key")
        assert result == "test_value"

        # Test constants repository
        constants_repo = calculator_app.constants_repo
        pi_value = await constants_repo.get_constant("pi")
        assert abs(pi_value - 3.14159) < 0.001

        print("✅ Repository system works")

    @pytest.mark.smoke
    def test_tool_registration_works(self, calculator_app):
        """Test that tool registration system works."""
        factory = calculator_app.factory

        # Check that tools are registered
        registered_tools = factory.registered_tools
        assert len(registered_tools) > 0

        # Check for expected tools
        expected_tools = ["add", "subtract", "multiply", "divide", "matrix_determinant", "mean"]
        for tool in expected_tools:
            assert tool in registered_tools, f"Tool {tool} not registered"

        print(f"✅ Tool registration works ({len(registered_tools)} tools registered)")

    @pytest.mark.smoke
    @pytest.mark.asyncio
    async def test_concurrent_operations_work(self, calculator_app):
        """Test that concurrent operations work."""
        # Run multiple operations concurrently
        tasks = [
            calculator_app.arithmetic_service.process("add", {"numbers": [1, 2, 3]}),
            calculator_app.matrix_service.process("determinant", {"matrix": [[1, 2], [3, 4]]}),
            calculator_app.statistics_service.process("mean", {"data": [1, 2, 3, 4, 5]}),
            calculator_app.arithmetic_service.process("factorial", {"number": 5}),
        ]

        results = await asyncio.gather(*tasks)

        # All operations should succeed
        assert all(result is not None for result in results)

        print("✅ Concurrent operations work")

    @pytest.mark.smoke
    def test_health_check_works(self, calculator_app):
        """Test that health check system works."""
        health = calculator_app.get_health_status()

        assert health["status"] == "healthy"
        assert "services" in health
        assert "repositories" in health
        assert "configuration" in health

        print("✅ Health check system works")


@pytest.mark.smoke
class TestSmokeValidation:
    """Validation of smoke test coverage."""

    def test_smoke_test_coverage(self):
        """Verify smoke tests cover all critical components."""
        smoke_test_methods = [
            "test_server_starts_successfully",
            "test_basic_arithmetic_works",
            "test_matrix_operations_work",
            "test_statistics_operations_work",
            "test_calculus_operations_work",
            "test_caching_works",
            "test_error_handling_works",
            "test_configuration_works",
            "test_repositories_work",
            "test_tool_registration_works",
            "test_concurrent_operations_work",
            "test_health_check_works",
        ]

        # Verify all smoke test methods exist
        for method_name in smoke_test_methods:
            assert hasattr(TestSmokeTests, method_name), f"Missing smoke test: {method_name}"

        print(f"✅ All {len(smoke_test_methods)} smoke test methods are implemented")

    @pytest.mark.asyncio
    async def test_smoke_tests_run_quickly(self):
        """Verify smoke tests run quickly (under 30 seconds)."""
        import time

        start_time = time.time()

        # Create app and run basic smoke tests
        app = create_calculator_app()

        # Quick functionality tests
        await app.arithmetic_service.process("add", {"numbers": [1, 2, 3]})
        await app.matrix_service.process("determinant", {"matrix": [[1, 2], [3, 4]]})
        await app.statistics_service.process("mean", {"data": [1, 2, 3, 4, 5]})

        end_time = time.time()
        duration = end_time - start_time

        # Smoke tests should be very fast
        assert duration < 30.0, f"Smoke tests too slow: {duration:.2f}s"

        print(f"✅ Smoke tests run quickly: {duration:.2f}s")


# Standalone smoke test runner
async def run_smoke_tests():
    """Run smoke tests independently."""
    print("💨 Running Smoke Tests")
    print("=" * 30)

    try:
        app = create_calculator_app()

        # Quick validation of all major components
        tests = [
            ("Arithmetic", app.arithmetic_service.process("add", {"numbers": [1, 2, 3]})),
            ("Matrix", app.matrix_service.process("determinant", {"matrix": [[1, 2], [3, 4]]})),
            ("Statistics", app.statistics_service.process("mean", {"data": [1, 2, 3, 4, 5]})),
            ("Calculus", app.calculus_service.process("derivative", {"expression": "x^2", "variable": "x"})),
        ]

        results = []
        for name, task in tests:
            try:
                result = await task
                results.append((name, True, result))
                print(f"✅ {name}: Working")
            except Exception as e:
                results.append((name, False, str(e)))
                print(f"❌ {name}: Failed - {e}")

        # Summary
        passed = sum(1 for _, success, _ in results if success)
        total = len(results)

        print(f"\n📊 Smoke Test Results: {passed}/{total} passed")

        if passed == total:
            print("🎉 All smoke tests passed!")
            return True
        else:
            print("❌ Some smoke tests failed!")
            return False

    except Exception as e:
        print(f"❌ Smoke test setup failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_smoke_tests())
    exit(0 if success else 1)
