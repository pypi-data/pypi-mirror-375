"""Unit tests for StatisticsService."""

import pytest

from calculator.services.statistics import StatisticsService


class TestStatisticsService:
    """Test cases for StatisticsService."""

    @pytest.fixture
    def stats_service(self):
        """Create StatisticsService instance for testing."""
        return StatisticsService()

    @pytest.mark.asyncio
    async def test_mean_calculation(self, stats_service):
        """Test mean calculation."""
        data = [1, 2, 3, 4, 5]

        result = await stats_service.process("mean", {"data": data})

        assert result == 3.0

    @pytest.mark.asyncio
    async def test_median_calculation(self, stats_service):
        """Test median calculation."""
        # Odd number of elements
        data_odd = [1, 2, 3, 4, 5]
        result = await stats_service.process("median", {"data": data_odd})
        assert result == 3.0

        # Even number of elements
        data_even = [1, 2, 3, 4]
        result = await stats_service.process("median", {"data": data_even})
        assert result == 2.5

    @pytest.mark.asyncio
    async def test_variance_calculation(self, stats_service):
        """Test variance calculation."""
        data = [1, 2, 3, 4, 5]

        # Sample variance
        result = await stats_service.process("variance", {
            "data": data,
            "population": False
        })
        assert abs(result - 2.5) < 1e-10

        # Population variance
        result = await stats_service.process("variance", {
            "data": data,
            "population": True
        })
        assert abs(result - 2.0) < 1e-10

    @pytest.mark.asyncio
    async def test_standard_deviation(self, stats_service):
        """Test standard deviation calculation."""
        data = [1, 2, 3, 4, 5]

        result = await stats_service.process("std_dev", {"data": data})

        # Should be sqrt(2.5) ≈ 1.58
        assert abs(result - 1.5811388300841898) < 1e-10

    @pytest.mark.asyncio
    async def test_correlation(self, stats_service):
        """Test correlation calculation."""
        x_data = [1, 2, 3, 4, 5]
        y_data = [2, 4, 6, 8, 10]  # Perfect positive correlation

        result = await stats_service.process("correlation", {
            "x_data": x_data,
            "y_data": y_data
        })

        assert abs(result - 1.0) < 1e-10

    @pytest.mark.asyncio
    async def test_percentile(self, stats_service):
        """Test percentile calculation."""
        data = list(range(1, 101))  # 1 to 100

        # 50th percentile should be around 50.5
        result = await stats_service.process("percentile", {
            "data": data,
            "percentile": 50
        })

        assert abs(result - 50.5) < 1.0

    @pytest.mark.asyncio
    async def test_descriptive_stats(self, stats_service):
        """Test comprehensive descriptive statistics."""
        data = [1, 2, 3, 4, 5]

        result = await stats_service.process("descriptive_stats", {"data": data})

        assert isinstance(result, dict)
        assert "mean" in result
        assert "median" in result
        assert "std_dev" in result
        assert "variance" in result
        assert "min" in result
        assert "max" in result
        assert "count" in result

    @pytest.mark.asyncio
    async def test_empty_data_error(self, stats_service):
        """Test error handling for empty data."""
        with pytest.raises(Exception):
            await stats_service.process("mean", {"data": []})

    @pytest.mark.asyncio
    async def test_invalid_data_error(self, stats_service):
        """Test error handling for invalid data."""
        with pytest.raises(Exception):
            await stats_service.process("mean", {"data": ["not", "numbers"]})

    @pytest.mark.asyncio
    async def test_correlation_different_lengths(self, stats_service):
        """Test error handling for correlation with different length arrays."""
        x_data = [1, 2, 3]
        y_data = [1, 2, 3, 4, 5]  # Different length

        with pytest.raises(Exception):
            await stats_service.process("correlation", {
                "x_data": x_data,
                "y_data": y_data
            })

    @pytest.mark.asyncio
    async def test_invalid_percentile(self, stats_service):
        """Test error handling for invalid percentile values."""
        data = [1, 2, 3, 4, 5]

        # Percentile out of range
        with pytest.raises(Exception):
            await stats_service.process("percentile", {
                "data": data,
                "percentile": 150  # Invalid: > 100
            })

        with pytest.raises(Exception):
            await stats_service.process("percentile", {
                "data": data,
                "percentile": -10  # Invalid: < 0
            })
