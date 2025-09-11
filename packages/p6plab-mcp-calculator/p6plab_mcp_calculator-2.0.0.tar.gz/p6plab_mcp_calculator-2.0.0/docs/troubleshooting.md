# Troubleshooting Guide - Scientific Calculator MCP Server

## Overview

This guide helps resolve common issues with the Scientific Calculator MCP Server v2.0.0. For security-specific troubleshooting, see the [Security Guide](security.md).

## Related Documentation

- **[Installation Guide](installation.md)** - Setup and installation instructions
- **[Configuration Guide](configuration.md)** - Tool group configuration
- **[Deployment Guide](deployment.md)** - Production deployment issues
- **[Security Guide](security.md)** - Security troubleshooting and best practices
- **[Developer Guide](DEVELOPER_GUIDE.md)** - Development troubleshooting

## Common Issues and Solutions

### Server Startup Issues

#### Issue: Server fails to start with "Module not found" error

**Symptoms:**
```
ImportError: No module named 'calculator.server'
ModuleNotFoundError: No module named 'fastmcp'
```

**Solutions:**

1. **Check Python Path:**
   ```bash
   # Ensure you're in the correct directory
   cd /path/to/calculator
   
   # Check if calculator module is importable
   python -c "import calculator; print('OK')"
   ```

2. **Install Dependencies:**
   ```bash
   # Install required packages
   pip install -r requirements.txt
   
   # Install in development mode
   pip install -e .
   ```

3. **Virtual Environment:**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

#### Issue: Configuration validation errors

**Symptoms:**
```
ValidationError: Configuration validation failed
pydantic.error_wrappers.ValidationError: 1 validation error for CalculatorConfig
```

**Solutions:**

1. **Check Environment Variables:**
   ```bash
   # List all calculator-related environment variables
   env | grep CALC
   
   # Check for invalid values
   echo $CALC_PRECISION  # Should be a number
   echo $CALC_PERF_CACHE_SIZE  # Should be a positive integer
   ```

2. **Reset to Defaults:**
   ```bash
   # Unset problematic variables
   unset CALC_PRECISION
   unset CALC_PERF_CACHE_SIZE
   
   # Or set valid values
   export CALC_PRECISION=15
   export CALC_PERF_CACHE_SIZE=1000
   ```

3. **Validate Configuration:**
   ```python
   from calculator.services.config import ConfigService
   
   try:
       config = ConfigService()
       print("Configuration is valid")
       print(config.get_config_summary())
   except Exception as e:
       print(f"Configuration error: {e}")
   ```

### Performance Issues

#### Issue: Operations are slow or timing out

**Symptoms:**
- Operations take longer than expected
- Timeout errors in logs
- High CPU or memory usage

**Diagnostic Steps:**

1. **Check Performance Metrics:**
   ```python
   from calculator.core.monitoring.metrics import metrics_collector
   
   # Get performance summary
   stats = await metrics_collector.get_summary_stats()
   print(f"Average operations per second: {stats['operations_per_second']}")
   print(f"Error rate: {stats['error_rate']:.2%}")
   
   # Get operation-specific stats
   operation_stats = await metrics_collector.get_operation_stats('matrix_multiply')
   print(f"Average time: {operation_stats['average_time']:.3f}s")
   ```

2. **Check Cache Performance:**
   ```python
   from calculator.repositories.cache import CacheRepository
   
   cache = CacheRepository()
   stats = await cache.get_stats()
   print(f"Cache hit rate: {stats['hit_rate']:.2%}")
   print(f"Cache size: {stats['current_size']}/{stats['max_size']}")
   ```

3. **Monitor System Resources:**
   ```python
   from calculator.core.monitoring.metrics import metrics_collector
   
   system_stats = await metrics_collector.get_system_stats()
   if system_stats:
       print(f"CPU usage: {system_stats['cpu_percent']:.1f}%")
       print(f"Memory usage: {system_stats['memory_percent']:.1f}%")
   ```

**Solutions:**

1. **Increase Cache Size:**
   ```bash
   export CALC_PERF_CACHE_SIZE=5000
   export CALC_PERF_CACHE_TTL_SECONDS=7200
   ```

2. **Adjust Computation Limits:**
   ```bash
   export CALC_PERF_MAX_COMPUTATION_TIME_SECONDS=60
   export CALC_PERF_MAX_MEMORY_MB=1024
   ```

3. **Enable Performance Monitoring:**
   ```bash
   export CALC_FEATURE_ENABLE_PERFORMANCE_MONITORING=true
   export CALC_LOGGING_LOG_LEVEL=INFO
   ```

#### Issue: Memory usage keeps growing

**Symptoms:**
- Increasing memory usage over time
- Out of memory errors
- System becomes unresponsive

**Diagnostic Steps:**

1. **Check Cache Size:**
   ```python
   from calculator.repositories.cache import CacheRepository
   
   cache = CacheRepository()
   stats = await cache.get_stats()
   print(f"Cache entries: {stats['current_size']}")
   print(f"Memory usage estimate: {stats.get('memory_usage_mb', 'unknown')} MB")
   ```

2. **Monitor Memory Growth:**
   ```bash
   # Monitor memory usage over time
   while true; do
       ps aux | grep python | grep calculator
       sleep 10
   done
   ```

**Solutions:**

1. **Reduce Cache Size:**
   ```bash
   export CALC_PERF_CACHE_SIZE=500
   export CALC_PERF_CACHE_TTL_SECONDS=1800  # 30 minutes
   ```

2. **Enable Cache Cleanup:**
   ```python
   from calculator.repositories.cache import CacheRepository
   
   cache = CacheRepository()
   await cache.cleanup_expired()  # Manual cleanup
   ```

3. **Restart Server Periodically:**
   ```bash
   # Add to cron for periodic restart
   0 2 * * * /path/to/restart_calculator.sh
   ```

### Calculation Errors

#### Issue: Incorrect calculation results

**Symptoms:**
- Mathematical operations return wrong results
- Inconsistent results for same inputs
- Precision issues with floating-point numbers

**Diagnostic Steps:**

1. **Check Precision Settings:**
   ```python
   from calculator.services.config import ConfigService
   
   config = ConfigService()
   print(f"Precision: {config.get_precision()}")
   ```

2. **Test with Known Values:**
   ```python
   from calculator.services.arithmetic import ArithmeticService
   
   service = ArithmeticService()
   
   # Test basic operations
   result = await service.process('add', {'numbers': [1, 2, 3]})
   assert result == 6, f"Expected 6, got {result}"
   
   result = await service.process('multiply', {'numbers': [2, 3, 4]})
   assert result == 24, f"Expected 24, got {result}"
   ```

3. **Check for Caching Issues:**
   ```python
   # Disable caching temporarily
   export CALC_FEATURE_ENABLE_CACHING=false
   
   # Test if results are consistent
   ```

**Solutions:**

1. **Adjust Precision:**
   ```bash
   export CALC_PRECISION=20  # Higher precision
   ```

2. **Clear Cache:**
   ```python
   from calculator.repositories.cache import CacheRepository
   
   cache = CacheRepository()
   await cache.clear()
   ```

3. **Check Algorithm Selection:**
   ```python
   # For matrix operations, check which algorithm is being used
   from calculator.strategies.matrix_solver import MatrixSolverContext
   
   solver = MatrixSolverContext()
   matrix = [[1, 2], [3, 4]]
   strategy = solver._select_strategy(matrix, [1, 2])
   print(f"Selected strategy: {type(strategy).__name__}")
   ```

#### Issue: Matrix operations fail with "Singular matrix" error

**Symptoms:**
```
ComputationError: Matrix is singular and cannot be inverted
LinAlgError: Singular matrix
```

**Diagnostic Steps:**

1. **Check Matrix Properties:**
   ```python
   import numpy as np
   
   matrix = [[1, 2], [2, 4]]  # Example singular matrix
   det = np.linalg.det(matrix)
   print(f"Determinant: {det}")  # Should be 0 or very close to 0
   ```

2. **Verify Input Data:**
   ```python
   # Check if matrix is properly formed
   matrix = [[1, 2], [3]]  # Invalid - rows have different lengths
   ```

**Solutions:**

1. **Check Matrix Validity:**
   ```python
   def is_matrix_valid(matrix):
       if not matrix or not matrix[0]:
           return False, "Empty matrix"
       
       row_length = len(matrix[0])
       for i, row in enumerate(matrix):
           if len(row) != row_length:
               return False, f"Row {i} has different length"
       
       return True, "Valid"
   
   valid, message = is_matrix_valid(your_matrix)
   print(f"Matrix validity: {message}")
   ```

2. **Use Alternative Algorithms:**
   ```python
   # For near-singular matrices, use SVD-based methods
   from calculator.strategies.matrix_solver import SVDSolver
   
   solver = SVDSolver()
   result = await solver.solve(matrix, vector)
   ```

3. **Add Regularization:**
   ```python
   # Add small value to diagonal for numerical stability
   import numpy as np
   
   matrix = np.array(matrix)
   regularized = matrix + 1e-10 * np.eye(matrix.shape[0])
   ```

### Security Issues

#### Issue: Rate limiting errors

**Symptoms:**
```
SecurityError: Rate limit exceeded: 2000/2000 requests in 60 seconds
SecurityError: Concurrent operation limit exceeded: 50/50 operations
```

**Diagnostic Steps:**

1. **Check Rate Limit Status:**
   ```python
   from calculator.core.security.rate_limiting import rate_limiter
   
   client_stats = rate_limiter.get_client_stats("your_client_id")
   print(f"Current requests: {client_stats['current_requests']}")
   print(f"Remaining requests: {client_stats['remaining_requests']}")
   ```

2. **Check Global Stats:**
   ```python
   global_stats = rate_limiter.get_global_stats()
   print(f"Total clients: {global_stats['total_clients']}")
   print(f"Total concurrent operations: {global_stats['total_concurrent_operations']}")
   ```

**Solutions:**

1. **Increase Rate Limits:**
   ```bash
   export CALC_SECURITY_RATE_LIMIT_PER_MINUTE=5000
   export CALC_SECURITY_MAX_CONCURRENT_OPERATIONS=100
   ```

2. **Implement Backoff Strategy:**
   ```python
   import asyncio
   import random
   
   async def call_with_backoff(operation, data, max_retries=3):
       for attempt in range(max_retries):
           try:
               return await operation(data)
           except SecurityError as e:
               if "rate limit" in str(e).lower() and attempt < max_retries - 1:
                   # Exponential backoff with jitter
                   delay = (2 ** attempt) + random.uniform(0, 1)
                   await asyncio.sleep(delay)
               else:
                   raise
   ```

3. **Use Client Identification:**
   ```python
   # Implement proper client identification
   client_id = f"user_{user_id}_{session_id}"
   ```

#### Issue: Input validation errors

**Symptoms:**
```
ValidationError: Array length 15000 exceeds maximum allowed length 10000
SecurityError: Expression contains forbidden characters
```

**Solutions:**

1. **Adjust Security Limits:**
   ```bash
   export CALC_SECURITY_MAX_ARRAY_LENGTH=20000
   export CALC_SECURITY_MAX_INPUT_SIZE=100000
   ```

2. **Validate Input Before Sending:**
   ```python
   from calculator.core.security.validation import InputValidator
   
   validator = InputValidator()
   
   try:
       validator.validate_array_length(your_array)
       validator.validate_expression_safety(your_expression)
   except (ValidationError, SecurityError) as e:
       print(f"Input validation failed: {e}")
   ```

### Configuration Issues

#### Issue: Environment variables not being recognized

**Symptoms:**
- Settings not taking effect
- Default values being used instead of configured values

**Diagnostic Steps:**

1. **Check Environment Variable Names:**
   ```bash
   # Correct format
   export CALC_PRECISION=15
   export CALC_PERF_CACHE_SIZE=1000
   
   # Incorrect format (won't work)
   export CALCULATOR_PRECISION=15  # Legacy format
   ```

2. **Verify Configuration Loading:**
   ```python
   import os
   from calculator.services.config import ConfigService
   
   print("Environment variables:")
   for key, value in os.environ.items():
       if key.startswith('CALC_'):
           print(f"  {key}={value}")
   
   config = ConfigService()
   print(f"Loaded precision: {config.get_precision()}")
   ```

**Solutions:**

1. **Use Correct Variable Names:**
   ```bash
   # Performance settings
   export CALC_PRECISION=15
   export CALC_PERF_CACHE_SIZE=1000
   export CALC_PERF_MAX_COMPUTATION_TIME_SECONDS=30
   
   # Feature flags
   export CALC_FEATURE_ENABLE_CACHING=true
   export CALC_FEATURE_ENABLE_PERFORMANCE_MONITORING=true
   
   # Security settings
   export CALC_SECURITY_RATE_LIMIT_PER_MINUTE=2000
   export CALC_SECURITY_MAX_CONCURRENT_OPERATIONS=50
   ```

2. **Check for Legacy Variables:**
   ```python
   from calculator.server.compatibility import LegacyEnvironmentMapper
   
   # Apply legacy mapping
   LegacyEnvironmentMapper.apply_legacy_mapping()
   ```

#### Issue: Configuration file not being loaded

**Symptoms:**
- YAML/JSON configuration files ignored
- Only environment variables taking effect

**Solutions:**

1. **Specify Configuration File:**
   ```bash
   export CALC_CONFIG_FILE=/path/to/config.yaml
   ```

2. **Check File Format:**
   ```yaml
   # config.yaml
   precision: 15
   performance:
     cache_size: 1000
     max_computation_time_seconds: 30
   features:
     enable_caching: true
     enable_performance_monitoring: true
   ```

3. **Validate Configuration File:**
   ```python
   import yaml
   from calculator.core.config.settings import CalculatorConfig
   
   with open('config.yaml', 'r') as f:
       config_data = yaml.safe_load(f)
   
   try:
       config = CalculatorConfig(**config_data)
       print("Configuration file is valid")
   except Exception as e:
       print(f"Configuration file error: {e}")
   ```

### Logging and Monitoring Issues

#### Issue: Logs not appearing or in wrong format

**Symptoms:**
- No log output
- Logs in unexpected format
- Missing correlation IDs

**Solutions:**

1. **Check Log Level:**
   ```bash
   export CALC_LOGGING_LOG_LEVEL=DEBUG
   export CALC_LOGGING_LOG_FORMAT=structured
   ```

2. **Enable Correlation IDs:**
   ```bash
   export CALC_LOGGING_ENABLE_CORRELATION_IDS=true
   ```

3. **Test Logging:**
   ```python
   from calculator.core.monitoring.logging import setup_structured_logging
   from calculator.services.config import ConfigService
   from loguru import logger
   
   config = ConfigService()
   setup_structured_logging(config)
   
   logger.info("Test log message", test_field="test_value")
   ```

#### Issue: Health checks failing

**Symptoms:**
```
{
  "status": "unhealthy",
  "error": "Service unavailable"
}
```

**Diagnostic Steps:**

1. **Check Individual Components:**
   ```python
   from calculator.server.app import create_calculator_app
   
   app = create_calculator_app()
   await app.initialize()
   
   # Test individual services
   try:
       result = await app.arithmetic_service.process('add', {'numbers': [1, 1]})
       print(f"Arithmetic service: OK (result: {result})")
   except Exception as e:
       print(f"Arithmetic service: FAILED ({e})")
   ```

2. **Check Repository Health:**
   ```python
   # Test cache repository
   try:
       await app.cache_repo.set("test_key", "test_value")
       value = await app.cache_repo.get("test_key")
       print(f"Cache repository: OK (value: {value})")
   except Exception as e:
       print(f"Cache repository: FAILED ({e})")
   ```

**Solutions:**

1. **Restart Services:**
   ```bash
   # Restart the calculator server
   pkill -f "python.*calculator"
   python -m calculator.server
   ```

2. **Clear Cache:**
   ```python
   from calculator.repositories.cache import CacheRepository
   
   cache = CacheRepository()
   await cache.clear()
   ```

3. **Check Dependencies:**
   ```bash
   # Check if required packages are installed
   pip list | grep -E "(fastmcp|pydantic|loguru|numpy|scipy)"
   ```

## Debugging Tools

### 1. Health Check Endpoint

```python
from calculator.server.app import create_calculator_app

app = create_calculator_app()
await app.initialize()

health = app.get_health_status()
print(json.dumps(health, indent=2))
```

### 2. Performance Profiling

```python
import cProfile
import pstats
from calculator.services.arithmetic import ArithmeticService

def profile_operation():
    service = ArithmeticService()
    # Your operation here
    result = asyncio.run(service.process('add', {'numbers': list(range(1000))}))
    return result

# Profile the operation
cProfile.run('profile_operation()', 'profile_stats')
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative').print_stats(10)
```

### 3. Memory Profiling

```python
import tracemalloc
from calculator.services.matrix import MatrixService

# Start tracing
tracemalloc.start()

# Your operation
service = MatrixService()
large_matrix = [[1.0] * 100 for _ in range(100)]
result = await service.process('determinant', {'matrix': large_matrix})

# Get memory usage
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")

tracemalloc.stop()
```

### 4. Configuration Debugging

```python
from calculator.services.config import ConfigService

config = ConfigService()

# Print all configuration
print("Current configuration:")
summary = config.get_config_summary()
for category, settings in summary.items():
    print(f"\n{category.upper()}:")
    for key, value in settings.items():
        print(f"  {key}: {value}")

# Check specific settings
print(f"\nPrecision: {config.get_precision()}")
print(f"Cache enabled: {config.is_caching_enabled()}")
print(f"Cache size: {config.get_cache_size()}")
```

## Getting Help

### 1. Enable Debug Mode

```bash
export CALC_DEV_MODE=true
export CALC_LOGGING_LOG_LEVEL=DEBUG
export CALC_DEV_ENABLE_DEBUG_ENDPOINTS=true
```

### 2. Collect System Information

```python
import sys
import platform
from calculator import __version__

print(f"Calculator version: {__version__}")
print(f"Python version: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Architecture: {platform.architecture()}")

# Check dependencies
import pkg_resources
required_packages = ['fastmcp', 'pydantic', 'loguru', 'numpy', 'scipy']
for package in required_packages:
    try:
        version = pkg_resources.get_distribution(package).version
        print(f"{package}: {version}")
    except pkg_resources.DistributionNotFound:
        print(f"{package}: NOT INSTALLED")
```

### 3. Generate Diagnostic Report

```python
from calculator.server.app import create_calculator_app
import json

async def generate_diagnostic_report():
    """Generate comprehensive diagnostic report."""
    app = create_calculator_app()
    await app.initialize()
    
    report = {
        'health': app.get_health_status(),
        'configuration': app.config.get_config_summary(),
        'performance': await app.get_application_stats(),
        'version': app.__version__ if hasattr(app, '__version__') else 'unknown'
    }
    
    return report

# Generate and save report
report = await generate_diagnostic_report()
with open('diagnostic_report.json', 'w') as f:
    json.dump(report, f, indent=2, default=str)

print("Diagnostic report saved to diagnostic_report.json")
```

### 4. Contact Support

When reporting issues, please include:

1. **Error Messages**: Full error messages and stack traces
2. **Configuration**: Environment variables and configuration files
3. **System Information**: OS, Python version, package versions
4. **Diagnostic Report**: Output from the diagnostic report generator
5. **Steps to Reproduce**: Detailed steps to reproduce the issue
6. **Expected vs Actual Behavior**: What you expected vs what happened

This troubleshooting guide covers the most common issues you might encounter. For additional help or to report bugs, please refer to the project documentation or contact the development team.