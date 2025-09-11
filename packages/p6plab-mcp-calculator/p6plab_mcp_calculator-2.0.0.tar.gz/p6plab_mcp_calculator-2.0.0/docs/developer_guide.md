# Developer Guide - Scientific Calculator MCP Server v2.0.0

## Getting Started

This guide will help you understand, extend, and contribute to the Scientific Calculator MCP Server v2.0.0. The system provides **68 mathematical tools** across **11 specialized domains** with a modular, production-ready architecture.

## Related Documentation

- **[Architecture Guide](ARCHITECTURE.md)** - System architecture and design patterns
- **[API Reference](API_REFERENCE.md)** - Complete API documentation
- **[Scripts and Tools](SCRIPTS_AND_TOOLS.md)** - Development scripts reference
- **[Security Guide](security.md)** - Security features and best practices
- **[CI/CD Guide](CI_CD.md)** - CI/CD integration and automation
- **[Release Guide](RELEASE.md)** - Release process and deployment

> 📚 **Scripts Reference**: For detailed information about all available scripts and tools, see [Scripts and Tools Reference](SCRIPTS_AND_TOOLS.md).

## Prerequisites

- Python 3.8+
- FastMCP v2.0+ framework knowledge
- Basic understanding of async/await patterns
- Familiarity with MCP (Model Context Protocol)
- Understanding of mathematical operations and algorithms
- Knowledge of Pydantic for data validation

## Development Setup

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd calculator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .
```

### 2. Configuration

Create a `.env` file for development:

```bash
# Performance settings
CALC_PRECISION=15
CALC_PERF_CACHE_SIZE=1000
CALC_PERF_MAX_COMPUTATION_TIME_SECONDS=30

# Feature flags
CALC_FEATURE_ENABLE_CACHING=true
CALC_FEATURE_ENABLE_PERFORMANCE_MONITORING=true
CALC_FEATURE_ENABLE_CURRENCY_CONVERSION=false

# Logging
CALC_LOGGING_LOG_LEVEL=DEBUG
CALC_LOGGING_LOG_FORMAT=structured

# Development settings
CALC_DEV_MODE=true
CALC_DEV_ENABLE_DEBUG_ENDPOINTS=true
```

### 3. Running the Server

```bash
# Run the server
python -m calculator.server

# Or run development tests
./scripts/dev/run-tests.sh
```

## Architecture Overview

The Scientific Calculator MCP Server v2.0.0 follows a modular, layered architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                 MCP Server (FastMCP)                       │
│                    70 Tools                                │
├─────────────────────────────────────────────────────────────┤
│                Server Layer                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │Tool Registry│ │ Middleware  │ │   Factory   │          │
│  │(11 Groups)  │ │   Stack     │ │             │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│                Service Layer (11 Services)                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Arithmetic  │ │   Matrix    │ │ Statistics  │          │
│  │(16 tools)   │ │(6 tools)    │ │(6 tools)    │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │  Calculus   │ │  Advanced   │ │   Complex   │          │
│  │(4 tools)    │ │(5 tools)    │ │(6 tools)    │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │    Units    │ │   Solver    │ │  Financial  │          │
│  │(7 tools)    │ │(6 tools)    │ │(7 tools)    │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
│  ┌─────────────┐ ┌─────────────┐                          │
│  │  Currency   │ │  Constants  │                          │
│  │(4 tools)    │ │(3 tools)    │                          │
│  └─────────────┘ └─────────────┘                          │
├─────────────────────────────────────────────────────────────┤
│               Repository Layer                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │    Cache    │ │  Constants  │ │  Currency   │          │
│  │ Repository  │ │ Repository  │ │ Repository  │          │
│  │(Redis-like) │ │(Math/Phys)  │ │(Live Rates) │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│                 Core Layer                                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │Configuration│ │  Security   │ │   Quality   │          │
│  │& Tool Groups│ │& Validation │ │& Monitoring │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

- **70 Tools**: Comprehensive mathematical operations across 11 domains
- **11 Services**: Specialized services for each mathematical domain
- **Tool Groups**: Configurable tool organization (basic always enabled, others optional)
- **FastMCP Integration**: Built on FastMCP v2.0+ framework
- **Production Ready**: Comprehensive security, testing, and monitoring

## Adding New Operations

### 1. Create a Service Method

First, add your operation to the appropriate service:

```python
# calculator/services/arithmetic.py
class ArithmeticService(BaseService):
    
    async def process(self, operation: str, data: Dict[str, Any]) -> Any:
        """Process arithmetic operations."""
        
        # Add your new operation
        if operation == 'my_new_operation':
            return await self.my_new_operation(data)
        
        # ... existing operations
    
    async def my_new_operation(self, data: Dict[str, Any]) -> float:
        """My new mathematical operation.
        
        Args:
            data: Input data containing required parameters
            
        Returns:
            Result of the operation
            
        Raises:
            ValidationError: If input validation fails
            ComputationError: If computation fails
        """
        # Validate input
        self._validate_required_fields(data, ['param1', 'param2'])
        
        param1 = data['param1']
        param2 = data['param2']
        
        # Perform computation
        try:
            result = self._compute_my_operation(param1, param2)
            
            # Cache result if caching is enabled
            if self.config.is_caching_enabled():
                cache_key = f"my_operation_{param1}_{param2}"
                await self.cache_repository.set(cache_key, result)
            
            return result
            
        except Exception as e:
            raise ComputationError(f"Failed to compute my operation: {str(e)}")
    
    def _compute_my_operation(self, param1: float, param2: float) -> float:
        """Internal computation logic."""
        # Your mathematical logic here
        return param1 * param2 + param1 ** param2
```

### 2. Create Input Validation Schema

Define a Pydantic model for input validation:

```python
# calculator/server/handlers/arithmetic.py
from pydantic import BaseModel, Field, validator

class MyOperationRequest(BaseModel):
    """Request model for my new operation."""
    param1: float = Field(..., description="First parameter")
    param2: float = Field(..., ge=0, description="Second parameter (must be non-negative)")
    
    @validator('param1')
    def validate_param1(cls, v):
        """Validate first parameter."""
        if abs(v) > 1000:
            raise ValueError("param1 must be between -1000 and 1000")
        return v
```

### 3. Register the MCP Tool

Add your operation to the tool registration:

```python
# calculator/server/handlers/arithmetic.py
def register_arithmetic_handlers(factory: ToolRegistrationFactory, service: ArithmeticService) -> None:
    """Register arithmetic operation handlers."""
    
    factory.register_service_tools(
        service_name="arithmetic",
        service_instance=service,
        tool_definitions=[
            # ... existing tools
            {
                'name': 'my_new_operation',
                'operation': 'my_new_operation',
                'description': 'Perform my new mathematical operation',
                'input_schema': MyOperationRequest,
                'tool_group': 'arithmetic',
                'examples': [
                    {
                        'param1': 5.0,
                        'param2': 2.0,
                        'result': 35.0  # 5 * 2 + 5^2 = 10 + 25 = 35
                    }
                ],
                'tags': ['arithmetic', 'custom']
            }
        ],
        tool_group="arithmetic"
    )
```

### 4. Add Tests

Create comprehensive tests for your operation:

```python
# tests/unit/services/test_arithmetic_service.py
import pytest
from calculator.services.arithmetic import ArithmeticService
from calculator.core.errors.exceptions import ValidationError, ComputationError

class TestMyNewOperation:
    """Test my new operation."""
    
    @pytest.fixture
    def service(self):
        """Create arithmetic service for testing."""
        return ArithmeticService()
    
    @pytest.mark.asyncio
    async def test_my_new_operation_success(self, service):
        """Test successful operation."""
        data = {'param1': 5.0, 'param2': 2.0}
        result = await service.process('my_new_operation', data)
        
        assert result == 35.0  # 5 * 2 + 5^2
    
    @pytest.mark.asyncio
    async def test_my_new_operation_validation_error(self, service):
        """Test validation error."""
        data = {'param1': 2000.0, 'param2': 2.0}  # param1 too large
        
        with pytest.raises(ValidationError):
            await service.process('my_new_operation', data)
    
    @pytest.mark.asyncio
    async def test_my_new_operation_missing_param(self, service):
        """Test missing parameter."""
        data = {'param1': 5.0}  # Missing param2
        
        with pytest.raises(ValidationError):
            await service.process('my_new_operation', data)
```

### 5. Add Integration Tests

Test the complete flow from MCP tool to result:

```python
# tests/integration/test_my_operation_integration.py
import pytest
from calculator.server.app import create_calculator_app

@pytest.mark.asyncio
async def test_my_operation_integration():
    """Test my operation through the full stack."""
    app = create_calculator_app()
    await app.initialize()
    
    # Simulate MCP tool call
    # This would typically be done through the MCP protocol
    # but we can test the service directly
    
    result = await app.arithmetic_service.process('my_new_operation', {
        'param1': 3.0,
        'param2': 4.0
    })
    
    assert result == 93.0  # 3 * 4 + 3^4 = 12 + 81 = 93
```

## Adding New Services

### 1. Create Service Class

```python
# calculator/services/my_service.py
from typing import Dict, Any
from .base import BaseService

class MyService(BaseService):
    """Service for my custom operations."""
    
    def __init__(self, config=None, cache_repository=None):
        """Initialize my service."""
        super().__init__(config, cache_repository)
        self.service_name = "my_service"
    
    async def process(self, operation: str, data: Dict[str, Any]) -> Any:
        """Process operations for my service."""
        
        if operation == 'my_operation':
            return await self.my_operation(data)
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    async def my_operation(self, data: Dict[str, Any]) -> Any:
        """My custom operation."""
        # Implementation here
        pass
```

### 2. Register Service in App

```python
# calculator/server/app.py
class CalculatorApp:
    
    def __init__(self, config: Optional[ConfigService] = None):
        # ... existing initialization
        
        # Add your service
        self.my_service = MyService(self.config, self.cache_repo)
    
    async def _register_all_tools(self) -> None:
        # ... existing registrations
        
        # Register your service tools
        if self.config.is_tool_group_enabled('my_service'):
            await self._register_my_service_tools()
    
    async def _register_my_service_tools(self) -> None:
        """Register my service tools."""
        from .handlers.my_service import register_my_service_handlers
        register_my_service_handlers(self.tool_factory, self.my_service)
```

### 3. Create Handlers

```python
# calculator/server/handlers/my_service.py
from ..factory import ToolRegistrationFactory
from ...services.my_service import MyService

def register_my_service_handlers(factory: ToolRegistrationFactory, service: MyService) -> None:
    """Register my service handlers."""
    
    factory.register_service_tools(
        service_name="my_service",
        service_instance=service,
        tool_definitions=[
            {
                'name': 'my_operation',
                'operation': 'my_operation',
                'description': 'My custom operation',
                'input_schema': MyOperationRequest,
                'tool_group': 'my_service'
            }
        ],
        tool_group="my_service"
    )
```

## Adding New Strategies

### 1. Create Strategy Interface

```python
# calculator/strategies/my_strategy.py
from abc import ABC, abstractmethod
from typing import Any, Dict

class MyStrategyInterface(ABC):
    """Interface for my strategy implementations."""
    
    @abstractmethod
    async def execute(self, data: Dict[str, Any]) -> Any:
        """Execute the strategy."""
        pass
    
    @abstractmethod
    def is_suitable(self, data: Dict[str, Any]) -> bool:
        """Check if strategy is suitable for the data."""
        pass
    
    @abstractmethod
    def get_performance_score(self, data: Dict[str, Any]) -> float:
        """Get expected performance score for the data."""
        pass

class FastMyStrategy(MyStrategyInterface):
    """Fast implementation of my strategy."""
    
    async def execute(self, data: Dict[str, Any]) -> Any:
        """Fast but less accurate implementation."""
        # Implementation here
        pass
    
    def is_suitable(self, data: Dict[str, Any]) -> bool:
        """Suitable for small datasets."""
        return len(data.get('items', [])) < 1000
    
    def get_performance_score(self, data: Dict[str, Any]) -> float:
        """High performance for small data."""
        return 0.9 if self.is_suitable(data) else 0.3

class AccurateMyStrategy(MyStrategyInterface):
    """Accurate implementation of my strategy."""
    
    async def execute(self, data: Dict[str, Any]) -> Any:
        """Accurate but slower implementation."""
        # Implementation here
        pass
    
    def is_suitable(self, data: Dict[str, Any]) -> bool:
        """Suitable for any dataset."""
        return True
    
    def get_performance_score(self, data: Dict[str, Any]) -> float:
        """Good performance for any data."""
        return 0.7
```

### 2. Create Strategy Context

```python
# calculator/strategies/my_strategy.py (continued)
class MyStrategyContext:
    """Context for selecting and executing my strategies."""
    
    def __init__(self):
        """Initialize strategy context."""
        self.strategies = [
            FastMyStrategy(),
            AccurateMyStrategy()
        ]
    
    def select_strategy(self, data: Dict[str, Any]) -> MyStrategyInterface:
        """Select best strategy for the data."""
        suitable_strategies = [s for s in self.strategies if s.is_suitable(data)]
        
        if not suitable_strategies:
            # Fallback to most general strategy
            return self.strategies[-1]
        
        # Select strategy with highest performance score
        return max(suitable_strategies, key=lambda s: s.get_performance_score(data))
    
    async def execute(self, data: Dict[str, Any]) -> Any:
        """Execute using the best strategy."""
        strategy = self.select_strategy(data)
        return await strategy.execute(data)
```

### 3. Integrate Strategy in Service

```python
# calculator/services/my_service.py (updated)
from ..strategies.my_strategy import MyStrategyContext

class MyService(BaseService):
    
    def __init__(self, config=None, cache_repository=None):
        super().__init__(config, cache_repository)
        self.strategy_context = MyStrategyContext()
    
    async def my_operation(self, data: Dict[str, Any]) -> Any:
        """My operation using strategy pattern."""
        
        # Use strategy for computation
        result = await self.strategy_context.execute(data)
        
        return result
```

## Error Handling Best Practices

### 1. Use Specific Exceptions

```python
from calculator.core.errors.exceptions import ValidationError, ComputationError, TimeoutError

async def my_operation(self, data: Dict[str, Any]) -> float:
    """My operation with proper error handling."""
    
    # Validation errors
    if 'required_param' not in data:
        raise ValidationError("Missing required parameter", field="required_param")
    
    # Computation errors
    try:
        result = complex_computation(data)
    except ZeroDivisionError:
        raise ComputationError("Division by zero in computation")
    except OverflowError:
        raise ComputationError("Numerical overflow in computation")
    
    # Timeout errors
    if computation_time > max_time:
        raise TimeoutError(f"Computation exceeded {max_time} seconds")
    
    return result
```

### 2. Use Error Handling Decorators

```python
from calculator.core.errors.handlers import handle_operation_errors

@handle_operation_errors("my_operation")
async def my_operation(self, data: Dict[str, Any]) -> float:
    """Operation with automatic error handling."""
    # Your implementation
    # Errors will be automatically caught and formatted
    pass
```

## Configuration Management

### 1. Add Configuration Options

```python
# calculator/core/config/settings.py
class MyServiceConfig(BaseModel):
    """Configuration for my service."""
    
    enable_feature: bool = Field(default=True, description="Enable my feature")
    max_iterations: int = Field(default=1000, ge=1, description="Maximum iterations")
    precision: float = Field(default=1e-6, gt=0, description="Computation precision")

class CalculatorConfig(BaseModel):
    # ... existing config
    
    my_service: MyServiceConfig = Field(default_factory=MyServiceConfig)
```

### 2. Use Configuration in Service

```python
class MyService(BaseService):
    
    def __init__(self, config=None, cache_repository=None):
        super().__init__(config, cache_repository)
        self.my_config = config.config.my_service if config else MyServiceConfig()
    
    async def my_operation(self, data: Dict[str, Any]) -> float:
        """Operation using configuration."""
        
        if not self.my_config.enable_feature:
            raise ComputationError("Feature is disabled")
        
        max_iter = self.my_config.max_iterations
        precision = self.my_config.precision
        
        # Use configuration in computation
        result = iterative_computation(data, max_iter, precision)
        return result
```

## Testing Guidelines

### 1. Unit Tests

Test individual components in isolation:

```python
import pytest
from unittest.mock import Mock, AsyncMock
from calculator.services.my_service import MyService

class TestMyService:
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration."""
        config = Mock()
        config.is_caching_enabled.return_value = True
        return config
    
    @pytest.fixture
    def mock_cache(self):
        """Mock cache repository."""
        cache = AsyncMock()
        cache.get.return_value = None  # Cache miss
        return cache
    
    @pytest.fixture
    def service(self, mock_config, mock_cache):
        """Create service with mocks."""
        return MyService(mock_config, mock_cache)
    
    @pytest.mark.asyncio
    async def test_my_operation_success(self, service):
        """Test successful operation."""
        data = {'param': 42}
        result = await service.my_operation(data)
        
        assert result is not None
        assert isinstance(result, float)
    
    @pytest.mark.asyncio
    async def test_my_operation_caching(self, service, mock_cache):
        """Test that results are cached."""
        data = {'param': 42}
        await service.my_operation(data)
        
        # Verify cache was called
        mock_cache.set.assert_called_once()
```

### 2. Integration Tests

Test component interactions:

```python
@pytest.mark.asyncio
async def test_service_integration():
    """Test service integration with real dependencies."""
    from calculator.services.config import ConfigService
    from calculator.repositories.cache import CacheRepository
    
    config = ConfigService()
    cache = CacheRepository()
    service = MyService(config, cache)
    
    result = await service.my_operation({'param': 42})
    
    assert result is not None
```

### 3. Performance Tests

Test performance characteristics:

```python
import time
import pytest

@pytest.mark.performance
@pytest.mark.asyncio
async def test_operation_performance():
    """Test operation performance."""
    service = MyService()
    
    start_time = time.time()
    result = await service.my_operation({'param': 42})
    end_time = time.time()
    
    execution_time = end_time - start_time
    
    assert execution_time < 1.0  # Should complete in under 1 second
    assert result is not None
```

## Monitoring and Observability

### 1. Add Metrics

```python
from calculator.core.monitoring.metrics import record_operation_metric

async def my_operation(self, data: Dict[str, Any]) -> float:
    """Operation with metrics."""
    start_time = time.time()
    
    try:
        result = await self._compute_result(data)
        
        # Record success metric
        execution_time = time.time() - start_time
        record_operation_metric("my_operation", execution_time, True)
        
        return result
        
    except Exception as e:
        # Record failure metric
        execution_time = time.time() - start_time
        record_operation_metric("my_operation", execution_time, False)
        raise
```

### 2. Add Logging

```python
from loguru import logger

async def my_operation(self, data: Dict[str, Any]) -> float:
    """Operation with structured logging."""
    
    logger.info("Starting my operation", operation="my_operation", params=data)
    
    try:
        result = await self._compute_result(data)
        
        logger.info("Operation completed successfully", 
                   operation="my_operation", 
                   result_type=type(result).__name__)
        
        return result
        
    except Exception as e:
        logger.error("Operation failed", 
                    operation="my_operation", 
                    error=str(e), 
                    error_type=type(e).__name__)
        raise
```

## Security Considerations

### 1. Input Validation

Always validate inputs thoroughly:

```python
from calculator.core.security.validation import validate_operation_input

async def my_operation(self, data: Dict[str, Any]) -> float:
    """Operation with security validation."""
    
    # Validate and sanitize input
    validated_data = validate_operation_input("my_operation", data)
    
    # Use validated data
    result = await self._compute_result(validated_data)
    return result
```

### 2. Rate Limiting

Apply rate limiting to expensive operations:

```python
from calculator.core.security.rate_limiting import rate_limit_decorator

@rate_limit_decorator()
async def expensive_operation(self, data: Dict[str, Any]) -> float:
    """Expensive operation with rate limiting."""
    # Implementation
    pass
```

### 3. Security Auditing

Add security auditing for sensitive operations:

```python
from calculator.core.security.audit import audit_operation

@audit_operation("my_operation")
async def my_operation(self, data: Dict[str, Any]) -> float:
    """Operation with security auditing."""
    # Implementation - all calls will be audited
    pass
```

## Debugging Tips

### 1. Enable Debug Logging

```bash
export CALC_LOGGING_LOG_LEVEL=DEBUG
export CALC_DEV_MODE=true
```

### 2. Use Health Checks

```python
# Check system health
from calculator.server.app import create_calculator_app

app = create_calculator_app()
await app.initialize()

health_status = app.get_health_status()
print(health_status)
```

### 3. Monitor Performance

```python
# Get performance metrics
from calculator.core.monitoring.metrics import metrics_collector

stats = await metrics_collector.get_summary_stats()
print(f"Total operations: {stats['total_operations']}")
print(f"Error rate: {stats['error_rate']:.2%}")
```

## Contributing Guidelines

### 1. Code Style

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Write comprehensive docstrings using Google style
- Keep functions under 50 lines when possible
- Keep modules under 800 lines

### 2. Testing Requirements

- Minimum 90% test coverage for new code
- Include unit tests, integration tests, and performance tests
- Test error conditions and edge cases
- Use meaningful test names and descriptions

### 3. Documentation

- Update API documentation for new operations
- Add examples to docstrings
- Update architecture documentation for significant changes
- Include migration notes for breaking changes

### 4. Performance

- Benchmark new operations against existing implementations
- Ensure operations complete within reasonable time limits
- Implement caching for expensive operations
- Use appropriate algorithms and data structures

### 5. Security

- Validate all inputs thoroughly
- Implement appropriate rate limiting
- Add security auditing for sensitive operations
- Follow principle of least privilege

## Common Patterns

### 1. Service Method Template

```python
async def my_operation(self, data: Dict[str, Any]) -> Any:
    """Template for service methods."""
    
    # 1. Validate input
    self._validate_required_fields(data, ['required_field'])
    
    # 2. Check cache
    cache_key = self._generate_cache_key("my_operation", data)
    if self.config.is_caching_enabled():
        cached_result = await self.cache_repository.get(cache_key)
        if cached_result is not None:
            return cached_result
    
    # 3. Perform computation
    try:
        result = await self._compute_my_operation(data)
    except Exception as e:
        raise ComputationError(f"Computation failed: {str(e)}")
    
    # 4. Cache result
    if self.config.is_caching_enabled():
        await self.cache_repository.set(cache_key, result)
    
    # 5. Return result
    return result
```

### 2. Error Handling Template

```python
from calculator.core.errors.handlers import handle_operation_errors

@handle_operation_errors("operation_name")
async def my_operation(self, data: Dict[str, Any]) -> Any:
    """Operation with standardized error handling."""
    
    # Validation errors
    if not self._is_valid_input(data):
        raise ValidationError("Invalid input", details=data)
    
    # Computation errors
    try:
        result = self._compute(data)
    except (ValueError, ArithmeticError) as e:
        raise ComputationError(f"Computation failed: {str(e)}")
    
    # Timeout errors
    if self._is_timeout_exceeded():
        raise TimeoutError("Operation timed out")
    
    return result
```

This developer guide provides a comprehensive foundation for working with the calculator's architecture. For specific questions or advanced use cases, refer to the architecture documentation or examine existing implementations in the codebase.