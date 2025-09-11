#!/usr/bin/env python3
"""
Load testing script for the MCP calculator server.
Tests performance under various load conditions.
"""

import asyncio
import random
import statistics
import sys
import time

from calculator.server.app import create_calculator_app


class LoadTester:
    """Load testing for MCP calculator server."""

    def __init__(self):
        self.app = None
        self.results = []

    async def setup(self):
        """Initialize the server."""
        print("🚀 Initializing MCP Server for load testing...")
        self.app = create_calculator_app()
        print("✅ Server initialized")
        return True

    async def single_operation_test(self, operation_type: str, duration: int = 10):
        """Test single operation type under load."""
        print(f"\n⚡ Load Testing: {operation_type} operations for {duration}s")

        operations = {
            "arithmetic": [
                ("add", {"numbers": [random.randint(1, 100) for _ in range(5)]}),
                ("multiply", {"numbers": [random.randint(1, 10) for _ in range(3)]}),
                ("power", {"base": random.randint(2, 10), "exponent": random.randint(2, 5)}),
                ("sqrt", {"number": random.randint(1, 1000)}),
                ("factorial", {"number": random.randint(1, 20)}),
            ],
            "matrix": [
                ("determinant", {"matrix": [[random.randint(1, 10) for _ in range(3)] for _ in range(3)]}),
                ("add", {
                    "matrix_a": [[random.randint(1, 10) for _ in range(2)] for _ in range(2)],
                    "matrix_b": [[random.randint(1, 10) for _ in range(2)] for _ in range(2)]
                }),
                ("multiply", {
                    "matrix_a": [[random.randint(1, 5) for _ in range(2)] for _ in range(2)],
                    "matrix_b": [[random.randint(1, 5) for _ in range(2)] for _ in range(2)]
                }),
            ],
            "statistics": [
                ("mean", {"data": [random.randint(1, 100) for _ in range(50)]}),
                ("std_dev", {"data": [random.randint(1, 100) for _ in range(30)]}),
                ("correlation", {
                    "x_data": [random.randint(1, 100) for _ in range(20)],
                    "y_data": [random.randint(1, 100) for _ in range(20)]
                }),
            ],
            "calculus": [
                ("derivative", {"expression": f"x^{random.randint(2, 5)}", "variable": "x"}),
                ("integral", {
                    "expression": f"{random.randint(1, 5)}*x + {random.randint(1, 10)}",
                    "variable": "x",
                    "lower_limit": 0,
                    "upper_limit": random.randint(1, 5)
                }),
            ]
        }

        if operation_type not in operations:
            print(f"❌ Unknown operation type: {operation_type}")
            return False

        # Get service
        service_map = {
            "arithmetic": self.app.arithmetic_service,
            "matrix": self.app.matrix_service,
            "statistics": self.app.statistics_service,
            "calculus": self.app.calculus_service,
        }
        service = service_map[operation_type]

        # Run load test
        start_time = time.time()
        end_time = start_time + duration
        completed_operations = 0
        response_times = []
        errors = 0

        while time.time() < end_time:
            # Select random operation
            op_name, params = random.choice(operations[operation_type])

            try:
                op_start = time.time()
                result = await service.process(op_name, params)
                op_end = time.time()

                response_time = op_end - op_start
                response_times.append(response_time)
                completed_operations += 1

            except Exception as e:
                errors += 1
                print(f"  Error in {op_name}: {e}")

        actual_duration = time.time() - start_time

        # Calculate statistics
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
            throughput = completed_operations / actual_duration
        else:
            avg_response_time = min_response_time = max_response_time = p95_response_time = throughput = 0

        print("  📊 Results:")
        print(f"    Duration: {actual_duration:.2f}s")
        print(f"    Completed operations: {completed_operations}")
        print(f"    Errors: {errors}")
        print(f"    Throughput: {throughput:.1f} ops/sec")
        print(f"    Avg response time: {avg_response_time*1000:.2f}ms")
        print(f"    Min response time: {min_response_time*1000:.2f}ms")
        print(f"    Max response time: {max_response_time*1000:.2f}ms")
        print(f"    95th percentile: {p95_response_time*1000:.2f}ms")

        # Store results
        self.results.append({
            "test_type": f"{operation_type}_load",
            "duration": actual_duration,
            "operations": completed_operations,
            "errors": errors,
            "throughput": throughput,
            "avg_response_time": avg_response_time,
            "p95_response_time": p95_response_time,
        })

        # Check if performance is acceptable
        success = (
            errors == 0 and
            throughput > 10 and  # At least 10 ops/sec
            avg_response_time < 0.1 and  # Less than 100ms average
            p95_response_time < 0.5  # Less than 500ms for 95th percentile
        )

        if success:
            print(f"  ✅ {operation_type} load test passed")
        else:
            print(f"  ❌ {operation_type} load test failed")

        return success

    async def concurrent_users_test(self, num_users: int = 50, duration: int = 30):
        """Test concurrent users scenario."""
        print(f"\n👥 Concurrent Users Test: {num_users} users for {duration}s")

        async def simulate_user(user_id: int):
            """Simulate a single user's workload."""
            operations_completed = 0
            errors = 0
            response_times = []

            user_start = time.time()
            user_end = user_start + duration

            while time.time() < user_end:
                # Random user behavior - mix of operations
                operation_choice = random.choice([
                    ("arithmetic", "add", {"numbers": [random.randint(1, 100) for _ in range(3)]}),
                    ("arithmetic", "multiply", {"numbers": [random.randint(1, 10) for _ in range(2)]}),
                    ("matrix", "determinant", {"matrix": [[random.randint(1, 5) for _ in range(2)] for _ in range(2)]}),
                    ("statistics", "mean", {"data": [random.randint(1, 50) for _ in range(10)]}),
                ])

                service_type, op_name, params = operation_choice

                try:
                    op_start = time.time()

                    if service_type == "arithmetic":
                        result = await self.app.arithmetic_service.process(op_name, params)
                    elif service_type == "matrix":
                        result = await self.app.matrix_service.process(op_name, params)
                    elif service_type == "statistics":
                        result = await self.app.statistics_service.process(op_name, params)

                    op_end = time.time()
                    response_times.append(op_end - op_start)
                    operations_completed += 1

                    # Small delay to simulate user think time
                    await asyncio.sleep(random.uniform(0.01, 0.05))

                except Exception:
                    errors += 1

            return {
                "user_id": user_id,
                "operations": operations_completed,
                "errors": errors,
                "response_times": response_times
            }

        # Start all users concurrently
        start_time = time.time()
        user_tasks = [simulate_user(i) for i in range(num_users)]
        user_results = await asyncio.gather(*user_tasks, return_exceptions=True)
        actual_duration = time.time() - start_time

        # Aggregate results
        total_operations = 0
        total_errors = 0
        all_response_times = []
        successful_users = 0

        for result in user_results:
            if isinstance(result, Exception):
                print(f"  ❌ User simulation failed: {result}")
                continue

            successful_users += 1
            total_operations += result["operations"]
            total_errors += result["errors"]
            all_response_times.extend(result["response_times"])

        # Calculate overall statistics
        if all_response_times:
            avg_response_time = statistics.mean(all_response_times)
            p95_response_time = statistics.quantiles(all_response_times, n=20)[18]
            throughput = total_operations / actual_duration
        else:
            avg_response_time = p95_response_time = throughput = 0

        print("  📊 Concurrent Users Results:")
        print(f"    Duration: {actual_duration:.2f}s")
        print(f"    Successful users: {successful_users}/{num_users}")
        print(f"    Total operations: {total_operations}")
        print(f"    Total errors: {total_errors}")
        print(f"    Overall throughput: {throughput:.1f} ops/sec")
        print(f"    Avg response time: {avg_response_time*1000:.2f}ms")
        print(f"    95th percentile: {p95_response_time*1000:.2f}ms")

        # Store results
        self.results.append({
            "test_type": "concurrent_users",
            "users": num_users,
            "duration": actual_duration,
            "successful_users": successful_users,
            "operations": total_operations,
            "errors": total_errors,
            "throughput": throughput,
            "avg_response_time": avg_response_time,
            "p95_response_time": p95_response_time,
        })

        # Check success criteria
        success = (
            successful_users >= num_users * 0.95 and  # 95% of users successful
            total_errors < total_operations * 0.01 and  # Less than 1% error rate
            throughput > num_users * 0.5 and  # At least 0.5 ops/sec per user
            p95_response_time < 1.0  # Less than 1 second for 95th percentile
        )

        if success:
            print("  ✅ Concurrent users test passed")
        else:
            print("  ❌ Concurrent users test failed")

        return success

    async def stress_test(self, max_concurrent: int = 100, ramp_up_time: int = 60):
        """Stress test with gradually increasing load."""
        print(f"\n🔥 Stress Test: Ramping up to {max_concurrent} concurrent operations over {ramp_up_time}s")

        async def stress_operation():
            """Single stress test operation."""
            # Mix of operations with varying complexity
            operations = [
                ("light", self.app.arithmetic_service.process("add", {"numbers": [1, 2, 3]})),
                ("medium", self.app.matrix_service.process("determinant", {"matrix": [[1, 2], [3, 4]]})),
                ("heavy", self.app.statistics_service.process("std_dev", {"data": list(range(100))})),
            ]

            complexity, task = random.choice(operations)
            start_time = time.time()

            try:
                result = await task
                end_time = time.time()
                return {
                    "success": True,
                    "complexity": complexity,
                    "response_time": end_time - start_time
                }
            except Exception as e:
                end_time = time.time()
                return {
                    "success": False,
                    "complexity": complexity,
                    "response_time": end_time - start_time,
                    "error": str(e)
                }

        # Gradually ramp up load
        start_time = time.time()
        all_results = []

        for second in range(ramp_up_time):
            # Calculate current load level
            progress = second / ramp_up_time
            current_concurrent = int(max_concurrent * progress)

            if current_concurrent > 0:
                # Launch concurrent operations
                tasks = [stress_operation() for _ in range(current_concurrent)]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process results
                for result in batch_results:
                    if isinstance(result, Exception):
                        all_results.append({
                            "success": False,
                            "complexity": "unknown",
                            "response_time": 0,
                            "error": str(result)
                        })
                    else:
                        all_results.append(result)

            # Small delay between batches
            await asyncio.sleep(1)

        actual_duration = time.time() - start_time

        # Analyze results
        successful = sum(1 for r in all_results if r["success"])
        failed = len(all_results) - successful

        if all_results:
            response_times = [r["response_time"] for r in all_results if r["success"]]
            if response_times:
                avg_response_time = statistics.mean(response_times)
                max_response_time = max(response_times)
                p95_response_time = statistics.quantiles(response_times, n=20)[18]
            else:
                avg_response_time = max_response_time = p95_response_time = 0

            throughput = len(all_results) / actual_duration
        else:
            avg_response_time = max_response_time = p95_response_time = throughput = 0

        print("  📊 Stress Test Results:")
        print(f"    Duration: {actual_duration:.2f}s")
        print(f"    Total operations: {len(all_results)}")
        print(f"    Successful: {successful}")
        print(f"    Failed: {failed}")
        print(f"    Success rate: {successful/len(all_results)*100:.1f}%" if all_results else "0%")
        print(f"    Throughput: {throughput:.1f} ops/sec")
        print(f"    Avg response time: {avg_response_time*1000:.2f}ms")
        print(f"    Max response time: {max_response_time*1000:.2f}ms")
        print(f"    95th percentile: {p95_response_time*1000:.2f}ms")

        # Store results
        self.results.append({
            "test_type": "stress_test",
            "max_concurrent": max_concurrent,
            "duration": actual_duration,
            "operations": len(all_results),
            "successful": successful,
            "failed": failed,
            "success_rate": successful/len(all_results) if all_results else 0,
            "throughput": throughput,
            "avg_response_time": avg_response_time,
            "max_response_time": max_response_time,
            "p95_response_time": p95_response_time,
        })

        # Check success criteria
        success_rate = successful/len(all_results) if all_results else 0
        success = (
            success_rate > 0.95 and  # 95% success rate
            p95_response_time < 2.0 and  # Less than 2 seconds for 95th percentile
            throughput > 10  # At least 10 ops/sec overall
        )

        if success:
            print("  ✅ Stress test passed")
        else:
            print("  ❌ Stress test failed")

        return success

    async def run_all_tests(self):
        """Run all load tests."""
        print("🔥 Load Testing Suite")
        print("=" * 50)

        if not await self.setup():
            return False

        tests = [
            ("Arithmetic Load", lambda: self.single_operation_test("arithmetic", 15)),
            ("Matrix Load", lambda: self.single_operation_test("matrix", 15)),
            ("Statistics Load", lambda: self.single_operation_test("statistics", 15)),
            ("Calculus Load", lambda: self.single_operation_test("calculus", 15)),
            ("Concurrent Users", lambda: self.concurrent_users_test(25, 20)),
            ("Stress Test", lambda: self.stress_test(50, 30)),
        ]

        passed = 0
        failed = 0

        for test_name, test_func in tests:
            try:
                print(f"\n🧪 Running {test_name}...")
                result = await test_func()
                if result:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"  ❌ {test_name}: Error - {e}")
                failed += 1

        # Summary
        print("\n" + "=" * 50)
        print("📊 LOAD TESTING SUMMARY")
        print("=" * 50)
        print(f"Tests Passed: {passed}")
        print(f"Tests Failed: {failed}")

        # Overall performance summary
        if self.results:
            avg_throughput = statistics.mean([r.get("throughput", 0) for r in self.results if r.get("throughput")])
            avg_response_time = statistics.mean([r.get("avg_response_time", 0) for r in self.results if r.get("avg_response_time")])

            print(f"Average Throughput: {avg_throughput:.1f} ops/sec")
            print(f"Average Response Time: {avg_response_time*1000:.2f}ms")

        if failed == 0:
            print("\n🎉 ALL LOAD TESTS PASSED!")
            print("✅ Server can handle expected load")
            return True
        else:
            print(f"\n❌ {failed} LOAD TESTS FAILED!")
            print("⚠️  Server may not handle expected load")
            return False


async def main():
    """Main test execution."""
    tester = LoadTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
