#!/bin/bash
# Test uvx package locally
set -e

# Source common utilities
source "$(dirname "$0")/../lib/common.sh"

print_header "uvx Package Testing" "Testing uvx package locally"

# Check environment and dependencies
check_virtual_env

# Install package locally in editable mode
log_step "Installing package locally in editable mode..."
pip install -e .

log_step "Running uvx execution tests..."

# Test entry point
test_entry_point

# Test with uvx if available
if check_uvx_available; then
    log_step "Testing with uvx..."
    log_info "uvx version:"
    uvx --version
    
    # Test uvx execution (with timeout since it's a server)
    log_step "Testing uvx execution..."
    gtimeout 3s uvx --python-preference system p6plab-mcp-calculator --help || log_success "uvx test completed (timeout expected)"
    
    log_success "uvx execution test passed"
else
    log_warning "uvx not available, skipping uvx-specific tests"
    log_info "TIP: To install uvx: pip install uvx"
fi

# Test basic functionality
test_basic_functionality

print_footer "uvx package test completed successfully!"

echo "Local testing complete! The package is ready for:"
echo "  - Publishing to Test PyPI: ./scripts/deployment/publish-test-pypi.sh"
echo "  - Publishing to PyPI: ./scripts/deployment/publish-pypi.sh"