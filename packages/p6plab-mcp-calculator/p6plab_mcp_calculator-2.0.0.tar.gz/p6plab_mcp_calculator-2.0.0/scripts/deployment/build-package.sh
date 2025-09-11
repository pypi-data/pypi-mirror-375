#!/bin/bash
# Build uvx-compatible package for distribution
set -e

# Source common utilities
source "$(dirname "$0")/../lib/common.sh"

print_header "Package Building" "Building uvx-compatible package for distribution"

# Check environment and dependencies
check_virtual_env
install_build_dependencies

# Run security scanning before building
run_security_scan

# Clean previous builds
log_step "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/

# Build the package
log_step "Building wheel and source distribution..."
python -m build --wheel --sdist

log_success "Package built successfully"

# Validate uvx compatibility
validate_uvx_compatibility

# Check dependencies
log_info "Dependencies:"
python -c "
import tomllib
with open('pyproject.toml', 'rb') as f:
    config = tomllib.load(f)
    deps = config.get('project', {}).get('dependencies', [])
    for dep in deps:
        print(f'  {dep}')
"

log_success "uvx compatibility validated"
log_info "Package files created in dist/:"
ls -la dist/

print_footer "Build complete!"

echo "You can now:"
echo "  - Test locally: ./scripts/deployment/test-uvx-package.sh"
echo "  - Publish to Test PyPI: ./scripts/deployment/publish-test-pypi.sh"
echo "  - Publish to PyPI: ./scripts/deployment/publish-pypi.sh"