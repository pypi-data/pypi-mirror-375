"""Main server application setup."""

from fastmcp import FastMCP
from loguru import logger

from ..repositories.cache import CacheRepository
from ..repositories.constants import ConstantsRepository
from ..repositories.currency import CurrencyRepository
from ..services.arithmetic import ArithmeticService
from ..services.calculus import CalculusService
from ..services.config import ConfigService
from ..services.matrix import MatrixService
from ..services.statistics import StatisticsService
from .factory import ToolRegistrationFactory
from .handlers.arithmetic import register_arithmetic_handlers
from .middleware import MiddlewareStack


class CalculatorServer:
    """Main calculator server application."""

    def __init__(self):
        """Initialize the calculator server."""
        self.mcp = FastMCP("Scientific Calculator")
        self.config_service = None
        self.services = {}
        self.repositories = {}
        self.factory = None
        self.middleware = None
        self._initialized = False

    def initialize(self) -> None:
        """Initialize all server components."""
        logger.info("Initializing Scientific Calculator MCP Server...")

        # Initialize configuration
        self._setup_configuration()

        # Initialize repositories
        self._setup_repositories()

        # Initialize services
        self._setup_services()

        # Initialize middleware and factory
        self._setup_middleware_and_factory()

        # Register all tools
        self._register_tools()

        # Log initialization summary
        self._log_initialization_summary()

        logger.info("Scientific Calculator MCP Server initialized successfully")
        self._initialized = True

    def _setup_configuration(self) -> None:
        """Set up configuration service."""
        try:
            self.config_service = ConfigService()
            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise

    def _setup_repositories(self) -> None:
        """Set up repository instances."""
        try:
            # Cache repository
            cache_size = self.config_service.get_cache_size()
            cache_ttl = self.config_service.get_cache_ttl()
            self.repositories["cache"] = CacheRepository(
                max_size=cache_size, default_ttl=cache_ttl
            )

            # Constants repository
            self.repositories["constants"] = ConstantsRepository()

            # Currency repository (if enabled)
            if self.config_service.is_currency_conversion_enabled():
                currency_ttl = self.config_service.get_config_value(
                    "external_apis.currency_cache_ttl", 3600
                )
                self.repositories["currency"] = CurrencyRepository(cache_ttl=currency_ttl)
            else:
                # Add a mock currency repository for validation compatibility
                from ..repositories.currency import MockCurrencyRepository
                self.repositories["currency"] = MockCurrencyRepository()

            logger.info(f"Initialized {len(self.repositories)} repositories")

        except Exception as e:
            logger.error(f"Failed to initialize repositories: {e}")
            raise

    def _setup_services(self) -> None:
        """Set up service instances."""
        try:
            cache_repo = self.repositories.get("cache")
            
            # Get enabled tool groups from configuration
            enabled_groups = self.config_service.get_enabled_tool_groups()
            logger.debug(f"Enabled tool groups: {enabled_groups}")
            
            # Arithmetic service (always enabled with basic group)
            if "basic" in enabled_groups:
                self.services["arithmetic"] = ArithmeticService(
                    config=self.config_service, cache=cache_repo
                )

            # Matrix service
            if "matrix" in enabled_groups:
                self.services["matrix"] = MatrixService(
                    config=self.config_service, cache=cache_repo
                )

            # Statistics service
            if "statistics" in enabled_groups:
                self.services["statistics"] = StatisticsService(
                    config=self.config_service, cache=cache_repo
                )

            # Calculus service
            if "calculus" in enabled_groups:
                self.services["calculus"] = CalculusService(
                    config=self.config_service, cache=cache_repo
                )

            # Advanced service (reuse arithmetic service)
            if "advanced" in enabled_groups:
                self.services["advanced"] = self.services.get("arithmetic") or ArithmeticService(
                    config=self.config_service, cache=cache_repo
                )

            # Complex service (reuse arithmetic service)
            if "complex" in enabled_groups:
                self.services["complex"] = self.services.get("arithmetic") or ArithmeticService(
                    config=self.config_service, cache=cache_repo
                )

            # Units service (reuse arithmetic service)
            if "units" in enabled_groups:
                self.services["units"] = self.services.get("arithmetic") or ArithmeticService(
                    config=self.config_service, cache=cache_repo
                )

            # Solver service (reuse calculus service)
            if "solver" in enabled_groups:
                self.services["solver"] = self.services.get("calculus") or CalculusService(
                    config=self.config_service, cache=cache_repo
                )

            # Financial service (reuse arithmetic service)
            if "financial" in enabled_groups:
                self.services["financial"] = self.services.get("arithmetic") or ArithmeticService(
                    config=self.config_service, cache=cache_repo
                )

            # Currency service (reuse arithmetic service)
            if "currency" in enabled_groups:
                self.services["currency"] = self.services.get("arithmetic") or ArithmeticService(
                    config=self.config_service, cache=cache_repo
                )

            # Constants service (reuse arithmetic service)
            if "constants" in enabled_groups:
                self.services["constants"] = self.services.get("arithmetic") or ArithmeticService(
                    config=self.config_service, cache=cache_repo
                )

            logger.info(f"Initialized {len(self.services)} services for groups: {enabled_groups}")

        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise

    def _setup_middleware_and_factory(self) -> None:
        """Set up middleware and tool factory."""
        try:
            # Initialize middleware stack
            self.middleware = MiddlewareStack(self.config_service)

            # Initialize tool registration factory
            self.factory = ToolRegistrationFactory(
                server=self.mcp, config_service=self.config_service
            )

            # Add cache service to factory for tool operations
            self.factory.cache_service = self.repositories.get("cache")

            logger.info("Middleware and factory initialized")

        except Exception as e:
            logger.error(f"Failed to initialize middleware and factory: {e}")
            raise

    def _register_tools(self) -> None:
        """Register all MCP tools."""
        try:
            # Register arithmetic tools
            if "arithmetic" in self.services:
                register_arithmetic_handlers(self.factory, self.services["arithmetic"])

            # Register matrix tools
            if "matrix" in self.services:
                self._register_matrix_tools()

            # Register statistics tools
            if "statistics" in self.services:
                self._register_statistics_tools()

            # Register calculus tools
            if "calculus" in self.services:
                self._register_calculus_tools()

            # Register advanced tools
            if "advanced" in self.services:
                self._register_advanced_tools()

            # Register complex tools
            if "complex" in self.services:
                self._register_complex_tools()

            # Register units tools
            if "units" in self.services:
                self._register_units_tools()

            # Register solver tools
            if "solver" in self.services:
                self._register_solver_tools()

            # Register financial tools
            if "financial" in self.services:
                self._register_financial_tools()

            # Register currency tools
            if "currency" in self.services:
                self._register_currency_tools()

            # Register constants tools
            if "constants" in self.services:
                self._register_constants_tools()

            # Get registration statistics
            stats = self.factory.get_registration_stats()
            logger.info(
                f"Registered {stats['enabled_tools']} tools across {len(stats['groups'])} groups"
            )

        except Exception as e:
            logger.error(f"Failed to register tools: {e}")
            raise

    def _register_matrix_tools(self) -> None:
        """Register matrix operation tools."""
        from typing import List, Optional

        from pydantic import BaseModel, Field

        class MatrixRequest(BaseModel):
            matrix_a: List[List[float]] = Field(..., description="First matrix")
            matrix_b: Optional[List[List[float]]] = Field(
                None, description="Second matrix (optional)"
            )
            operation_type: Optional[str] = Field(None, description="Operation type")

        class SingleMatrixRequest(BaseModel):
            matrix: List[List[float]] = Field(..., description="Input matrix")

        class LinearSystemRequest(BaseModel):
            matrix_a: List[List[float]] = Field(..., description="Coefficient matrix")
            vector_b: List[float] = Field(..., description="Right-hand side vector")

        matrix_tools = [
            {
                "name": "matrix_add",
                "operation": "add",
                "description": "Add two matrices",
                "input_schema": MatrixRequest,
                "tool_group": "matrix",
                "tags": ["matrix", "linear_algebra"],
            },
            {
                "name": "matrix_multiply",
                "operation": "multiply",
                "description": "Multiply two matrices",
                "input_schema": MatrixRequest,
                "tool_group": "matrix",
                "tags": ["matrix", "linear_algebra"],
            },
            {
                "name": "matrix_determinant",
                "operation": "determinant",
                "description": "Calculate matrix determinant",
                "input_schema": SingleMatrixRequest,
                "tool_group": "matrix",
                "tags": ["matrix", "determinant"],
            },
            {
                "name": "matrix_inverse",
                "operation": "inverse",
                "description": "Calculate matrix inverse",
                "input_schema": SingleMatrixRequest,
                "tool_group": "matrix",
                "tags": ["matrix", "inverse"],
            },
            {
                "name": "matrix_eigenvalues",
                "operation": "eigenvalues",
                "description": "Calculate matrix eigenvalues",
                "input_schema": SingleMatrixRequest,
                "tool_group": "matrix",
                "tags": ["matrix", "eigenvalues"],
            },
            {
                "name": "solve_linear_system",
                "operation": "solve",
                "description": "Solve linear system Ax = b",
                "input_schema": LinearSystemRequest,
                "tool_group": "matrix",
                "tags": ["matrix", "linear_system"],
            },
        ]

        self.factory.register_service_tools(
            service_name="matrix",
            service_instance=self.services["matrix"],
            tool_definitions=matrix_tools,
            tool_group="matrix",
        )

    def _register_statistics_tools(self) -> None:
        """Register statistics tools."""
        from typing import List, Optional

        from pydantic import BaseModel, Field

        class StatisticsRequest(BaseModel):
            data: List[float] = Field(..., description="List of numerical data")
            population: Optional[bool] = Field(
                False, description="Population statistics (vs sample)"
            )

        class CorrelationRequest(BaseModel):
            x_data: List[float] = Field(..., description="X variable data")
            y_data: List[float] = Field(..., description="Y variable data")

        class PercentileRequest(BaseModel):
            data: List[float] = Field(..., description="List of numerical data")
            percentile: float = Field(..., ge=0, le=100, description="Percentile value (0-100)")

        stats_tools = [
            {
                "name": "mean",
                "operation": "mean",
                "description": "Calculate arithmetic mean",
                "input_schema": StatisticsRequest,
                "tool_group": "statistics",
                "tags": ["statistics", "descriptive"],
            },
            {
                "name": "median",
                "operation": "median",
                "description": "Calculate median value",
                "input_schema": StatisticsRequest,
                "tool_group": "statistics",
                "tags": ["statistics", "descriptive"],
            },
            {
                "name": "std_dev",
                "operation": "std_dev",
                "description": "Calculate standard deviation",
                "input_schema": StatisticsRequest,
                "tool_group": "statistics",
                "tags": ["statistics", "variability"],
            },
            {
                "name": "correlation",
                "operation": "correlation",
                "description": "Calculate correlation coefficient",
                "input_schema": CorrelationRequest,
                "tool_group": "statistics",
                "tags": ["statistics", "correlation"],
            },
            {
                "name": "percentile",
                "operation": "percentile",
                "description": "Calculate percentile value",
                "input_schema": PercentileRequest,
                "tool_group": "statistics",
                "tags": ["statistics", "percentile"],
            },
            {
                "name": "descriptive_stats",
                "operation": "descriptive_stats",
                "description": "Calculate comprehensive descriptive statistics",
                "input_schema": StatisticsRequest,
                "tool_group": "statistics",
                "tags": ["statistics", "comprehensive"],
            },
        ]

        self.factory.register_service_tools(
            service_name="statistics",
            service_instance=self.services["statistics"],
            tool_definitions=stats_tools,
            tool_group="statistics",
        )

    def _register_calculus_tools(self) -> None:
        """Register calculus tools."""
        from typing import Optional

        from pydantic import BaseModel, Field

        class DerivativeRequest(BaseModel):
            expression: str = Field(..., description="Mathematical expression")
            variable: str = Field(..., description="Variable to differentiate with respect to")
            order: Optional[int] = Field(1, ge=1, le=10, description="Order of derivative")

        class IntegralRequest(BaseModel):
            expression: str = Field(..., description="Mathematical expression")
            variable: str = Field(..., description="Variable to integrate with respect to")
            lower_bound: Optional[str] = Field(
                None, description="Lower bound for definite integral"
            )
            upper_bound: Optional[str] = Field(
                None, description="Upper bound for definite integral"
            )

        class LimitRequest(BaseModel):
            expression: str = Field(..., description="Mathematical expression")
            variable: str = Field(..., description="Variable")
            approach_value: str = Field(..., description="Value to approach")
            direction: Optional[str] = Field("both", description="Direction (left, right, both)")

        class SeriesRequest(BaseModel):
            expression: str = Field(..., description="Mathematical expression")
            variable: str = Field(..., description="Variable")
            center: Optional[float] = Field(0, description="Center point for series expansion")
            order: Optional[int] = Field(5, ge=1, le=20, description="Order of series expansion")

        calculus_tools = [
            {
                "name": "derivative",
                "operation": "derivatives.symbolic",
                "description": "Calculate symbolic derivative",
                "input_schema": DerivativeRequest,
                "tool_group": "calculus",
                "tags": ["calculus", "derivatives"],
            },
            {
                "name": "integral",
                "operation": "integrals.symbolic",
                "description": "Calculate symbolic integral",
                "input_schema": IntegralRequest,
                "tool_group": "calculus",
                "tags": ["calculus", "integrals"],
            },
            {
                "name": "limit",
                "operation": "limits.limit",
                "description": "Calculate limit of expression",
                "input_schema": LimitRequest,
                "tool_group": "calculus",
                "tags": ["calculus", "limits"],
            },
            {
                "name": "taylor_series",
                "operation": "series.taylor",
                "description": "Calculate Taylor series expansion",
                "input_schema": SeriesRequest,
                "tool_group": "calculus",
                "tags": ["calculus", "series"],
            },
        ]

        self.factory.register_service_tools(
            service_name="calculus",
            service_instance=self.services["calculus"],
            tool_definitions=calculus_tools,
            tool_group="calculus",
        )

    def _register_advanced_tools(self) -> None:
        """Register advanced mathematical function tools."""
        from typing import Optional

        from pydantic import BaseModel, Field

        class TrigonometricRequest(BaseModel):
            function: str = Field(..., description="Trigonometric function (sin, cos, tan, asin, acos, atan)")
            value: float = Field(..., description="Input value")
            unit: Optional[str] = Field("radians", description="Unit for input (radians or degrees)")

        class LogarithmRequest(BaseModel):
            value: float = Field(..., gt=0, description="Input value (must be positive)")
            base: Optional[float] = Field(None, description="Logarithm base (default: natural log)")

        class ExponentialRequest(BaseModel):
            value: float = Field(..., description="Exponent value")
            base: Optional[float] = Field(None, description="Base (default: e)")

        class HyperbolicRequest(BaseModel):
            function: str = Field(..., description="Hyperbolic function (sinh, cosh, tanh)")
            value: float = Field(..., description="Input value")

        class AngleConversionRequest(BaseModel):
            value: float = Field(..., description="Angle value")
            from_unit: str = Field(..., description="Source unit (radians or degrees)")
            to_unit: str = Field(..., description="Target unit (radians or degrees)")

        advanced_tools = [
            {
                "name": "trigonometric",
                "operation": "sin",  # Will be dynamically mapped based on function parameter
                "description": "Calculate trigonometric functions (sin, cos, tan, asin, acos, atan)",
                "input_schema": TrigonometricRequest,
                "tool_group": "advanced",
                "tags": ["advanced", "trigonometry"],
            },
            {
                "name": "logarithm",
                "operation": "log",
                "description": "Calculate logarithmic functions (natural log, log base 10, custom base)",
                "input_schema": LogarithmRequest,
                "tool_group": "advanced",
                "tags": ["advanced", "logarithm"],
            },
            {
                "name": "exponential",
                "operation": "exp",
                "description": "Calculate exponential functions (e^x, custom base)",
                "input_schema": ExponentialRequest,
                "tool_group": "advanced",
                "tags": ["advanced", "exponential"],
            },
            {
                "name": "hyperbolic",
                "operation": "sinh",  # Will be dynamically mapped based on function parameter
                "description": "Calculate hyperbolic functions (sinh, cosh, tanh)",
                "input_schema": HyperbolicRequest,
                "tool_group": "advanced",
                "tags": ["advanced", "hyperbolic"],
            },
            {
                "name": "convert_angle",
                "operation": "convert_angle",
                "description": "Convert angles between radians and degrees",
                "input_schema": AngleConversionRequest,
                "tool_group": "advanced",
                "tags": ["advanced", "conversion"],
            },
        ]

        self.factory.register_service_tools(
            service_name="advanced",
            service_instance=self.services["advanced"],
            tool_definitions=advanced_tools,
            tool_group="advanced",
        )

    def _register_complex_tools(self) -> None:
        """Register complex number operation tools."""
        from typing import Optional

        from pydantic import BaseModel, Field

        class ComplexNumberRequest(BaseModel):
            real: float = Field(..., description="Real part of complex number")
            imaginary: float = Field(..., description="Imaginary part of complex number")

        class ComplexArithmeticRequest(BaseModel):
            complex1: ComplexNumberRequest = Field(..., description="First complex number")
            complex2: ComplexNumberRequest = Field(..., description="Second complex number")
            operation: str = Field(..., description="Arithmetic operation (add, subtract, multiply, divide)")

        class ComplexFunctionRequest(BaseModel):
            complex_number: ComplexNumberRequest = Field(..., description="Complex number input")
            function: Optional[str] = Field(None, description="Function to apply (exp, log, sin, cos)")

        complex_tools = [
            {
                "name": "complex_arithmetic",
                "operation": "complex_arithmetic",
                "description": "Perform arithmetic operations on complex numbers",
                "input_schema": ComplexArithmeticRequest,
                "tool_group": "complex",
                "tags": ["complex", "arithmetic"],
            },
            {
                "name": "complex_magnitude",
                "operation": "complex_magnitude",
                "description": "Calculate the magnitude (absolute value) of a complex number",
                "input_schema": ComplexNumberRequest,
                "tool_group": "complex",
                "tags": ["complex", "magnitude"],
            },
            {
                "name": "complex_phase",
                "operation": "complex_phase",
                "description": "Calculate the phase (argument) of a complex number",
                "input_schema": ComplexNumberRequest,
                "tool_group": "complex",
                "tags": ["complex", "phase"],
            },
            {
                "name": "complex_conjugate",
                "operation": "complex_conjugate",
                "description": "Calculate the complex conjugate of a complex number",
                "input_schema": ComplexNumberRequest,
                "tool_group": "complex",
                "tags": ["complex", "conjugate"],
            },
            {
                "name": "polar_conversion",
                "operation": "polar_conversion",
                "description": "Convert complex number between rectangular and polar forms",
                "input_schema": ComplexNumberRequest,
                "tool_group": "complex",
                "tags": ["complex", "polar"],
            },
            {
                "name": "complex_functions",
                "operation": "complex_functions",
                "description": "Apply mathematical functions to complex numbers",
                "input_schema": ComplexFunctionRequest,
                "tool_group": "complex",
                "tags": ["complex", "functions"],
            },
        ]

        self.factory.register_service_tools(
            service_name="complex",
            service_instance=self.services["complex"],
            tool_definitions=complex_tools,
            tool_group="complex",
        )

    def _register_units_tools(self) -> None:
        """Register unit conversion tools."""
        from typing import Optional
        
        from pydantic import BaseModel, Field

        class UnitConversionRequest(BaseModel):
            value: float = Field(..., description="Value to convert")
            from_unit: str = Field(..., description="Source unit")
            to_unit: str = Field(..., description="Target unit")
            unit_type: Optional[str] = Field(None, description="Unit category (length, weight, etc.)")

        class UnitInfoRequest(BaseModel):
            unit_name: str = Field(..., description="Unit name or symbol")
            category: Optional[str] = Field(None, description="Unit category")

        units_tools = [
            {
                "name": "convert_units",
                "operation": "convert_units",
                "description": "Convert between different units of measurement",
                "input_schema": UnitConversionRequest,
                "tool_group": "units",
                "tags": ["units", "conversion"],
            },
            {
                "name": "get_available_units",
                "operation": "get_available_units",
                "description": "Get list of available units by category",
                "input_schema": UnitInfoRequest,
                "tool_group": "units",
                "tags": ["units", "list"],
            },
            {
                "name": "validate_unit_compatibility",
                "operation": "validate_unit_compatibility",
                "description": "Check if two units can be converted",
                "input_schema": UnitConversionRequest,
                "tool_group": "units",
                "tags": ["units", "validation"],
            },
            {
                "name": "get_conversion_factor",
                "operation": "get_conversion_factor",
                "description": "Get conversion factor between two units",
                "input_schema": UnitConversionRequest,
                "tool_group": "units",
                "tags": ["units", "factor"],
            },
            {
                "name": "convert_multiple_units",
                "operation": "convert_multiple_units",
                "description": "Convert multiple values at once",
                "input_schema": UnitConversionRequest,
                "tool_group": "units",
                "tags": ["units", "batch"],
            },
            {
                "name": "find_unit_by_name",
                "operation": "find_unit_by_name",
                "description": "Search for units by name or symbol",
                "input_schema": UnitInfoRequest,
                "tool_group": "units",
                "tags": ["units", "search"],
            },
            {
                "name": "get_unit_info",
                "operation": "get_unit_info",
                "description": "Get detailed information about a unit",
                "input_schema": UnitInfoRequest,
                "tool_group": "units",
                "tags": ["units", "info"],
            },
        ]

        self.factory.register_service_tools(
            service_name="units",
            service_instance=self.services["units"],
            tool_definitions=units_tools,
            tool_group="units",
        )

    def _register_solver_tools(self) -> None:
        """Register equation solver tools."""
        from typing import List, Optional
        
        from pydantic import BaseModel, Field

        class LinearEquationRequest(BaseModel):
            equation: str = Field(..., description="Linear equation (e.g., '2*x + 3 = 7')")
            variable: str = Field(default="x", description="Variable to solve for")

        class QuadraticEquationRequest(BaseModel):
            a: float = Field(..., ne=0, description="Coefficient a (cannot be zero)")
            b: float = Field(..., description="Coefficient b")
            c: float = Field(..., description="Coefficient c")

        class PolynomialRequest(BaseModel):
            coefficients: List[float] = Field(..., description="Polynomial coefficients (highest degree first)")

        class SystemRequest(BaseModel):
            equations: List[str] = Field(..., description="List of equations")
            variables: List[str] = Field(..., description="List of variables")

        class RootFindingRequest(BaseModel):
            expression: str = Field(..., description="Mathematical expression")
            variable: str = Field(default="x", description="Variable")
            initial_guess: Optional[float] = Field(None, description="Initial guess for root")

        solver_tools = [
            {
                "name": "solve_linear",
                "operation": "solve_linear",
                "description": "Solve linear equations",
                "input_schema": LinearEquationRequest,
                "tool_group": "solver",
                "tags": ["solver", "linear"],
            },
            {
                "name": "solve_quadratic",
                "operation": "solve_quadratic",
                "description": "Solve quadratic equations",
                "input_schema": QuadraticEquationRequest,
                "tool_group": "solver",
                "tags": ["solver", "quadratic"],
            },
            {
                "name": "solve_polynomial",
                "operation": "solve_polynomial",
                "description": "Solve polynomial equations",
                "input_schema": PolynomialRequest,
                "tool_group": "solver",
                "tags": ["solver", "polynomial"],
            },
            {
                "name": "solve_system",
                "operation": "solve_system",
                "description": "Solve systems of equations",
                "input_schema": SystemRequest,
                "tool_group": "solver",
                "tags": ["solver", "system"],
            },
            {
                "name": "find_roots",
                "operation": "find_roots",
                "description": "Find roots of arbitrary functions",
                "input_schema": RootFindingRequest,
                "tool_group": "solver",
                "tags": ["solver", "roots"],
            },
            {
                "name": "analyze_equation",
                "operation": "analyze_equation",
                "description": "Analyze equation properties",
                "input_schema": LinearEquationRequest,
                "tool_group": "solver",
                "tags": ["solver", "analysis"],
            },
        ]

        self.factory.register_service_tools(
            service_name="solver",
            service_instance=self.services["solver"],
            tool_definitions=solver_tools,
            tool_group="solver",
        )

    def _register_financial_tools(self) -> None:
        """Register financial calculation tools."""
        from typing import List
        
        from pydantic import BaseModel, Field

        class CompoundInterestRequest(BaseModel):
            principal: float = Field(..., gt=0, description="Principal amount")
            rate: float = Field(..., gt=0, description="Interest rate (as decimal)")
            time: float = Field(..., gt=0, description="Time period")
            compound_frequency: int = Field(default=1, gt=0, description="Compounding frequency per year")

        class LoanRequest(BaseModel):
            principal: float = Field(..., gt=0, description="Loan amount")
            rate: float = Field(..., gt=0, description="Interest rate (as decimal)")
            term: int = Field(..., gt=0, description="Loan term in periods")

        class NPVRequest(BaseModel):
            cash_flows: List[float] = Field(..., description="List of cash flows")
            discount_rate: float = Field(..., description="Discount rate (as decimal)")

        class AnnuityRequest(BaseModel):
            payment: float = Field(..., description="Payment amount")
            rate: float = Field(..., gt=0, description="Interest rate per period")
            periods: int = Field(..., gt=0, description="Number of periods")

        financial_tools = [
            {
                "name": "compound_interest",
                "operation": "compound_interest",
                "description": "Calculate compound interest",
                "input_schema": CompoundInterestRequest,
                "tool_group": "financial",
                "tags": ["financial", "interest"],
            },
            {
                "name": "loan_payment",
                "operation": "loan_payment",
                "description": "Calculate loan payments",
                "input_schema": LoanRequest,
                "tool_group": "financial",
                "tags": ["financial", "loan"],
            },
            {
                "name": "net_present_value",
                "operation": "net_present_value",
                "description": "Calculate net present value",
                "input_schema": NPVRequest,
                "tool_group": "financial",
                "tags": ["financial", "npv"],
            },
            {
                "name": "internal_rate_of_return",
                "operation": "internal_rate_of_return",
                "description": "Calculate internal rate of return",
                "input_schema": NPVRequest,
                "tool_group": "financial",
                "tags": ["financial", "irr"],
            },
            {
                "name": "present_value",
                "operation": "present_value",
                "description": "Calculate present value",
                "input_schema": NPVRequest,
                "tool_group": "financial",
                "tags": ["financial", "pv"],
            },
            {
                "name": "future_value_annuity",
                "operation": "future_value_annuity",
                "description": "Calculate future value of annuity",
                "input_schema": AnnuityRequest,
                "tool_group": "financial",
                "tags": ["financial", "annuity"],
            },
            {
                "name": "amortization_schedule",
                "operation": "amortization_schedule",
                "description": "Generate amortization schedule",
                "input_schema": LoanRequest,
                "tool_group": "financial",
                "tags": ["financial", "amortization"],
            },
        ]

        self.factory.register_service_tools(
            service_name="financial",
            service_instance=self.services["financial"],
            tool_definitions=financial_tools,
            tool_group="financial",
        )

    def _register_currency_tools(self) -> None:
        """Register currency conversion tools."""
        from pydantic import BaseModel, Field

        class CurrencyConversionRequest(BaseModel):
            amount: float = Field(..., gt=0, description="Amount to convert")
            from_currency: str = Field(..., min_length=3, max_length=3, description="Source currency code")
            to_currency: str = Field(..., min_length=3, max_length=3, description="Target currency code")

        class CurrencyInfoRequest(BaseModel):
            currency_code: str = Field(..., min_length=3, max_length=3, description="Currency code")

        currency_tools = [
            {
                "name": "convert_currency",
                "operation": "convert_currency",
                "description": "Convert between currencies",
                "input_schema": CurrencyConversionRequest,
                "tool_group": "currency",
                "tags": ["currency", "conversion"],
            },
            {
                "name": "get_exchange_rate",
                "operation": "get_exchange_rate",
                "description": "Get exchange rate between currencies",
                "input_schema": CurrencyConversionRequest,
                "tool_group": "currency",
                "tags": ["currency", "rate"],
            },
            {
                "name": "get_supported_currencies",
                "operation": "get_supported_currencies",
                "description": "Get list of supported currencies",
                "input_schema": CurrencyInfoRequest,
                "tool_group": "currency",
                "tags": ["currency", "list"],
            },
            {
                "name": "get_currency_info",
                "operation": "get_currency_info",
                "description": "Get information about a currency",
                "input_schema": CurrencyInfoRequest,
                "tool_group": "currency",
                "tags": ["currency", "info"],
            },
        ]

        self.factory.register_service_tools(
            service_name="currency",
            service_instance=self.services["currency"],
            tool_definitions=currency_tools,
            tool_group="currency",
        )

    def _register_constants_tools(self) -> None:
        """Register mathematical constants tools."""
        from typing import Optional
        
        from pydantic import BaseModel, Field

        class ConstantRequest(BaseModel):
            name: str = Field(..., description="Constant name")
            category: Optional[str] = Field(None, description="Constant category")

        class ConstantSearchRequest(BaseModel):
            query: str = Field(..., description="Search query")
            category: Optional[str] = Field(None, description="Category to search in")

        constants_tools = [
            {
                "name": "get_constant",
                "operation": "get_constant",
                "description": "Get mathematical or physical constant",
                "input_schema": ConstantRequest,
                "tool_group": "constants",
                "tags": ["constants", "math"],
            },
            {
                "name": "list_constants",
                "operation": "list_constants",
                "description": "List available constants by category",
                "input_schema": ConstantRequest,
                "tool_group": "constants",
                "tags": ["constants", "list"],
            },
            {
                "name": "search_constants",
                "operation": "search_constants",
                "description": "Search for constants by name or description",
                "input_schema": ConstantSearchRequest,
                "tool_group": "constants",
                "tags": ["constants", "search"],
            },
        ]

        self.factory.register_service_tools(
            service_name="constants",
            service_instance=self.services["constants"],
            tool_definitions=constants_tools,
            tool_group="constants",
        )

    def _log_initialization_summary(self) -> None:
        """Log initialization summary."""
        config_summary = self.config_service.get_config_summary()

        logger.info("=== Calculator Server Configuration ===")
        logger.info(f"Precision: {config_summary['precision']}")
        logger.info(f"Cache Size: {config_summary['cache_size']}")
        logger.info(f"Max Computation Time: {config_summary['max_computation_time']}s")
        logger.info(f"Max Memory: {config_summary['max_memory_mb']}MB")

        logger.info("=== Enabled Features ===")
        for feature, enabled in config_summary["features"].items():
            status = "✓" if enabled else "✗"
            logger.info(f"{status} {feature.replace('_', ' ').title()}")

        logger.info("=== Tool Groups ===")
        for group in config_summary["tool_groups"]:
            logger.info(f"✓ {group}")

        logger.info(f"Log Level: {config_summary['log_level']}")

    def get_server(self) -> FastMCP:
        """Get the FastMCP server instance.

        Returns:
            FastMCP server instance
        """
        return self.mcp

    def get_health_status(self) -> dict:
        """Get server health status.

        Returns:
            Dictionary with health status information
        """
        return {
            "status": "healthy",
            "services": dict.fromkeys(self.services.keys(), "active"),
            "repositories": dict.fromkeys(self.repositories.keys(), "active"),
            "configuration": "loaded",
            "tools_registered": self.factory.get_registration_stats()["enabled_tools"]
            if self.factory
            else 0,
        }

    async def shutdown(self):
        """Shutdown the server and cleanup resources."""
        logger.info("Shutting down Scientific Calculator MCP Server...")

        # Cleanup repositories
        for repo in self.repositories.values():
            if hasattr(repo, 'cleanup'):
                await repo.cleanup()

        # Cleanup services
        for service in self.services.values():
            if hasattr(service, 'cleanup'):
                await service.cleanup()

        logger.info("Server shutdown complete")

    # Properties for backward compatibility with validation script
    @property
    def config(self):
        """Get configuration service."""
        return self.config_service

    @property
    def arithmetic_service(self):
        """Get arithmetic service."""
        return self.services.get("arithmetic")

    @property
    def matrix_service(self):
        """Get matrix service."""
        return self.services.get("matrix")

    @property
    def statistics_service(self):
        """Get statistics service."""
        return self.services.get("statistics")

    @property
    def calculus_service(self):
        """Get calculus service."""
        return self.services.get("calculus")

    @property
    def cache_repo(self):
        """Get cache repository."""
        return self.repositories.get("cache")

    @property
    def constants_repo(self):
        """Get constants repository."""
        return self.repositories.get("constants")

    @property
    def currency_repo(self):
        """Get currency repository."""
        return self.repositories.get("currency")

    @property
    def is_initialized(self) -> bool:
        """Check if server is initialized."""
        return self._initialized


def create_server() -> CalculatorServer:
    """Create and initialize the calculator server.

    Returns:
        Initialized calculator server instance
    """
    server = CalculatorServer()
    server.initialize()
    return server


# For backward compatibility and direct execution
def main():
    """Main entry point for the calculator server."""
    try:
        server = create_server()
        logger.info("Calculator server ready to serve requests")
        return server.get_server()
    except Exception as e:
        logger.error(f"Failed to start calculator server: {e}")
        raise


# Aliases for backward compatibility
CalculatorApp = CalculatorServer
create_calculator_app = create_server


def run_calculator_server():
    """Run the calculator server."""
    return main()


if __name__ == "__main__":
    main()
