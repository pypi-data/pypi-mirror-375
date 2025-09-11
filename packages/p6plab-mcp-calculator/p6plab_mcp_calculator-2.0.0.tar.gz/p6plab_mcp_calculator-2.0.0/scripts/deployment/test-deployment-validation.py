#!/usr/bin/env python3
"""
Deployment Validation Script
Consolidated deployment validation with common test utilities.
"""

import asyncio
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import common test utilities
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from test_utils import TestSuite


class DeploymentValidator(TestSuite):
    """Validates deployment readiness."""

    def __init__(self):
        super().__init__("Deployment Validation")
        self.temp_dirs = []

    def cleanup(self):
        """Clean up temporary directories."""
        for temp_dir in self.temp_dirs:
            if temp_dir.exists():
                subprocess.run(["rm", "-rf", str(temp_dir)], check=False)

    async def test_package_build(self):
        """Test package building."""
        print("📦 Testing Package Build...")

        try:
            # Build package
            result = subprocess.run([
                sys.executable, "-m", "build",
                "--wheel", "--sdist",
                "--outdir", "deployment-test-dist/"
            ], capture_output=True, text=True, check=True)

            # Check if files were created
            dist_dir = Path("deployment-test-dist")
            wheel_files = list(dist_dir.glob("*.whl"))
            sdist_files = list(dist_dir.glob("*.tar.gz"))

            assert len(wheel_files) > 0, "No wheel file created"
            assert len(sdist_files) > 0, "No source distribution created"

            self.record_success("package_build", f"Wheel: {wheel_files[0].name}, Source: {sdist_files[0].name}")

        except subprocess.CalledProcessError as e:
            self.record_failure("package_build", f"Build failed: {e.stderr}")
        except Exception as e:
            self.record_failure("package_build", str(e))

    async def test_fresh_installation(self):
        """Test installation in a fresh environment."""
        print("\n🆕 Testing Fresh Installation...")

        try:
            # Create temporary virtual environment
            temp_dir = Path(tempfile.mkdtemp(prefix="calc_deploy_test_"))
            self.temp_dirs.append(temp_dir)

            venv_dir = temp_dir / "test_venv"

            # Create virtual environment
            subprocess.run([
                sys.executable, "-m", "venv", str(venv_dir)
            ], check=True)

            # Get paths for the virtual environment
            if os.name == 'nt':  # Windows
                python_path = venv_dir / "Scripts" / "python.exe"
                pip_path = venv_dir / "Scripts" / "pip.exe"
            else:  # Unix-like
                python_path = venv_dir / "bin" / "python"
                pip_path = venv_dir / "bin" / "pip"

            # Install the package
            wheel_files = list(Path("deployment-test-dist").glob("*.whl"))
            if wheel_files:
                subprocess.run([
                    str(pip_path), "install", str(wheel_files[0])
                ], check=True)

                # Test import
                subprocess.run([
                    str(python_path), "-c",
                    "import calculator; print('Import successful')"
                ], capture_output=True, text=True, check=True)

                # Test basic functionality
                test_code = """
import asyncio
from calculator.server.app import create_calculator_app

async def test():
    app = create_calculator_app()
    result = await app.arithmetic_service.process('add', {'numbers': [1, 2, 3]})
    assert result == 6.0
    print('Basic functionality test passed')

asyncio.run(test())
"""

                subprocess.run([
                    str(python_path), "-c", test_code
                ], capture_output=True, text=True, check=True)

                self.record_success("fresh_installation", "Package installs and works correctly")

            else:
                raise Exception("No wheel file found for installation")

        except Exception as e:
            self.record_failure("fresh_installation", str(e))

    async def test_uvx_compatibility(self):
        """Test uvx compatibility."""
        print("\n🔧 Testing uvx Compatibility...")

        try:
            # Check if uvx is available
            try:
                subprocess.run(["uvx", "--version"],
                             capture_output=True, check=True)
                uvx_available = True
            except (subprocess.CalledProcessError, FileNotFoundError):
                uvx_available = False

            if not uvx_available:
                self.record_skip("uvx_compatibility", "uvx not available")
                return

            # Check pyproject.toml has correct entry points
            pyproject_path = Path("pyproject.toml")
            if pyproject_path.exists():
                with open(pyproject_path) as f:
                    content = f.read()
                    if "[project.scripts]" in content or "[tool.poetry.scripts]" in content:
                        self.record_success("uvx_compatibility", "Entry points configured for uvx")
                    else:
                        self.record_warning("uvx_compatibility", "No entry points found for uvx")
            else:
                self.record_failure("uvx_compatibility", "pyproject.toml not found")

        except Exception as e:
            self.record_failure("uvx_compatibility", str(e))

    async def test_dependency_resolution(self):
        """Test dependency resolution."""
        print("\n📚 Testing Dependency Resolution...")

        try:
            # Create temporary virtual environment
            temp_dir = Path(tempfile.mkdtemp(prefix="calc_deps_test_"))
            self.temp_dirs.append(temp_dir)

            venv_dir = temp_dir / "deps_venv"

            # Create virtual environment
            subprocess.run([
                sys.executable, "-m", "venv", str(venv_dir)
            ], check=True)

            # Get paths
            if os.name == 'nt':  # Windows
                pip_path = venv_dir / "Scripts" / "pip.exe"
            else:  # Unix-like
                pip_path = venv_dir / "bin" / "pip"

            # Install package and check dependencies
            wheel_files = list(Path("deployment-test-dist").glob("*.whl"))
            if wheel_files:
                # Actually install
                subprocess.run([
                    str(pip_path), "install", str(wheel_files[0])
                ], check=True)

                # Check installed packages
                result = subprocess.run([
                    str(pip_path), "list"
                ], capture_output=True, text=True, check=True)

                installed_packages = result.stdout
                required_packages = ["fastmcp", "numpy", "sympy", "pydantic"]

                missing_packages = []
                for package in required_packages:
                    if package.lower() not in installed_packages.lower():
                        missing_packages.append(package)

                if missing_packages:
                    self.record_warning("dependency_resolution", f"Missing packages: {missing_packages}")
                else:
                    self.record_success("dependency_resolution", "All required dependencies installed")

        except Exception as e:
            self.record_failure("dependency_resolution", str(e))

    async def test_cross_platform_compatibility(self):
        """Test cross-platform compatibility."""
        print("\n🌐 Testing Cross-Platform Compatibility...")

        try:
            # Test platform-specific imports
            import platform
            current_platform = platform.system()

            # Test imports that might be platform-specific
            platform_sensitive_imports = [
                "calculator.server.app",
                "calculator.core.config",
                "calculator.services.arithmetic",
                "calculator.repositories.cache"
            ]

            for module_name in platform_sensitive_imports:
                try:
                    __import__(module_name)
                except ImportError as e:
                    raise Exception(f"{module_name}: Import failed - {e}")

            # Test file path handling
            from calculator.server.app import create_calculator_app
            app = create_calculator_app()

            # This should work on all platforms
            assert app is not None

            self.record_success("cross_platform_compatibility", f"Works on {current_platform}")

        except Exception as e:
            self.record_failure("cross_platform_compatibility", str(e))

    async def test_production_configuration(self):
        """Test production configuration."""
        print("\n⚙️ Testing Production Configuration...")

        try:
            # Test with production-like environment variables
            prod_env = os.environ.copy()
            prod_env.update({
                "CALC_LOG_LEVEL": "WARNING",
                "CALC_MAX_COMPUTATION_TIME": "60",
                "CALC_CACHE_SIZE": "2000",
                "CALC_ENABLE_PERFORMANCE_MONITORING": "true"
            })

            # Test configuration loading
            test_code = """
import os
from calculator.services.config import ConfigService

config = ConfigService()
assert config.get_max_computation_time() == 60
assert config.get_cache_size() == 2000
assert config.is_performance_monitoring_enabled() == True
print('Production configuration test passed')
"""

            subprocess.run([
                sys.executable, "-c", test_code
            ], env=prod_env, capture_output=True, text=True, check=True)

            self.record_success("production_configuration", "Production configuration loads correctly")

        except Exception as e:
            self.record_failure("production_configuration", str(e))

    async def run_all_tests(self):
        """Run all deployment validation tests."""
        print("🚀 Deployment Validation Test Suite")
        print("=" * 50)

        try:
            await self.test_package_build()
            await self.test_fresh_installation()
            await self.test_uvx_compatibility()
            await self.test_dependency_resolution()
            await self.test_cross_platform_compatibility()
            await self.test_production_configuration()

            # Print summary and save results
            success = self.print_summary()
            self.save_results("deployment_validation_results.json")

            if success:
                print("\n🎉 Deployment validation successful! Ready for deployment.")
            else:
                print("\n❌ Some deployment tests failed. Fix issues before deployment.")

            return success

        finally:
            # Cleanup
            self.cleanup()
            # Clean up build artifacts
            subprocess.run(["rm", "-rf", "deployment-test-dist/"], check=False)


async def main():
    """Main entry point."""
    validator = DeploymentValidator()
    success = await validator.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
