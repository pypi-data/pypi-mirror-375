"""Matrix solver strategies for different algorithms."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import numpy as np
from scipy.linalg import cholesky, lu, qr, svd

from ..core.errors.exceptions import ComputationError, ValidationError


class MatrixSolverStrategy(ABC):
    """Abstract strategy for matrix solving."""

    @abstractmethod
    def can_handle(self, matrix: np.ndarray, vector: Optional[np.ndarray] = None) -> bool:
        """Check if strategy can handle this matrix.

        Args:
            matrix: Input matrix
            vector: Optional vector for linear systems

        Returns:
            True if strategy can handle the matrix
        """
        pass

    @abstractmethod
    def solve(self, matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
        """Solve the matrix equation Ax = b.

        Args:
            matrix: Coefficient matrix A
            vector: Right-hand side vector b

        Returns:
            Solution vector x
        """
        pass

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """Get information about the strategy.

        Returns:
            Dictionary with strategy information
        """
        pass

    def get_priority(self) -> int:
        """Get priority of this strategy (lower = higher priority).

        Returns:
            Priority value
        """
        return 100  # Default priority


class LUDecompositionStrategy(MatrixSolverStrategy):
    """LU decomposition strategy for general square matrices."""

    def can_handle(self, matrix: np.ndarray, vector: Optional[np.ndarray] = None) -> bool:
        """Check if LU decomposition can handle this matrix."""
        # Can handle any square matrix that's not singular
        if matrix.shape[0] != matrix.shape[1]:
            return False

        # Check if matrix is not singular
        try:
            det = np.linalg.det(matrix)
            return abs(det) > 1e-12
        except:
            return False

    def solve(self, matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
        """Solve using LU decomposition."""
        try:
            # Perform LU decomposition with partial pivoting
            P, L, U = lu(matrix)

            # Solve Ly = Pb
            Pb = P @ vector
            y = np.linalg.solve(L, Pb)

            # Solve Ux = y
            x = np.linalg.solve(U, y)

            return x

        except Exception as e:
            raise ComputationError(f"LU decomposition failed: {str(e)}")

    def get_info(self) -> Dict[str, Any]:
        """Get LU decomposition strategy information."""
        return {
            "name": "LU Decomposition",
            "description": "General purpose solver using LU decomposition with partial pivoting",
            "complexity": "O(n³)",
            "suitable_for": "General square matrices",
            "advantages": ["Stable with partial pivoting", "Good for multiple right-hand sides"],
            "disadvantages": ["Not suitable for singular matrices"],
        }

    def get_priority(self) -> int:
        """LU decomposition has medium priority."""
        return 50


class CholeskyStrategy(MatrixSolverStrategy):
    """Cholesky decomposition strategy for positive definite matrices."""

    def can_handle(self, matrix: np.ndarray, vector: Optional[np.ndarray] = None) -> bool:
        """Check if Cholesky decomposition can handle this matrix."""
        # Must be square
        if matrix.shape[0] != matrix.shape[1]:
            return False

        # Check if matrix is symmetric
        if not np.allclose(matrix, matrix.T, rtol=1e-10):
            return False

        # Check if matrix is positive definite
        try:
            eigenvals = np.linalg.eigvals(matrix)
            return np.all(eigenvals > 1e-12)
        except:
            return False

    def solve(self, matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
        """Solve using Cholesky decomposition."""
        try:
            # Perform Cholesky decomposition: A = L * L.T
            L = cholesky(matrix, lower=True)

            # Solve Ly = b
            y = np.linalg.solve(L, vector)

            # Solve L.T * x = y
            x = np.linalg.solve(L.T, y)

            return x

        except Exception as e:
            raise ComputationError(f"Cholesky decomposition failed: {str(e)}")

    def get_info(self) -> Dict[str, Any]:
        """Get Cholesky strategy information."""
        return {
            "name": "Cholesky Decomposition",
            "description": "Efficient solver for symmetric positive definite matrices",
            "complexity": "O(n³/3)",
            "suitable_for": "Symmetric positive definite matrices",
            "advantages": ["Twice as fast as LU", "Numerically stable", "Lower memory usage"],
            "disadvantages": ["Only for positive definite matrices"],
        }

    def get_priority(self) -> int:
        """Cholesky has high priority for suitable matrices."""
        return 10


class QRDecompositionStrategy(MatrixSolverStrategy):
    """QR decomposition strategy for overdetermined systems."""

    def can_handle(self, matrix: np.ndarray, vector: Optional[np.ndarray] = None) -> bool:
        """Check if QR decomposition can handle this matrix."""
        # Can handle any matrix (including non-square)
        # Particularly good for overdetermined systems (m > n)
        return matrix.shape[0] >= matrix.shape[1]

    def solve(self, matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
        """Solve using QR decomposition."""
        try:
            # Perform QR decomposition: A = Q * R
            Q, R = qr(matrix)

            # Solve R * x = Q.T * b
            Qtb = Q.T @ vector

            # R is upper triangular, solve using back substitution
            n = R.shape[1]
            x = np.linalg.solve(R[:n, :n], Qtb[:n])

            return x

        except Exception as e:
            raise ComputationError(f"QR decomposition failed: {str(e)}")

    def get_info(self) -> Dict[str, Any]:
        """Get QR strategy information."""
        return {
            "name": "QR Decomposition",
            "description": "Solver using QR decomposition, good for overdetermined systems",
            "complexity": "O(mn²)",
            "suitable_for": "Overdetermined systems (m ≥ n), least squares problems",
            "advantages": ["Handles overdetermined systems", "Numerically stable"],
            "disadvantages": ["Slower than LU for square matrices"],
        }

    def get_priority(self) -> int:
        """QR has medium-low priority for square matrices, higher for overdetermined."""
        return 60


class SVDStrategy(MatrixSolverStrategy):
    """SVD strategy for rank-deficient and ill-conditioned matrices."""

    def can_handle(self, matrix: np.ndarray, vector: Optional[np.ndarray] = None) -> bool:
        """Check if SVD can handle this matrix."""
        # SVD can handle any matrix
        return True

    def solve(self, matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
        """Solve using SVD (pseudo-inverse)."""
        try:
            # Perform SVD: A = U * S * V.T
            U, s, Vt = svd(matrix, full_matrices=False)

            # Calculate pseudo-inverse using SVD
            # A+ = V * S+ * U.T where S+ is pseudo-inverse of diagonal matrix S

            # Threshold for singular values
            threshold = 1e-12 * max(matrix.shape) * s[0]

            # Create pseudo-inverse of S
            s_inv = np.zeros_like(s)
            s_inv[s > threshold] = 1.0 / s[s > threshold]

            # Calculate solution: x = A+ * b
            x = Vt.T @ (s_inv * (U.T @ vector))

            return x

        except Exception as e:
            raise ComputationError(f"SVD solution failed: {str(e)}")

    def get_info(self) -> Dict[str, Any]:
        """Get SVD strategy information."""
        return {
            "name": "SVD (Singular Value Decomposition)",
            "description": "Most robust solver using pseudo-inverse, handles rank-deficient matrices",
            "complexity": "O(mn²)",
            "suitable_for": "Rank-deficient matrices, ill-conditioned systems, any matrix",
            "advantages": [
                "Handles any matrix",
                "Most numerically stable",
                "Provides minimum norm solution",
            ],
            "disadvantages": ["Slowest method", "May be overkill for well-conditioned matrices"],
        }

    def get_priority(self) -> int:
        """SVD has lowest priority (fallback strategy)."""
        return 90


class IterativeStrategy(MatrixSolverStrategy):
    """Iterative strategy for large sparse matrices."""

    def __init__(self, method="cg", max_iter=1000, tol=1e-6):
        """Initialize iterative strategy.

        Args:
            method: Iterative method ('cg', 'gmres', 'bicgstab')
            max_iter: Maximum number of iterations
            tol: Convergence tolerance
        """
        self.method = method
        self.max_iter = max_iter
        self.tol = tol

    def can_handle(self, matrix: np.ndarray, vector: Optional[np.ndarray] = None) -> bool:
        """Check if iterative method can handle this matrix."""
        # Good for large matrices
        if matrix.shape[0] < 100:
            return False

        # For CG, matrix must be symmetric positive definite
        if self.method == "cg":
            if matrix.shape[0] != matrix.shape[1]:
                return False
            if not np.allclose(matrix, matrix.T, rtol=1e-10):
                return False
            try:
                eigenvals = np.linalg.eigvals(matrix)
                return np.all(eigenvals > 1e-12)
            except:
                return False

        # GMRES and BiCGSTAB can handle general matrices
        return matrix.shape[0] == matrix.shape[1]

    def solve(self, matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
        """Solve using iterative method."""
        try:
            from scipy.sparse.linalg import bicgstab, cg, gmres

            if self.method == "cg":
                x, info = cg(matrix, vector, maxiter=self.max_iter, tol=self.tol)
            elif self.method == "gmres":
                x, info = gmres(matrix, vector, maxiter=self.max_iter, tol=self.tol)
            elif self.method == "bicgstab":
                x, info = bicgstab(matrix, vector, maxiter=self.max_iter, tol=self.tol)
            else:
                raise ValidationError(f"Unknown iterative method: {self.method}")

            if info != 0:
                raise ComputationError(f"Iterative method did not converge (info={info})")

            return x

        except Exception as e:
            raise ComputationError(f"Iterative solution failed: {str(e)}")

    def get_info(self) -> Dict[str, Any]:
        """Get iterative strategy information."""
        return {
            "name": f"Iterative ({self.method.upper()})",
            "description": f"Iterative solver using {self.method.upper()} method",
            "complexity": "O(n²) per iteration",
            "suitable_for": "Large sparse matrices",
            "advantages": ["Memory efficient", "Good for sparse matrices"],
            "disadvantages": [
                "May not converge",
                "Requires good preconditioner for difficult problems",
            ],
            "parameters": {
                "method": self.method,
                "max_iter": self.max_iter,
                "tolerance": self.tol,
            },
        }

    def get_priority(self) -> int:
        """Iterative methods have low priority for general use."""
        return 70


class MatrixSolverContext:
    """Context for selecting and executing appropriate matrix solving strategy."""

    def __init__(self):
        """Initialize solver context with available strategies."""
        self.strategies = [
            CholeskyStrategy(),
            LUDecompositionStrategy(),
            QRDecompositionStrategy(),
            IterativeStrategy("cg"),
            SVDStrategy(),  # Fallback strategy
        ]

    def add_strategy(self, strategy: MatrixSolverStrategy) -> None:
        """Add a new strategy to the context.

        Args:
            strategy: Strategy to add
        """
        self.strategies.append(strategy)
        # Sort by priority
        self.strategies.sort(key=lambda s: s.get_priority())

    def solve(self, matrix: np.ndarray, vector: np.ndarray) -> Dict[str, Any]:
        """Select and execute appropriate solving strategy.

        Args:
            matrix: Coefficient matrix A
            vector: Right-hand side vector b

        Returns:
            Dictionary with solution and metadata
        """
        if matrix.shape[0] != len(vector):
            raise ValidationError("Matrix rows must equal vector length")

        # Try strategies in priority order
        for strategy in self.strategies:
            if strategy.can_handle(matrix, vector):
                try:
                    solution = strategy.solve(matrix, vector)

                    # Verify solution quality
                    residual = np.linalg.norm(matrix @ solution - vector)
                    condition_number = np.linalg.cond(matrix)

                    return {
                        "solution": solution.tolist(),
                        "strategy_used": strategy.get_info()["name"],
                        "strategy_info": strategy.get_info(),
                        "residual_norm": float(residual),
                        "condition_number": float(condition_number),
                        "matrix_shape": matrix.shape,
                        "well_conditioned": condition_number < 1e12,
                    }

                except ComputationError:
                    # Try next strategy
                    continue

        # If no strategy worked
        raise ComputationError("No suitable strategy found for solving the linear system")

    def get_best_strategy(
        self, matrix: np.ndarray, vector: Optional[np.ndarray] = None
    ) -> MatrixSolverStrategy:
        """Get the best strategy for a given matrix.

        Args:
            matrix: Input matrix
            vector: Optional vector

        Returns:
            Best strategy for the matrix
        """
        for strategy in self.strategies:
            if strategy.can_handle(matrix, vector):
                return strategy

        # Return SVD as fallback
        return SVDStrategy()

    def analyze_matrix(self, matrix: np.ndarray) -> Dict[str, Any]:
        """Analyze matrix properties and recommend strategies.

        Args:
            matrix: Matrix to analyze

        Returns:
            Dictionary with matrix analysis and strategy recommendations
        """
        analysis = {
            "shape": matrix.shape,
            "square": matrix.shape[0] == matrix.shape[1],
            "symmetric": False,
            "positive_definite": False,
            "condition_number": None,
            "rank": None,
            "determinant": None,
            "suitable_strategies": [],
        }

        try:
            # Check if square
            if analysis["square"]:
                analysis["determinant"] = float(np.linalg.det(matrix))
                analysis["condition_number"] = float(np.linalg.cond(matrix))

                # Check symmetry
                analysis["symmetric"] = np.allclose(matrix, matrix.T, rtol=1e-10)

                # Check positive definiteness
                if analysis["symmetric"]:
                    try:
                        eigenvals = np.linalg.eigvals(matrix)
                        analysis["positive_definite"] = np.all(eigenvals > 1e-12)
                    except:
                        pass

            # Calculate rank
            analysis["rank"] = int(np.linalg.matrix_rank(matrix))

            # Find suitable strategies
            for strategy in self.strategies:
                if strategy.can_handle(matrix):
                    strategy_info = strategy.get_info()
                    strategy_info["priority"] = strategy.get_priority()
                    analysis["suitable_strategies"].append(strategy_info)

            # Sort by priority
            analysis["suitable_strategies"].sort(key=lambda s: s["priority"])

        except Exception as e:
            analysis["error"] = str(e)

        return analysis
