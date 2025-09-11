#!/bin/bash
# Production readiness validation script
# Streamlined checks before production deployment
set -e

# Source common utilities
source "$(dirname "$0")/../lib/common.sh"

print_header "Production Readiness Validation" "Comprehensive checks before production deployment"

# Check environment and dependencies
check_virtual_env
install_common_dependencies

log_step "Step 1: Version and Metadata Validation..."
python3 -c "
import calculator
print(f'✅ Version: {calculator.__version__}')
print(f'✅ Author: {calculator.__author__}')
print(f'✅ Description: {calculator.__description__}')
"

log_step "Step 2: Core Functionality Validation..."
python3 -c "
import asyncio
from calculator.server.app import create_calculator_app

async def test_core():
    app = create_calculator_app()
    
    # Test all services are available
    assert app.arithmetic_service is not None, 'Arithmetic service missing'
    assert app.matrix_service is not None, 'Matrix service missing'
    assert app.statistics_service is not None, 'Statistics service missing'
    assert app.calculus_service is not None, 'Calculus service missing'
    
    # Test basic operations
    result = await app.arithmetic_service.process('add', {'numbers': [1, 2, 3]})
    assert result == 6.0, f'Arithmetic test failed: {result}'
    
    result = await app.matrix_service.process('determinant', {'matrix': [[1, 2], [3, 4]]})
    assert abs(result - (-2.0)) < 1e-10, f'Matrix test failed: {result}'
    
    result = await app.statistics_service.process('mean', {'data': [1, 2, 3, 4, 5]})
    assert result == 3.0, f'Statistics test failed: {result}'
    
    print('✅ All core functionality tests passed')

asyncio.run(test_core())
"

log_step "Step 3: Security Validation..."
run_security_scan

log_step "Step 4: Performance Validation..."
python3 scripts/monitoring/benchmark-performance.py || {
    log_error "Performance validation failed"
    exit 1
}

log_step "Step 5: Memory Usage Validation..."
python3 scripts/monitoring/test-memory-usage.py || {
    log_error "Memory usage validation failed"
    exit 1
}

log_step "Step 6: Backward Compatibility Validation..."
python3 -c "
import asyncio
from calculator.server.compatibility import LegacyServerInterface

async def test_legacy():
    legacy = LegacyServerInterface()
    
    # Test legacy calculation interface
    result = await legacy.calculate('add', numbers=[1, 2, 3])
    assert result == 6.0, f'Legacy add failed: {result}'
    
    result = await legacy.calculate('matrix_determinant', matrix=[[1, 2], [3, 4]])
    assert abs(result - (-2.0)) < 1e-10, f'Legacy matrix failed: {result}'
    
    # Test legacy health check
    health = legacy.get_health_status()
    assert health['status'] == 'healthy', f'Legacy health failed: {health}'
    
    print('✅ Backward compatibility validated')

asyncio.run(test_legacy())
"

log_step "Step 7: Package Build Validation..."
test_package_build

log_step "Step 8: Package Installation Test..."
# Test installation in a temporary environment
python3 -m venv temp-test-env
source temp-test-env/bin/activate
pip install --quiet dist/*.whl
python3 -c "
import calculator
from calculator.server import main
print('✅ Package installs and imports correctly')
" || {
    log_error "Package installation test failed"
    deactivate
    rm -rf temp-test-env
    exit 1
}
deactivate
rm -rf temp-test-env

log_step "Step 9: End-to-End Integration Test..."
python3 tests/e2e/test_mcp_server_e2e.py || {
    log_error "End-to-end integration test failed"
    exit 1
}

log_step "Step 10: Comprehensive Test Suite..."
python3 -m pytest tests/ -x --tb=short -q || {
    log_error "Comprehensive test suite failed"
    exit 1
}

log_step "Step 11: Final Refactoring Validation..."
python3 scripts/dev/validate-refactoring.py || {
    log_error "Final refactoring validation failed"
    exit 1
}

log_step "Step 12: Cleanup..."
cleanup_artifacts

print_footer "PRODUCTION READINESS VALIDATION COMPLETE!"

echo "✅ Version and metadata: Valid"
echo "✅ Core functionality: Working"
echo "✅ Security scan: Passed"
echo "✅ Performance: Meets requirements"
echo "✅ Memory usage: Within limits"
echo "✅ Backward compatibility: Maintained"
echo "✅ Package build: Successful"
echo "✅ Package installation: Working"
echo "✅ End-to-end integration: Passed"
echo "✅ Comprehensive tests: All passed"
echo "✅ Refactoring validation: 100% pass rate"
echo ""
echo "🚀 READY FOR PRODUCTION DEPLOYMENT!"
echo ""
echo "Next steps:"
echo "  1. Deploy to staging: ./scripts/deployment/deploy-pipeline.sh staging"
echo "  2. Run staging tests: ./scripts/deployment/test-staging-deployment.sh"
echo "  3. Deploy to production: ./scripts/deployment/deploy-pipeline.sh production"