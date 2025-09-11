#!/usr/bin/env python3
"""
Common test utilities for calculator scripts.
Shared functions to reduce code duplication across test scripts.
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# Add the calculator module to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from calculator.server.app import create_calculator_app


class TestResult:
    """Represents a test result."""

    def __init__(self, name: str, status: str, message: str = "", details: Dict[str, Any] = None):
        self.name = name
        self.status = status  # "passed", "failed", "warning", "skipped"
        self.message = message
        self.details = details or {}
        self.timestamp = time.time()


class TestSuite:
    """Base class for test suites."""

    def __init__(self, name: str):
        self.name = name
        self.results: List[TestResult] = []
        self.app = None

    def record_success(self, test_name: str, message: str = "", details: Dict[str, Any] = None):
        """Record a successful test."""
        self.results.append(TestResult(test_name, "passed", message, details))
        print(f"  ✅ {test_name}: {message}")

    def record_failure(self, test_name: str, message: str = "", details: Dict[str, Any] = None):
        """Record a failed test."""
        self.results.append(TestResult(test_name, "failed", message, details))
        print(f"  ❌ {test_name}: {message}")

    def record_warning(self, test_name: str, message: str = "", details: Dict[str, Any] = None):
        """Record a warning."""
        self.results.append(TestResult(test_name, "warning", message, details))
        print(f"  ⚠️  {test_name}: {message}")

    def record_skip(self, test_name: str, message: str = "", details: Dict[str, Any] = None):
        """Record a skipped test."""
        self.results.append(TestResult(test_name, "skipped", message, details))
        print(f"  ⏭️  {test_name}: {message}")

    def get_summary(self) -> Dict[str, Any]:
        """Get test summary."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == "passed")
        failed = sum(1 for r in self.results if r.status == "failed")
        warnings = sum(1 for r in self.results if r.status == "warning")
        skipped = sum(1 for r in self.results if r.status == "skipped")

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "skipped": skipped,
            "success_rate": (passed / total * 100) if total > 0 else 0
        }

    def print_summary(self):
        """Print test summary."""
        summary = self.get_summary()

        print(f"\n📊 {self.name} Test Summary")
        print("=" * 50)
        print(f"Total Tests: {summary['total']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failed']} ❌")
        print(f"Warnings: {summary['warnings']} ⚠️")
        print(f"Skipped: {summary['skipped']} ⏭️")
        print(f"Success Rate: {summary['success_rate']:.1f}%")

        if summary['failed'] == 0:
            print(f"\n🎉 All {self.name} tests passed!")
            return True
        else:
            print(f"\n❌ {summary['failed']} test(s) failed.")
            return False

    def save_results(self, filename: str):
        """Save results to JSON file."""
        # Use RESULTS_DIR environment variable if available, otherwise current directory
        import os
        results_dir = os.environ.get('RESULTS_DIR', '.')
        if results_dir != '.':
            os.makedirs(results_dir, exist_ok=True)
            filepath = os.path.join(results_dir, filename)
        else:
            filepath = filename
            
        results_data = {
            "suite_name": self.name,
            "summary": self.get_summary(),
            "results": [
                {
                    "name": r.name,
                    "status": r.status,
                    "message": r.message,
                    "details": r.details,
                    "timestamp": r.timestamp
                }
                for r in self.results
            ]
        }

        with open(filepath, 'w') as f:
            json.dump(results_data, f, indent=2)

        print(f"📄 Results saved to: {filepath}")


async def create_test_app() -> Any:
    """Create a calculator app for testing."""
    return create_calculator_app()


async def test_basic_operations(app) -> List[TestResult]:
    """Test basic arithmetic operations."""
    results = []

    test_cases = [
        ('add', {'numbers': [1, 2, 3, 4, 5]}, 15.0),
        ('subtract', {'a': 10, 'b': 3}, 7.0),
        ('multiply', {'numbers': [2, 3, 4]}, 24.0),
        ('divide', {'a': 10, 'b': 2}, 5.0),
        ('power', {'base': 2, 'exponent': 3}, 8.0),
        ('sqrt', {'number': 16}, 4.0),
        ('factorial', {'number': 5}, 120),
        ('sine', {'angle': 0, 'unit': 'radians'}, 0.0),
        ('cosine', {'angle': 0, 'unit': 'radians'}, 1.0)
    ]

    for operation, params, expected in test_cases:
        try:
            result = await app.arithmetic_service.process(operation, params)
            if abs(result - expected) < 1e-10:
                results.append(TestResult(f"arithmetic_{operation}", "passed", f"Result: {result}"))
            else:
                results.append(TestResult(f"arithmetic_{operation}", "failed", f"Expected {expected}, got {result}"))
        except Exception as e:
            results.append(TestResult(f"arithmetic_{operation}", "failed", str(e)))

    return results


async def test_matrix_operations(app) -> List[TestResult]:
    """Test matrix operations."""
    results = []

    matrix_a = [[1, 2], [3, 4]]
    matrix_b = [[5, 6], [7, 8]]

    test_cases = [
        ('add', {'matrix_a': matrix_a, 'matrix_b': matrix_b}, [[6, 8], [10, 12]]),
        ('multiply', {'matrix_a': matrix_a, 'matrix_b': matrix_b}, [[19, 22], [43, 50]]),
        ('determinant', {'matrix': matrix_a}, -2.0),
        ('transpose', {'matrix': [[1, 2, 3], [4, 5, 6]]}, [[1, 4], [2, 5], [3, 6]])
    ]

    for operation, params, expected in test_cases:
        try:
            result = await app.matrix_service.process(operation, params)
            if result == expected or (isinstance(expected, float) and abs(result - expected) < 1e-10):
                results.append(TestResult(f"matrix_{operation}", "passed", "Correct result"))
            else:
                results.append(TestResult(f"matrix_{operation}", "failed", f"Expected {expected}, got {result}"))
        except Exception as e:
            results.append(TestResult(f"matrix_{operation}", "failed", str(e)))

    return results


async def test_statistics_operations(app) -> List[TestResult]:
    """Test statistics operations."""
    results = []

    test_data = [1, 2, 3, 4, 5]

    test_cases = [
        ('mean', {'data': test_data}, 3.0),
        ('median', {'data': test_data}, 3.0),
        ('variance', {'data': test_data, 'population': False}, 2.5),
        ('correlation', {'x_data': [1, 2, 3], 'y_data': [2, 4, 6]}, 1.0)
    ]

    for operation, params, expected in test_cases:
        try:
            result = await app.statistics_service.process(operation, params)
            if abs(result - expected) < 1e-10:
                results.append(TestResult(f"statistics_{operation}", "passed", f"Result: {result}"))
            else:
                results.append(TestResult(f"statistics_{operation}", "failed", f"Expected {expected}, got {result}"))
        except Exception as e:
            results.append(TestResult(f"statistics_{operation}", "failed", str(e)))

    return results


async def test_calculus_operations(app) -> List[TestResult]:
    """Test calculus operations."""
    results = []

    # Test derivative
    try:
        result = await app.calculus_service.process('derivative', {
            'expression': 'x^2 + 2*x + 1',
            'variable': 'x'
        })
        if result is not None:
            results.append(TestResult("calculus_derivative", "passed", "Derivative computed"))
        else:
            results.append(TestResult("calculus_derivative", "failed", "No result returned"))
    except Exception as e:
        results.append(TestResult("calculus_derivative", "failed", str(e)))

    # Test integral
    try:
        result = await app.calculus_service.process('integral', {
            'expression': '2*x + 1',
            'variable': 'x',
            'lower_limit': 0,
            'upper_limit': 2
        })
        if isinstance(result, (int, float)) and abs(result - 6.0) < 1e-10:
            results.append(TestResult("calculus_integral", "passed", f"Result: {result}"))
        else:
            results.append(TestResult("calculus_integral", "failed", f"Expected 6.0, got {result}"))
    except Exception as e:
        results.append(TestResult("calculus_integral", "failed", str(e)))

    return results


async def test_service_initialization(app) -> List[TestResult]:
    """Test that all services are properly initialized."""
    results = []

    services = ['arithmetic_service', 'matrix_service', 'statistics_service', 'calculus_service']
    for service_name in services:
        if hasattr(app, service_name) and getattr(app, service_name) is not None:
            results.append(TestResult(f"service_init_{service_name}", "passed", "Service available"))
        else:
            results.append(TestResult(f"service_init_{service_name}", "failed", "Service not available"))

    return results


async def test_repository_initialization(app) -> List[TestResult]:
    """Test that all repositories are properly initialized."""
    results = []

    repositories = ['cache_repo', 'constants_repo', 'currency_repo']
    for repo_name in repositories:
        if hasattr(app, repo_name) and getattr(app, repo_name) is not None:
            results.append(TestResult(f"repo_init_{repo_name}", "passed", "Repository available"))
        else:
            results.append(TestResult(f"repo_init_{repo_name}", "failed", "Repository not available"))

    return results


async def measure_performance(app, operation_func, iterations: int = 100) -> Dict[str, float]:
    """Measure performance of an operation."""
    times = []

    # Warm up
    for _ in range(10):
        try:
            await operation_func()
        except:
            continue

    # Measure
    for _ in range(iterations):
        try:
            start = time.perf_counter()
            await operation_func()
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to milliseconds
        except:
            continue

    if not times:
        return {"avg_ms": 0, "min_ms": 0, "max_ms": 0, "ops_per_sec": 0}

    import statistics
    avg_ms = statistics.mean(times)

    return {
        "avg_ms": avg_ms,
        "min_ms": min(times),
        "max_ms": max(times),
        "ops_per_sec": 1000 / avg_ms if avg_ms > 0 else 0
    }


async def test_concurrent_operations(app, num_operations: int = 20) -> TestResult:
    """Test concurrent operations."""
    try:
        tasks = []
        for i in range(num_operations):
            task = app.arithmetic_service.process('add', {'numbers': [i, i+1, i+2]})
            tasks.append(task)

        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time

        successful = sum(1 for r in results if not isinstance(r, Exception))
        failed = len(results) - successful

        if failed == 0:
            return TestResult(
                "concurrent_operations",
                "passed",
                f"All {len(results)} operations succeeded in {total_time:.3f}s"
            )
        else:
            return TestResult(
                "concurrent_operations",
                "warning",
                f"{failed} out of {len(results)} failed"
            )
    except Exception as e:
        return TestResult("concurrent_operations", "failed", str(e))


def validate_app_initialization(app) -> TestResult:
    """Validate that the app is properly initialized."""
    try:
        if not hasattr(app, 'is_initialized') or not app.is_initialized:
            return TestResult("app_initialization", "failed", "App not marked as initialized")

        return TestResult("app_initialization", "passed", "App properly initialized")
    except Exception as e:
        return TestResult("app_initialization", "failed", str(e))


async def run_comprehensive_validation(app_name: str = "Calculator") -> bool:
    """Run comprehensive validation suite."""
    suite = TestSuite(f"{app_name} Validation")

    print(f"🔍 Starting {app_name} Comprehensive Validation")
    print("=" * 60)

    try:
        # Initialize application
        print("\n📋 Initializing Application...")
        app = await create_test_app()

        # Validate initialization
        init_result = validate_app_initialization(app)
        if init_result.status == "passed":
            suite.record_success(init_result.name, init_result.message)
        else:
            suite.record_failure(init_result.name, init_result.message)

        # Test service initialization
        print("\n🔧 Testing Service Initialization...")
        service_results = await test_service_initialization(app)
        for result in service_results:
            if result.status == "passed":
                suite.record_success(result.name, result.message)
            else:
                suite.record_failure(result.name, result.message)

        # Test repository initialization
        print("\n📚 Testing Repository Initialization...")
        repo_results = await test_repository_initialization(app)
        for result in repo_results:
            if result.status == "passed":
                suite.record_success(result.name, result.message)
            else:
                suite.record_failure(result.name, result.message)

        # Test core functionality
        print("\n🧮 Testing Core Functionality...")

        # Arithmetic operations
        arithmetic_results = await test_basic_operations(app)
        for result in arithmetic_results:
            if result.status == "passed":
                suite.record_success(result.name, result.message)
            else:
                suite.record_failure(result.name, result.message)

        # Matrix operations
        matrix_results = await test_matrix_operations(app)
        for result in matrix_results:
            if result.status == "passed":
                suite.record_success(result.name, result.message)
            else:
                suite.record_failure(result.name, result.message)

        # Statistics operations
        stats_results = await test_statistics_operations(app)
        for result in stats_results:
            if result.status == "passed":
                suite.record_success(result.name, result.message)
            else:
                suite.record_failure(result.name, result.message)

        # Calculus operations
        calculus_results = await test_calculus_operations(app)
        for result in calculus_results:
            if result.status == "passed":
                suite.record_success(result.name, result.message)
            else:
                suite.record_failure(result.name, result.message)

        # Test concurrent operations
        print("\n🔄 Testing Concurrent Operations...")
        concurrent_result = await test_concurrent_operations(app)
        if concurrent_result.status == "passed":
            suite.record_success(concurrent_result.name, concurrent_result.message)
        elif concurrent_result.status == "warning":
            suite.record_warning(concurrent_result.name, concurrent_result.message)
        else:
            suite.record_failure(concurrent_result.name, concurrent_result.message)

        # Shutdown app
        if hasattr(app, 'shutdown'):
            await app.shutdown()

    except Exception as e:
        suite.record_failure("critical_error", f"Critical validation error: {e}")

    # Print summary and return success status
    return suite.print_summary()


if __name__ == "__main__":
    success = asyncio.run(run_comprehensive_validation())
    sys.exit(0 if success else 1)
