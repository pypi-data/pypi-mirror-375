# Design Document - Calculator Codebase Refactoring

## Overview

This design document outlines the architectural refactoring of the Scientific Calculator MCP Server to transform it from a monolithic structure into a modular, maintainable, and scalable system. The refactoring will preserve all existing functionality while improving code quality, performance, and developer experience.

The current codebase consists of 13,844 lines with a monolithic server.py file of 2,615 lines. The new architecture will implement modern software engineering patterns including service layers, dependency injection, strategy patterns, and repository patterns to create a more maintainable and extensible system.

## Architecture

### High-Level Architecture

The refactored system will follow a layered architecture pattern:

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server Layer                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Tool Factory  │  │   Middleware    │  │   Handlers   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  Math Services  │  │ Config Service  │  │ Cache Service│ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                  Repository Layer                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Cache Repository│  │Constants Repo   │  │Currency Repo │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                     Core Layer                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  Base Classes   │  │   Strategies    │  │  Validators  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Module Structure

The new modular structure will organize code into focused, single-responsibility modules:

```
calculator/
├── server/
│   ├── __init__.py
│   ├── app.py              # Main server setup (< 200 lines)
│   ├── middleware.py       # Request/response middleware
│   ├── handlers/           # Tool handlers (< 100 lines each)
│   │   ├── __init__.py
│   │   ├── arithmetic.py
│   │   ├── matrix.py
│   │   ├── calculus.py
│   │   └── ...
│   └── factory.py          # Tool registration factory
├── services/
│   ├── __init__.py
│   ├── base.py            # Base service classes
│   ├── arithmetic.py      # Arithmetic service
│   ├── matrix.py          # Matrix operations service
│   ├── calculus/          # Split calculus into focused modules
│   │   ├── __init__.py
│   │   ├── derivatives.py
│   │   ├── integrals.py
│   │   ├── limits.py
│   │   ├── series.py
│   │   └── numerical.py
│   ├── statistics.py      # Statistical operations service
│   └── config.py          # Configuration service
├── repositories/
│   ├── __init__.py
│   ├── base.py            # Base repository interface
│   ├── cache.py           # Cache repository
│   ├── constants.py       # Constants repository
│   └── currency.py        # Currency data repository
├── strategies/
│   ├── __init__.py
│   ├── matrix_solver.py   # Matrix solving strategies
│   ├── numerical.py       # Numerical method strategies
│   └── optimization.py    # Optimization strategies
├── core/
│   ├── base/              # Base classes and interfaces
│   │   ├── __init__.py
│   │   ├── operation.py   # Base operation class
│   │   ├── service.py     # Base service class
│   │   └── validator.py   # Base validator class
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py    # Pydantic configuration models
│   │   └── loader.py      # Configuration loader
│   ├── errors/
│   │   ├── __init__.py
│   │   ├── exceptions.py  # Custom exceptions
│   │   └── handlers.py    # Error handling decorators
│   └── monitoring/
│       ├── __init__.py
│       ├── metrics.py     # Performance metrics
│       └── logging.py     # Structured logging
└── utils/                 # Existing utils remain
```

## Components and Interfaces

### Base Classes and Interfaces

#### BaseOperation Abstract Class
```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel

class BaseOperation(ABC):
    """Abstract base class for all mathematical operations."""
    
    @abstractmethod
    async def execute(self, params: BaseModel) -> Dict[str, Any]:
        """Execute the mathematical operation."""
        pass
    
    @abstractmethod
    def validate_input(self, params: BaseModel) -> bool:
        """Validate input parameters."""
        pass
    
    def format_result(self, result: Any) -> Dict[str, Any]:
        """Format operation result consistently."""
        pass
```

#### BaseService Abstract Class
```python
class BaseService(ABC):
    """Abstract base class for all services."""
    
    def __init__(self, config: ConfigService, cache: CacheRepository):
        self.config = config
        self.cache = cache
    
    @abstractmethod
    async def process(self, operation: str, params: Dict[str, Any]) -> Any:
        """Process service operation."""
        pass
```

#### BaseRepository Interface
```python
class BaseRepository(ABC):
    """Abstract base class for all repositories."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve data by key."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store data with optional TTL."""
        pass
```

### Service Layer Components

#### Configuration Service
Centralized configuration management using Pydantic models:

```python
class CalculatorConfig(BaseSettings):
    """Main configuration model."""
    
    # Performance settings
    max_computation_time: int = 30
    max_memory_mb: int = 512
    cache_ttl_seconds: int = 3600
    
    # Feature toggles
    enable_currency_conversion: bool = False
    enable_advanced_calculus: bool = True
    enable_matrix_operations: bool = True
    
    # Tool filtering
    enabled_tool_groups: List[str] = ["basic", "advanced", "matrix"]
    
    # External APIs
    currency_api_key: Optional[str] = None
    currency_fallback_enabled: bool = True
    
    class Config:
        env_prefix = "CALC_"
        case_sensitive = False
```

#### Cache Service
Intelligent caching with TTL and memory management:

```python
class CacheService:
    """Service for managing computation caching."""
    
    def __init__(self, config: CalculatorConfig):
        self.config = config
        self.cache = {}
        self.access_times = {}
    
    async def get_or_compute(self, key: str, compute_func: Callable, ttl: int = None) -> Any:
        """Get cached result or compute and cache."""
        pass
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern."""
        pass
```

### Tool Registration Factory

The factory pattern will eliminate repetitive tool registration code:

```python
class ToolRegistrationFactory:
    """Factory for registering MCP tools with standardized patterns."""
    
    def __init__(self, server: FastMCP, config: ConfigService):
        self.server = server
        self.config = config
        self.registered_tools = {}
    
    def register_operation_tool(
        self,
        name: str,
        operation_class: Type[BaseOperation],
        description: str,
        input_schema: Type[BaseModel],
        tool_group: str = "basic"
    ) -> None:
        """Register a mathematical operation as an MCP tool."""
        
        if not self._is_tool_enabled(tool_group):
            return
            
        @self.server.tool(name=name, description=description)
        async def tool_handler(params: input_schema) -> Dict[str, Any]:
            try:
                operation = operation_class(
                    config=self.config,
                    cache=self.cache_service
                )
                return await operation.execute(params)
            except Exception as e:
                return self._handle_tool_error(e, name, params)
        
        self.registered_tools[name] = {
            "handler": tool_handler,
            "group": tool_group,
            "operation_class": operation_class
        }
```

### Strategy Patterns

#### Matrix Solver Strategies
Different algorithms for matrix operations based on matrix characteristics:

```python
class MatrixSolverStrategy(ABC):
    """Abstract strategy for matrix solving."""
    
    @abstractmethod
    def can_handle(self, matrix: np.ndarray) -> bool:
        """Check if strategy can handle this matrix."""
        pass
    
    @abstractmethod
    def solve(self, matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
        """Solve the matrix equation."""
        pass

class LUDecompositionStrategy(MatrixSolverStrategy):
    """LU decomposition strategy for general matrices."""
    pass

class CholeskyStrategy(MatrixSolverStrategy):
    """Cholesky decomposition for positive definite matrices."""
    pass

class MatrixSolverContext:
    """Context for selecting appropriate matrix solving strategy."""
    
    def __init__(self):
        self.strategies = [
            CholeskyStrategy(),
            LUDecompositionStrategy(),
            # ... other strategies
        ]
    
    def solve(self, matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
        """Select and execute appropriate solving strategy."""
        for strategy in self.strategies:
            if strategy.can_handle(matrix):
                return strategy.solve(matrix, vector)
        raise ValueError("No suitable strategy found for matrix")
```

### Repository Pattern Implementation

#### Cache Repository
```python
class CacheRepository(BaseRepository):
    """Repository for caching computed results."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.cache = {}
        self.metadata = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired."""
        if key not in self.cache:
            return None
            
        metadata = self.metadata[key]
        if time.time() > metadata['expires_at']:
            await self.delete(key)
            return None
            
        metadata['last_accessed'] = time.time()
        metadata['access_count'] += 1
        return self.cache[key]
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cached value with TTL."""
        if len(self.cache) >= self.max_size:
            await self._evict_lru()
            
        ttl = ttl or self.default_ttl
        self.cache[key] = value
        self.metadata[key] = {
            'created_at': time.time(),
            'expires_at': time.time() + ttl,
            'last_accessed': time.time(),
            'access_count': 1
        }
        return True
```

## Data Models

### Enhanced Request/Response Models

The existing Pydantic models will be extended with better validation and type safety:

```python
class CalculationRequest(BaseModel):
    """Base request model for all calculations."""
    
    operation: str
    precision: Optional[int] = Field(default=15, ge=1, le=50)
    cache_enabled: bool = True
    timeout_seconds: Optional[int] = Field(default=30, ge=1, le=300)

class MatrixOperationRequest(CalculationRequest):
    """Request model for matrix operations."""
    
    matrix_a: List[List[float]]
    matrix_b: Optional[List[List[float]]] = None
    operation_type: Literal["multiply", "inverse", "determinant", "eigenvalues"]
    
    @validator('matrix_a')
    def validate_matrix_a(cls, v):
        """Validate matrix structure and dimensions."""
        if not v or not all(isinstance(row, list) for row in v):
            raise ValueError("Matrix must be a list of lists")
        
        row_length = len(v[0])
        if not all(len(row) == row_length for row in v):
            raise ValueError("All matrix rows must have the same length")
        
        return v

class CalculationResponse(BaseModel):
    """Enhanced response model with metadata."""
    
    result: Any
    operation: str
    execution_time_ms: float
    cached: bool = False
    precision_used: int
    warnings: List[str] = []
    metadata: Dict[str, Any] = {}
```

### Configuration Models

```python
class PerformanceConfig(BaseModel):
    """Performance-related configuration."""
    
    max_computation_time: int = Field(default=30, ge=1, le=300)
    max_memory_mb: int = Field(default=512, ge=64, le=4096)
    cache_ttl_seconds: int = Field(default=3600, ge=60, le=86400)
    max_cache_size: int = Field(default=1000, ge=10, le=10000)

class FeatureConfig(BaseModel):
    """Feature toggle configuration."""
    
    enable_currency_conversion: bool = False
    enable_advanced_calculus: bool = True
    enable_matrix_operations: bool = True
    enable_caching: bool = True
    enable_performance_monitoring: bool = True

class SecurityConfig(BaseModel):
    """Security-related configuration."""
    
    max_input_size: int = Field(default=10000, ge=100, le=100000)
    allowed_operations: Set[str] = set()
    rate_limit_per_minute: int = Field(default=1000, ge=1, le=10000)
```

## Error Handling

### Standardized Error Handling System

A comprehensive error handling system with decorators and consistent patterns:

```python
class CalculatorError(Exception):
    """Base exception for calculator operations."""
    
    def __init__(self, message: str, operation: str = None, context: Dict = None):
        self.message = message
        self.operation = operation
        self.context = context or {}
        super().__init__(message)

class ValidationError(CalculatorError):
    """Raised when input validation fails."""
    pass

class ComputationError(CalculatorError):
    """Raised when mathematical computation fails."""
    pass

class TimeoutError(CalculatorError):
    """Raised when operation exceeds time limit."""
    pass

def handle_operation_errors(operation_name: str):
    """Decorator for standardized error handling."""
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                
                return {
                    "success": True,
                    "result": result,
                    "execution_time_ms": execution_time,
                    "operation": operation_name
                }
                
            except ValidationError as e:
                logger.warning(f"Validation error in {operation_name}: {e.message}")
                return {
                    "success": False,
                    "error": "validation_error",
                    "message": e.message,
                    "operation": operation_name,
                    "suggestions": _get_validation_suggestions(e)
                }
                
            except ComputationError as e:
                logger.error(f"Computation error in {operation_name}: {e.message}")
                return {
                    "success": False,
                    "error": "computation_error",
                    "message": e.message,
                    "operation": operation_name,
                    "context": e.context
                }
                
            except Exception as e:
                logger.error(f"Unexpected error in {operation_name}: {str(e)}")
                return {
                    "success": False,
                    "error": "internal_error",
                    "message": "An unexpected error occurred",
                    "operation": operation_name
                }
        
        return wrapper
    return decorator
```

### Error Recovery Strategies

```python
class ErrorRecoveryService:
    """Service for handling error recovery and fallbacks."""
    
    def __init__(self, config: CalculatorConfig):
        self.config = config
        self.fallback_strategies = {}
    
    async def execute_with_fallback(
        self,
        primary_func: Callable,
        fallback_funcs: List[Callable],
        operation_name: str
    ) -> Any:
        """Execute operation with fallback strategies."""
        
        errors = []
        
        # Try primary function
        try:
            return await primary_func()
        except Exception as e:
            errors.append(f"Primary: {str(e)}")
            logger.warning(f"Primary method failed for {operation_name}: {e}")
        
        # Try fallback functions
        for i, fallback_func in enumerate(fallback_funcs):
            try:
                result = await fallback_func()
                logger.info(f"Fallback {i+1} succeeded for {operation_name}")
                return result
            except Exception as e:
                errors.append(f"Fallback {i+1}: {str(e)}")
                logger.warning(f"Fallback {i+1} failed for {operation_name}: {e}")
        
        # All methods failed
        raise ComputationError(
            f"All methods failed for {operation_name}",
            operation=operation_name,
            context={"errors": errors}
        )
```

## Testing Strategy

### Comprehensive Testing Architecture

The testing strategy will ensure all refactored components work correctly:

#### Unit Testing Structure
```python
# Test structure mirrors source structure
tests/
├── unit/
│   ├── services/
│   │   ├── test_arithmetic_service.py
│   │   ├── test_matrix_service.py
│   │   └── test_calculus/
│   │       ├── test_derivatives.py
│   │       ├── test_integrals.py
│   │       └── ...
│   ├── repositories/
│   │   ├── test_cache_repository.py
│   │   └── test_constants_repository.py
│   ├── strategies/
│   │   ├── test_matrix_strategies.py
│   │   └── test_numerical_strategies.py
│   └── core/
│       ├── test_base_classes.py
│       └── test_error_handling.py
├── integration/
│   ├── test_service_integration.py
│   ├── test_tool_registration.py
│   └── test_end_to_end.py
├── performance/
│   ├── test_cache_performance.py
│   ├── test_computation_performance.py
│   └── benchmarks.py
└── fixtures/
    ├── matrix_data.py
    ├── calculation_data.py
    └── config_fixtures.py
```

#### Test Base Classes
```python
class BaseServiceTest:
    """Base class for service tests."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing."""
        return CalculatorConfig(
            max_computation_time=5,
            cache_ttl_seconds=60,
            enable_caching=True
        )
    
    @pytest.fixture
    def mock_cache(self):
        """Mock cache repository for testing."""
        return AsyncMock(spec=CacheRepository)
    
    @pytest.fixture
    def service(self, mock_config, mock_cache):
        """Create service instance for testing."""
        return self.service_class(config=mock_config, cache=mock_cache)

class BaseIntegrationTest:
    """Base class for integration tests."""
    
    @pytest.fixture
    async def app(self):
        """Create test application instance."""
        config = CalculatorConfig(enable_caching=False)  # Disable caching for tests
        app = create_test_app(config)
        yield app
        await app.cleanup()
```

#### Performance Testing
```python
class PerformanceTestSuite:
    """Performance testing for refactored components."""
    
    @pytest.mark.performance
    async def test_cache_performance(self):
        """Test cache hit/miss performance."""
        cache = CacheRepository(max_size=1000)
        
        # Measure cache set performance
        start_time = time.time()
        for i in range(1000):
            await cache.set(f"key_{i}", f"value_{i}")
        set_time = time.time() - start_time
        
        # Measure cache get performance
        start_time = time.time()
        for i in range(1000):
            await cache.get(f"key_{i}")
        get_time = time.time() - start_time
        
        assert set_time < 1.0  # Should complete in under 1 second
        assert get_time < 0.1  # Should complete in under 100ms
    
    @pytest.mark.performance
    async def test_matrix_operation_performance(self):
        """Test matrix operation performance improvements."""
        service = MatrixService(config=test_config, cache=test_cache)
        
        # Test with different matrix sizes
        for size in [10, 50, 100]:
            matrix = np.random.rand(size, size)
            
            start_time = time.time()
            result = await service.calculate_determinant(matrix)
            execution_time = time.time() - start_time
            
            # Performance requirements based on matrix size
            max_time = size * 0.01  # 10ms per dimension
            assert execution_time < max_time
```

## Design Decisions and Rationales

### 1. Layered Architecture Choice
**Decision:** Implement a 4-layer architecture (Server, Service, Repository, Core)
**Rationale:** 
- Separates concerns clearly between presentation, business logic, data access, and core utilities
- Enables independent testing of each layer
- Supports dependency injection and loose coupling
- Facilitates future extensions and modifications

### 2. Strategy Pattern for Complex Operations
**Decision:** Use strategy patterns for matrix operations and numerical methods
**Rationale:**
- Allows selection of optimal algorithms based on input characteristics
- Enables easy addition of new algorithms without modifying existing code
- Improves performance by choosing the most efficient method for each case
- Supports A/B testing of different algorithmic approaches

### 3. Repository Pattern for Data Access
**Decision:** Implement repository pattern for caching, constants, and external data
**Rationale:**
- Abstracts data access logic from business logic
- Enables easy swapping of storage backends (memory, file, database)
- Supports consistent caching strategies across all data types
- Facilitates testing with mock repositories

### 4. Factory Pattern for Tool Registration
**Decision:** Create a factory for MCP tool registration
**Rationale:**
- Eliminates 60%+ of repetitive boilerplate code
- Ensures consistent error handling and logging across all tools
- Supports dynamic tool filtering based on configuration
- Simplifies addition of new mathematical operations

### 5. Pydantic for Configuration Management
**Decision:** Use Pydantic models for all configuration
**Rationale:**
- Provides automatic validation and type conversion
- Generates clear error messages for invalid configuration
- Supports environment variable loading with type safety
- Enables configuration documentation through model schemas

### 6. Async/Await Throughout
**Decision:** Maintain async patterns throughout the refactored codebase
**Rationale:**
- Preserves compatibility with existing FastMCP async patterns
- Enables non-blocking operations for expensive computations
- Supports concurrent request handling
- Allows for future integration with async external APIs

### 7. Modular Calculus Split
**Decision:** Split calculus.py into focused modules (derivatives, integrals, limits, series, numerical)
**Rationale:**
- Reduces individual file size from 800+ lines to <200 lines each
- Groups related functionality together
- Enables independent development and testing of each calculus area
- Improves code navigation and maintenance

### 8. Centralized Error Handling
**Decision:** Implement decorator-based error handling with custom exception hierarchy
**Rationale:**
- Ensures consistent error responses across all operations
- Reduces error handling code duplication
- Provides structured logging with operation context
- Enables error recovery strategies and fallback mechanisms

### 9. Performance Monitoring Integration
**Decision:** Build monitoring and metrics collection into the core architecture
**Rationale:**
- Enables identification of performance bottlenecks
- Supports optimization decisions with real data
- Provides insights into cache effectiveness and usage patterns
- Facilitates capacity planning and resource optimization

### 10. Backward Compatibility Preservation
**Decision:** Maintain all existing MCP tool interfaces unchanged
**Rationale:**
- Ensures zero-disruption migration for existing users
- Allows gradual adoption of new features
- Reduces risk of breaking existing integrations
- Supports A/B testing of old vs new implementations