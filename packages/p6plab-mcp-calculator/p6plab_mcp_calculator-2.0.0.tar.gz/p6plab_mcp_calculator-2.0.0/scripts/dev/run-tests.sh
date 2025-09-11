#!/bin/bash
# Development test suite - focused on quick feedback for developers
set -e

# Source common utilities
source "$(dirname "$0")/../lib/common.sh"

# Parse command line arguments
SKIP_LINTING=false
SKIP_SECURITY=false
QUICK_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-linting)
            SKIP_LINTING=true
            shift
            ;;
        --skip-security)
            SKIP_SECURITY=true
            shift
            ;;
        --quick)
            QUICK_MODE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --skip-linting    Skip code linting checks"
            echo "  --skip-security   Skip security scanning"
            echo "  --quick          Run only core functionality tests"
            echo "  -h, --help       Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

print_header "Development Test Suite" "Quick validation for development workflow"

# Check environment and dependencies
check_virtual_env

log_step "Installing test dependencies..."
pip install pytest pytest-asyncio pytest-cov > /dev/null 2>&1 || {
    log_error "Failed to install test dependencies"
    exit 1
}
log_success "Test dependencies installed"

# Quick mode - only essential tests
if [[ "$QUICK_MODE" == "true" ]]; then
    log_step "Quick Mode: Testing core functionality only..."
    
    # Test basic imports and app creation
    log_info "Testing imports and app creation..."
    python -c "
from calculator.server.app import create_calculator_app
app = create_calculator_app()
print('✅ Core functionality working')
" || {
        log_error "Core functionality test failed"
        exit 1
    }
    
    # Run validation script
    log_info "Running validation script..."
    python scripts/dev/validate-refactoring.py || {
        log_error "Validation failed"
        exit 1
    }
    
    print_footer "Quick tests completed successfully!"
    exit 0
fi

# Code quality checks (optional)
if [[ "$SKIP_LINTING" == "false" ]]; then
    log_step "Running code quality checks..."
    
    log_info "Checking code formatting..."
    if command -v ruff &> /dev/null; then
        ruff check calculator/ --fix --quiet || {
            log_warning "Linting issues found (some may be auto-fixed)"
        }
        log_success "Code formatting checked"
    else
        log_warning "Ruff not installed, skipping linting"
    fi
else
    log_info "Skipping linting checks (--skip-linting specified)"
fi

# Security scan (optional)
if [[ "$SKIP_SECURITY" == "false" ]]; then
    log_step "Running security scan..."
    
    if command -v bandit &> /dev/null; then
        bandit -r calculator/ -q || {
            log_warning "Security scan found issues"
        }
        log_success "Security scan completed"
    else
        log_warning "Bandit not installed, skipping security scan"
    fi
else
    log_info "Skipping security scan (--skip-security specified)"
fi

# Core functionality tests
log_step "Testing core functionality..."

# Test basic imports and app creation
log_info "Testing imports and app creation..."
python -c "
from calculator.server.app import create_calculator_app
app = create_calculator_app()
print('✅ Core functionality working')
" || {
    log_error "Core functionality test failed"
    exit 1
}

# Run comprehensive validation
log_info "Running comprehensive validation..."
python scripts/dev/validate-refactoring.py || {
    log_error "Validation failed"
    exit 1
}

# Test performance (basic)
log_step "Testing performance..."
python scripts/monitoring/benchmark-performance.py > /dev/null || {
    log_warning "Performance test had issues (check logs)"
}
log_success "Performance test completed"

print_footer "Development tests completed successfully!"

echo ""
echo "Next steps:"
echo "  - Run full test suite: ./scripts/ci/run-all-tests.sh"
echo "  - Test production readiness: ./scripts/ci/test-production-readiness.sh"
echo "  - Build package: ./scripts/deployment/build-package.sh"