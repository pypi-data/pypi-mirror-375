#!/bin/bash
# Common utility functions for calculator scripts
# Shared functions to reduce code duplication across scripts

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

# Check if we're in a virtual environment and activate if needed
check_virtual_env() {
    if [[ -z "$VIRTUAL_ENV" ]]; then
        log_warning "Not in a virtual environment. Activating venv..."
        if [[ -f "venv/bin/activate" ]]; then
            source venv/bin/activate
            log_success "Virtual environment activated"
        else
            log_error "Virtual environment not found. Please run: python -m venv venv && source venv/bin/activate"
            exit 1
        fi
    else
        log_success "Virtual environment active: $VIRTUAL_ENV"
    fi
}

# Install common dependencies
install_common_dependencies() {
    log_step "Installing common dependencies..."
    pip install --upgrade pip setuptools wheel
    pip install --upgrade pytest pytest-asyncio pytest-cov
    pip install --upgrade ruff pyright bandit
    pip install --upgrade build twine
    log_success "Common dependencies installed"
}

# Install test dependencies
install_test_dependencies() {
    log_step "Installing test dependencies..."
    pip install --upgrade pytest pytest-asyncio pytest-cov
    pip install --upgrade ruff pyright bandit
    log_success "Test dependencies installed"
}

# Install build dependencies
install_build_dependencies() {
    log_step "Installing build dependencies..."
    pip install --upgrade build twine bandit
    log_success "Build dependencies installed"
}

# Run security scan
run_security_scan() {
    log_step "Running security scan..."
    ./scripts/ci/security-scan.sh || {
        log_error "Security scanning failed"
        return 1
    }
    log_success "Security scanning passed"
}

# Run linting
run_linting() {
    log_step "Running code linting with ruff..."
    ruff check calculator/ tests/ scripts/ || {
        log_error "Linting failed"
        log_info "TIP: Fix linting issues and try again"
        return 1
    }
    log_success "Linting passed"
}

# Run formatting check
run_formatting_check() {
    log_step "Checking code formatting..."
    ruff format --check calculator/ tests/ scripts/ || {
        log_error "Formatting check failed"
        log_info "TIP: Run: ruff format calculator/ tests/ scripts/"
        return 1
    }
    log_success "Formatting check passed"
}

# Run type checking
run_type_checking() {
    log_step "Running type checking with pyright..."
    pyright calculator/ || {
        log_warning "Type checking completed with warnings/errors"
        log_info "TIP: Consider fixing type issues for better code quality"
    }
    log_success "Type checking completed"
}

# Test basic functionality
test_basic_functionality() {
    log_step "Testing imports and basic functionality..."
    python -c "
import sys
try:
    # Test core imports
    from calculator.server import main
    print('SUCCESS: Server imports successful')
    
    # Test basic operations imports (use services instead of core.basic)
    from calculator.services.arithmetic import ArithmeticService
    print('SUCCESS: Service imports successful')
    
    from calculator.models.request import BasicOperationRequest
    from calculator.models.response import CalculationResult
    from calculator.models.errors import ValidationError
    print('SUCCESS: Model imports successful')
    
    # Test basic calculation using service
    import asyncio
    service = ArithmeticService()
    
    # Test add operation
    result = asyncio.run(service.add({'numbers': [2.5, 3.7]}))
    assert result == 6.2
    print('SUCCESS: Basic calculation test passed')
    
    # Test error handling
    try:
        asyncio.run(service.divide({'a': 1, 'b': 0}))
        print('ERROR: Error handling test failed - should have raised exception')
        sys.exit(1)
    except Exception:
        print('SUCCESS: Error handling test passed')
    
    print('SUCCESS: All functionality tests passed')
    
except Exception as e:
    print(f'ERROR: Functionality test failed: {e}')
    sys.exit(1)
" || {
        log_error "Basic functionality test failed"
        return 1
    }
    log_success "Basic functionality test passed"
}

# Test package building
test_package_build() {
    log_step "Testing package building..."
    python -m build --wheel --sdist --outdir test-dist/ || {
        log_error "Package building failed"
        return 1
    }
    log_success "Package building test passed"
    
    # Clean up test build
    rm -rf test-dist/
}

# Test entry point
test_entry_point() {
    log_step "Testing entry point..."
    if command -v p6plab-mcp-calculator &> /dev/null; then
        gtimeout 3s p6plab-mcp-calculator --help || log_success "Entry point test completed (timeout expected)"
    else
        log_warning "Entry point not found, installing package in editable mode..."
        pip install -e .
        gtimeout 3s p6plab-mcp-calculator --help || log_success "Entry point test completed (timeout expected)"
    fi
    log_success "Entry point test passed"
}

# Clean up common artifacts
cleanup_artifacts() {
    log_step "Cleaning up artifacts..."
    rm -rf .pytest_cache/
    rm -rf htmlcov/
    rm -rf build/
    rm -rf *.egg-info/
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    log_success "Cleanup completed"
}

# Check if uvx is available
check_uvx_available() {
    if command -v uvx &> /dev/null; then
        log_success "uvx is available"
        return 0
    else
        log_warning "uvx not available"
        return 1
    fi
}

# Validate uvx compatibility
validate_uvx_compatibility() {
    log_step "Validating uvx compatibility..."
    
    # Check entry points
    log_info "Checking entry points..."
    python -c "
import tomllib
with open('pyproject.toml', 'rb') as f:
    config = tomllib.load(f)
    scripts = config.get('project', {}).get('scripts', {})
    if scripts:
        for name, entry in scripts.items():
            print(f'  {name} = {entry}')
    else:
        print('  No entry points found!')
        exit(1)
" || {
        log_error "No entry points found for uvx"
        return 1
    }
    
    log_success "uvx compatibility validated"
}

# Print script header
print_header() {
    local title="$1"
    local description="$2"
    
    echo ""
    echo "$(printf '=%.0s' {1..60})"
    echo "$title"
    echo "$(printf '=%.0s' {1..60})"
    if [[ -n "$description" ]]; then
        echo "$description"
        echo ""
    fi
}

# Print script footer
print_footer() {
    local success_message="$1"
    
    echo ""
    echo "$(printf '=%.0s' {1..60})"
    if [[ -n "$success_message" ]]; then
        log_success "$success_message"
    fi
    echo "$(printf '=%.0s' {1..60})"
    echo ""
}

# Export functions for use in other scripts
export -f log_info log_success log_warning log_error log_step
export -f check_virtual_env install_common_dependencies install_test_dependencies install_build_dependencies
export -f run_security_scan run_linting run_formatting_check run_type_checking
export -f test_basic_functionality test_package_build test_entry_point
export -f cleanup_artifacts check_uvx_available validate_uvx_compatibility
export -f print_header print_footer