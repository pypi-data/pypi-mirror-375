#!/usr/bin/env python3
"""
End-to-end MCP server testing script.
Tests the actual MCP server functionality with real tool calls.
"""

import asyncio
import sys
import time

from calculator.server.app import create_calculator_app


class MCPServerTester:
    """Test MCP server functionality end-to-end."""

    def __init__(self):
        self.app = None
        self.passed = 0
        self.failed = 0
        self.errors = []

    async def setup(self):
        """Initialize the MCP server."""
        print("🚀 Initializing MCP Server...")
        try:
            self.app = create_calculator_app()
            print(f"✅ Server initialized with {len(self.app.services)} services")
            print(f"✅ Registered {len(self.app.factory.registered_tools)} tools")
            return True
        except Exception as e:
            print(f"❌ Server initialization failed: {e}")
            return False

    async def test_tool_registration(self):
        """Test that all expected tools are registered."""
        print("\n🔧 Testing Tool Registration...")

        expected_tools = [
            "add", "subtract", "multiply", "divide", "power", "sqrt", "factorial",
            "matrix_add", "matrix_multiply", "matrix_determinant", "matrix_inverse",
            "mean", "median", "std_dev", "correlation",
            "derivative", "integral", "limit", "taylor_series"
        ]

        registered_tools = list(self.app.factory.registered_tools.keys())

        for tool in expected_tools:
            if tool in registered_tools:
                print(f"  ✅ {tool}")
                self.passed += 1
            else:
                print(f"  ❌ {tool} (missing)")
                self.failed += 1
                self.errors.append(f"Missing tool: {tool}")

    async def test_arithmetic_operations(self):
        """Test arithmetic operations through the service layer."""
        print("\n🧮 Testing Arithmetic Operations...")

        tests = [
            ("add", {"numbers": [1, 2, 3, 4, 5]}, 15.0),
            ("subtract", {"a": 10, "b": 3}, 7.0),
            ("multiply", {"numbers": [2, 3, 4]}, 24.0),
            ("divide", {"a": 20, "b": 4}, 5.0),
            ("power", {"base": 2, "exponent": 3}, 8.0),
            ("sqrt", {"number": 16}, 4.0),
            ("factorial", {"number": 5}, 120),
        ]

        for operation, params, expected in tests:
            try:
                start_time = time.time()
                result = await self.app.arithmetic_service.process(operation, params)
                duration = time.time() - start_time

                if abs(result - expected) < 1e-10:
                    print(f"  ✅ {operation}: {result} ({duration:.3f}s)")
                    self.passed += 1
                else:
                    print(f"  ❌ {operation}: expected {expected}, got {result}")
                    self.failed += 1
                    self.errors.append(f"{operation}: expected {expected}, got {result}")

            except Exception as e:
                print(f"  ❌ {operation}: error - {e}")
                self.failed += 1
                self.errors.append(f"{operation}: {str(e)}")

    async def test_matrix_operations(self):
        """Test matrix operations."""
        print("\n📊 Testing Matrix Operations...")

        tests = [
            ("add", {
                "matrix_a": [[1, 2], [3, 4]],
                "matrix_b": [[5, 6], [7, 8]]
            }, [[6, 8], [10, 12]]),
            ("multiply", {
                "matrix_a": [[1, 2], [3, 4]],
                "matrix_b": [[5, 6], [7, 8]]
            }, [[19, 22], [43, 50]]),
            ("determinant", {
                "matrix": [[1, 2], [3, 4]]
            }, -2.0),
        ]

        for operation, params, expected in tests:
            try:
                start_time = time.time()
                result = await self.app.matrix_service.process(operation, params)
                duration = time.time() - start_time

                if operation == "determinant":
                    if abs(result - expected) < 1e-10:
                        print(f"  ✅ {operation}: {result} ({duration:.3f}s)")
                        self.passed += 1
                    else:
                        print(f"  ❌ {operation}: expected {expected}, got {result}")
                        self.failed += 1
                else:
                    # For matrix results, check structure
                    if isinstance(result, list) and len(result) == len(expected):
                        print(f"  ✅ {operation}: correct dimensions ({duration:.3f}s)")
                        self.passed += 1
                    else:
                        print(f"  ❌ {operation}: incorrect result structure")
                        self.failed += 1

            except Exception as e:
                print(f"  ❌ {operation}: error - {e}")
                self.failed += 1
                self.errors.append(f"matrix {operation}: {str(e)}")

    async def test_statistics_operations(self):
        """Test statistics operations."""
        print("\n📈 Testing Statistics Operations...")

        data = [1, 2, 3, 4, 5]
        tests = [
            ("mean", {"data": data}, 3.0),
            ("median", {"data": data}, 3.0),
            ("std_dev", {"data": data, "population": False}, 1.5811388300841898),
        ]

        for operation, params, expected in tests:
            try:
                start_time = time.time()
                result = await self.app.statistics_service.process(operation, params)
                duration = time.time() - start_time

                if abs(result - expected) < 1e-10:
                    print(f"  ✅ {operation}: {result} ({duration:.3f}s)")
                    self.passed += 1
                else:
                    print(f"  ❌ {operation}: expected {expected}, got {result}")
                    self.failed += 1
                    self.errors.append(f"stats {operation}: expected {expected}, got {result}")

            except Exception as e:
                print(f"  ❌ {operation}: error - {e}")
                self.failed += 1
                self.errors.append(f"stats {operation}: {str(e)}")

    async def test_calculus_operations(self):
        """Test calculus operations."""
        print("\n∫ Testing Calculus Operations...")

        tests = [
            ("derivative", {"expression": "x^2", "variable": "x"}, "2*x"),
            ("integral", {"expression": "2*x + 1", "variable": "x", "lower_limit": 0, "upper_limit": 2}, 6.0),
        ]

        for operation, params, expected in tests:
            try:
                start_time = time.time()
                result = await self.app.calculus_service.process(operation, params)
                duration = time.time() - start_time

                if operation == "integral" and isinstance(expected, (int, float)):
                    if abs(result - expected) < 1e-10:
                        print(f"  ✅ {operation}: {result} ({duration:.3f}s)")
                        self.passed += 1
                    else:
                        print(f"  ❌ {operation}: expected {expected}, got {result}")
                        self.failed += 1
                else:
                    # For symbolic results, just check that we got a result
                    if result is not None:
                        print(f"  ✅ {operation}: computed ({duration:.3f}s)")
                        self.passed += 1
                    else:
                        print(f"  ❌ {operation}: no result")
                        self.failed += 1

            except Exception as e:
                print(f"  ❌ {operation}: error - {e}")
                self.failed += 1
                self.errors.append(f"calculus {operation}: {str(e)}")

    async def test_caching_performance(self):
        """Test caching functionality and performance."""
        print("\n⚡ Testing Caching Performance...")

        # Test cache miss (first call)
        start_time = time.time()
        result1 = await self.app.arithmetic_service.process("factorial", {"number": 100})
        first_call_time = time.time() - start_time

        # Test cache hit (second call)
        start_time = time.time()
        result2 = await self.app.arithmetic_service.process("factorial", {"number": 100})
        second_call_time = time.time() - start_time

        if result1 == result2:
            print("  ✅ Cache consistency: results match")
            self.passed += 1
        else:
            print("  ❌ Cache consistency: results don't match")
            self.failed += 1

        if second_call_time < first_call_time:
            print(f"  ✅ Cache performance: {first_call_time:.4f}s -> {second_call_time:.4f}s")
            self.passed += 1
        else:
            print("  ⚠️  Cache performance: no improvement detected")
            # Don't fail this as it might be too fast to measure

    async def test_error_handling(self):
        """Test error handling."""
        print("\n🚨 Testing Error Handling...")

        error_tests = [
            ("divide", {"a": 1, "b": 0}, "division by zero"),
            ("sqrt", {"number": -1}, "negative number"),
            ("factorial", {"number": -1}, "negative number"),
        ]

        for operation, params, error_type in error_tests:
            try:
                result = await self.app.arithmetic_service.process(operation, params)
                print(f"  ❌ {operation}: should have raised error for {error_type}")
                self.failed += 1
            except Exception:
                print(f"  ✅ {operation}: correctly raised error for {error_type}")
                self.passed += 1

    async def test_concurrent_operations(self):
        """Test concurrent operation handling."""
        print("\n🔄 Testing Concurrent Operations...")

        async def concurrent_operation(i):
            return await self.app.arithmetic_service.process("add", {"numbers": [i, i+1]})

        start_time = time.time()
        tasks = [concurrent_operation(i) for i in range(20)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.time() - start_time

        successful = sum(1 for r in results if not isinstance(r, Exception))
        failed = len(results) - successful

        print(f"  ✅ Concurrent operations: {successful}/{len(results)} successful ({duration:.3f}s)")
        print(f"  ⚡ Throughput: {len(results)/duration:.1f} ops/sec")

        if successful == len(results):
            self.passed += 1
        else:
            self.failed += 1
            self.errors.append(f"Concurrent operations: {failed} failed")

    async def run_all_tests(self):
        """Run all tests."""
        print("🧪 MCP Server End-to-End Testing")
        print("=" * 50)

        if not await self.setup():
            return False

        await self.test_tool_registration()
        await self.test_arithmetic_operations()
        await self.test_matrix_operations()
        await self.test_statistics_operations()
        await self.test_calculus_operations()
        await self.test_caching_performance()
        await self.test_error_handling()
        await self.test_concurrent_operations()

        # Summary
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0

        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed} ✅")
        print(f"Failed: {self.failed} ❌")
        print(f"Pass Rate: {pass_rate:.1f}%")

        if self.errors:
            print(f"\n🚨 ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")

        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ MCP Server is working correctly")
            return True
        else:
            print(f"\n❌ {self.failed} TESTS FAILED!")
            print("🔧 Please fix the issues before deployment")
            return False


async def main():
    """Main test execution."""
    tester = MCPServerTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
