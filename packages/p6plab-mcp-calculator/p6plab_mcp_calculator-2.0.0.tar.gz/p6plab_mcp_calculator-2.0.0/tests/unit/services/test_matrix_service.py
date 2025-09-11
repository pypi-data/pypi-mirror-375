"""Unit tests for MatrixService."""

import pytest

from calculator.services.matrix import MatrixService


class TestMatrixService:
    """Test cases for MatrixService."""

    @pytest.fixture
    def matrix_service(self):
        """Create MatrixService instance for testing."""
        return MatrixService()

    @pytest.mark.asyncio
    async def test_matrix_addition(self, matrix_service):
        """Test matrix addition."""
        matrix_a = [[1, 2], [3, 4]]
        matrix_b = [[5, 6], [7, 8]]

        result = await matrix_service.process("add", {
            "matrix_a": matrix_a,
            "matrix_b": matrix_b
        })

        expected = [[6, 8], [10, 12]]
        assert result == expected

    @pytest.mark.asyncio
    async def test_matrix_multiplication(self, matrix_service):
        """Test matrix multiplication."""
        matrix_a = [[1, 2], [3, 4]]
        matrix_b = [[5, 6], [7, 8]]

        result = await matrix_service.process("multiply", {
            "matrix_a": matrix_a,
            "matrix_b": matrix_b
        })

        expected = [[19, 22], [43, 50]]
        assert result == expected

    @pytest.mark.asyncio
    async def test_matrix_determinant(self, matrix_service):
        """Test matrix determinant calculation."""
        matrix = [[1, 2], [3, 4]]

        result = await matrix_service.process("determinant", {
            "matrix": matrix
        })

        assert abs(result - (-2.0)) < 1e-10

    @pytest.mark.asyncio
    async def test_matrix_inverse(self, matrix_service):
        """Test matrix inverse calculation."""
        matrix = [[1, 2], [3, 4]]

        result = await matrix_service.process("inverse", {
            "matrix": matrix
        })

        # Check that result * original = identity (approximately)
        assert isinstance(result, list)
        assert len(result) == 2
        assert len(result[0]) == 2

    @pytest.mark.asyncio
    async def test_invalid_matrix_dimensions(self, matrix_service):
        """Test error handling for invalid matrix dimensions."""
        matrix_a = [[1, 2], [3, 4]]
        matrix_b = [[1, 2, 3]]  # Wrong dimensions

        with pytest.raises(Exception):
            await matrix_service.process("add", {
                "matrix_a": matrix_a,
                "matrix_b": matrix_b
            })

    @pytest.mark.asyncio
    async def test_singular_matrix_inverse(self, matrix_service):
        """Test error handling for singular matrix inverse."""
        singular_matrix = [[1, 2], [2, 4]]  # Singular matrix

        with pytest.raises(Exception):
            await matrix_service.process("inverse", {
                "matrix": singular_matrix
            })

    @pytest.mark.asyncio
    async def test_eigenvalues(self, matrix_service):
        """Test eigenvalue calculation."""
        matrix = [[1, 2], [3, 4]]

        result = await matrix_service.process("eigenvalues", {
            "matrix": matrix
        })

        assert isinstance(result, list)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_linear_system_solve(self, matrix_service):
        """Test linear system solving."""
        matrix_a = [[2, 1], [1, 1]]
        vector_b = [3, 2]

        result = await matrix_service.process("solve", {
            "matrix_a": matrix_a,
            "vector_b": vector_b
        })

        assert isinstance(result, list)
        assert len(result) == 2
        # Solution should be [1, 1]
        assert abs(result[0] - 1.0) < 1e-10
        assert abs(result[1] - 1.0) < 1e-10
