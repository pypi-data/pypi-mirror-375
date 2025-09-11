"""Strategy patterns for complex operations."""

from .matrix_solver import (
    CholeskyStrategy,
    IterativeStrategy,
    LUDecompositionStrategy,
    MatrixSolverContext,
    MatrixSolverStrategy,
    QRDecompositionStrategy,
    SVDStrategy,
)
from .numerical import (
    BisectionRootFindingStrategy,
    BrentOptimizationStrategy,
    BrentRootFindingStrategy,
    GoldenSectionStrategy,
    NelderMeadStrategy,
    NewtonRootFindingStrategy,
    NumericalMethodContext,
    NumericalStrategy,
    SecantRootFindingStrategy,
)
from .optimization import (
    BFGSStrategy,
    ConstrainedOptimizationStrategy,
    DifferentialEvolutionStrategy,
    OptimizationContext,
    OptimizationStrategy,
    ScalarBrentStrategy,
)

__all__ = [
    # Matrix solver strategies
    "MatrixSolverStrategy",
    "MatrixSolverContext",
    "LUDecompositionStrategy",
    "CholeskyStrategy",
    "QRDecompositionStrategy",
    "SVDStrategy",
    "IterativeStrategy",
    # Numerical method strategies
    "NumericalStrategy",
    "NumericalMethodContext",
    "BrentRootFindingStrategy",
    "NewtonRootFindingStrategy",
    "SecantRootFindingStrategy",
    "BisectionRootFindingStrategy",
    "BrentOptimizationStrategy",
    "GoldenSectionStrategy",
    "NelderMeadStrategy",
    # Optimization strategies
    "OptimizationStrategy",
    "OptimizationContext",
    "ScalarBrentStrategy",
    "BFGSStrategy",
    "ConstrainedOptimizationStrategy",
    "DifferentialEvolutionStrategy",
]
