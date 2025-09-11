#!/usr/bin/env python3
"""
Performance benchmarking script for the refactored calculator.
Provides detailed performance analysis and comparison.
"""

import asyncio
import json
import os
import statistics
import sys
import time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calculator.server.app import create_calculator_app


class PerformanceBenchmark:
    """Performance benchmarking suite."""

    def __init__(self):
        self.app = None
        self.results = {}
        self.baseline_results = {}

    async def setup(self):
        """Initialize the calculator app."""
        print("🚀 Initializing Calculator App for Benchmarking...")
        self.app = create_calculator_app()
        print("✅ App initialized successfully")

    async def benchmark_arithmetic_operations(self):
        """Benchmark arithmetic operations."""
        print("\n🧮 Benchmarking Arithmetic Operations...")

        operations = [
            ("add", {"numbers": list(range(1, 101))}),  # Sum 1-100
            ("multiply", {"numbers": [2, 3, 4, 5, 6]}),
            ("power", {"base": 2, "exponent": 20}),
            ("factorial", {"number": 20}),
            ("sqrt", {"number": 1000000}),
            ("sine", {"angle": 1.5708, "unit": "radians"}),
            ("cosine", {"angle": 0, "unit": "radians"}),
            ("log", {"number": 1000, "base": 10}),
        ]

        results = {}

        for operation, params in operations:
            times = []

            # Warm up
            for _ in range(10):
                await self.app.arithmetic_service.process(operation, params)

            # Benchmark
            for _ in range(100):
                start = time.perf_counter()
                result = await self.app.arithmetic_service.process(operation, params)
                end = time.perf_counter()
                times.append((end - start) * 1000)  # Convert to milliseconds

            results[operation] = {
                "avg_ms": statistics.mean(times),
                "median_ms": statistics.median(times),
                "min_ms": min(times),
                "max_ms": max(times),
                "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
                "ops_per_sec": 1000 / statistics.mean(times),
            }

            print(f"  {operation:12}: {results[operation]['avg_ms']:.3f}ms avg, {results[operation]['ops_per_sec']:.0f} ops/sec")

        self.results["arithmetic"] = results

    async def benchmark_matrix_operations(self):
        """Benchmark matrix operations."""
        print("\n📊 Benchmarking Matrix Operations...")

        # Test different matrix sizes
        sizes = [5, 10, 20]
        operations = ["add", "multiply", "determinant", "transpose"]

        results = {}

        for size in sizes:
            # Generate test matrices
            matrix_a = [[1.0] * size for _ in range(size)]
            matrix_b = [[2.0] * size for _ in range(size)]

            size_results = {}

            for operation in operations:
                if operation in ["add", "multiply"]:
                    params = {"matrix_a": matrix_a, "matrix_b": matrix_b}
                else:
                    params = {"matrix": matrix_a}

                times = []

                # Warm up
                for _ in range(5):
                    try:
                        await self.app.matrix_service.process(operation, params)
                    except:
                        continue

                # Benchmark
                iterations = 50 if size <= 10 else 10
                for _ in range(iterations):
                    try:
                        start = time.perf_counter()
                        result = await self.app.matrix_service.process(operation, params)
                        end = time.perf_counter()
                        times.append((end - start) * 1000)
                    except:
                        continue

                if times:
                    size_results[operation] = {
                        "avg_ms": statistics.mean(times),
                        "median_ms": statistics.median(times),
                        "min_ms": min(times),
                        "max_ms": max(times),
                        "ops_per_sec": 1000 / statistics.mean(times),
                        "successful_ops": len(times),
                        "total_attempts": iterations,
                    }

                    print(f"  {operation:12} {size}x{size}: {size_results[operation]['avg_ms']:.3f}ms avg")

            results[f"{size}x{size}"] = size_results

        self.results["matrix"] = results

    async def benchmark_statistics_operations(self):
        """Benchmark statistics operations."""
        print("\n📈 Benchmarking Statistics Operations...")

        # Test different data sizes
        data_sizes = [100, 1000, 10000]
        operations = ["mean", "median", "std_dev", "variance", "descriptive_stats"]

        results = {}

        for size in data_sizes:
            # Generate test data
            data = list(range(1, size + 1))

            size_results = {}

            for operation in operations:
                params = {"data": data}
                if operation in ["std_dev", "variance"]:
                    params["population"] = False

                times = []

                # Warm up
                for _ in range(5):
                    await self.app.statistics_service.process(operation, params)

                # Benchmark
                iterations = 50 if size <= 1000 else 10
                for _ in range(iterations):
                    start = time.perf_counter()
                    result = await self.app.statistics_service.process(operation, params)
                    end = time.perf_counter()
                    times.append((end - start) * 1000)

                size_results[operation] = {
                    "avg_ms": statistics.mean(times),
                    "median_ms": statistics.median(times),
                    "throughput_items_per_ms": size / statistics.mean(times),
                    "ops_per_sec": 1000 / statistics.mean(times),
                }

                print(f"  {operation:15} {size:5} items: {size_results[operation]['avg_ms']:.3f}ms avg, {size_results[operation]['throughput_items_per_ms']:.0f} items/ms")

            results[f"{size}_items"] = size_results

        self.results["statistics"] = results

    async def benchmark_calculus_operations(self):
        """Benchmark calculus operations."""
        print("\n∫ Benchmarking Calculus Operations...")

        operations = [
            ("derivative", {"expression": "x^3 + 2*x^2 + x + 1", "variable": "x"}),
            ("integral", {"expression": "2*x + 1", "variable": "x"}),
            ("integral", {"expression": "2*x + 1", "variable": "x", "lower_limit": 0, "upper_limit": 2}),
            ("limit", {"expression": "sin(x)/x", "variable": "x", "approach_value": "0"}),
            ("taylor_series", {"expression": "sin(x)", "variable": "x", "center": 0, "order": 5}),
        ]

        results = {}

        for i, (operation, params) in enumerate(operations):
            operation_key = f"{operation}_{i+1}"
            times = []

            # Warm up
            for _ in range(3):
                try:
                    await self.app.calculus_service.process(operation, params)
                except:
                    continue

            # Benchmark
            for _ in range(20):
                try:
                    start = time.perf_counter()
                    result = await self.app.calculus_service.process(operation, params)
                    end = time.perf_counter()
                    times.append((end - start) * 1000)
                except:
                    continue

            if times:
                results[operation_key] = {
                    "operation": operation,
                    "params": str(params),
                    "avg_ms": statistics.mean(times),
                    "median_ms": statistics.median(times),
                    "min_ms": min(times),
                    "max_ms": max(times),
                    "ops_per_sec": 1000 / statistics.mean(times),
                    "successful_ops": len(times),
                }

                print(f"  {operation:12}: {results[operation_key]['avg_ms']:.3f}ms avg")

        self.results["calculus"] = results

    async def benchmark_caching_performance(self):
        """Benchmark caching performance."""
        print("\n⚡ Benchmarking Caching Performance...")

        # Test cache miss vs cache hit
        operation = "factorial"
        params = {"number": 50}

        # Cache miss (first call)
        cache_miss_times = []
        for _ in range(10):
            # Clear cache by using different numbers
            start = time.perf_counter()
            result = await self.app.arithmetic_service.process(operation, {"number": 50 + _})
            end = time.perf_counter()
            cache_miss_times.append((end - start) * 1000)

        # Cache hit (repeated calls)
        cache_hit_times = []
        for _ in range(10):
            start = time.perf_counter()
            result = await self.app.arithmetic_service.process(operation, params)
            end = time.perf_counter()
            cache_hit_times.append((end - start) * 1000)

        results = {
            "cache_miss": {
                "avg_ms": statistics.mean(cache_miss_times),
                "median_ms": statistics.median(cache_miss_times),
            },
            "cache_hit": {
                "avg_ms": statistics.mean(cache_hit_times),
                "median_ms": statistics.median(cache_hit_times),
            },
            "speedup_factor": statistics.mean(cache_miss_times) / statistics.mean(cache_hit_times),
        }

        print(f"  Cache miss:  {results['cache_miss']['avg_ms']:.3f}ms avg")
        print(f"  Cache hit:   {results['cache_hit']['avg_ms']:.3f}ms avg")
        print(f"  Speedup:     {results['speedup_factor']:.1f}x faster")

        self.results["caching"] = results

    async def benchmark_concurrent_operations(self):
        """Benchmark concurrent operations."""
        print("\n🔄 Benchmarking Concurrent Operations...")

        async def single_operation(op_id: int):
            start = time.perf_counter()
            result = await self.app.arithmetic_service.process("add", {"numbers": [1, 2, 3, op_id]})
            end = time.perf_counter()
            return (end - start) * 1000

        concurrency_levels = [1, 10, 50, 100]
        results = {}

        for concurrency in concurrency_levels:
            # Run concurrent operations
            start_total = time.perf_counter()
            tasks = [single_operation(i) for i in range(concurrency)]
            execution_times = await asyncio.gather(*tasks)
            end_total = time.perf_counter()

            total_time = (end_total - start_total) * 1000

            results[f"concurrency_{concurrency}"] = {
                "total_time_ms": total_time,
                "avg_operation_time_ms": statistics.mean(execution_times),
                "max_operation_time_ms": max(execution_times),
                "throughput_ops_per_sec": concurrency / (total_time / 1000),
                "concurrency_level": concurrency,
            }

            print(f"  {concurrency:3} concurrent: {results[f'concurrency_{concurrency}']['total_time_ms']:.3f}ms total, {results[f'concurrency_{concurrency}']['throughput_ops_per_sec']:.0f} ops/sec")

        self.results["concurrent"] = results

    def generate_report(self):
        """Generate performance report."""
        print("\n" + "="*60)
        print("📊 PERFORMANCE BENCHMARK REPORT")
        print("="*60)

        # Overall summary
        total_operations = 0
        avg_response_times = []

        for category, category_results in self.results.items():
            if category == "concurrent":
                continue

            print(f"\n{category.upper()} OPERATIONS:")
            print("-" * 40)

            for operation, metrics in category_results.items():
                if isinstance(metrics, dict) and "avg_ms" in metrics:
                    total_operations += 1
                    avg_response_times.append(metrics["avg_ms"])

                    if "ops_per_sec" in metrics:
                        print(f"  {operation:20}: {metrics['avg_ms']:6.3f}ms avg, {metrics['ops_per_sec']:8.0f} ops/sec")
                    else:
                        print(f"  {operation:20}: {metrics['avg_ms']:6.3f}ms avg")

        # Performance summary
        if avg_response_times:
            overall_avg = statistics.mean(avg_response_times)
            overall_median = statistics.median(avg_response_times)

            print("\nOVERALL PERFORMANCE SUMMARY:")
            print("-" * 40)
            print(f"  Total operations tested: {total_operations}")
            print(f"  Average response time:   {overall_avg:.3f}ms")
            print(f"  Median response time:    {overall_median:.3f}ms")
            print(f"  Fastest operation:       {min(avg_response_times):.3f}ms")
            print(f"  Slowest operation:       {max(avg_response_times):.3f}ms")

        # Caching performance
        if "caching" in self.results:
            cache_results = self.results["caching"]
            print("\nCACHING PERFORMANCE:")
            print("-" * 40)
            print(f"  Cache speedup factor:    {cache_results['speedup_factor']:.1f}x")
            print(f"  Cache hit time:          {cache_results['cache_hit']['avg_ms']:.3f}ms")
            print(f"  Cache miss time:         {cache_results['cache_miss']['avg_ms']:.3f}ms")

        # Concurrent performance
        if "concurrent" in self.results:
            print("\nCONCURRENCY PERFORMANCE:")
            print("-" * 40)
            for key, metrics in self.results["concurrent"].items():
                level = metrics["concurrency_level"]
                throughput = metrics["throughput_ops_per_sec"]
                print(f"  {level:3} concurrent ops:     {throughput:8.0f} ops/sec")

    def save_results(self, filename: str = "performance_results.json"):
        """Save results to JSON file."""
        # Use RESULTS_DIR environment variable if available, otherwise current directory
        import os
        results_dir = os.environ.get('RESULTS_DIR', '.')
        if results_dir != '.':
            os.makedirs(results_dir, exist_ok=True)
            filepath = os.path.join(results_dir, filename)
        else:
            filepath = filename
            
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Results saved to {filepath}")

    async def run_all_benchmarks(self):
        """Run all performance benchmarks."""
        await self.setup()

        await self.benchmark_arithmetic_operations()
        await self.benchmark_matrix_operations()
        await self.benchmark_statistics_operations()
        await self.benchmark_calculus_operations()
        await self.benchmark_caching_performance()
        await self.benchmark_concurrent_operations()

        self.generate_report()
        self.save_results()

        print("\n🎉 Performance benchmarking complete!")
        return self.results


async def main():
    """Main benchmark execution."""
    benchmark = PerformanceBenchmark()
    results = await benchmark.run_all_benchmarks()

    # Performance validation
    print("\n🔍 Performance Validation:")

    # Check if performance meets requirements
    validation_passed = True

    # Arithmetic operations should be fast
    if "arithmetic" in results:
        for op, metrics in results["arithmetic"].items():
            if metrics["avg_ms"] > 10:  # 10ms threshold
                print(f"  ⚠️  {op} is slow: {metrics['avg_ms']:.3f}ms")
                validation_passed = False
            else:
                print(f"  ✅ {op}: {metrics['avg_ms']:.3f}ms")

    # Caching should provide speedup
    if "caching" in results:
        speedup = results["caching"]["speedup_factor"]
        if speedup < 1.2:  # More realistic expectation for fast operations
            print(f"  ⚠️  Cache speedup is low: {speedup:.1f}x")
            validation_passed = False
        else:
            print(f"  ✅ Cache speedup: {speedup:.1f}x")

    if validation_passed:
        print("\n✅ All performance requirements met!")
        return 0
    else:
        print("\n⚠️  Some performance requirements not met")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
