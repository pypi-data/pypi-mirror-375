#!/usr/bin/env python3
"""
Resource usage and memory leak testing script.
Tests memory usage, CPU usage, and resource cleanup.
"""

import asyncio
import gc
import sys
import time

import psutil

from calculator.server.app import create_calculator_app


class ResourceUsageTester:
    """Test resource usage and memory leaks."""

    def __init__(self):
        self.process = psutil.Process()
        self.initial_memory = None
        self.app = None

    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / 1024 / 1024

    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        return self.process.cpu_percent()

    async def setup(self):
        """Initialize the server and record baseline metrics."""
        print("🚀 Initializing MCP Server for resource testing...")

        # Record initial memory
        self.initial_memory = self.get_memory_usage()
        print(f"📊 Initial memory usage: {self.initial_memory:.2f} MB")

        # Initialize server
        self.app = create_calculator_app()

        # Record post-initialization memory
        post_init_memory = self.get_memory_usage()
        init_overhead = post_init_memory - self.initial_memory
        print(f"📊 Post-initialization memory: {post_init_memory:.2f} MB")
        print(f"📊 Initialization overhead: {init_overhead:.2f} MB")

        return True

    async def test_memory_usage_under_load(self):
        """Test memory usage under sustained load."""
        print("\n🧠 Testing Memory Usage Under Load...")

        memory_samples = []
        operations_per_batch = 100
        num_batches = 10

        for batch in range(num_batches):
            # Perform batch of operations
            tasks = []
            for i in range(operations_per_batch):
                task = self.app.arithmetic_service.process("add", {"numbers": [i, i+1, i+2]})
                tasks.append(task)

            # Execute batch
            await asyncio.gather(*tasks)

            # Record memory usage
            memory_usage = self.get_memory_usage()
            memory_samples.append(memory_usage)

            print(f"  Batch {batch+1}/{num_batches}: {memory_usage:.2f} MB")

            # Small delay to allow garbage collection
            await asyncio.sleep(0.1)

        # Analyze memory trend
        initial_batch_memory = memory_samples[0]
        final_batch_memory = memory_samples[-1]
        memory_growth = final_batch_memory - initial_batch_memory

        print("\n📈 Memory Analysis:")
        print(f"  Initial batch memory: {initial_batch_memory:.2f} MB")
        print(f"  Final batch memory: {final_batch_memory:.2f} MB")
        print(f"  Memory growth: {memory_growth:.2f} MB")

        # Check for memory leaks (growth > 10MB is concerning)
        if memory_growth > 10:
            print("  ⚠️  Potential memory leak detected!")
            return False
        else:
            print("  ✅ Memory usage stable")
            return True

    async def test_garbage_collection_effectiveness(self):
        """Test garbage collection effectiveness."""
        print("\n🗑️  Testing Garbage Collection...")

        # Record memory before creating objects
        gc.collect()  # Force garbage collection
        memory_before = self.get_memory_usage()

        # Create many temporary objects
        large_results = []
        for i in range(1000):
            result = await self.app.matrix_service.process("multiply", {
                "matrix_a": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                "matrix_b": [[9, 8, 7], [6, 5, 4], [3, 2, 1]]
            })
            large_results.append(result)

        memory_after_creation = self.get_memory_usage()

        # Clear references and force garbage collection
        large_results.clear()
        del large_results
        gc.collect()

        memory_after_gc = self.get_memory_usage()

        print(f"  Memory before: {memory_before:.2f} MB")
        print(f"  Memory after creation: {memory_after_creation:.2f} MB")
        print(f"  Memory after GC: {memory_after_gc:.2f} MB")

        memory_freed = memory_after_creation - memory_after_gc
        print(f"  Memory freed by GC: {memory_freed:.2f} MB")

        # Check if significant memory was freed
        if memory_freed > 1:  # At least 1MB should be freed
            print("  ✅ Garbage collection effective")
            return True
        else:
            print("  ⚠️  Garbage collection may not be working effectively")
            return False

    async def test_cpu_usage_under_load(self):
        """Test CPU usage under computational load."""
        print("\n⚡ Testing CPU Usage Under Load...")

        # Reset CPU measurement
        self.process.cpu_percent()

        # Perform CPU-intensive operations
        start_time = time.time()
        tasks = []

        # Matrix operations (CPU intensive)
        for i in range(50):
            task = self.app.matrix_service.process("determinant", {
                "matrix": [[i+1, i+2, i+3], [i+4, i+5, i+6], [i+7, i+8, i+9]]
            })
            tasks.append(task)

        # Statistical operations (CPU intensive)
        for i in range(50):
            data = list(range(i, i+100))
            task = self.app.statistics_service.process("std_dev", {"data": data})
            tasks.append(task)

        # Execute all tasks
        await asyncio.gather(*tasks)

        duration = time.time() - start_time
        cpu_usage = self.process.cpu_percent()

        print(f"  Operations completed in: {duration:.2f} seconds")
        print(f"  CPU usage during test: {cpu_usage:.1f}%")
        print(f"  Throughput: {len(tasks)/duration:.1f} ops/sec")

        # Check if CPU usage is reasonable (not stuck at 100%)
        if cpu_usage < 95:
            print("  ✅ CPU usage reasonable")
            return True
        else:
            print("  ⚠️  High CPU usage detected")
            return False

    async def test_concurrent_resource_usage(self):
        """Test resource usage under concurrent load."""
        print("\n🔄 Testing Concurrent Resource Usage...")

        memory_before = self.get_memory_usage()
        self.process.cpu_percent()  # Reset CPU measurement

        async def concurrent_workload():
            """Simulate concurrent user workload."""
            operations = [
                ("arithmetic", "factorial", {"number": 50}),
                ("matrix", "determinant", {"matrix": [[1, 2], [3, 4]]}),
                ("statistics", "mean", {"data": list(range(100))}),
                ("calculus", "derivative", {"expression": "x^3 + 2*x^2 + x", "variable": "x"}),
            ]

            tasks = []
            for service_name, operation, params in operations:
                if service_name == "arithmetic":
                    task = self.app.arithmetic_service.process(operation, params)
                elif service_name == "matrix":
                    task = self.app.matrix_service.process(operation, params)
                elif service_name == "statistics":
                    task = self.app.statistics_service.process(operation, params)
                elif service_name == "calculus":
                    task = self.app.calculus_service.process(operation, params)
                tasks.append(task)

            return await asyncio.gather(*tasks)

        # Run multiple concurrent workloads
        start_time = time.time()
        concurrent_tasks = [concurrent_workload() for _ in range(20)]
        results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
        duration = time.time() - start_time

        memory_after = self.get_memory_usage()
        cpu_usage = self.process.cpu_percent()

        successful = sum(1 for r in results if not isinstance(r, Exception))
        total_operations = len(concurrent_tasks) * 4  # 4 operations per workload

        print(f"  Concurrent workloads: {successful}/{len(concurrent_tasks)} successful")
        print(f"  Total operations: {total_operations}")
        print(f"  Duration: {duration:.2f} seconds")
        print(f"  Throughput: {total_operations/duration:.1f} ops/sec")
        print(f"  Memory usage: {memory_before:.2f} -> {memory_after:.2f} MB")
        print(f"  CPU usage: {cpu_usage:.1f}%")

        # Check if all workloads completed successfully
        if successful == len(concurrent_tasks):
            print("  ✅ All concurrent workloads completed successfully")
            return True
        else:
            print("  ❌ Some concurrent workloads failed")
            return False

    async def test_resource_cleanup(self):
        """Test resource cleanup after operations."""
        print("\n🧹 Testing Resource Cleanup...")

        # Record initial state
        initial_memory = self.get_memory_usage()

        # Perform operations that create temporary resources
        for i in range(100):
            # Operations that might create temporary objects
            await self.app.arithmetic_service.process("factorial", {"number": 20})
            await self.app.matrix_service.process("inverse", {
                "matrix": [[1, 2], [3, 4]]
            })
            await self.app.statistics_service.process("descriptive_stats", {
                "data": list(range(100))
            })

        # Force cleanup
        gc.collect()
        await asyncio.sleep(0.5)  # Allow async cleanup

        final_memory = self.get_memory_usage()
        memory_difference = final_memory - initial_memory

        print(f"  Initial memory: {initial_memory:.2f} MB")
        print(f"  Final memory: {final_memory:.2f} MB")
        print(f"  Memory difference: {memory_difference:.2f} MB")

        # Check if memory usage returned close to initial level
        if memory_difference < 5:  # Less than 5MB growth is acceptable
            print("  ✅ Resource cleanup effective")
            return True
        else:
            print("  ⚠️  Potential resource leak detected")
            return False

    async def run_all_tests(self):
        """Run all resource usage tests."""
        print("🔬 Resource Usage Testing")
        print("=" * 50)

        if not await self.setup():
            return False

        tests = [
            ("Memory Usage Under Load", self.test_memory_usage_under_load),
            ("Garbage Collection", self.test_garbage_collection_effectiveness),
            ("CPU Usage Under Load", self.test_cpu_usage_under_load),
            ("Concurrent Resource Usage", self.test_concurrent_resource_usage),
            ("Resource Cleanup", self.test_resource_cleanup),
        ]

        passed = 0
        failed = 0

        for test_name, test_func in tests:
            try:
                result = await test_func()
                if result:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"  ❌ {test_name}: Error - {e}")
                failed += 1

        # Final memory check
        final_memory = self.get_memory_usage()
        total_memory_growth = final_memory - self.initial_memory

        print("\n" + "=" * 50)
        print("📊 RESOURCE USAGE SUMMARY")
        print("=" * 50)
        print(f"Tests Passed: {passed}")
        print(f"Tests Failed: {failed}")
        print(f"Initial Memory: {self.initial_memory:.2f} MB")
        print(f"Final Memory: {final_memory:.2f} MB")
        print(f"Total Memory Growth: {total_memory_growth:.2f} MB")

        if failed == 0 and total_memory_growth < 20:
            print("\n🎉 ALL RESOURCE TESTS PASSED!")
            print("✅ No significant resource leaks detected")
            return True
        else:
            print(f"\n❌ {failed} RESOURCE TESTS FAILED!")
            if total_memory_growth >= 20:
                print("⚠️  Significant memory growth detected")
            return False


async def main():
    """Main test execution."""
    tester = ResourceUsageTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
