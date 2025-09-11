#!/usr/bin/env python3
"""
Comprehensive validation script for the calculator refactoring.
Consolidated validation combining refactoring, MCP integration, and deployment checks.
"""

import asyncio
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict

# Add the calculator module to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import common test utilities
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from test_utils import TestSuite, create_test_app, run_comprehensive_validation


class RefactoringValidator(TestSuite):
    """Comprehensive refactoring validator."""

    def __init__(self):
        super().__init__("Calculator Refactoring")
        self.app = None

    async def run_validation(self) -> Dict[str, Any]:
        """Run complete validation suite."""
        print("🔍 Starting Calculator Refactoring Validation")
        print("=" * 60)

        try:
            # Run comprehensive validation from test_utils
            success = await run_comprehensive_validation("Calculator Refactoring")

            if success:
                self.record_success("comprehensive_validation", "All core tests passed")
            else:
                self.record_failure("comprehensive_validation", "Some core tests failed")

            # Additional refactoring-specific tests
            await self._validate_architecture()
            await self._validate_performance()
            await self._validate_security()
            await self._validate_backward_compatibility()
            self._validate_documentation()

        except Exception as e:
            self.record_failure("critical_validation_error", str(e))
            traceback.print_exc()

        finally:
            if self.app and hasattr(self.app, 'shutdown'):
                await self.app.shutdown()

        return self.get_summary()

    async def _validate_architecture(self):
        """Validate architectural requirements."""
        print("\n🏗️ Validating Architecture...")

        try:
            # Initialize app if not already done
            if not self.app:
                self.app = await create_test_app()

            # Validate modular structure
            modules = [
                'calculator.server',
                'calculator.services',
                'calculator.repositories',
                'calculator.strategies',
                'calculator.core'
            ]

            for module_name in modules:
                try:
                    __import__(module_name)
                    self.record_success(f"module_{module_name}", "Module importable")
                except ImportError as e:
                    self.record_failure(f"module_{module_name}", f"Import failed: {e}")

            # Check file sizes (should be under 800 lines each)
            self._check_file_sizes()

            # Validate service layer
            services = [
                self.app.arithmetic_service,
                self.app.matrix_service,
                self.app.statistics_service,
                self.app.calculus_service
            ]

            for service in services:
                if hasattr(service, 'process') and callable(service.process):
                    self.record_success(f"service_interface_{type(service).__name__}", "Has process method")
                else:
                    self.record_failure(f"service_interface_{type(service).__name__}", "Missing process method")

            # Validate configuration system
            config = self.app.config
            config_methods = [
                'get_precision',
                'get_cache_size',
                'get_max_computation_time',
                'is_caching_enabled',
                'is_performance_monitoring_enabled'
            ]

            for method_name in config_methods:
                if hasattr(config, method_name) and callable(getattr(config, method_name)):
                    try:
                        result = getattr(config, method_name)()
                        self.record_success(f"config_{method_name}", f"Returns: {type(result).__name__}")
                    except Exception as e:
                        self.record_failure(f"config_{method_name}", str(e))
                else:
                    self.record_failure(f"config_{method_name}", "Method not available")

        except Exception as e:
            self.record_failure("architecture_validation", str(e))

    def _check_file_sizes(self):
        """Check that files are under the 800-line limit."""
        try:
            project_root = Path(__file__).parent.parent.parent
            python_files = list(project_root.rglob("*.py"))

            large_files = []
            for file_path in python_files:
                if file_path.name.startswith('.') or 'venv' in str(file_path) or '__pycache__' in str(file_path):
                    continue

                try:
                    with open(file_path, encoding='utf-8') as f:
                        line_count = sum(1 for _ in f)

                    if line_count > 800:
                        large_files.append((str(file_path.relative_to(project_root)), line_count))
                except Exception:
                    continue

            if large_files:
                self.record_warning("file_size_compliance", f"Large files found: {large_files}")
            else:
                self.record_success("file_size_compliance", "All files under 800 lines")

        except Exception as e:
            self.record_failure("file_size_check", str(e))

    async def _validate_performance(self):
        """Validate performance requirements."""
        print("\n⚡ Validating Performance...")

        try:
            if not self.app:
                self.app = await create_test_app()

            # Test response times
            operations = [
                (self.app.arithmetic_service, 'add', {'numbers': list(range(1000))}, 1.0),
                (self.app.matrix_service, 'determinant', {'matrix': [[1, 2], [3, 4]]}, 0.1),
                (self.app.statistics_service, 'mean', {'data': list(range(10000))}, 1.0)
            ]

            for service, operation, params, max_time in operations:
                start_time = time.time()
                await service.process(operation, params)
                execution_time = time.time() - start_time

                if execution_time <= max_time:
                    self.record_success(f"performance_{operation}", f"Completed in {execution_time:.3f}s")
                else:
                    self.record_warning(f"performance_{operation}", f"Slow execution: {execution_time:.3f}s")

            # Test caching performance
            service = self.app.arithmetic_service

            # First call (should cache)
            start_time = time.time()
            result1 = await service.process('factorial', {'number': 50})
            first_time = time.time() - start_time

            # Second call (should use cache)
            start_time = time.time()
            result2 = await service.process('factorial', {'number': 50})
            second_time = time.time() - start_time

            if result1 == result2:
                self.record_success("caching_consistency", "Results match")

                if second_time <= first_time:
                    self.record_success("caching_performance", f"Cache hit faster: {second_time:.3f}s vs {first_time:.3f}s")
                else:
                    self.record_warning("caching_performance", f"Cache not faster: {second_time:.3f}s vs {first_time:.3f}s")
            else:
                self.record_failure("caching_consistency", "Results don't match")

        except Exception as e:
            self.record_failure("performance_validation", str(e))

    async def _validate_security(self):
        """Validate security requirements."""
        print("\n🔒 Validating Security...")

        try:
            if not self.app:
                self.app = await create_test_app()

            from calculator.core.errors.exceptions import ComputationError, ValidationError

            service = self.app.arithmetic_service

            # Test validation error
            try:
                await service.process('add', {})  # Missing numbers parameter
                self.record_failure("security_validation_error", "No error raised for invalid input")
            except ValidationError:
                self.record_success("security_validation_error", "Validation error raised correctly")
            except Exception as e:
                self.record_warning("security_validation_error", f"Unexpected error type: {type(e).__name__}")

            # Test computation error
            try:
                await service.process('divide', {'a': 1, 'b': 0})  # Division by zero
                self.record_failure("security_computation_error", "No error raised for division by zero")
            except ComputationError:
                self.record_success("security_computation_error", "Computation error raised correctly")
            except Exception as e:
                self.record_warning("security_computation_error", f"Unexpected error type: {type(e).__name__}")

            # Test input validation
            try:
                await service.process('add', {'numbers': []})
                self.record_failure("security_empty_input", "No error for empty input")
            except ValidationError:
                self.record_success("security_empty_input", "Empty input rejected")
            except Exception as e:
                self.record_warning("security_empty_input", f"Unexpected error: {type(e).__name__}")

        except Exception as e:
            self.record_failure("security_validation", str(e))

    async def _validate_backward_compatibility(self):
        """Validate backward compatibility."""
        print("\n🔄 Validating Backward Compatibility...")

        try:
            # Test legacy imports
            legacy_modules = [
                'calculator.core.basic',
                'calculator.core.matrix',
                'calculator.core.statistics',
                'calculator.core.calculus'
            ]

            for module_name in legacy_modules:
                try:
                    __import__(module_name, fromlist=[''])
                    self.record_success(f"legacy_import_{module_name}", "Legacy import works")
                except ImportError as e:
                    self.record_failure(f"legacy_import_{module_name}", f"Import failed: {e}")

            # Test legacy server interface
            try:
                from calculator.server.compatibility import LegacyServerInterface

                if not self.app:
                    self.app = await create_test_app()

                legacy_server = LegacyServerInterface(self.app.config)

                # Test legacy calculation method
                result = await legacy_server.calculate('add', numbers=[1, 2, 3])
                if result == 6.0:
                    self.record_success("legacy_interface", "Legacy calculation works")
                else:
                    self.record_failure("legacy_interface", f"Expected 6.0, got {result}")

                # Test legacy health status
                health = legacy_server.get_health_status()
                if health.get('status') == 'healthy':
                    self.record_success("legacy_health", "Legacy health check works")
                else:
                    self.record_failure("legacy_health", f"Unexpected health status: {health}")

            except Exception as e:
                self.record_failure("legacy_server_interface", str(e))

        except Exception as e:
            self.record_failure("backward_compatibility_validation", str(e))

    def _validate_documentation(self):
        """Validate documentation completeness."""
        print("\n📚 Validating Documentation...")

        project_root = Path(__file__).parent.parent.parent

        # Check for required documentation files
        required_docs = [
            'docs/ARCHITECTURE.md',
            'docs/DEVELOPER_GUIDE.md',
            'docs/TROUBLESHOOTING.md',
            'docs/API_REFERENCE.md',
            'docs/MIGRATION.md',
            'README.md'
        ]

        for doc_path in required_docs:
            full_path = project_root / doc_path
            if full_path.exists():
                # Check file size (should have content)
                size = full_path.stat().st_size
                if size > 1000:  # At least 1KB of content
                    self.record_success(f"doc_{doc_path}", f"Exists ({size} bytes)")
                else:
                    self.record_warning(f"doc_{doc_path}", f"Too small ({size} bytes)")
            else:
                self.record_failure(f"doc_{doc_path}", "File missing")


async def main():
    """Main validation execution."""
    validator = RefactoringValidator()
    results = await validator.run_validation()

    # Save results
    validator.save_results("refactoring_validation_results.json")

    # Print final summary
    success = validator.print_summary()

    if success:
        print("\n🎉 REFACTORING VALIDATION COMPLETE!")
        print("The calculator refactoring is fully validated and ready for production!")
    else:
        print("\n❌ REFACTORING VALIDATION FAILED!")
        print("Please review the issues and fix them before proceeding.")

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
