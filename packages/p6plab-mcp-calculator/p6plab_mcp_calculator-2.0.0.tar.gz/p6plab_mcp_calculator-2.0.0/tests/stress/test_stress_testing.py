"""
Stress testing for the refactored calculator.
Tests system behavior under extreme load conditions.
"""

import asyncio
import random
import time

import pytest
import pytest_asyncio

from calculator.server.app import create_calculator_app


class TestStressTesting:
    """Stress testing suite."""

    @pytest_asyncio.fixture
    async def calculator_app(self):
        """Create calculator application for stress testing."""
        app = create_calculator_app()
        return app

    @pytest.mark.stress
    @pytest.mark.asyncio
    async def test_high_volume_arithmetic_operations(self, calculator_app):
        """Test system under high volume of arithmetic operations."""
        print("\n🔥 High Volume Arithmetic Stress Test")

        async def arithmetic_operation(op_id: int):
            """Perform a random arithmetic operation."""
            operations = [
                ("add", {"numbers": [random.randint(1, 100) for _ in range(10)]}),
                ("multiply", {"numbers": [random.randint(1, 10) for _ in range(5)]}),
                ("power", {"base": random.randint(2, 10), "exponent": random.randint(1, 5)}),
                ("factorial", {"number": random.randint(1, 20)}),
                ("sqrt", {"number": random.randint(1, 10000)}),
                ("sine", {"angle": random.uniform(0, 6.28), "unit": "radians"}),
                ("log", {"number": random.randint(1, 1000), "base": random.randint(2, 10)}),
            ]

            operation, params = random.choice(operations)
            try:
                result = await calculator_app.arithmetic_service.process(operation, params)
                return {"success": True, "operation": operation, "result": result}
            except Exception as e:
                return {"success": False, "operation": operation, "error": str(e)}

        # Execute high volume of operations
        num_operations = 5000
        batch_size = 100

        start_time = time.time()
        all_results = []

        for batch_start in range(0, num_operations, batch_size):
            batch_end = min(batch_start + batch_size, num_operations)
            batch_tasks = [arithmetic_operation(i) for i in range(batch_start, batch_end)]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            all_results.extend(batch_results)

            # Progress indicator
            if batch_start % 1000 == 0:
                print(f"  Completed {batch_start}/{num_operations} operations...")

        end_time = time.time()
        total_time = end_time - start_time

        # Analyze results
        successful_ops = sum(1 for r in all_results if isinstance(r, dict) and r.get("success", False))
        failed_ops = len(all_results) - successful_ops
        throughput = num_operations / total_time

        print(f"  Results: {successful_ops}/{num_operations} successful ({failed_ops} failed)")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Throughput: {throughput:.1f} ops/sec")

        # Stress test should have high success rate
        success_rate = successful_ops / num_operations
        assert success_rate > 0.95, f"Success rate too low: {success_rate:.2%}"

        # Should maintain reasonable throughput under stress
        assert throughput > 100, f"Throughput too low: {throughput:.1f} ops/sec"

    @pytest.mark.stress
    @pytest.mark.asyncio
    async def test_large_matrix_operations_stress(self, calculator_app):
        """Test system with large matrix operations."""
        print("\n🔥 Large Matrix Operations Stress Test")

        async def matrix_operation(size: int, op_id: int):
            """Perform matrix operation with given size."""
            # Generate random matrices
            matrix_a = [[random.uniform(-10, 10) for _ in range(size)] for _ in range(size)]
            matrix_b = [[random.uniform(-10, 10) for _ in range(size)] for _ in range(size)]

            operations = [
                ("add", {"matrix_a": matrix_a, "matrix_b": matrix_b}),
                ("multiply", {"matrix_a": matrix_a, "matrix_b": matrix_b}),
                ("determinant", {"matrix": matrix_a}),
                ("transpose", {"matrix": matrix_a}),
            ]

            operation, params = random.choice(operations)

            try:
                start = time.time()
                result = await calculator_app.matrix_service.process(operation, params)
                end = time.time()
                return {
                    "success": True,
                    "operation": operation,
                    "size": size,
                    "execution_time": end - start,
                }
            except Exception as e:
                return {
                    "success": False,
                    "operation": operation,
                    "size": size,
                    "error": str(e),
                }

        # Test with various matrix sizes
        matrix_sizes = [10, 20, 30, 50]  # Reasonable sizes for stress testing
        operations_per_size = 20

        all_results = []

        for size in matrix_sizes:
            print(f"  Testing {size}x{size} matrices...")

            tasks = [matrix_operation(size, i) for i in range(operations_per_size)]
            size_results = await asyncio.gather(*tasks, return_exceptions=True)
            all_results.extend(size_results)

        # Analyze results
        successful_ops = sum(1 for r in all_results if isinstance(r, dict) and r.get("success", False))
        failed_ops = len(all_results) - successful_ops

        # Get execution times for successful operations
        execution_times = [
            r["execution_time"] for r in all_results
            if isinstance(r, dict) and r.get("success", False)
        ]

        if execution_times:
            avg_time = sum(execution_times) / len(execution_times)
            max_time = max(execution_times)
            print(f"  Results: {successful_ops}/{len(all_results)} successful")
            print(f"  Average execution time: {avg_time:.3f}s")
            print(f"  Maximum execution time: {max_time:.3f}s")

            # Matrix operations should complete within reasonable time
            assert avg_time < 5.0, f"Average execution time too high: {avg_time:.3f}s"
            assert max_time < 30.0, f"Maximum execution time too high: {max_time:.3f}s"

        # Should have reasonable success rate
        success_rate = successful_ops / len(all_results)
        assert success_rate > 0.8, f"Success rate too low: {success_rate:.2%}"

    @pytest.mark.stress
    @pytest.mark.asyncio
    async def test_large_dataset_statistics_stress(self, calculator_app):
        """Test system with large statistical datasets."""
        print("\n🔥 Large Dataset Statistics Stress Test")

        async def statistics_operation(data_size: int, op_id: int):
            """Perform statistics operation with given data size."""
            # Generate random dataset
            data = [random.gauss(0, 1) for _ in range(data_size)]

            operations = [
                ("mean", {"data": data}),
                ("median", {"data": data}),
                ("std_dev", {"data": data, "population": False}),
                ("variance", {"data": data, "population": False}),
                ("descriptive_stats", {"data": data}),
            ]

            operation, params = random.choice(operations)

            try:
                start = time.time()
                result = await calculator_app.statistics_service.process(operation, params)
                end = time.time()
                return {
                    "success": True,
                    "operation": operation,
                    "data_size": data_size,
                    "execution_time": end - start,
                }
            except Exception as e:
                return {
                    "success": False,
                    "operation": operation,
                    "data_size": data_size,
                    "error": str(e),
                }

        # Test with various data sizes
        data_sizes = [1000, 10000, 50000, 100000]
        operations_per_size = 10

        all_results = []

        for size in data_sizes:
            print(f"  Testing datasets with {size} items...")

            tasks = [statistics_operation(size, i) for i in range(operations_per_size)]
            size_results = await asyncio.gather(*tasks, return_exceptions=True)
            all_results.extend(size_results)

        # Analyze results
        successful_ops = sum(1 for r in all_results if isinstance(r, dict) and r.get("success", False))
        failed_ops = len(all_results) - successful_ops

        # Get execution times for successful operations
        execution_times = [
            r["execution_time"] for r in all_results
            if isinstance(r, dict) and r.get("success", False)
        ]

        if execution_times:
            avg_time = sum(execution_times) / len(execution_times)
            max_time = max(execution_times)
            print(f"  Results: {successful_ops}/{len(all_results)} successful")
            print(f"  Average execution time: {avg_time:.3f}s")
            print(f"  Maximum execution time: {max_time:.3f}s")

            # Statistics operations should be reasonably fast even with large datasets
            assert avg_time < 2.0, f"Average execution time too high: {avg_time:.3f}s"
            assert max_time < 10.0, f"Maximum execution time too high: {max_time:.3f}s"

        # Should have high success rate
        success_rate = successful_ops / len(all_results)
        assert success_rate > 0.95, f"Success rate too low: {success_rate:.2%}"

    @pytest.mark.stress
    @pytest.mark.asyncio
    async def test_extreme_concurrency_stress(self, calculator_app):
        """Test system under extreme concurrency."""
        print("\n🔥 Extreme Concurrency Stress Test")

        async def mixed_operation(op_id: int):
            """Perform a random mixed operation."""
            operation_type = random.choice(["arithmetic", "matrix", "statistics"])

            try:
                if operation_type == "arithmetic":
                    result = await calculator_app.arithmetic_service.process(
                        "add", {"numbers": [op_id, op_id + 1, op_id + 2]}
                    )
                elif operation_type == "matrix":
                    matrix = [[1, 2], [3, 4]]
                    result = await calculator_app.matrix_service.process(
                        "determinant", {"matrix": matrix}
                    )
                else:  # statistics
                    data = [random.randint(1, 100) for _ in range(50)]
                    result = await calculator_app.statistics_service.process(
                        "mean", {"data": data}
                    )

                return {"success": True, "type": operation_type, "result": result}
            except Exception as e:
                return {"success": False, "type": operation_type, "error": str(e)}

        # Test extreme concurrency levels
        concurrency_levels = [100, 500, 1000]

        for concurrency in concurrency_levels:
            print(f"  Testing {concurrency} concurrent operations...")

            start_time = time.time()

            # Create and execute concurrent tasks
            tasks = [mixed_operation(i) for i in range(concurrency)]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            end_time = time.time()
            total_time = end_time - start_time

            # Analyze results
            successful_ops = sum(
                1 for r in results
                if isinstance(r, dict) and r.get("success", False)
            )
            failed_ops = len(results) - successful_ops
            throughput = concurrency / total_time

            print(f"    Results: {successful_ops}/{concurrency} successful ({failed_ops} failed)")
            print(f"    Total time: {total_time:.2f}s")
            print(f"    Throughput: {throughput:.1f} ops/sec")

            # Should maintain reasonable success rate even under extreme load
            success_rate = successful_ops / concurrency
            assert success_rate > 0.8, f"Success rate too low at {concurrency} concurrency: {success_rate:.2%}"

            # Should complete within reasonable time
            assert total_time < 30.0, f"Total time too high at {concurrency} concurrency: {total_time:.2f}s"

    @pytest.mark.stress
    @pytest.mark.asyncio
    async def test_memory_pressure_stress(self, calculator_app):
        """Test system under memory pressure."""
        print("\n🔥 Memory Pressure Stress Test")

        async def memory_intensive_operation(op_id: int):
            """Perform memory-intensive operations."""
            try:
                # Large matrix operations
                size = 50
                matrix_a = [[random.uniform(-1, 1) for _ in range(size)] for _ in range(size)]
                matrix_b = [[random.uniform(-1, 1) for _ in range(size)] for _ in range(size)]

                result1 = await calculator_app.matrix_service.process(
                    "multiply", {"matrix_a": matrix_a, "matrix_b": matrix_b}
                )

                # Large dataset statistics
                large_data = [random.gauss(0, 1) for _ in range(10000)]
                result2 = await calculator_app.statistics_service.process(
                    "descriptive_stats", {"data": large_data}
                )

                # Complex arithmetic
                large_numbers = list(range(1000))
                result3 = await calculator_app.arithmetic_service.process(
                    "add", {"numbers": large_numbers}
                )

                return {"success": True, "operations": 3}
            except Exception as e:
                return {"success": False, "error": str(e)}

        # Run memory-intensive operations in batches
        batch_size = 20
        num_batches = 10

        all_results = []

        for batch in range(num_batches):
            print(f"  Running memory pressure batch {batch + 1}/{num_batches}...")

            # Create batch of memory-intensive tasks
            tasks = [memory_intensive_operation(i) for i in range(batch_size)]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            all_results.extend(batch_results)

            # Brief pause between batches to allow garbage collection
            await asyncio.sleep(0.1)

        # Analyze results
        successful_ops = sum(1 for r in all_results if isinstance(r, dict) and r.get("success", False))
        failed_ops = len(all_results) - successful_ops

        print(f"  Results: {successful_ops}/{len(all_results)} successful ({failed_ops} failed)")

        # Should handle memory pressure reasonably well
        success_rate = successful_ops / len(all_results)
        assert success_rate > 0.7, f"Success rate too low under memory pressure: {success_rate:.2%}"

    @pytest.mark.stress
    @pytest.mark.asyncio
    async def test_error_handling_under_stress(self, calculator_app):
        """Test error handling under stress conditions."""
        print("\n🔥 Error Handling Under Stress Test")

        async def error_prone_operation(op_id: int):
            """Perform operations that may cause errors."""
            error_operations = [
                # Division by zero
                ("arithmetic", "divide", {"a": random.randint(1, 100), "b": 0}),
                # Negative factorial
                ("arithmetic", "factorial", {"number": -random.randint(1, 10)}),
                # Singular matrix inverse
                ("matrix", "inverse", {"matrix": [[1, 2], [2, 4]]}),  # Singular matrix
                # Empty data statistics
                ("statistics", "mean", {"data": []}),
                # Invalid matrix dimensions
                ("matrix", "add", {"matrix_a": [[1, 2]], "matrix_b": [[1], [2]]}),
            ]

            service_name, operation, params = random.choice(error_operations)

            try:
                if service_name == "arithmetic":
                    result = await calculator_app.arithmetic_service.process(operation, params)
                elif service_name == "matrix":
                    result = await calculator_app.matrix_service.process(operation, params)
                else:  # statistics
                    result = await calculator_app.statistics_service.process(operation, params)

                # If we get here, the operation unexpectedly succeeded
                return {"success": True, "unexpected": True, "operation": f"{service_name}.{operation}"}
            except Exception as e:
                # Expected error - this is good
                return {
                    "success": True,
                    "expected_error": True,
                    "operation": f"{service_name}.{operation}",
                    "error_type": type(e).__name__,
                }

        # Run many error-prone operations concurrently
        num_operations = 1000

        print(f"  Running {num_operations} error-prone operations...")

        start_time = time.time()
        tasks = [error_prone_operation(i) for i in range(num_operations)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        total_time = end_time - start_time

        # Analyze results
        expected_errors = sum(1 for r in results if isinstance(r, dict) and r.get("expected_error", False))
        unexpected_successes = sum(1 for r in results if isinstance(r, dict) and r.get("unexpected", False))
        system_failures = sum(1 for r in results if not isinstance(r, dict))

        print("  Results:")
        print(f"    Expected errors: {expected_errors}")
        print(f"    Unexpected successes: {unexpected_successes}")
        print(f"    System failures: {system_failures}")
        print(f"    Total time: {total_time:.2f}s")
        print(f"    Throughput: {num_operations / total_time:.1f} ops/sec")

        # Error handling should be robust - no system failures
        assert system_failures == 0, f"System failures detected: {system_failures}"

        # Most operations should result in expected errors (proper error handling)
        error_handling_rate = expected_errors / num_operations
        assert error_handling_rate > 0.8, f"Error handling rate too low: {error_handling_rate:.2%}"

    @pytest.mark.stress
    @pytest.mark.asyncio
    async def test_sustained_load_stress(self, calculator_app):
        """Test system under sustained load over time."""
        print("\n🔥 Sustained Load Stress Test")

        async def continuous_operation(duration_seconds: int):
            """Run operations continuously for specified duration."""
            end_time = time.time() + duration_seconds
            operation_count = 0
            error_count = 0

            while time.time() < end_time:
                try:
                    # Mix of different operations
                    operation_type = random.choice(["arithmetic", "matrix", "statistics"])

                    if operation_type == "arithmetic":
                        await calculator_app.arithmetic_service.process(
                            "add", {"numbers": [random.randint(1, 100) for _ in range(10)]}
                        )
                    elif operation_type == "matrix":
                        size = random.randint(5, 15)
                        matrix = [[random.uniform(-1, 1) for _ in range(size)] for _ in range(size)]
                        await calculator_app.matrix_service.process("determinant", {"matrix": matrix})
                    else:  # statistics
                        data = [random.gauss(0, 1) for _ in range(random.randint(100, 1000))]
                        await calculator_app.statistics_service.process("mean", {"data": data})

                    operation_count += 1

                    # Brief pause to prevent overwhelming the system
                    await asyncio.sleep(0.001)

                except Exception:
                    error_count += 1

            return {"operations": operation_count, "errors": error_count}

        # Run sustained load test
        duration = 30  # 30 seconds
        num_workers = 10  # 10 concurrent workers

        print(f"  Running sustained load test for {duration}s with {num_workers} workers...")

        start_time = time.time()
        tasks = [continuous_operation(duration) for _ in range(num_workers)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        actual_duration = end_time - start_time

        # Analyze results
        total_operations = sum(r["operations"] for r in results)
        total_errors = sum(r["errors"] for r in results)
        average_throughput = total_operations / actual_duration
        error_rate = total_errors / total_operations if total_operations > 0 else 0

        print("  Results:")
        print(f"    Duration: {actual_duration:.1f}s")
        print(f"    Total operations: {total_operations}")
        print(f"    Total errors: {total_errors}")
        print(f"    Average throughput: {average_throughput:.1f} ops/sec")
        print(f"    Error rate: {error_rate:.2%}")

        # System should maintain reasonable performance under sustained load
        assert average_throughput > 50, f"Throughput too low: {average_throughput:.1f} ops/sec"
        assert error_rate < 0.05, f"Error rate too high: {error_rate:.2%}"
        assert total_operations > 1000, f"Too few operations completed: {total_operations}"


@pytest.mark.stress
class TestStressValidation:
    """Validation tests for stress testing results."""

    @pytest.mark.asyncio
    async def test_system_recovery_after_stress(self):
        """Test that system recovers properly after stress testing."""
        print("\n🔄 System Recovery After Stress Test")

        # Create fresh app instance
        app = create_calculator_app()

        # Perform stress operations
        stress_tasks = []
        for i in range(100):
            task = app.arithmetic_service.process("factorial", {"number": random.randint(1, 20)})
            stress_tasks.append(task)

        await asyncio.gather(*stress_tasks, return_exceptions=True)

        # Test that system still works normally after stress
        normal_operations = [
            (app.arithmetic_service, "add", {"numbers": [1, 2, 3]}),
            (app.matrix_service, "determinant", {"matrix": [[1, 2], [3, 4]]}),
            (app.statistics_service, "mean", {"data": [1, 2, 3, 4, 5]}),
        ]

        for service, operation, params in normal_operations:
            result = await service.process(operation, params)
            assert result is not None, f"System not recovered: {operation} failed"

        print("  ✅ System recovered successfully after stress testing")

    def test_stress_test_coverage(self):
        """Verify that stress tests cover all major components."""
        # This test ensures we have stress tests for all major components
        stress_test_methods = [
            "test_high_volume_arithmetic_operations",
            "test_large_matrix_operations_stress",
            "test_large_dataset_statistics_stress",
            "test_extreme_concurrency_stress",
            "test_memory_pressure_stress",
            "test_error_handling_under_stress",
            "test_sustained_load_stress",
        ]

        # Verify all stress test methods exist
        for method_name in stress_test_methods:
            assert hasattr(TestStressTesting, method_name), f"Missing stress test: {method_name}"

        print(f"  ✅ All {len(stress_test_methods)} stress test methods are implemented")
