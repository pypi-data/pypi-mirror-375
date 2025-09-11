# API Reference - Scientific Calculator MCP Server v2.0.0

## Overview

The Scientific Calculator MCP Server v2.0.0 provides **68 comprehensive mathematical tools** across **11 specialized domains** through the Model Context Protocol (MCP). This reference documents all available tools, their parameters, and expected responses.

## Tool Categories (68 Tools Total)

- [Basic Arithmetic (8 tools)](#basic-arithmetic-8-tools) - Always Enabled
- [Advanced Mathematics (5 tools)](#advanced-mathematics-5-tools) - Optional
- [Statistics & Probability (5 tools)](#statistics--probability-5-tools) - Optional
- [Matrix Operations (8 tools)](#matrix-operations-8-tools) - Optional
- [Complex Numbers (6 tools)](#complex-numbers-6-tools) - Optional
- [Unit Conversion (7 tools)](#unit-conversion-7-tools) - Optional
- [Calculus Operations (9 tools)](#calculus-operations-9-tools) - Optional
- [Equation Solving (6 tools)](#equation-solving-6-tools) - Optional
- [Financial Mathematics (7 tools)](#financial-mathematics-7-tools) - Optional
- [Currency Conversion (4 tools)](#currency-conversion-4-tools) - Optional & Privacy-Controlled
- [Constants & References (3 tools)](#constants--references-3-tools) - Optional

## Tool Group Configuration

By default, only **Basic Arithmetic** (16 tools) is enabled. Enable additional groups with environment variables:

```bash
CALCULATOR_ENABLE_ALL=true                # All 70 tools
CALCULATOR_ENABLE_SCIENTIFIC=true         # Scientific computing preset
CALCULATOR_ENABLE_BUSINESS=true           # Business/finance preset
CALCULATOR_ENABLE_ENGINEERING=true        # Engineering preset

# Or enable individual groups:
CALCULATOR_ENABLE_ADVANCED=true           # 5 tools
CALCULATOR_ENABLE_STATISTICS=true         # 6 tools
CALCULATOR_ENABLE_MATRIX=true             # 6 tools
# ... etc
```

## Basic Arithmetic (16 tools)

**Always Enabled** - Core mathematical operations that form the foundation of all calculations.

### Core Operations

#### `add`
Add two numbers with high precision.

**Parameters:**
```json
{
  "a": 15.7,
  "b": 23.8
}
```

**Response:**
```json
{
  "result": 39.5,
  "operation": "add",
  "precision": 15
}
```

#### `subtract`
Subtract two numbers with high precision.

**Parameters:**
```json
{
  "a": 10,
  "b": 3
}
```

**Response:**
```json
{
  "result": 7.0,
  "operation": "subtract"
}
```

#### `multiply`
Multiply two numbers with high precision.

**Parameters:**
```json
{
  "a": 2.5,
  "b": 4.0
}
```

**Response:**
```json
{
  "result": 10.0,
  "operation": "multiply"
}
```

#### `divide`
Divide two numbers with high precision.

**Parameters:**
```json
{
  "a": 10,
  "b": 2
}
```

**Response:**
```json
{
  "result": 5.0,
  "operation": "divide"
}
```

**Error Cases:**
```json
// Division by zero
{"a": 10, "b": 0} → {"error": "Division by zero"}
```

#### `subtract`
Subtract two numbers.

**Parameters:**
```json
{
  "a": 10,
  "b": 3
}
```

**Response:**
```json
{
  "result": 7.0,
  "operation": "subtract"
}
```

#### `multiply`
Multiply multiple numbers together.

**Parameters:**
```json
{
  "numbers": [2, 3, 4]
}
```

**Response:**
```json
{
  "result": 24.0,
  "operation": "multiply",
  "input_count": 3
}
```

#### `divide`
Divide two numbers.

**Parameters:**
```json
{
  "a": 10,
  "b": 2
}
```

**Response:**
```json
{
  "result": 5.0,
  "operation": "divide"
}
```

**Error Cases:**
```json
// Division by zero
{"a": 10, "b": 0} → {"error": "Division by zero"}
```

### Advanced Arithmetic

#### `power`
Raise a number to a power.

**Parameters:**
```json
{
  "base": 2,
  "exponent": 3
}
```

**Response:**
```json
{
  "result": 8.0,
  "operation": "power"
}
```

#### `sqrt`
Calculate square root.

**Parameters:**
```json
{
  "number": 16
}
```

**Response:**
```json
{
  "result": 4.0,
  "operation": "sqrt"
}
```

#### `factorial`
Calculate factorial of a number.

**Parameters:**
```json
{
  "number": 5
}
```

**Response:**
```json
{
  "result": 120,
  "operation": "factorial"
}
```

**Constraints:**
- Input must be non-negative integer
- Maximum input: 1000

#### `gcd`
Calculate greatest common divisor.

**Parameters:**
```json
{
  "numbers": [12, 18, 24]
}
```

**Response:**
```json
{
  "result": 6,
  "operation": "gcd"
}
```

#### `lcm`
Calculate least common multiple.

**Parameters:**
```json
{
  "numbers": [4, 6, 8]
}
```

**Response:**
```json
{
  "result": 24,
  "operation": "lcm"
}
```

### Trigonometric Functions

#### `sine`
Calculate sine of an angle.

**Parameters:**
```json
{
  "angle": 1.5708,
  "unit": "radians"
}
```

**Response:**
```json
{
  "result": 1.0,
  "operation": "sine",
  "unit": "radians"
}
```

**Units:** `"radians"` (default) or `"degrees"`

#### `cosine`
Calculate cosine of an angle.

**Parameters:**
```json
{
  "angle": 0,
  "unit": "radians"
}
```

**Response:**
```json
{
  "result": 1.0,
  "operation": "cosine",
  "unit": "radians"
}
```

#### `tangent`
Calculate tangent of an angle.

**Parameters:**
```json
{
  "angle": 0.7854,
  "unit": "radians"
}
```

**Response:**
```json
{
  "result": 1.0,
  "operation": "tangent",
  "unit": "radians"
}
```

### Inverse Trigonometric Functions

#### `arcsine`
Calculate arcsine (inverse sine).

**Parameters:**
```json
{
  "value": 0.5,
  "unit": "radians"
}
```

**Response:**
```json
{
  "result": 0.5236,
  "operation": "arcsine",
  "unit": "radians"
}
```

#### `arccosine`
Calculate arccosine (inverse cosine).

**Parameters:**
```json
{
  "value": 0.5,
  "unit": "radians"
}
```

**Response:**
```json
{
  "result": 1.0472,
  "operation": "arccosine",
  "unit": "radians"
}
```

#### `arctangent`
Calculate arctangent (inverse tangent).

**Parameters:**
```json
{
  "value": 1.0,
  "unit": "radians"
}
```

**Response:**
```json
{
  "result": 0.7854,
  "operation": "arctangent",
  "unit": "radians"
}
```

### Logarithmic Functions

#### `logarithm`
Calculate logarithm with specified base.

**Parameters:**
```json
{
  "number": 8,
  "base": 2
}
```

**Response:**
```json
{
  "result": 3.0,
  "operation": "logarithm",
  "base": 2
}
```

**Special Bases:**
- `base: "e"` - Natural logarithm
- `base: 10` - Common logarithm (default)

#### `exponential`
Calculate exponential function (e^x).

**Parameters:**
```json
{
  "exponent": 2
}
```

**Response:**
```json
{
  "result": 7.389,
  "operation": "exponential"
}
```

## Matrix Operations

### Basic Matrix Operations

#### `matrix_add`
Add two matrices.

**Parameters:**
```json
{
  "matrix_a": [[1, 2], [3, 4]],
  "matrix_b": [[5, 6], [7, 8]]
}
```

**Response:**
```json
{
  "result": [[6, 8], [10, 12]],
  "operation": "matrix_add",
  "dimensions": [2, 2]
}
```

#### `matrix_subtract`
Subtract two matrices.

**Parameters:**
```json
{
  "matrix_a": [[5, 6], [7, 8]],
  "matrix_b": [[1, 2], [3, 4]]
}
```

**Response:**
```json
{
  "result": [[4, 4], [4, 4]],
  "operation": "matrix_subtract",
  "dimensions": [2, 2]
}
```

#### `matrix_multiply`
Multiply two matrices.

**Parameters:**
```json
{
  "matrix_a": [[1, 2], [3, 4]],
  "matrix_b": [[5, 6], [7, 8]]
}
```

**Response:**
```json
{
  "result": [[19, 22], [43, 50]],
  "operation": "matrix_multiply",
  "result_dimensions": [2, 2]
}
```

#### `matrix_transpose`
Transpose a matrix.

**Parameters:**
```json
{
  "matrix": [[1, 2, 3], [4, 5, 6]]
}
```

**Response:**
```json
{
  "result": [[1, 4], [2, 5], [3, 6]],
  "operation": "matrix_transpose",
  "original_dimensions": [2, 3],
  "result_dimensions": [3, 2]
}
```

### Matrix Properties

#### `matrix_determinant`
Calculate matrix determinant.

**Parameters:**
```json
{
  "matrix": [[1, 2], [3, 4]]
}
```

**Response:**
```json
{
  "result": -2.0,
  "operation": "matrix_determinant",
  "dimensions": [2, 2]
}
```

**Constraints:**
- Matrix must be square
- Maximum size: 1000x1000

#### `matrix_trace`
Calculate matrix trace (sum of diagonal elements).

**Parameters:**
```json
{
  "matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
}
```

**Response:**
```json
{
  "result": 15.0,
  "operation": "matrix_trace",
  "dimensions": [3, 3]
}
```

#### `matrix_rank`
Calculate matrix rank.

**Parameters:**
```json
{
  "matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
}
```

**Response:**
```json
{
  "result": 2,
  "operation": "matrix_rank",
  "dimensions": [3, 3]
}
```

#### `matrix_norm`
Calculate matrix norm.

**Parameters:**
```json
{
  "matrix": [[1, 2], [3, 4]],
  "norm_type": "frobenius"
}
```

**Response:**
```json
{
  "result": 5.477,
  "operation": "matrix_norm",
  "norm_type": "frobenius"
}
```

**Norm Types:**
- `"frobenius"` - Frobenius norm (default)
- `"1"` - 1-norm (maximum column sum)
- `"2"` - 2-norm (spectral norm)
- `"inf"` - Infinity norm (maximum row sum)

### Advanced Matrix Operations

#### `matrix_inverse`
Calculate matrix inverse.

**Parameters:**
```json
{
  "matrix": [[1, 2], [3, 4]]
}
```

**Response:**
```json
{
  "result": [[-2.0, 1.0], [1.5, -0.5]],
  "operation": "matrix_inverse",
  "determinant": -2.0
}
```

**Error Cases:**
```json
// Singular matrix
{"matrix": [[1, 2], [2, 4]]} → {"error": "Matrix is singular"}
```

#### `matrix_eigenvalues`
Calculate matrix eigenvalues.

**Parameters:**
```json
{
  "matrix": [[1, 2], [2, 1]]
}
```

**Response:**
```json
{
  "result": [3.0, -1.0],
  "operation": "matrix_eigenvalues",
  "dimensions": [2, 2]
}
```

#### `matrix_eigenvectors`
Calculate matrix eigenvalues and eigenvectors.

**Parameters:**
```json
{
  "matrix": [[1, 2], [2, 1]]
}
```

**Response:**
```json
{
  "result": {
    "eigenvalues": [3.0, -1.0],
    "eigenvectors": [[0.7071, 0.7071], [0.7071, -0.7071]]
  },
  "operation": "matrix_eigenvectors"
}
```

### Matrix Decompositions

#### `matrix_lu_decomposition`
Perform LU decomposition.

**Parameters:**
```json
{
  "matrix": [[2, 1], [1, 1]]
}
```

**Response:**
```json
{
  "result": {
    "P": [[1, 0], [0, 1]],
    "L": [[1, 0], [0.5, 1]],
    "U": [[2, 1], [0, 0.5]]
  },
  "operation": "matrix_lu_decomposition"
}
```

#### `matrix_qr_decomposition`
Perform QR decomposition.

**Parameters:**
```json
{
  "matrix": [[1, 1], [1, 0], [0, 1]]
}
```

**Response:**
```json
{
  "result": {
    "Q": [[-0.7071, 0.4082], [-0.7071, -0.4082], [0, 0.8165]],
    "R": [[-1.4142, -0.7071], [0, 1.2247]]
  },
  "operation": "matrix_qr_decomposition"
}
```

#### `matrix_svd`
Perform Singular Value Decomposition.

**Parameters:**
```json
{
  "matrix": [[1, 2], [3, 4], [5, 6]]
}
```

**Response:**
```json
{
  "result": {
    "U": [[-0.2298, 0.8835], [-0.5247, 0.2408], [-0.8196, -0.4019]],
    "S": [9.5255, 0.5143],
    "Vt": [[-0.6196, -0.7849], [-0.7849, 0.6196]]
  },
  "operation": "matrix_svd"
}
```

### Linear Systems

#### `solve_linear_system`
Solve linear system Ax = b.

**Parameters:**
```json
{
  "matrix_a": [[2, 1], [1, 1]],
  "vector_b": [3, 2]
}
```

**Response:**
```json
{
  "result": [1.0, 1.0],
  "operation": "solve_linear_system",
  "method": "lu_decomposition"
}
```

## Statistical Operations

### Descriptive Statistics

#### `mean`
Calculate arithmetic mean.

**Parameters:**
```json
{
  "data": [1, 2, 3, 4, 5]
}
```

**Response:**
```json
{
  "result": 3.0,
  "operation": "mean",
  "count": 5
}
```

#### `median`
Calculate median value.

**Parameters:**
```json
{
  "data": [1, 2, 3, 4, 5]
}
```

**Response:**
```json
{
  "result": 3.0,
  "operation": "median",
  "count": 5
}
```

#### `mode`
Calculate mode (most frequent value).

**Parameters:**
```json
{
  "data": [1, 2, 2, 3, 4]
}
```

**Response:**
```json
{
  "result": 2,
  "operation": "mode",
  "frequency": 2
}
```

**Multiple Modes:**
```json
{
  "result": [1, 2],
  "operation": "mode",
  "frequency": 2,
  "multimodal": true
}
```

#### `variance`
Calculate variance.

**Parameters:**
```json
{
  "data": [1, 2, 3, 4, 5],
  "population": false
}
```

**Response:**
```json
{
  "result": 2.5,
  "operation": "variance",
  "type": "sample",
  "count": 5
}
```

**Parameters:**
- `population`: `true` for population variance, `false` for sample variance (default)

#### `std_dev`
Calculate standard deviation.

**Parameters:**
```json
{
  "data": [1, 2, 3, 4, 5],
  "population": false
}
```

**Response:**
```json
{
  "result": 1.5811,
  "operation": "std_dev",
  "type": "sample",
  "variance": 2.5
}
```

#### `range`
Calculate range statistics.

**Parameters:**
```json
{
  "data": [1, 2, 3, 4, 5]
}
```

**Response:**
```json
{
  "result": {
    "min": 1,
    "max": 5,
    "range": 4
  },
  "operation": "range"
}
```

#### `quartiles`
Calculate quartiles and IQR.

**Parameters:**
```json
{
  "data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
}
```

**Response:**
```json
{
  "result": {
    "Q1": 3.25,
    "Q2": 5.5,
    "Q3": 7.75,
    "IQR": 4.5
  },
  "operation": "quartiles"
}
```

#### `percentile`
Calculate specific percentile.

**Parameters:**
```json
{
  "data": [1, 2, 3, 4, 5],
  "percentile": 90
}
```

**Response:**
```json
{
  "result": 4.6,
  "operation": "percentile",
  "percentile": 90
}
```

### Correlation and Regression

#### `correlation`
Calculate Pearson correlation coefficient.

**Parameters:**
```json
{
  "x_data": [1, 2, 3, 4, 5],
  "y_data": [2, 4, 6, 8, 10]
}
```

**Response:**
```json
{
  "result": 1.0,
  "operation": "correlation",
  "type": "pearson",
  "strength": "perfect_positive"
}
```

#### `covariance`
Calculate covariance between two datasets.

**Parameters:**
```json
{
  "x_data": [1, 2, 3, 4, 5],
  "y_data": [2, 4, 6, 8, 10]
}
```

**Response:**
```json
{
  "result": 5.0,
  "operation": "covariance",
  "count": 5
}
```

### Statistical Tests

#### `t_test`
Perform t-test.

**Parameters:**
```json
{
  "type": "one_sample",
  "data": [1, 2, 3, 4, 5],
  "population_mean": 2.5
}
```

**Response:**
```json
{
  "result": {
    "t_statistic": 1.0,
    "p_value": 0.374,
    "degrees_of_freedom": 4,
    "critical_value": 2.776
  },
  "operation": "t_test",
  "type": "one_sample"
}
```

**Two-Sample T-Test:**
```json
{
  "type": "two_sample",
  "data1": [1, 2, 3, 4, 5],
  "data2": [2, 3, 4, 5, 6],
  "equal_var": true
}
```

#### `anova`
Perform one-way ANOVA.

**Parameters:**
```json
{
  "groups": [
    [1, 2, 3, 4, 5],
    [2, 3, 4, 5, 6],
    [3, 4, 5, 6, 7]
  ]
}
```

**Response:**
```json
{
  "result": {
    "f_statistic": 6.0,
    "p_value": 0.015,
    "degrees_of_freedom": [2, 12],
    "critical_value": 3.885
  },
  "operation": "anova",
  "groups": 3
}
```

## Calculus Operations

### Derivatives

#### `derivative`
Calculate symbolic derivative.

**Parameters:**
```json
{
  "expression": "x^2 + 2*x + 1",
  "variable": "x"
}
```

**Response:**
```json
{
  "result": "2*x + 2",
  "operation": "derivative",
  "variable": "x",
  "order": 1
}
```

**Higher-Order Derivatives:**
```json
{
  "expression": "x^3 + 2*x^2 + x",
  "variable": "x",
  "order": 2
}
```

#### `numerical_derivative`
Calculate numerical derivative at a point.

**Parameters:**
```json
{
  "expression": "x^2 + 2*x + 1",
  "variable": "x",
  "point": 2,
  "method": "central"
}
```

**Response:**
```json
{
  "result": 6.0,
  "operation": "numerical_derivative",
  "point": 2,
  "method": "central",
  "step_size": 1e-5
}
```

**Methods:**
- `"central"` - Central difference (default, most accurate)
- `"forward"` - Forward difference
- `"backward"` - Backward difference

### Integrals

#### `integral`
Calculate symbolic integral.

**Parameters:**
```json
{
  "expression": "2*x + 1",
  "variable": "x"
}
```

**Response:**
```json
{
  "result": "x^2 + x + C",
  "operation": "integral",
  "variable": "x",
  "type": "indefinite"
}
```

**Definite Integral:**
```json
{
  "expression": "2*x + 1",
  "variable": "x",
  "lower_limit": 0,
  "upper_limit": 2
}
```

**Response:**
```json
{
  "result": 6.0,
  "operation": "integral",
  "type": "definite",
  "limits": [0, 2]
}
```

#### `numerical_integral`
Calculate numerical integral.

**Parameters:**
```json
{
  "expression": "sin(x)",
  "variable": "x",
  "lower_limit": 0,
  "upper_limit": 3.14159,
  "method": "simpson"
}
```

**Response:**
```json
{
  "result": 2.0,
  "operation": "numerical_integral",
  "method": "simpson",
  "intervals": 1000,
  "error_estimate": 1e-10
}
```

**Methods:**
- `"simpson"` - Simpson's rule (default)
- `"trapezoidal"` - Trapezoidal rule
- `"gaussian"` - Gaussian quadrature

### Limits

#### `limit`
Calculate symbolic limit.

**Parameters:**
```json
{
  "expression": "(sin(x))/x",
  "variable": "x",
  "point": 0,
  "direction": "both"
}
```

**Response:**
```json
{
  "result": 1,
  "operation": "limit",
  "point": 0,
  "direction": "both"
}
```

**Directions:**
- `"both"` - Two-sided limit (default)
- `"left"` - Left-sided limit
- `"right"` - Right-sided limit

**Infinite Limits:**
```json
{
  "expression": "1/x",
  "variable": "x",
  "point": "infinity"
}
```

### Series Expansions

#### `taylor_series`
Calculate Taylor series expansion.

**Parameters:**
```json
{
  "expression": "sin(x)",
  "variable": "x",
  "point": 0,
  "order": 5
}
```

**Response:**
```json
{
  "result": "x - x^3/6 + x^5/120 + O(x^6)",
  "operation": "taylor_series",
  "center": 0,
  "order": 5
}
```

#### `series_expansion`
General series expansion.

**Parameters:**
```json
{
  "expression": "1/(1-x)",
  "variable": "x",
  "point": 0,
  "order": 4,
  "type": "power"
}
```

**Response:**
```json
{
  "result": "1 + x + x^2 + x^3 + x^4 + O(x^5)",
  "operation": "series_expansion",
  "type": "power",
  "convergence_radius": 1
}
```

## Utility Operations

### Mathematical Constants

#### `get_constant`
Retrieve mathematical or physical constants.

**Parameters:**
```json
{
  "name": "pi"
}
```

**Response:**
```json
{
  "result": 3.141592653589793,
  "operation": "get_constant",
  "name": "pi",
  "description": "Ratio of circle circumference to diameter"
}
```

**Available Constants:**
- `"pi"` - π (3.14159...)
- `"e"` - Euler's number (2.71828...)
- `"tau"` - τ = 2π (6.28318...)
- `"phi"` - Golden ratio (1.61803...)
- `"c"` - Speed of light (299792458 m/s)
- `"h"` - Planck constant (6.62607e-34 J⋅s)
- `"k"` - Boltzmann constant (1.38065e-23 J/K)
- `"na"` - Avogadro's number (6.02214e23 mol⁻¹)
- `"g"` - Standard gravity (9.80665 m/s²)

#### `list_constants`
List all available constants.

**Parameters:**
```json
{}
```

**Response:**
```json
{
  "result": {
    "mathematical": ["pi", "e", "tau", "phi"],
    "physical": ["c", "h", "k", "na", "g"],
    "total_count": 9
  },
  "operation": "list_constants"
}
```

### Unit Conversions

#### `convert_units`
Convert between different units.

**Parameters:**
```json
{
  "value": 100,
  "from_unit": "celsius",
  "to_unit": "fahrenheit"
}
```

**Response:**
```json
{
  "result": 212.0,
  "operation": "convert_units",
  "from_unit": "celsius",
  "to_unit": "fahrenheit",
  "conversion_factor": "°F = °C × 9/5 + 32"
}
```

**Supported Unit Categories:**
- **Length**: meter, kilometer, centimeter, millimeter, inch, foot, yard, mile
- **Weight**: gram, kilogram, pound, ounce, ton
- **Temperature**: celsius, fahrenheit, kelvin
- **Time**: second, minute, hour, day, week, month, year
- **Energy**: joule, calorie, kilocalorie, watt_hour, kilowatt_hour
- **Pressure**: pascal, bar, atmosphere, psi, torr
- **Volume**: liter, milliliter, gallon, quart, pint, cup, fluid_ounce

### Currency Conversion (Optional)

#### `convert_currency`
Convert between currencies (requires API key).

**Parameters:**
```json
{
  "amount": 100,
  "from_currency": "USD",
  "to_currency": "EUR"
}
```

**Response:**
```json
{
  "result": 85.23,
  "operation": "convert_currency",
  "from_currency": "USD",
  "to_currency": "EUR",
  "exchange_rate": 0.8523,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Note:** Currency conversion is disabled by default. Enable with:
```bash
export CALC_FEATURE_ENABLE_CURRENCY_CONVERSION=true
export CALC_EXTERNAL_APIS_CURRENCY_API_KEY=your_api_key
```

### System Information

#### `health_check`
Check system health and status.

**Parameters:**
```json
{}
```

**Response:**
```json
{
  "result": {
    "status": "healthy",
    "services": {
      "arithmetic": "available",
      "matrix": "available",
      "statistics": "available",
      "calculus": "available"
    },
    "performance": {
      "cache_hit_rate": 0.85,
      "average_response_time": 0.023,
      "total_operations": 1547
    },
    "uptime": 3600
  },
  "operation": "health_check"
}
```

#### `calculator_info`
Get calculator information and capabilities.

**Parameters:**
```json
{}
```

**Response:**
```json
{
  "result": {
    "name": "Scientific Calculator MCP Server",
    "version": "2.0.0",
    "capabilities": {
      "arithmetic": true,
      "matrix": true,
      "statistics": true,
      "calculus": true,
      "currency_conversion": false
    },
    "limits": {
      "max_array_length": 10000,
      "max_matrix_size": 1000,
      "max_computation_time": 30
    },
    "tool_count": 67
  },
  "operation": "calculator_info"
}
```

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "error": {
    "type": "ValidationError",
    "message": "Invalid input parameter",
    "field": "numbers",
    "details": {
      "provided": "not_a_number",
      "expected": "array of numbers"
    },
    "operation": "add",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Error Types

#### `ValidationError`
Input validation failed.

**Common Causes:**
- Missing required parameters
- Invalid parameter types
- Values outside allowed ranges
- Malformed data structures

**Example:**
```json
{
  "error": {
    "type": "ValidationError",
    "message": "Array length 15000 exceeds maximum allowed length 10000",
    "field": "numbers"
  }
}
```

#### `ComputationError`
Mathematical computation failed.

**Common Causes:**
- Division by zero
- Square root of negative number
- Matrix singularity
- Numerical overflow/underflow

**Example:**
```json
{
  "error": {
    "type": "ComputationError",
    "message": "Matrix is singular and cannot be inverted",
    "operation": "matrix_inverse"
  }
}
```

#### `TimeoutError`
Operation exceeded time limit.

**Example:**
```json
{
  "error": {
    "type": "TimeoutError",
    "message": "Operation exceeded maximum computation time of 30 seconds",
    "operation": "matrix_eigenvalues"
  }
}
```

#### `SecurityError`
Security validation failed.

**Common Causes:**
- Rate limit exceeded
- Input size too large
- Forbidden expressions
- Suspicious activity detected

**Example:**
```json
{
  "error": {
    "type": "SecurityError",
    "message": "Rate limit exceeded: 2000/2000 requests in 60 seconds",
    "retry_after": 45
  }
}
```

## Rate Limits and Constraints

### Default Limits

- **Requests per minute**: 2000
- **Concurrent operations**: 50
- **Maximum input size**: 50KB
- **Maximum array length**: 10,000 elements
- **Maximum matrix size**: 1000×1000
- **Maximum computation time**: 30 seconds
- **Maximum memory per operation**: 100MB

### Adjusting Limits

Limits can be adjusted via environment variables:

```bash
export CALC_SECURITY_RATE_LIMIT_PER_MINUTE=5000
export CALC_SECURITY_MAX_CONCURRENT_OPERATIONS=100
export CALC_SECURITY_MAX_INPUT_SIZE=100000
export CALC_SECURITY_MAX_ARRAY_LENGTH=20000
export CALC_SECURITY_MAX_MATRIX_SIZE=2000
export CALC_PERF_MAX_COMPUTATION_TIME_SECONDS=60
export CALC_PERF_MAX_MEMORY_MB=200
```

## Performance Considerations

### Caching

Results are automatically cached for expensive operations:

- **Cache TTL**: 1 hour (configurable)
- **Cache size**: 1000 entries (configurable)
- **Cache key**: Based on operation and parameters
- **Cache hit rate**: Typically 70-90%

### Algorithm Selection

The calculator automatically selects optimal algorithms:

- **Matrix operations**: LU, QR, SVD, or Cholesky based on matrix properties
- **Numerical integration**: Simpson's rule, Gaussian quadrature, or adaptive methods
- **Statistical calculations**: Optimized for data size and distribution

### Memory Management

- **Lazy loading**: Modules loaded on demand
- **Memory limits**: Per-operation memory constraints
- **Garbage collection**: Automatic cleanup of large intermediate results
- **Resource monitoring**: Continuous memory usage tracking

## Authentication and Security

### Input Validation

All inputs are validated for:

- **Type safety**: Correct data types
- **Range validation**: Values within acceptable limits
- **Size limits**: Arrays and matrices within size constraints
- **Content filtering**: Mathematical expressions checked for safety

### Security Features

- **Rate limiting**: Per-client request limits
- **Input sanitization**: Automatic cleaning of potentially dangerous input
- **Audit logging**: All operations logged for security monitoring
- **Error handling**: No sensitive information in error messages

### Privacy

- **No data persistence**: Results not stored permanently
- **Minimal logging**: Only essential information logged
- **No external dependencies**: Core operations work offline
- **Optional features**: External APIs (currency) disabled by default

This API reference provides comprehensive documentation for all calculator operations. For implementation examples and advanced usage patterns, refer to the [Examples Guide](examples.md) and [Developer Guide](DEVELOPER_GUIDE.md).

## Related Documentation

- **[Installation Guide](installation.md)** - Setup and installation instructions
- **[Configuration Guide](configuration.md)** - Tool group configuration and environment variables
- **[Examples Guide](examples.md)** - Usage examples and tutorials
- **[Troubleshooting Guide](troubleshooting.md)** - Common issues and solutions
- **[Developer Guide](DEVELOPER_GUIDE.md)** - Development and contribution guide
- **[Security Guide](security.md)** - Security features and best practices