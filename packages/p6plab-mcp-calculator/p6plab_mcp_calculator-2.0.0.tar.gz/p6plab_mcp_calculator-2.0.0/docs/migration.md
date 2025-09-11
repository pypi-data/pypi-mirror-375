# Migration Guide - Calculator Refactoring

This guide helps you migrate from the old monolithic calculator server to the new modular architecture.

## Related Documentation

- **[Installation Guide](installation.md)** - Setup and installation instructions
- **[Configuration Guide](configuration.md)** - Tool group configuration and environment variables
- **[API Reference](API_REFERENCE.md)** - Complete API documentation
- **[Developer Guide](DEVELOPER_GUIDE.md)** - Development setup and contribution guide
- **[Troubleshooting Guide](troubleshooting.md)** - Common issues and solutions

## Overview

The Scientific Calculator MCP Server has been refactored from a monolithic architecture to a modular, layered architecture. This migration preserves all existing functionality while improving maintainability, performance, and extensibility.

## What's Changed

### Architecture Changes

**Before (Monolithic):**
```
calculator/
├── server.py (2,615 lines)
├── core/ (various modules)
├── models/
└── utils/
```

**After (Modular):**
```
calculator/
├── server/ (Server layer)
├── services/ (Business logic)
├── repositories/ (Data access)
├── strategies/ (Algorithm selection)
├── core/ (Base classes, errors, config, monitoring)
├── models/ (Existing models)
└── utils/ (Existing utils)
```

### Key Improvements

1. **Modular Architecture**: Code split into focused modules under 500 lines each
2. **Service Layer**: Business logic separated from presentation logic
3. **Repository Pattern**: Consistent data access with caching and fallbacks
4. **Strategy Patterns**: Automatic algorithm selection for optimal performance
5. **Centralized Configuration**: Pydantic-based configuration with validation
6. **Enhanced Error Handling**: Comprehensive error handling with recovery strategies
7. **Performance Monitoring**: Built-in metrics collection and health checks

## Backward Compatibility

### ✅ Fully Compatible

- **Environment Variables**: All existing environment variables continue to work
- **MCP Tool Interfaces**: All MCP tools have identical interfaces
- **Response Formats**: All response formats remain unchanged
- **Configuration Options**: All configuration options are preserved
- **Error Types**: All existing error types and messages are maintained

### 📝 Import Path Changes (Optional)

While old import paths continue to work, new import paths are recommended:

**Old (Still Works):**
```python
from calculator.core.basic import add_numbers
from calculator.core.matrix import multiply_matrices
```

**New (Recommended):**
```python
from calculator.services.arithmetic import ArithmeticService
from calculator.services.matrix import MatrixService
```

## Migration Steps

### For End Users (No Action Required)

If you're using the calculator as an MCP server, **no changes are required**:

- All MCP tool names remain the same
- All parameters and response formats are identical
- All environment variables continue to work
- Server startup process is unchanged

### For Developers Extending the Calculator

#### 1. Update Import Statements (Optional)

**Old:**
```python
from calculator.core import basic, matrix, statistics
```

**New:**
```python
from calculator.services import ArithmeticService, MatrixService, StatisticsService
```

#### 2. Use New Service Architecture (Recommended)

**Old:**
```python
# Direct function calls
result = basic.add_numbers([1, 2, 3])
```

**New:**
```python
# Service-based approach
service = ArithmeticService()
result = await service.process('add', {'numbers': [1, 2, 3]})
```

#### 3. Leverage New Configuration System

**Old:**
```python
import os
PRECISION = int(os.getenv("CALCULATOR_PRECISION", "15"))
```

**New:**
```python
from calculator.services.config import ConfigService
config = ConfigService()
precision = config.get_precision()
```

#### 4. Use Enhanced Error Handling

**Old:**
```python
try:
    result = some_calculation()
except Exception as e:
    return {"error": str(e)}
```

**New:**
```python
from calculator.core.errors.handlers import handle_operation_errors

@handle_operation_errors("my_operation")
async def my_operation():
    # Your code here
    pass
```

## New Features Available

### 1. Strategy Patterns

Automatic algorithm selection for optimal performance:

```python
from calculator.strategies.matrix_solver import MatrixSolverContext

solver = MatrixSolverContext()
result = solver.solve(matrix, vector)  # Automatically selects best algorithm
```

### 2. Advanced Caching

Intelligent caching with TTL and memory management:

```python
from calculator.services.cache import CacheService

cache_service = CacheService(cache_repository)
result = await cache_service.get_or_compute(key, compute_function)
```

### 3. Performance Monitoring

Built-in metrics collection:

```python
from calculator.core.monitoring.metrics import metrics_collector

# Metrics are automatically collected
performance_summary = metrics_collector.get_performance_summary()
```

### 4. Health Checks

System health monitoring:

```python
from calculator.server.health import HealthChecker

health_checker = HealthChecker(config_service)
health_status = await health_checker.check_system_health()
```

## Configuration Migration

### Environment Variables (No Changes Required)

All existing environment variables continue to work:

```bash
# These all continue to work exactly as before
export CALCULATOR_PRECISION=15
export CALCULATOR_CACHE_SIZE=1000
export CALCULATOR_MAX_COMPUTATION_TIME=30
export CALCULATOR_MAX_MEMORY_MB=512
export CALCULATOR_ENABLE_CURRENCY_CONVERSION=false
export CALCULATOR_LOG_LEVEL=INFO
```

### New Configuration Options (Optional)

Additional configuration options are now available:

```bash
# Performance tuning
export CALC_PERF_CACHE_TTL_SECONDS=7200
export CALC_PERF_MAX_CACHE_SIZE=2000

# Feature toggles
export CALC_FEATURE_ENABLE_PERFORMANCE_MONITORING=true
export CALC_FEATURE_ENABLE_ADVANCED_CALCULUS=true

# Security settings
export CALC_SECURITY_MAX_INPUT_SIZE=50000
export CALC_SECURITY_RATE_LIMIT_PER_MINUTE=2000

# Tool filtering
export CALC_TOOLS_ENABLED_TOOL_GROUPS=basic,advanced,matrix,statistics
export CALC_TOOLS_DISABLED_TOOLS=currency_convert,experimental_feature
```

## Testing Your Migration

### 1. Verify Server Startup

```bash
# Test that server starts normally
python -m calculator.server
```

### 2. Test MCP Tool Compatibility

```python
# Test that all your existing MCP tool calls work
# No changes should be required to your MCP client code
```

### 3. Verify Configuration

```python
from calculator.services.config import ConfigService

config = ConfigService()
print(config.get_config_summary())  # Should show all your settings
```

### 4. Check Performance

The new architecture should provide:
- 15%+ improvement in response times for common operations
- 50%+ reduction in computation time for repeated operations (due to caching)
- Better memory usage patterns

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem:** `ImportError: cannot import name 'X' from 'calculator.core'`

**Solution:** Update import paths to use new service architecture:
```python
# Old
from calculator.core.basic import add_numbers

# New
from calculator.services.arithmetic import ArithmeticService
```

#### 2. Configuration Not Loading

**Problem:** Configuration values not being applied

**Solution:** Check environment variable names and ensure they follow the expected format:
```bash
# Ensure variables are properly set
export CALCULATOR_PRECISION=15  # Legacy format (still works)
# OR
export CALC_PRECISION=15        # New format
```

#### 3. Performance Issues

**Problem:** Operations seem slower than before

**Solution:** 
1. Enable caching: `export CALC_FEATURE_ENABLE_CACHING=true`
2. Check performance monitoring: `export CALC_FEATURE_ENABLE_PERFORMANCE_MONITORING=true`
3. Review cache hit rates in health check endpoint

#### 4. Tool Registration Issues

**Problem:** Some tools not appearing

**Solution:** Check tool group configuration:
```bash
export CALC_TOOLS_ENABLED_TOOL_GROUPS=basic,advanced,matrix,statistics,calculus
```

### Getting Help

1. **Check Logs**: The new architecture provides detailed structured logging
2. **Health Check**: Use the health check endpoint to diagnose issues
3. **Performance Metrics**: Review performance metrics for bottlenecks
4. **Configuration Summary**: Use `config.get_config_summary()` to verify settings

## Rollback Plan

If you need to rollback to the old architecture:

1. **Backup**: Keep a backup of your original `server.py`
2. **Environment**: Your environment variables will work with both versions
3. **Data**: No data migration is required (stateless system)
4. **Clients**: MCP clients will work with both versions without changes

## Benefits of Migration

### Immediate Benefits

- **Better Error Messages**: More detailed error information with context
- **Performance Monitoring**: Built-in metrics and health checks
- **Improved Caching**: Intelligent caching with better hit rates
- **Enhanced Logging**: Structured logging with correlation IDs

### Long-term Benefits

- **Easier Maintenance**: Modular code is easier to understand and modify
- **Better Testing**: Each component can be tested in isolation
- **Performance Optimization**: Strategy patterns automatically select optimal algorithms
- **Extensibility**: Easy to add new operations and features
- **Scalability**: Better resource management and performance monitoring

## Next Steps

1. **Monitor Performance**: Use the new monitoring features to track performance improvements
2. **Explore New Features**: Try the new strategy patterns and advanced caching
3. **Update Development Practices**: Use the new service architecture for extensions
4. **Contribute**: The modular architecture makes it easier to contribute new features

For questions or issues, please refer to the troubleshooting section or check the detailed documentation in each module.