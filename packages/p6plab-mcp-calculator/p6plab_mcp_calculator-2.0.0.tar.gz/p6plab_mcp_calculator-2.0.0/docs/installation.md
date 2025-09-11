# Installation Guide v2.0.0

## Prerequisites
- Python 3.8+ (Python 3.13 recommended)
- pip package manager or uvx

## Related Documentation

- **[Configuration Guide](configuration.md)** - Tool group configuration and environment variables
- **[API Reference](API_REFERENCE.md)** - Complete API documentation
- **[Examples Guide](examples.md)** - Usage examples and tutorials
- **[Troubleshooting Guide](troubleshooting.md)** - Common installation issues
- **[Deployment Guide](deployment.md)** - Production deployment options

## Installation Methods

### Method 1: Using uvx (Recommended for MCP)
The easiest way to use the Scientific Calculator MCP Server:
```bash
# Install and run latest stable version
uvx p6plab-mcp-calculator@latest

# Install from Test PyPI for development/testing
uvx --index-url https://test.pypi.org/simple/ p6plab-mcp-calculator@latest
```

### Method 2: From PyPI
```bash
pip install p6plab-mcp-calculator
```

### Method 3: From Source
```bash
git clone https://github.com/yourusername/p6plab-mcp-calculator.git
cd p6plab-mcp-calculator
pip install -e .
```

## Tool Group Configuration

The Scientific Calculator MCP Server v2.0.0 supports **selective tool enabling** through environment variables. By default, only **basic arithmetic tools** (8 tools) are enabled. You can enable additional tool groups as needed.

### Available Tool Groups (68 Tools Total)

| Group | Tools | Description |
|-------|-------|-------------|
| **basic** | 8 tools | Core arithmetic operations (add, subtract, multiply, divide, power, sqrt, calculate) |
| **advanced** | 5 tools | Advanced math functions (trigonometric, logarithmic, exponential, hyperbolic, angle conversion) |
| **statistics** | 5 tools | Statistical analysis (descriptive_stats, correlation, hypothesis_test) |
| **matrix** | 8 tools | Matrix operations (matrix_multiply, matrix_determinant, matrix_inverse, solve_linear_system) |
| **complex** | 6 tools | Complex number operations (complex_arithmetic, complex_magnitude, polar_conversion) |
| **units** | 7 tools | Unit conversions (convert_units, get_available_units, validate_unit_compatibility) |
| **calculus** | 9 tools | Calculus operations (derivative, integral, taylor_series, find_critical_points) |
| **solver** | 6 tools | Equation solving (solve_linear, solve_quadratic, solve_polynomial, find_roots) |
| **financial** | 7 tools | Financial mathematics (compound_interest, loan_payment, net_present_value) |
| **currency** | 4 tools | Currency conversion with live exchange rates (convert_currency, get_exchange_rate) |
| **constants** | 3 tools | Mathematical and physical constants database (get_constant, list_constants, search_constants) |

### Environment Variables

#### Individual Group Controls
```bash
# Enable specific tool groups (basic tools are always enabled)
export CALCULATOR_ENABLE_ADVANCED=true   # Advanced mathematical functions
export CALCULATOR_ENABLE_STATISTICS=true # Statistical analysis tools
export CALCULATOR_ENABLE_MATRIX=true     # Matrix operations
export CALCULATOR_ENABLE_COMPLEX=true    # Complex number operations
export CALCULATOR_ENABLE_UNITS=true      # Unit conversion tools
export CALCULATOR_ENABLE_CALCULUS=true   # Calculus operations
export CALCULATOR_ENABLE_SOLVER=true     # Equation solving tools
export CALCULATOR_ENABLE_FINANCIAL=true  # Financial mathematics
export CALCULATOR_ENABLE_CURRENCY=true   # Currency conversion
export CALCULATOR_ENABLE_CONSTANTS=true  # Constants database
```

#### Preset Combinations
```bash
# Enable all 68 tools
export CALCULATOR_ENABLE_ALL=true

# Enable scientific computing tools (42+ tools)
# Includes: basic, advanced, statistics, matrix, complex, calculus
export CALCULATOR_ENABLE_SCIENTIFIC=true

# Enable business tools (22+ tools)  
# Includes: basic, financial, currency, units
export CALCULATOR_ENABLE_BUSINESS=true

# Enable engineering tools (38+ tools)
# Includes: basic, advanced, matrix, complex, calculus, units, constants
export CALCULATOR_ENABLE_ENGINEERING=true
```

#### Boolean Values
Environment variables accept various boolean formats:
- **True values**: `true`, `TRUE`, `1`, `yes`, `on`, `enable`, `enabled`
- **False values**: `false`, `FALSE`, `0`, `no`, `off`, `disable`, `disabled`, `""` (empty)

## MCP Client Configuration

### For Kiro IDE
Add to your `.kiro/settings/mcp.json`:

#### Basic Configuration (16 tools only)
```json
{
  "mcpServers": {
    "p6plab-mcp-calculator": {
      "command": "uvx",
      "args": ["p6plab-mcp-calculator@latest"],
      "env": {
        "CALCULATOR_PRECISION": "15",
        "CALCULATOR_LOG_LEVEL": "INFO"
      },
      "disabled": false,
      "autoApprove": ["add", "subtract", "multiply", "divide"]
    }
  }
}
```

#### Scientific Configuration (~42 tools)
```json
{
  "mcpServers": {
    "p6plab-mcp-calculator": {
      "command": "uvx",
      "args": ["p6plab-mcp-calculator@latest"],
      "env": {
        "CALCULATOR_PRECISION": "15",
        "CALCULATOR_LOG_LEVEL": "INFO",
        "CALCULATOR_ENABLE_SCIENTIFIC": "true"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

#### Business Configuration (~34 tools)
```json
{
  "mcpServers": {
    "p6plab-mcp-calculator": {
      "command": "uvx",
      "args": ["p6plab-mcp-calculator@latest"],
      "env": {
        "CALCULATOR_PRECISION": "15",
        "CALCULATOR_LOG_LEVEL": "INFO",
        "CALCULATOR_ENABLE_BUSINESS": "true",
        "CALCULATOR_ENABLE_CURRENCY_CONVERSION": "true"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

#### All Tools Configuration (70 tools)
```json
{
  "mcpServers": {
    "p6plab-mcp-calculator": {
      "command": "uvx",
      "args": ["p6plab-mcp-calculator@latest"],
      "env": {
        "CALCULATOR_PRECISION": "15",
        "CALCULATOR_LOG_LEVEL": "INFO",
        "CALCULATOR_ENABLE_ALL": "true"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

#### Custom Configuration
```json
{
  "mcpServers": {
    "scientific-calculator": {
      "command": "uvx",
      "args": [
        "--from",
        "p6plab-mcp-calculator",
        "p6plab-mcp-calculator"
      ],
      "env": {
        "CALCULATOR_LOG_LEVEL": "INFO",
        "CALCULATOR_ENABLE_ADVANCED": "true",
        "CALCULATOR_ENABLE_MATRIX": "true",
        "CALCULATOR_ENABLE_CALCULUS": "true"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### For Amazon Q Developer
Add to your `.amazonq/mcp.json`:
```json
{
  "mcpServers": {
    "scientific-calculator": {
      "command": "uvx",
      "args": [
        "--from",
        "p6plab-mcp-calculator",
        "p6plab-mcp-calculator"
      ],
      "env": {
        "CALCULATOR_ENABLE_SCIENTIFIC": "true"
      }
    }
  }
}
```

### For Claude Desktop
```json
{
  "mcpServers": {
    "scientific-calculator": {
      "command": "uvx",
      "args": ["--from", "p6plab-mcp-calculator", "p6plab-mcp-calculator"],
      "env": {
        "CALCULATOR_ENABLE_ALL": "true"
      }
    }
  }
}
```

### For Development (Direct Python)
```json
{
  "mcpServers": {
    "scientific-calculator-dev": {
      "command": "/path/to/your/venv/bin/python",
      "args": ["-m", "calculator.server"],
      "cwd": "/path/to/p6plab-mcp-calculator",
      "env": {
        "CALCULATOR_LOG_LEVEL": "DEBUG",
        "CALCULATOR_ENABLE_ALL": "true"
      }
    }
  }
}
```

## Verification

### Check Tool Count
Verify the correct number of tools are available:
```bash
python -c "
import asyncio
from calculator.server import mcp
async def verify():
    tools = await mcp.get_tools()
    print(f'✅ {len(tools)} tools available')
    if len(tools) == 8:
        print('📊 Basic configuration (8 tools)')
    elif len(tools) >= 40:
        print('🔬 Scientific/Engineering configuration (40+ tools)')
    elif len(tools) == 68:
        print('🚀 All tools configuration (68 tools)')
    else:
        print(f'🔧 Custom configuration ({len(tools)} tools)')
asyncio.run(verify())
"
```

### Test Health Check
Use the health_check tool to see detailed configuration:
```bash
# The health_check tool will show:
# - Enabled/disabled tool groups
# - Total tool count
# - Configuration source
# - Warnings and recommendations
```

## Configuration Examples

### Minimal Setup (Data Entry)
```bash
# Only basic arithmetic - 8 tools
# No environment variables needed (default)
```

### Scientific Research
```bash
export CALCULATOR_ENABLE_SCIENTIFIC=true
# Includes: basic, advanced, statistics, matrix, complex, calculus
# Total: 42+ tools
```

### Business Analysis
```bash
export CALCULATOR_ENABLE_BUSINESS=true
# Includes: basic, financial, currency, units
# Total: 22+ tools
```

### Engineering Work
```bash
export CALCULATOR_ENABLE_ENGINEERING=true
# Includes: basic, advanced, matrix, complex, calculus, units, constants
# Total: 38+ tools
```

### Data Science
```bash
# Basic tools are always enabled
export CALCULATOR_ENABLE_STATISTICS=true
export CALCULATOR_ENABLE_MATRIX=true
export CALCULATOR_ENABLE_CALCULUS=true
# Custom combination for data science work
```

### Full Mathematics Suite
```bash
export CALCULATOR_ENABLE_ALL=true
# All 68 tools available
```

## Dependencies
The package automatically installs the following dependencies:
- **fastmcp>=2.0.0** - MCP server framework
- **numpy>=1.21.0** - Numerical computing
- **scipy>=1.7.0** - Scientific computing
- **sympy>=1.9.0** - Symbolic mathematics
- **pydantic>=2.0.0** - Data validation
- **loguru>=0.6.0** - Logging

## Python Version Compatibility
- **Python 3.10+**: Full compatibility with all 68 tools
- **Python 3.13**: Recommended for development
- **uvx environment**: Uses Python 3.10 (fully supported)

## Legacy Support
The server maintains backward compatibility with the legacy environment variable:
```bash
# Legacy (deprecated) - use CALCULATOR_ENABLE_ALL instead
export CALCULATOR_ENABLE_ALL_TOOLS=true
```

## Troubleshooting
If you see fewer than expected tools, check the [troubleshooting guide](troubleshooting.md) for common issues and solutions.

### Common Issues
- **Only 8 tools showing**: Default configuration (basic only)
- **Import errors**: Check Python version and dependencies
- **Configuration not working**: Verify environment variable names and values
- **Performance issues**: Consider using fewer tool groups for better performance