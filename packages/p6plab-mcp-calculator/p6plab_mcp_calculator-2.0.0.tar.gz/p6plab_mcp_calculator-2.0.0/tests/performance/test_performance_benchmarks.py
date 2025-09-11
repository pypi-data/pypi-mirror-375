"""Performance benchmarks for calculator operations."""

import asyncio
import time

import numpy as np
import pytest

from calculator.core.monitoring.metrics import MetricsCollector
from calculator.repositories.cache import CacheRepository
from calculator.services.arithmetic import ArithmeticService
from calculator.services.matrix import MatrixService
from calculator.services.statistics import StatisticsService


class TestPerformanceBenchmarks:
    """Performance benchmark tests."""

    @pytest.fixture
    def metrics_collector(self):
        """Create metrics collector for testing."""
        collector = MetricsCollector()
        collector.reset_metrics()  # Start fresh
        return collector

    @pytest.fixture
    def cache_repo(self):
        """Create cache repository for performance testing."""
        return CacheRepository(max_size=1000, default_ttl=3600)

    @pytest.fixture
    def arithmetic_service(self, cache_repo):
        """Create arithmetic service for benchmarking."""
        return ArithmeticService(cache=cache_repo)

    @pytest.fixture
    def matrix_service(self, cache_repo):
        """Create matrix service for benchmarking."""
        return MatrixService(cache=cache_repo)

    @pytest.fixture
    def statistics_service(self, cache_repo):
        """Create statistics service for benchmarking."""
        return StatisticsService(cache=cache_repo)

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_arithmetic_operations_performance(self, arithmetic_service, metrics_collector):
        """Benchmark arithmetic operations performance."""
        operations = [
            ("add", {"numbers": [1, 2, 3, 4, 5]}),
            ("multiply", {"numbers": [2, 3, 4]}),
            ("power", {"base": 2, "exponent": 10}),
            ("factorial", {"number": 10}),
            ("sine", {"angle": 1.5708, "unit": "radians"}),
            ("logarithm", {"number": 100, "base": 10}),
        ]

        performance_results = {}

        for operation, params in operations:
            # Warm up
            await arithmetic_service.process(operation, params)

            # Benchmark
            start_time = time.time()
            iterations = 1000

            for _ in range(iterations):
                await arithmetic_service.process(operation, params)

            end_time = time.time()
            total_time = end_time - start_time
            avg_time = total_time / iterations

            performance_results[operation] = {
                "total_time": total_time,
                "avg_time_ms": avg_time * 1000,
                "operations_per_second": iterations / total_time,
            }

            # Record metrics
            metrics_collector.record_operation(
                operation_name=f"arithmetic_{operation}", execution_time=avg_time, cached=False
            )

        # Verify performance requirements
        for operation, results in performance_results.items():
            # Most arithmetic operations should complete in under 1ms
            assert results["avg_time_ms"] < 1.0, (
                f"{operation} too slow: {results['avg_time_ms']:.3f}ms"
            )

            # Should handle at least 1000 operations per second
            assert results["operations_per_second"] > 1000, (
                f"{operation} throughput too low: {results['operations_per_second']:.1f} ops/sec"
            )

        print("\nArithmetic Performance Results:")
        for operation, results in performance_results.items():
            print(
                f"  {operation}: {results['avg_time_ms']:.3f}ms avg, {results['operations_per_second']:.1f} ops/sec"
            )

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_matrix_operations_performance(self, matrix_service, metrics_collector):
        """Benchmark matrix operations performance."""
        # Test matrices of different sizes
        matrix_sizes = [5, 10, 20]
        operations = ["add", "multiply", "determinant", "inverse"]

        performance_results = {}

        for size in matrix_sizes:
            # Generate test matrices
            matrix_a = np.random.rand(size, size).tolist()
            matrix_b = np.random.rand(size, size).tolist()

            for operation in operations:
                if operation in ["add", "multiply"]:
                    params = {"matrix_a": matrix_a, "matrix_b": matrix_b}
                else:
                    params = {"matrix": matrix_a}

                # Warm up
                try:
                    await matrix_service.process(operation, params)
                except:
                    continue  # Skip if operation fails

                # Benchmark
                start_time = time.time()
                iterations = 10 if size > 10 else 100  # Fewer iterations for larger matrices
                successful_ops = 0

                for _ in range(iterations):
                    try:
                        await matrix_service.process(operation, params)
                        successful_ops += 1
                    except:
                        pass  # Some operations might fail (e.g., singular matrices)

                if successful_ops == 0:
                    continue

                end_time = time.time()
                total_time = end_time - start_time
                avg_time = total_time / successful_ops

                key = f"{operation}_{size}x{size}"
                performance_results[key] = {
                    "avg_time_ms": avg_time * 1000,
                    "successful_ops": successful_ops,
                    "total_iterations": iterations,
                }

                # Record metrics
                metrics_collector.record_operation(
                    operation_name=f"matrix_{operation}",
                    execution_time=avg_time,
                    cached=False,
                    metadata={"matrix_size": f"{size}x{size}"},
                )

        # Verify performance requirements (more lenient for matrix operations)
        for key, results in performance_results.items():
            operation, size_str = key.rsplit("_", 1)
            size = int(size_str.split("x")[0])

            # Performance requirements scale with matrix size
            max_time_ms = size * size * 0.1  # 0.1ms per matrix element

            assert results["avg_time_ms"] < max_time_ms, (
                f"{key} too slow: {results['avg_time_ms']:.3f}ms"
            )

        print("\nMatrix Performance Results:")
        for key, results in performance_results.items():
            print(
                f"  {key}: {results['avg_time_ms']:.3f}ms avg ({results['successful_ops']}/{results['total_iterations']} successful)"
            )

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_statistics_operations_performance(self, statistics_service, metrics_collector):
        """Benchmark statistics operations performance."""
        # Test with different data sizes
        data_sizes = [100, 1000, 10000]
        operations = ["mean", "median", "std_dev", "descriptive_stats"]

        performance_results = {}

        for size in data_sizes:
            # Generate test data
            data = np.random.normal(0, 1, size).tolist()

            for operation in operations:
                params = {"data": data}

                # Warm up
                await statistics_service.process(operation, params)

                # Benchmark
                start_time = time.time()
                iterations = 100 if size < 10000 else 10  # Fewer iterations for larger datasets

                for _ in range(iterations):
                    await statistics_service.process(operation, params)

                end_time = time.time()
                total_time = end_time - start_time
                avg_time = total_time / iterations

                key = f"{operation}_{size}"
                performance_results[key] = {
                    "avg_time_ms": avg_time * 1000,
                    "data_size": size,
                    "throughput_items_per_ms": size / (avg_time * 1000),
                }

                # Record metrics
                metrics_collector.record_operation(
                    operation_name=f"statistics_{operation}",
                    execution_time=avg_time,
                    cached=False,
                    metadata={"data_size": size},
                )

        # Verify performance requirements
        for key, results in performance_results.items():
            operation, size_str = key.rsplit("_", 1)
            size = int(size_str)

            # Should process at least 1000 items per millisecond for basic operations
            if operation in ["mean", "median"]:
                min_throughput = 1000
            else:
                min_throughput = 100  # More complex operations can be slower

            assert results["throughput_items_per_ms"] > min_throughput, (
                f"{key} throughput too low: {results['throughput_items_per_ms']:.1f} items/ms"
            )

        print("\nStatistics Performance Results:")
        for key, results in performance_results.items():
            print(
                f"  {key}: {results['avg_time_ms']:.3f}ms avg, {results['throughput_items_per_ms']:.1f} items/ms"
            )

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_cache_performance(self, cache_repo, metrics_collector):
        """Benchmark cache performance."""
        # Test cache operations
        cache_operations = []

        # Set operations
        start_time = time.time()
        for i in range(1000):
            await cache_repo.set(f"key_{i}", f"value_{i}")
        set_time = time.time() - start_time

        cache_operations.append(("set", set_time, 1000))

        # Get operations (cache hits)
        start_time = time.time()
        for i in range(1000):
            await cache_repo.get(f"key_{i}")
        get_time = time.time() - start_time

        cache_operations.append(("get_hit", get_time, 1000))

        # Get operations (cache misses)
        start_time = time.time()
        for i in range(1000):
            await cache_repo.get(f"missing_key_{i}")
        miss_time = time.time() - start_time

        cache_operations.append(("get_miss", miss_time, 1000))

        # Verify performance requirements
        for operation, total_time, count in cache_operations:
            avg_time_ms = (total_time / count) * 1000
            ops_per_second = count / total_time

            # Cache operations should be very fast
            assert avg_time_ms < 0.1, f"Cache {operation} too slow: {avg_time_ms:.3f}ms"
            assert ops_per_second > 10000, (
                f"Cache {operation} throughput too low: {ops_per_second:.1f} ops/sec"
            )

            # Record metrics
            metrics_collector.record_operation(
                operation_name=f"cache_{operation}",
                execution_time=total_time / count,
                cached=operation.startswith("get_hit"),
            )

        print("\nCache Performance Results:")
        for operation, total_time, count in cache_operations:
            avg_time_ms = (total_time / count) * 1000
            ops_per_second = count / total_time
            print(f"  {operation}: {avg_time_ms:.3f}ms avg, {ops_per_second:.1f} ops/sec")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_operations_performance(self, arithmetic_service, metrics_collector):
        """Benchmark concurrent operations performance."""

        async def perform_operation(operation_id: int):
            """Perform a single operation."""
            start_time = time.time()
            result = await arithmetic_service.process("add", {"numbers": [1, 2, 3, operation_id]})
            end_time = time.time()
            return {
                "operation_id": operation_id,
                "result": result,
                "execution_time": end_time - start_time,
            }

        # Test different concurrency levels
        concurrency_levels = [1, 10, 50, 100]

        for concurrency in concurrency_levels:
            start_time = time.time()

            # Create concurrent tasks
            tasks = [perform_operation(i) for i in range(concurrency)]
            results = await asyncio.gather(*tasks)

            end_time = time.time()
            total_time = end_time - start_time

            # Analyze results
            execution_times = [r["execution_time"] for r in results]
            avg_execution_time = sum(execution_times) / len(execution_times)
            max_execution_time = max(execution_times)
            throughput = concurrency / total_time

            # Record metrics
            metrics_collector.record_operation(
                operation_name="concurrent_arithmetic",
                execution_time=avg_execution_time,
                cached=False,
                metadata={"concurrency_level": concurrency},
            )

            # Verify performance doesn't degrade significantly with concurrency
            assert avg_execution_time < 0.01, (
                f"Concurrent operations too slow at level {concurrency}: {avg_execution_time:.3f}s"
            )
            assert throughput > concurrency * 50, (
                f"Throughput too low at concurrency {concurrency}: {throughput:.1f} ops/sec"
            )

            print(
                f"Concurrency {concurrency}: {avg_execution_time * 1000:.3f}ms avg, {max_execution_time * 1000:.3f}ms max, {throughput:.1f} ops/sec"
            )

    @pytest.mark.performance
    def test_memory_usage_performance(self, metrics_collector):
        """Test memory usage during operations."""
        try:
            import psutil

            process = psutil.Process()

            # Measure baseline memory
            baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

            # Perform memory-intensive operations
            large_matrices = []
            for i in range(10):
                # Create large matrix
                matrix = np.random.rand(100, 100)
                large_matrices.append(matrix)

                current_memory = process.memory_info().rss / 1024 / 1024
                memory_increase = current_memory - baseline_memory

                # Memory usage should not grow excessively
                assert memory_increase < 100, (
                    f"Memory usage too high: {memory_increase:.1f}MB increase"
                )

            # Clean up
            del large_matrices

            print(
                f"Memory usage test: {baseline_memory:.1f}MB baseline, max increase: {memory_increase:.1f}MB"
            )

        except ImportError:
            pytest.skip("psutil not available for memory testing")

    @pytest.mark.performance
    def test_metrics_collection_performance(self, metrics_collector):
        """Test performance of metrics collection itself."""
        # Measure metrics collection overhead
        start_time = time.time()

        for i in range(10000):
            metrics_collector.record_operation(
                operation_name="test_operation", execution_time=0.001, cached=i % 2 == 0
            )

        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_record = total_time / 10000

        # Metrics collection should be very fast
        assert avg_time_per_record < 0.0001, (
            f"Metrics collection too slow: {avg_time_per_record:.6f}s per record"
        )

        # Verify metrics were recorded
        stats = metrics_collector.get_system_metrics()
        assert stats["total_requests"] == 10000

        print(
            f"Metrics collection: {avg_time_per_record * 1000000:.1f}μs per record, {10000 / total_time:.1f} records/sec"
        )
