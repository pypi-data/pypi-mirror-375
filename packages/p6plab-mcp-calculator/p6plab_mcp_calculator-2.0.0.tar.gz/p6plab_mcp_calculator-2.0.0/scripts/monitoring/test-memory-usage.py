#!/usr/bin/env python3
"""
Memory usage testing script for the refactored calculator.
Tests memory consumption and leak detection.
"""

import asyncio
import gc
import os
import sys
import time
from typing import Dict

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import psutil
except ImportError:
    print("❌ psutil not installed. Install with: pip install psutil")
    sys.exit(1)

from calculator.server.app import create_calculator_app


class MemoryTester:
    """Memory usage testing suite."""

    def __init__(self):
        self.app = None
        self.process = psutil.Process()
        self.baseline_memory = 0
        self.memory_snapshots = []

    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage in MB."""
        memory_info = self.process.memory_info()
        return {
            "rss_mb": memory_info.rss / 1024 / 1024,  # Resident Set Size
            "vms_mb": memory_info.vms / 1024 / 1024,  # Virtual Memory Size
        }

    def take_memory_snapshot(self, label: str):
        """Take a memory snapshot with a label."""
        memory = self.get_memory_usage()
        memory["label"] = label
        memory["timestamp"] = time.time()
        self.memory_snapshots.append(memory)
        print(f"📊 {label}: {memory['rss_mb']:.1f}MB RSS, {memory['vms_mb']:.1f}MB VMS")

    async def setup(self):
        """Initialize the calculator app."""
        print("🚀 Initializing Calculator App for Memory Testing...")

        # Take baseline measurement
        self.take_memory_snapshot("Baseline (before app creation)")

        # Create app
        self.app = create_calculator_app()
        self.take_memory_snapshot("After app creation")

        # Set baseline
        self.baseline_memory = self.memory_snapshots[-1]["rss_mb"]
        print(f"✅ Baseline memory usage: {self.baseline_memory:.1f}MB")

    async def test_arithmetic_memory_usage(self):
        """Test memory usage during arithmetic operations."""
        print("\n🧮 Testing Arithmetic Operations Memory Usage...")

        # Perform many arithmetic operations
        for i in range(1000):
            await self.app.arithmetic_service.process("add", {"numbers": list(range(100))})
            await self.app.arithmetic_service.process("multiply", {"numbers": [2, 3, 4, 5]})
            await self.app.arithmetic_service.process("factorial", {"number": 20})

            if i % 200 == 0:
                self.take_memory_snapshot(f"After {i+1} arithmetic operations")

        # Force garbage collection
        gc.collect()
        self.take_memory_snapshot("After arithmetic operations + GC")

    async def test_matrix_memory_usage(self):
        """Test memory usage during matrix operations."""
        print("\n📊 Testing Matrix Operations Memory Usage...")

        # Test with increasingly large matrices
        sizes = [10, 20, 50, 100]

        for size in sizes:
            # Create large matrices
            matrix_a = [[1.0] * size for _ in range(size)]
            matrix_b = [[2.0] * size for _ in range(size)]

            # Perform operations
            for _ in range(10):
                await self.app.matrix_service.process("add", {"matrix_a": matrix_a, "matrix_b": matrix_b})
                await self.app.matrix_service.process("multiply", {"matrix_a": matrix_a, "matrix_b": matrix_b})
                await self.app.matrix_service.process("determinant", {"matrix": matrix_a})

            self.take_memory_snapshot(f"After {size}x{size} matrix operations")

            # Clean up references
            del matrix_a, matrix_b
            gc.collect()

        self.take_memory_snapshot("After matrix operations + GC")

    async def test_statistics_memory_usage(self):
        """Test memory usage during statistics operations."""
        print("\n📈 Testing Statistics Operations Memory Usage...")

        # Test with increasingly large datasets
        data_sizes = [1000, 10000, 100000]

        for size in data_sizes:
            # Create large dataset
            data = list(range(size))

            # Perform operations
            await self.app.statistics_service.process("mean", {"data": data})
            await self.app.statistics_service.process("median", {"data": data})
            await self.app.statistics_service.process("std_dev", {"data": data})
            await self.app.statistics_service.process("descriptive_stats", {"data": data})

            self.take_memory_snapshot(f"After {size} item statistics operations")

            # Clean up
            del data
            gc.collect()

        self.take_memory_snapshot("After statistics operations + GC")

    async def test_caching_memory_usage(self):
        """Test memory usage of caching system."""
        print("\n⚡ Testing Caching Memory Usage...")

        # Fill cache with many operations
        for i in range(1000):
            # Use different parameters to avoid cache hits
            await self.app.arithmetic_service.process("factorial", {"number": i % 100 + 1})
            await self.app.arithmetic_service.process("power", {"base": i % 10 + 1, "exponent": i % 5 + 1})

            if i % 200 == 0:
                self.take_memory_snapshot(f"After {i+1} cached operations")

        # Check cache statistics
        if hasattr(self.app.cache_repo, 'get_cache_stats'):
            cache_stats = await self.app.cache_repo.get_cache_stats()
            print(f"📊 Cache stats: {cache_stats}")

        self.take_memory_snapshot("After cache filling")

    async def test_concurrent_memory_usage(self):
        """Test memory usage during concurrent operations."""
        print("\n🔄 Testing Concurrent Operations Memory Usage...")

        async def concurrent_operation(op_id: int):
            # Mix of different operations
            await self.app.arithmetic_service.process("add", {"numbers": [op_id, op_id + 1, op_id + 2]})
            await self.app.matrix_service.process("determinant", {"matrix": [[1, 2], [3, 4]]})
            await self.app.statistics_service.process("mean", {"data": [1, 2, 3, 4, 5]})

        # Test different concurrency levels
        concurrency_levels = [10, 50, 100]

        for level in concurrency_levels:
            tasks = [concurrent_operation(i) for i in range(level)]
            await asyncio.gather(*tasks)

            self.take_memory_snapshot(f"After {level} concurrent operations")
            gc.collect()

        self.take_memory_snapshot("After concurrent operations + GC")

    async def test_memory_leak_detection(self):
        """Test for memory leaks by repeating operations."""
        print("\n🔍 Testing for Memory Leaks...")

        # Baseline measurement
        initial_memory = self.get_memory_usage()["rss_mb"]

        # Repeat the same operations many times
        for cycle in range(5):
            print(f"  Running cycle {cycle + 1}/5...")

            # Arithmetic operations
            for _ in range(100):
                await self.app.arithmetic_service.process("add", {"numbers": [1, 2, 3, 4, 5]})
                await self.app.arithmetic_service.process("factorial", {"number": 10})

            # Matrix operations
            matrix = [[1, 2], [3, 4]]
            for _ in range(50):
                await self.app.matrix_service.process("determinant", {"matrix": matrix})
                await self.app.matrix_service.process("transpose", {"matrix": matrix})

            # Statistics operations
            data = list(range(100))
            for _ in range(50):
                await self.app.statistics_service.process("mean", {"data": data})
                await self.app.statistics_service.process("std_dev", {"data": data})

            # Force garbage collection
            gc.collect()

            current_memory = self.get_memory_usage()["rss_mb"]
            memory_increase = current_memory - initial_memory

            self.take_memory_snapshot(f"Leak test cycle {cycle + 1}")

            print(f"    Memory increase: {memory_increase:+.1f}MB")

            # Check for significant memory increase (potential leak)
            if memory_increase > 50:  # 50MB threshold
                print(f"    ⚠️  Potential memory leak detected: {memory_increase:.1f}MB increase")
            else:
                print(f"    ✅ Memory usage stable: {memory_increase:+.1f}MB")

    def analyze_memory_usage(self):
        """Analyze memory usage patterns."""
        print("\n" + "="*60)
        print("📊 MEMORY USAGE ANALYSIS")
        print("="*60)

        if len(self.memory_snapshots) < 2:
            print("❌ Insufficient memory snapshots for analysis")
            return

        baseline = self.memory_snapshots[0]["rss_mb"]
        peak_memory = max(snapshot["rss_mb"] for snapshot in self.memory_snapshots)
        final_memory = self.memory_snapshots[-1]["rss_mb"]

        print(f"Baseline memory:     {baseline:.1f}MB")
        print(f"Peak memory:         {peak_memory:.1f}MB")
        print(f"Final memory:        {final_memory:.1f}MB")
        print(f"Peak increase:       {peak_memory - baseline:+.1f}MB")
        print(f"Final increase:      {final_memory - baseline:+.1f}MB")

        # Memory efficiency analysis
        memory_efficiency = (peak_memory - baseline) / baseline * 100
        print(f"Memory efficiency:   {memory_efficiency:.1f}% increase from baseline")

        # Check for memory leaks
        memory_leak_indicator = final_memory - baseline
        if memory_leak_indicator > 20:  # 20MB threshold
            print(f"⚠️  Potential memory leak: {memory_leak_indicator:.1f}MB not released")
        else:
            print(f"✅ Memory management good: {memory_leak_indicator:+.1f}MB final increase")

        # Show memory timeline
        print("\nMemory Timeline:")
        print("-" * 40)
        for snapshot in self.memory_snapshots:
            increase = snapshot["rss_mb"] - baseline
            print(f"  {snapshot['label']:<35}: {snapshot['rss_mb']:6.1f}MB ({increase:+5.1f}MB)")

    def generate_memory_report(self):
        """Generate detailed memory report."""
        print("\nDETAILED MEMORY REPORT:")
        print("-" * 40)

        # System memory info
        system_memory = psutil.virtual_memory()
        print(f"System total memory: {system_memory.total / 1024 / 1024 / 1024:.1f}GB")
        print(f"System available:    {system_memory.available / 1024 / 1024 / 1024:.1f}GB")
        print(f"System usage:        {system_memory.percent:.1f}%")

        # Process memory details
        memory_info = self.process.memory_info()
        memory_percent = self.process.memory_percent()

        print("\nProcess memory details:")
        print(f"  RSS (Resident):    {memory_info.rss / 1024 / 1024:.1f}MB")
        print(f"  VMS (Virtual):     {memory_info.vms / 1024 / 1024:.1f}MB")
        print(f"  Memory percent:    {memory_percent:.2f}% of system")

        # Memory recommendations
        print("\nRecommendations:")
        if memory_percent > 5:
            print("  ⚠️  High memory usage - consider optimization")
        else:
            print("  ✅ Memory usage is reasonable")

        final_memory = self.memory_snapshots[-1]["rss_mb"] if self.memory_snapshots else 0
        if final_memory > 200:
            print("  ⚠️  Consider implementing memory limits")
        else:
            print("  ✅ Memory usage within acceptable limits")

    async def run_all_tests(self):
        """Run all memory tests."""
        await self.setup()

        await self.test_arithmetic_memory_usage()
        await self.test_matrix_memory_usage()
        await self.test_statistics_memory_usage()
        await self.test_caching_memory_usage()
        await self.test_concurrent_memory_usage()
        await self.test_memory_leak_detection()

        self.analyze_memory_usage()
        self.generate_memory_report()

        print("\n🎉 Memory testing complete!")

        # Return success/failure based on memory usage
        final_memory = self.memory_snapshots[-1]["rss_mb"]
        baseline_memory = self.memory_snapshots[0]["rss_mb"]
        memory_increase = final_memory - baseline_memory

        if memory_increase > 100:  # 100MB threshold
            print(f"❌ Memory usage too high: {memory_increase:.1f}MB increase")
            return False
        else:
            print(f"✅ Memory usage acceptable: {memory_increase:+.1f}MB increase")
            return True


async def main():
    """Main memory testing execution."""
    print("🧠 Calculator Memory Usage Testing")
    print("=" * 50)

    tester = MemoryTester()
    success = await tester.run_all_tests()

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
