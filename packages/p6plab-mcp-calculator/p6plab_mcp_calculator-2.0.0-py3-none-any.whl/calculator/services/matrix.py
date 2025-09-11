"""Matrix operations service."""

from typing import Any, Dict, List

import numpy as np

from ..core.errors.exceptions import ComputationError, ValidationError
from .base import BaseService


class MatrixService(BaseService):
    """Service for matrix operations with strategy pattern support."""

    def __init__(self, config=None, cache=None):
        """Initialize matrix service."""
        super().__init__(config, cache)

    async def process(self, operation: str, params: Dict[str, Any]) -> Any:
        """Process matrix operation.

        Args:
            operation: Name of the matrix operation
            params: Parameters for the operation

        Returns:
            Result of the matrix operation
        """
        operation_map = {
            "add": self.add_matrices,
            "subtract": self.subtract_matrices,
            "multiply": self.multiply_matrices,
            "transpose": self.transpose_matrix,
            "determinant": self.calculate_determinant,
            "inverse": self.calculate_inverse,
            "eigenvalues": self.calculate_eigenvalues,
            "eigenvectors": self.calculate_eigenvectors,
            "rank": self.calculate_rank,
            "trace": self.calculate_trace,
            "norm": self.calculate_norm,
            "solve": self.solve_linear_system,
            "lu_decomposition": self.lu_decomposition,
            "qr_decomposition": self.qr_decomposition,
            "svd": self.singular_value_decomposition,
            "cholesky": self.cholesky_decomposition,
        }

        if operation not in operation_map:
            raise ValidationError(f"Unknown matrix operation: {operation}")

        return await operation_map[operation](params)

    def _validate_matrix(self, matrix: List[List[float]], name: str = "matrix") -> np.ndarray:
        """Validate and convert matrix to numpy array.

        Args:
            matrix: Matrix as list of lists
            name: Name of the matrix for error messages

        Returns:
            Validated numpy array
        """
        if not matrix:
            raise ValidationError(f"{name} cannot be empty")

        if not all(isinstance(row, list) for row in matrix):
            raise ValidationError(f"{name} must be a list of lists")

        # Check if all rows have the same length
        row_length = len(matrix[0])
        if not all(len(row) == row_length for row in matrix):
            raise ValidationError(f"All rows in {name} must have the same length")

        try:
            return np.array(matrix, dtype=float)
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid {name} format: {str(e)}")

    async def add_matrices(self, params: Dict[str, Any]) -> List[List[float]]:
        """Add two matrices.

        Args:
            params: Dictionary containing 'matrix_a' and 'matrix_b'

        Returns:
            Sum of the matrices
        """
        matrix_a = params.get("matrix_a")
        matrix_b = params.get("matrix_b")

        if matrix_a is None or matrix_b is None:
            raise ValidationError("Both matrix_a and matrix_b are required for addition")

        try:
            a = self._validate_matrix(matrix_a, "matrix_a")
            b = self._validate_matrix(matrix_b, "matrix_b")

            if a.shape != b.shape:
                raise ValidationError("Matrices must have the same dimensions for addition")

            result = a + b
            return result.tolist()

        except np.linalg.LinAlgError as e:
            raise ComputationError(f"Matrix addition failed: {str(e)}")

    async def subtract_matrices(self, params: Dict[str, Any]) -> List[List[float]]:
        """Subtract two matrices.

        Args:
            params: Dictionary containing 'matrix_a' and 'matrix_b'

        Returns:
            Difference of the matrices (matrix_a - matrix_b)
        """
        matrix_a = params.get("matrix_a")
        matrix_b = params.get("matrix_b")

        if matrix_a is None or matrix_b is None:
            raise ValidationError("Both matrix_a and matrix_b are required for subtraction")

        try:
            a = self._validate_matrix(matrix_a, "matrix_a")
            b = self._validate_matrix(matrix_b, "matrix_b")

            if a.shape != b.shape:
                raise ValidationError("Matrices must have the same dimensions for subtraction")

            result = a - b
            return result.tolist()

        except np.linalg.LinAlgError as e:
            raise ComputationError(f"Matrix subtraction failed: {str(e)}")

    async def multiply_matrices(self, params: Dict[str, Any]) -> List[List[float]]:
        """Multiply two matrices.

        Args:
            params: Dictionary containing 'matrix_a' and 'matrix_b'

        Returns:
            Product of the matrices
        """
        matrix_a = params.get("matrix_a")
        matrix_b = params.get("matrix_b")

        if matrix_a is None or matrix_b is None:
            raise ValidationError("Both matrix_a and matrix_b are required for multiplication")

        try:
            a = self._validate_matrix(matrix_a, "matrix_a")
            b = self._validate_matrix(matrix_b, "matrix_b")

            if a.shape[1] != b.shape[0]:
                raise ValidationError(
                    "Number of columns in matrix_a must equal number of rows in matrix_b"
                )

            result = np.dot(a, b)
            return result.tolist()

        except np.linalg.LinAlgError as e:
            raise ComputationError(f"Matrix multiplication failed: {str(e)}")

    async def transpose_matrix(self, params: Dict[str, Any]) -> List[List[float]]:
        """Transpose a matrix.

        Args:
            params: Dictionary containing 'matrix'

        Returns:
            Transposed matrix
        """
        matrix = params.get("matrix")

        if matrix is None:
            raise ValidationError("Matrix is required for transpose operation")

        try:
            m = self._validate_matrix(matrix, "matrix")
            result = m.T
            return result.tolist()

        except Exception as e:
            raise ComputationError(f"Matrix transpose failed: {str(e)}")

    async def calculate_determinant(self, params: Dict[str, Any]) -> float:
        """Calculate matrix determinant.

        Args:
            params: Dictionary containing 'matrix'

        Returns:
            Determinant of the matrix
        """
        matrix = params.get("matrix")

        if matrix is None:
            raise ValidationError("Matrix is required for determinant calculation")

        try:
            m = self._validate_matrix(matrix, "matrix")

            if m.shape[0] != m.shape[1]:
                raise ValidationError("Matrix must be square for determinant calculation")

            det = np.linalg.det(m)
            return float(det)

        except np.linalg.LinAlgError as e:
            raise ComputationError(f"Determinant calculation failed: {str(e)}")

    async def calculate_inverse(self, params: Dict[str, Any]) -> List[List[float]]:
        """Calculate matrix inverse.

        Args:
            params: Dictionary containing 'matrix'

        Returns:
            Inverse of the matrix
        """
        matrix = params.get("matrix")

        if matrix is None:
            raise ValidationError("Matrix is required for inverse calculation")

        try:
            m = self._validate_matrix(matrix, "matrix")

            if m.shape[0] != m.shape[1]:
                raise ValidationError("Matrix must be square for inverse calculation")

            # Check if matrix is singular
            det = np.linalg.det(m)
            if abs(det) < 1e-10:
                raise ComputationError("Matrix is singular and cannot be inverted")

            inverse = np.linalg.inv(m)
            return inverse.tolist()

        except np.linalg.LinAlgError as e:
            raise ComputationError(f"Matrix inverse calculation failed: {str(e)}")

    async def calculate_eigenvalues(self, params: Dict[str, Any]) -> List[complex]:
        """Calculate matrix eigenvalues.

        Args:
            params: Dictionary containing 'matrix'

        Returns:
            List of eigenvalues
        """
        matrix = params.get("matrix")

        if matrix is None:
            raise ValidationError("Matrix is required for eigenvalue calculation")

        try:
            m = self._validate_matrix(matrix, "matrix")

            if m.shape[0] != m.shape[1]:
                raise ValidationError("Matrix must be square for eigenvalue calculation")

            eigenvalues = np.linalg.eigvals(m)

            # Convert to list, handling complex numbers
            result = []
            for val in eigenvalues:
                if np.isreal(val):
                    result.append(float(val.real))
                else:
                    result.append(complex(val))

            return result

        except np.linalg.LinAlgError as e:
            raise ComputationError(f"Eigenvalue calculation failed: {str(e)}")

    async def calculate_eigenvectors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate matrix eigenvalues and eigenvectors.

        Args:
            params: Dictionary containing 'matrix'

        Returns:
            Dictionary with eigenvalues and eigenvectors
        """
        matrix = params.get("matrix")

        if matrix is None:
            raise ValidationError("Matrix is required for eigenvector calculation")

        try:
            m = self._validate_matrix(matrix, "matrix")

            if m.shape[0] != m.shape[1]:
                raise ValidationError("Matrix must be square for eigenvector calculation")

            eigenvalues, eigenvectors = np.linalg.eig(m)

            # Convert eigenvalues
            eigenvals_list = []
            for val in eigenvalues:
                if np.isreal(val):
                    eigenvals_list.append(float(val.real))
                else:
                    eigenvals_list.append(complex(val))

            # Convert eigenvectors
            eigenvecs_list = []
            for i in range(eigenvectors.shape[1]):
                vec = eigenvectors[:, i]
                if np.all(np.isreal(vec)):
                    eigenvecs_list.append(vec.real.tolist())
                else:
                    eigenvecs_list.append([complex(x) for x in vec])

            return {"eigenvalues": eigenvals_list, "eigenvectors": eigenvecs_list}

        except np.linalg.LinAlgError as e:
            raise ComputationError(f"Eigenvector calculation failed: {str(e)}")

    async def calculate_rank(self, params: Dict[str, Any]) -> int:
        """Calculate matrix rank.

        Args:
            params: Dictionary containing 'matrix'

        Returns:
            Rank of the matrix
        """
        matrix = params.get("matrix")

        if matrix is None:
            raise ValidationError("Matrix is required for rank calculation")

        try:
            m = self._validate_matrix(matrix, "matrix")
            rank = np.linalg.matrix_rank(m)
            return int(rank)

        except Exception as e:
            raise ComputationError(f"Matrix rank calculation failed: {str(e)}")

    async def calculate_trace(self, params: Dict[str, Any]) -> float:
        """Calculate matrix trace.

        Args:
            params: Dictionary containing 'matrix'

        Returns:
            Trace of the matrix
        """
        matrix = params.get("matrix")

        if matrix is None:
            raise ValidationError("Matrix is required for trace calculation")

        try:
            m = self._validate_matrix(matrix, "matrix")

            if m.shape[0] != m.shape[1]:
                raise ValidationError("Matrix must be square for trace calculation")

            trace = np.trace(m)
            return float(trace)

        except Exception as e:
            raise ComputationError(f"Matrix trace calculation failed: {str(e)}")

    async def calculate_norm(self, params: Dict[str, Any]) -> float:
        """Calculate matrix norm.

        Args:
            params: Dictionary containing 'matrix' and optional 'norm_type'

        Returns:
            Norm of the matrix
        """
        matrix = params.get("matrix")
        norm_type = params.get("norm_type", "frobenius")

        if matrix is None:
            raise ValidationError("Matrix is required for norm calculation")

        try:
            m = self._validate_matrix(matrix, "matrix")

            if norm_type.lower() == "frobenius":
                norm = np.linalg.norm(m, "fro")
            elif norm_type.lower() == "1":
                norm = np.linalg.norm(m, 1)
            elif norm_type.lower() == "2":
                norm = np.linalg.norm(m, 2)
            elif norm_type.lower() == "inf":
                norm = np.linalg.norm(m, np.inf)
            else:
                raise ValidationError(f"Unknown norm type: {norm_type}")

            return float(norm)

        except np.linalg.LinAlgError as e:
            raise ComputationError(f"Matrix norm calculation failed: {str(e)}")

    async def solve_linear_system(self, params: Dict[str, Any]) -> List[float]:
        """Solve linear system Ax = b.

        Args:
            params: Dictionary containing 'matrix_a' and 'vector_b'

        Returns:
            Solution vector x
        """
        matrix_a = params.get("matrix_a")
        vector_b = params.get("vector_b")

        if matrix_a is None or vector_b is None:
            raise ValidationError(
                "Both matrix_a and vector_b are required for solving linear system"
            )

        try:
            a = self._validate_matrix(matrix_a, "matrix_a")
            b = np.array(vector_b, dtype=float)

            if a.shape[0] != a.shape[1]:
                raise ValidationError("Matrix A must be square for linear system solving")

            if a.shape[0] != len(b):
                raise ValidationError("Matrix A rows must equal vector b length")

            # Check if system is solvable
            det = np.linalg.det(a)
            if abs(det) < 1e-10:
                raise ComputationError("Linear system has no unique solution (singular matrix)")

            solution = np.linalg.solve(a, b)
            return solution.tolist()

        except np.linalg.LinAlgError as e:
            raise ComputationError(f"Linear system solving failed: {str(e)}")

    async def lu_decomposition(self, params: Dict[str, Any]) -> Dict[str, List[List[float]]]:
        """Perform LU decomposition.

        Args:
            params: Dictionary containing 'matrix'

        Returns:
            Dictionary with L, U, and P matrices
        """
        matrix = params.get("matrix")

        if matrix is None:
            raise ValidationError("Matrix is required for LU decomposition")

        try:
            from scipy.linalg import lu

            m = self._validate_matrix(matrix, "matrix")

            if m.shape[0] != m.shape[1]:
                raise ValidationError("Matrix must be square for LU decomposition")

            P, L, U = lu(m)

            return {"P": P.tolist(), "L": L.tolist(), "U": U.tolist()}

        except Exception as e:
            raise ComputationError(f"LU decomposition failed: {str(e)}")

    async def qr_decomposition(self, params: Dict[str, Any]) -> Dict[str, List[List[float]]]:
        """Perform QR decomposition.

        Args:
            params: Dictionary containing 'matrix'

        Returns:
            Dictionary with Q and R matrices
        """
        matrix = params.get("matrix")

        if matrix is None:
            raise ValidationError("Matrix is required for QR decomposition")

        try:
            m = self._validate_matrix(matrix, "matrix")

            Q, R = np.linalg.qr(m)

            return {"Q": Q.tolist(), "R": R.tolist()}

        except np.linalg.LinAlgError as e:
            raise ComputationError(f"QR decomposition failed: {str(e)}")

    async def singular_value_decomposition(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform Singular Value Decomposition.

        Args:
            params: Dictionary containing 'matrix'

        Returns:
            Dictionary with U, S, and Vt matrices
        """
        matrix = params.get("matrix")

        if matrix is None:
            raise ValidationError("Matrix is required for SVD")

        try:
            m = self._validate_matrix(matrix, "matrix")

            U, S, Vt = np.linalg.svd(m)

            return {"U": U.tolist(), "S": S.tolist(), "Vt": Vt.tolist()}

        except np.linalg.LinAlgError as e:
            raise ComputationError(f"SVD failed: {str(e)}")

    async def cholesky_decomposition(self, params: Dict[str, Any]) -> List[List[float]]:
        """Perform Cholesky decomposition.

        Args:
            params: Dictionary containing 'matrix'

        Returns:
            Lower triangular matrix L such that A = L * L.T
        """
        matrix = params.get("matrix")

        if matrix is None:
            raise ValidationError("Matrix is required for Cholesky decomposition")

        try:
            m = self._validate_matrix(matrix, "matrix")

            if m.shape[0] != m.shape[1]:
                raise ValidationError("Matrix must be square for Cholesky decomposition")

            # Check if matrix is positive definite
            eigenvals = np.linalg.eigvals(m)
            if not np.all(eigenvals > 0):
                raise ComputationError(
                    "Matrix must be positive definite for Cholesky decomposition"
                )

            L = np.linalg.cholesky(m)
            return L.tolist()

        except np.linalg.LinAlgError as e:
            raise ComputationError(f"Cholesky decomposition failed: {str(e)}")
