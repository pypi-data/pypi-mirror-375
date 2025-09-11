# Scripts and Tools Reference

This document provides a comprehensive guide to all scripts and tools available in the Scientific Calculator MCP Server project.

## Related Documentation

- **[Developer Guide](DEVELOPER_GUIDE.md)** - Development setup and contribution guide
- **[CI/CD Guide](CI_CD.md)** - CI/CD integration and automation
- **[Release Guide](RELEASE.md)** - Release process and deployment
- **[Security Guide](security.md)** - Security scanning and best practices
- **[Troubleshooting Guide](troubleshooting.md)** - Common issues and solutions

## Overview

The project uses a well-organized script structure to reduce duplication and improve maintainability. Scripts are organized by purpose and workflow phase.

## Script Organization

```
scripts/
├── lib/                    # 📚 Shared Utilities
│   ├── common.sh          # Shell functions and utilities
│   └── test_utils.py      # Python test framework
├── dev/                   # 🛠️ Development Scripts  
│   ├── run-tests.sh       # Quick development test suite
│   └── validate-refactoring.py  # Comprehensive validation
├── ci/                    # 🔄 CI/CD Scripts
│   ├── run-all-tests.sh   # Complete test suite (12 phases)
│   ├── security-scan.sh   # Security scanning with bandit
│   └── test-production-readiness.sh  # Production validation
├── deployment/            # 🚀 Deployment Scripts
│   ├── build-package.sh   # uvx-compatible package building
│   ├── deploy-pipeline.sh # Complete deployment pipeline
│   ├── test-uvx-package.sh # Local package testing
│   ├── test-uvx-install.sh # uvx installation testing
│   ├── validate-release.sh # Release validation
│   ├── test-deployment-validation.py  # Deployment validation
│   ├── publish-test-pypi.sh  # Test PyPI publishing
│   └── publish-pypi.sh    # Production PyPI publishing
├── monitoring/            # 📊 Performance Monitoring
│   ├── benchmark-performance.py  # Performance benchmarking
│   └── test-memory-usage.py      # Memory usage testing
├── clean.sh              # 🧹 Cross-cutting cleanup utility
└── update-version.sh     # 📝 Version management utility
```

## Shared Utilities

### `scripts/lib/common.sh`

**Purpose**: Provides shared shell functions used across multiple scripts.

**Key Functions**:
- `check_virtual_env()` - Ensures virtual environment is active
- `install_*_dependencies()` - Installs different dependency sets
- `run_security_scan()` - Executes security scanning
- `run_linting()` - Performs code linting with ruff
- `run_formatting_check()` - Checks code formatting
- `test_basic_functionality()` - Tests core application functionality
- `cleanup_artifacts()` - Cleans build and test artifacts
- Logging functions: `log_info()`, `log_success()`, `log_warning()`, `log_error()`

**Usage**:
```bash
# Source the utilities in your script
source "$(dirname "$0")/../lib/common.sh"

# Use the functions
check_virtual_env
run_linting
log_success "Operation completed"
```

### `scripts/lib/test_utils.py`

**Purpose**: Provides Python test framework and utilities for validation scripts.

**Key Classes**:
- `TestSuite` - Base class for organizing test results
- `TestResult` - Represents individual test outcomes

**Key Functions**:
- `create_test_app()` - Creates calculator app for testing
- `test_basic_operations()` - Tests arithmetic operations
- `test_matrix_operations()` - Tests matrix functionality
- `test_statistics_operations()` - Tests statistical functions
- `measure_performance()` - Performance measurement utilities
- `run_comprehensive_validation()` - Complete validation suite

**Usage**:
```python
from test_utils import TestSuite, run_comprehensive_validation

# Create a test suite
suite = TestSuite("My Tests")

# Run comprehensive validation
success = await run_comprehensive_validation("My App")
```

## Development Scripts

### `scripts/dev/run-tests.sh`

**Purpose**: Quick development test suite for fast feedback during development.

**What it does**:
1. Checks virtual environment
2. Installs test dependencies
3. Runs code quality checks (linting, formatting, type checking)
4. Executes security scan
5. Runs unit tests with coverage
6. Tests basic functionality
7. Tests package building
8. Tests entry point

**Usage**:
```bash
./scripts/dev/run-tests.sh
```

**When to use**: During active development for quick validation of changes.

### `scripts/dev/validate-refactoring.py`

**Purpose**: Comprehensive validation combining refactoring, MCP integration, and deployment checks.

**What it does**:
1. Runs comprehensive validation from test_utils
2. Validates architectural requirements
3. Tests performance requirements
4. Validates security measures
5. Tests backward compatibility
6. Validates documentation completeness

**Usage**:
```bash
./scripts/dev/validate-refactoring.py
```

**When to use**: Before major commits or when validating large changes.

## CI/CD Scripts

### `scripts/ci/run-all-tests.sh`

**Purpose**: Complete test suite for CI/CD pipelines with comprehensive coverage.

**Test Phases** (12 phases):
1. **Code Quality**: Linting, formatting, type checking
2. **Security**: Security scanning with bandit
3. **Unit Tests**: Unit tests with coverage reporting
4. **Integration Tests**: Integration and system tests
5. **End-to-End Tests**: E2E and MCP server tests
6. **Performance Tests**: Benchmarks, memory usage, load testing
7. **Compatibility Tests**: Backward compatibility, regression tests
8. **Smoke Tests**: Basic functionality verification
9. **Validation Tests**: Refactoring and production readiness
10. **Deployment Tests**: Package building and validation
11. **Final Validation**: Complete refactoring test

**Usage**:
```bash
./scripts/ci/run-all-tests.sh
```

**Output**: Detailed test results saved to `test-results/` directory with timestamps.

**When to use**: In CI/CD pipelines for comprehensive validation.

### `scripts/ci/security-scan.sh`

**Purpose**: Dedicated security scanning with bandit.

**What it does**:
1. Installs bandit if not available
2. Runs security scan with JSON output for CI/CD
3. Runs console output for developer feedback
4. Parses results and blocks on High/Medium severity issues
5. Generates detailed security reports

**Usage**:
```bash
./scripts/ci/security-scan.sh
```

**Output**: 
- Console output for immediate feedback
- `reports/security-report.json` for detailed analysis

**When to use**: 
- As part of CI/CD security gates
- Before package building
- Regular security audits

### `scripts/ci/test-production-readiness.sh`

**Purpose**: Validates production deployment readiness.

**What it does**:
1. Validates version and metadata
2. Tests core functionality
3. Runs security validation
4. Executes performance benchmarks
5. Tests memory usage
6. Validates backward compatibility
7. Tests package building and installation
8. Runs end-to-end integration tests
9. Executes comprehensive test suite
10. Performs final refactoring validation

**Usage**:
```bash
./scripts/ci/test-production-readiness.sh
```

**When to use**: Before production deployments to ensure readiness.

## Deployment Scripts

### `scripts/deployment/build-package.sh`

**Purpose**: Builds uvx-compatible package for distribution.

**What it does**:
1. Checks virtual environment
2. Installs build dependencies
3. Runs security scan before building
4. Cleans previous builds
5. Builds wheel and source distribution
6. Validates uvx compatibility
7. Checks dependencies and entry points

**Usage**:
```bash
./scripts/deployment/build-package.sh
```

**Output**: Package files in `dist/` directory.

### `scripts/deployment/deploy-pipeline.sh`

**Purpose**: Complete deployment pipeline for test or production.

**Parameters**:
- `test` - Deploy to Test PyPI
- `production` - Deploy to production PyPI

**What it does**:
1. Pre-deployment validation (comprehensive tests)
2. Cleans and builds package
3. Tests package locally
4. Publishes to specified repository
5. Tests installation from repository
6. Provides deployment summary and next steps

**Usage**:
```bash
# Deploy to Test PyPI
./scripts/deployment/deploy-pipeline.sh test

# Deploy to production PyPI
./scripts/deployment/deploy-pipeline.sh production
```

### `scripts/deployment/test-uvx-package.sh`

**Purpose**: Tests uvx package locally before publishing.

**What it does**:
1. Installs package in editable mode
2. Tests entry point availability
3. Tests help command execution
4. Tests uvx execution (if uvx available)
5. Tests Python imports and basic functionality

**Usage**:
```bash
./scripts/deployment/test-uvx-package.sh
```

### `scripts/deployment/test-uvx-install.sh`

**Purpose**: Tests uvx installation from PyPI repositories.

**Parameters**:
- `pypi` (default) - Test installation from production PyPI
- `testpypi` - Test installation from Test PyPI

**What it does**:
1. Checks uvx availability
2. Tests installation from specified repository
3. Verifies package can be executed
4. Tests basic functionality

**Usage**:
```bash
# Test from production PyPI
./scripts/deployment/test-uvx-install.sh pypi

# Test from Test PyPI
./scripts/deployment/test-uvx-install.sh testpypi
```

### `scripts/deployment/validate-release.sh`

**Purpose**: Validates release readiness before publishing.

**What it does**:
1. Checks current version
2. Validates required files exist
3. Tests server import
4. Tests basic functionality
5. Tests package building
6. Validates entry points configuration

**Usage**:
```bash
./scripts/deployment/validate-release.sh
```

### `scripts/deployment/test-deployment-validation.py`

**Purpose**: Comprehensive deployment validation in clean environments.

**What it does**:
1. Tests package building
2. Tests fresh installation in temporary virtual environment
3. Tests uvx compatibility
4. Tests dependency resolution
5. Tests cross-platform compatibility
6. Tests production configuration

**Usage**:
```bash
./scripts/deployment/test-deployment-validation.py
```

### `scripts/deployment/publish-test-pypi.sh`

**Purpose**: Publishes package to Test PyPI for testing.

**What it does**:
1. Checks virtual environment and dependencies
2. Validates package files exist
3. Checks/prompts for credentials
4. Uploads to Test PyPI
5. Tests installation from Test PyPI

**Usage**:
```bash
./scripts/deployment/publish-test-pypi.sh
```

**Prerequisites**: 
- Package built with `build-package.sh`
- Test PyPI credentials configured

### `scripts/deployment/publish-pypi.sh`

**Purpose**: Publishes package to production PyPI.

**What it does**:
1. Multiple confirmation prompts for safety
2. Checks virtual environment and dependencies
3. Validates package files exist
4. Checks/prompts for credentials
5. Uploads to production PyPI
6. Tests installation from PyPI

**Usage**:
```bash
./scripts/deployment/publish-pypi.sh
```

**Prerequisites**: 
- Package tested on Test PyPI
- Production PyPI credentials configured
- Manual confirmation required

## Monitoring Scripts

### `scripts/monitoring/benchmark-performance.py`

**Purpose**: Comprehensive performance benchmarking and analysis.

**What it benchmarks**:
1. **Arithmetic Operations**: Basic math functions with timing
2. **Matrix Operations**: Different matrix sizes and operations
3. **Statistics Operations**: Various data sizes and statistical functions
4. **Calculus Operations**: Symbolic and numerical calculus
5. **Caching Performance**: Cache hit vs miss performance
6. **Concurrent Operations**: Multi-threaded performance testing

**Usage**:
```bash
./scripts/monitoring/benchmark-performance.py
```

**Output**: 
- Console performance report
- `performance_results.json` with detailed metrics (saved to test-results directory when run via CI)
- Performance validation against requirements

### `scripts/monitoring/test-memory-usage.py`

**Purpose**: Memory usage analysis and leak detection.

**What it tests**:
1. **Application Initialization**: Memory usage during startup
2. **Operation Memory Usage**: Memory consumption during calculations
3. **Caching Memory Impact**: Memory usage of caching system
4. **Concurrent Memory Usage**: Memory usage under concurrent load
5. **Memory Leak Detection**: Repeated operations to detect leaks
6. **Resource Management**: Memory cleanup and garbage collection

**Usage**:
```bash
./scripts/monitoring/test-memory-usage.py
```

**Output**:
- Memory usage timeline and analysis
- Memory leak detection results
- Resource management recommendations

## Cross-Cutting Utilities

### `scripts/clean.sh`

**Purpose**: Cleans build artifacts, caches, and temporary files.

**What it cleans**:
1. **Python Artifacts**: `__pycache__`, `*.pyc`, `build/`, `dist/`, `*.egg-info/`
2. **Test Artifacts**: `.pytest_cache/`, `htmlcov/`, `.coverage`
3. **Documentation**: `docs/_build/`
4. **uvx Cache**: uvx/uv cache directories
5. **Temporary Files**: `*.tmp`, `*.temp`, `.DS_Store`
6. **IDE Files**: `.vscode/`, `.idea/`

**Usage**:
```bash
./scripts/clean.sh
```

**When to use**: 
- Before building packages
- When troubleshooting build issues
- Regular maintenance

### `scripts/update-version.sh`

**Purpose**: Updates version numbers and creates git tags.

**Parameters**:
- `patch` (default) - Increment patch version (1.0.0 → 1.0.1)
- `minor` - Increment minor version (1.0.0 → 1.1.0)
- `major` - Increment major version (1.0.0 → 2.0.0)

**What it does**:
1. Parses current version from `calculator/__init__.py`
2. Calculates new version based on type
3. Prompts for confirmation
4. Updates version in source code
5. Optionally creates git tag and commit

**Usage**:
```bash
# Patch version update
./scripts/update-version.sh patch

# Minor version update
./scripts/update-version.sh minor

# Major version update
./scripts/update-version.sh major
```

## Script Dependencies and Relationships

### Dependency Graph

```
Development Workflow:
run-tests.sh → common.sh, security-scan.sh
validate-refactoring.py → test_utils.py

CI/CD Workflow:
run-all-tests.sh → common.sh, security-scan.sh, test-production-readiness.sh
test-production-readiness.sh → common.sh, security-scan.sh, benchmark-performance.py, test-memory-usage.py

Deployment Workflow:
deploy-pipeline.sh → build-package.sh, test-uvx-package.sh, publish-*.sh, test-uvx-install.sh
build-package.sh → common.sh, security-scan.sh
publish-*.sh → common.sh
```

### Script Execution Order

**Development**:
1. `clean.sh` (optional)
2. `dev/run-tests.sh` (quick validation)
3. `dev/validate-refactoring.py` (comprehensive validation)

**CI/CD**:
1. `ci/run-all-tests.sh` (comprehensive testing)
2. `ci/test-production-readiness.sh` (production validation)

**Release**:
1. `update-version.sh` (version management)
2. `deployment/validate-release.sh` (release validation)
3. `deployment/deploy-pipeline.sh test` (test deployment)
4. `deployment/deploy-pipeline.sh production` (production deployment)

## Best Practices

### Script Usage Guidelines

1. **Development**: Use `dev/` scripts for quick feedback during development
2. **CI/CD**: Use `ci/` scripts for comprehensive validation in pipelines
3. **Deployment**: Use `deployment/` scripts for package management and publishing
4. **Monitoring**: Use `monitoring/` scripts for performance analysis
5. **Maintenance**: Use root-level utilities for cleanup and version management

### Error Handling

All scripts implement consistent error handling:
- Exit codes: 0 for success, 1 for failure
- Colored output for better visibility
- Detailed error messages with troubleshooting tips
- Cleanup on failure where appropriate

### Logging and Output

Scripts use consistent logging patterns:
- `✅` for success messages
- `❌` for error messages  
- `⚠️` for warnings
- `ℹ️` for informational messages
- `📋` for step indicators

### Performance Considerations

- Scripts use shared utilities to reduce duplication
- Parallel execution where possible (e.g., in `run-all-tests.sh`)
- Efficient cleanup and artifact management
- Caching of expensive operations

## Troubleshooting

### Common Issues

1. **Permission Denied**: Run `chmod +x scripts/path/to/script.sh`
2. **Virtual Environment**: Scripts will auto-activate `venv` if available
3. **Missing Dependencies**: Scripts auto-install required dependencies
4. **Path Issues**: All scripts use relative paths from project root

### Debug Mode

Enable debug output for troubleshooting:
```bash
# For shell scripts
bash -x ./scripts/path/to/script.sh

# For Python scripts
CALCULATOR_DEBUG_MODE=true ./scripts/path/to/script.py
```

### Getting Help

- Check script output for troubleshooting tips
- Review logs in `test-results/` directory
- Check security reports in `reports/` directory
- Refer to individual script documentation in source code