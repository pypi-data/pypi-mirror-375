"""Statistics service for statistical operations."""

import statistics
from typing import Any, Dict, List, Union

import numpy as np
from scipy import stats

from ..core.errors.exceptions import ComputationError, ValidationError
from .base import BaseService


class StatisticsService(BaseService):
    """Service for statistical operations and analysis."""

    def __init__(self, config=None, cache=None):
        """Initialize statistics service."""
        super().__init__(config, cache)

    async def process(self, operation: str, params: Dict[str, Any]) -> Any:
        """Process statistical operation.

        Args:
            operation: Name of the statistical operation
            params: Parameters for the operation

        Returns:
            Result of the statistical operation
        """
        operation_map = {
            "mean": self.calculate_mean,
            "median": self.calculate_median,
            "mode": self.calculate_mode,
            "variance": self.calculate_variance,
            "std_dev": self.calculate_standard_deviation,
            "range": self.calculate_range,
            "quartiles": self.calculate_quartiles,
            "percentile": self.calculate_percentile,
            "correlation": self.calculate_correlation,
            "covariance": self.calculate_covariance,
            "regression": self.linear_regression,
            "histogram": self.create_histogram,
            "normal_test": self.test_normality,
            "t_test": self.t_test,
            "chi_square": self.chi_square_test,
            "anova": self.anova_test,
            "descriptive_stats": self.descriptive_statistics,
        }

        if operation not in operation_map:
            raise ValidationError(f"Unknown statistical operation: {operation}")

        return await operation_map[operation](params)

    def _validate_data(self, data: List[Union[int, float]], name: str = "data") -> List[float]:
        """Validate statistical data.

        Args:
            data: List of numerical values
            name: Name of the data for error messages

        Returns:
            Validated list of floats
        """
        if not data:
            raise ValidationError(f"{name} cannot be empty")

        if not isinstance(data, list):
            raise ValidationError(f"{name} must be a list")

        try:
            return [float(x) for x in data]
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid {name} format: all values must be numeric")

    async def calculate_mean(self, params: Dict[str, Any]) -> float:
        """Calculate arithmetic mean.

        Args:
            params: Dictionary containing 'data' list

        Returns:
            Mean of the data
        """
        data = params.get("data")
        if data is None:
            raise ValidationError("Data is required for mean calculation")

        validated_data = self._validate_data(data)

        try:
            return statistics.mean(validated_data)
        except statistics.StatisticsError as e:
            raise ComputationError(f"Mean calculation failed: {str(e)}")

    async def calculate_median(self, params: Dict[str, Any]) -> float:
        """Calculate median.

        Args:
            params: Dictionary containing 'data' list

        Returns:
            Median of the data
        """
        data = params.get("data")
        if data is None:
            raise ValidationError("Data is required for median calculation")

        validated_data = self._validate_data(data)

        try:
            return statistics.median(validated_data)
        except statistics.StatisticsError as e:
            raise ComputationError(f"Median calculation failed: {str(e)}")

    async def calculate_mode(self, params: Dict[str, Any]) -> Union[float, List[float]]:
        """Calculate mode.

        Args:
            params: Dictionary containing 'data' list

        Returns:
            Mode(s) of the data
        """
        data = params.get("data")
        if data is None:
            raise ValidationError("Data is required for mode calculation")

        validated_data = self._validate_data(data)

        try:
            # Use scipy.stats.mode for better handling of multimodal data
            mode_result = stats.mode(validated_data, keepdims=False)

            if hasattr(mode_result, "mode"):
                # Newer scipy versions
                modes = mode_result.mode
                counts = mode_result.count
            else:
                # Older scipy versions
                modes = mode_result[0]
                counts = mode_result[1]

            # Handle single mode vs multiple modes
            if isinstance(modes, np.ndarray):
                if len(modes) == 1:
                    return float(modes[0])
                else:
                    return [float(m) for m in modes]
            else:
                return float(modes)

        except Exception as e:
            raise ComputationError(f"Mode calculation failed: {str(e)}")

    async def calculate_variance(self, params: Dict[str, Any]) -> float:
        """Calculate variance.

        Args:
            params: Dictionary containing 'data' list and optional 'population' flag

        Returns:
            Variance of the data
        """
        data = params.get("data")
        population = params.get("population", False)

        if data is None:
            raise ValidationError("Data is required for variance calculation")

        validated_data = self._validate_data(data)

        if len(validated_data) < 2:
            raise ValidationError("At least 2 data points are required for variance calculation")

        try:
            if population:
                return statistics.pvariance(validated_data)
            else:
                return statistics.variance(validated_data)
        except statistics.StatisticsError as e:
            raise ComputationError(f"Variance calculation failed: {str(e)}")

    async def calculate_standard_deviation(self, params: Dict[str, Any]) -> float:
        """Calculate standard deviation.

        Args:
            params: Dictionary containing 'data' list and optional 'population' flag

        Returns:
            Standard deviation of the data
        """
        data = params.get("data")
        population = params.get("population", False)

        if data is None:
            raise ValidationError("Data is required for standard deviation calculation")

        validated_data = self._validate_data(data)

        if len(validated_data) < 2:
            raise ValidationError(
                "At least 2 data points are required for standard deviation calculation"
            )

        try:
            if population:
                return statistics.pstdev(validated_data)
            else:
                return statistics.stdev(validated_data)
        except statistics.StatisticsError as e:
            raise ComputationError(f"Standard deviation calculation failed: {str(e)}")

    async def calculate_range(self, params: Dict[str, Any]) -> Dict[str, float]:
        """Calculate range statistics.

        Args:
            params: Dictionary containing 'data' list

        Returns:
            Dictionary with min, max, and range
        """
        data = params.get("data")
        if data is None:
            raise ValidationError("Data is required for range calculation")

        validated_data = self._validate_data(data)

        try:
            min_val = min(validated_data)
            max_val = max(validated_data)
            range_val = max_val - min_val

            return {"min": min_val, "max": max_val, "range": range_val}
        except Exception as e:
            raise ComputationError(f"Range calculation failed: {str(e)}")

    async def calculate_quartiles(self, params: Dict[str, Any]) -> Dict[str, float]:
        """Calculate quartiles.

        Args:
            params: Dictionary containing 'data' list

        Returns:
            Dictionary with Q1, Q2 (median), Q3, and IQR
        """
        data = params.get("data")
        if data is None:
            raise ValidationError("Data is required for quartile calculation")

        validated_data = self._validate_data(data)

        if len(validated_data) < 4:
            raise ValidationError("At least 4 data points are required for quartile calculation")

        try:
            q1 = np.percentile(validated_data, 25)
            q2 = np.percentile(validated_data, 50)  # median
            q3 = np.percentile(validated_data, 75)
            iqr = q3 - q1

            return {"Q1": float(q1), "Q2": float(q2), "Q3": float(q3), "IQR": float(iqr)}
        except Exception as e:
            raise ComputationError(f"Quartile calculation failed: {str(e)}")

    async def calculate_percentile(self, params: Dict[str, Any]) -> float:
        """Calculate specific percentile.

        Args:
            params: Dictionary containing 'data' list and 'percentile' value

        Returns:
            Value at the specified percentile
        """
        data = params.get("data")
        percentile = params.get("percentile")

        if data is None:
            raise ValidationError("Data is required for percentile calculation")

        if percentile is None:
            raise ValidationError("Percentile value is required")

        if not 0 <= percentile <= 100:
            raise ValidationError("Percentile must be between 0 and 100")

        validated_data = self._validate_data(data)

        try:
            result = np.percentile(validated_data, percentile)
            return float(result)
        except Exception as e:
            raise ComputationError(f"Percentile calculation failed: {str(e)}")

    async def calculate_correlation(self, params: Dict[str, Any]) -> float:
        """Calculate correlation coefficient.

        Args:
            params: Dictionary containing 'x_data' and 'y_data' lists

        Returns:
            Pearson correlation coefficient
        """
        x_data = params.get("x_data")
        y_data = params.get("y_data")

        if x_data is None or y_data is None:
            raise ValidationError(
                "Both x_data and y_data are required for correlation calculation"
            )

        x_validated = self._validate_data(x_data, "x_data")
        y_validated = self._validate_data(y_data, "y_data")

        if len(x_validated) != len(y_validated):
            raise ValidationError("x_data and y_data must have the same length")

        if len(x_validated) < 2:
            raise ValidationError(
                "At least 2 data points are required for correlation calculation"
            )

        try:
            correlation, _ = stats.pearsonr(x_validated, y_validated)
            return float(correlation)
        except Exception as e:
            raise ComputationError(f"Correlation calculation failed: {str(e)}")

    async def calculate_covariance(self, params: Dict[str, Any]) -> float:
        """Calculate covariance.

        Args:
            params: Dictionary containing 'x_data' and 'y_data' lists

        Returns:
            Covariance between x and y data
        """
        x_data = params.get("x_data")
        y_data = params.get("y_data")

        if x_data is None or y_data is None:
            raise ValidationError("Both x_data and y_data are required for covariance calculation")

        x_validated = self._validate_data(x_data, "x_data")
        y_validated = self._validate_data(y_data, "y_data")

        if len(x_validated) != len(y_validated):
            raise ValidationError("x_data and y_data must have the same length")

        if len(x_validated) < 2:
            raise ValidationError("At least 2 data points are required for covariance calculation")

        try:
            covariance_matrix = np.cov(x_validated, y_validated)
            covariance = covariance_matrix[0, 1]
            return float(covariance)
        except Exception as e:
            raise ComputationError(f"Covariance calculation failed: {str(e)}")

    async def linear_regression(self, params: Dict[str, Any]) -> Dict[str, float]:
        """Perform linear regression.

        Args:
            params: Dictionary containing 'x_data' and 'y_data' lists

        Returns:
            Dictionary with slope, intercept, r_value, p_value, and std_err
        """
        x_data = params.get("x_data")
        y_data = params.get("y_data")

        if x_data is None or y_data is None:
            raise ValidationError("Both x_data and y_data are required for linear regression")

        x_validated = self._validate_data(x_data, "x_data")
        y_validated = self._validate_data(y_data, "y_data")

        if len(x_validated) != len(y_validated):
            raise ValidationError("x_data and y_data must have the same length")

        if len(x_validated) < 2:
            raise ValidationError("At least 2 data points are required for linear regression")

        try:
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                x_validated, y_validated
            )

            return {
                "slope": float(slope),
                "intercept": float(intercept),
                "r_value": float(r_value),
                "r_squared": float(r_value**2),
                "p_value": float(p_value),
                "std_err": float(std_err),
            }
        except Exception as e:
            raise ComputationError(f"Linear regression failed: {str(e)}")

    async def create_histogram(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create histogram data.

        Args:
            params: Dictionary containing 'data' list and optional 'bins' count

        Returns:
            Dictionary with histogram data
        """
        data = params.get("data")
        bins = params.get("bins", 10)

        if data is None:
            raise ValidationError("Data is required for histogram creation")

        validated_data = self._validate_data(data)

        try:
            counts, bin_edges = np.histogram(validated_data, bins=bins)

            # Calculate bin centers
            bin_centers = [
                (bin_edges[i] + bin_edges[i + 1]) / 2 for i in range(len(bin_edges) - 1)
            ]

            return {
                "counts": counts.tolist(),
                "bin_edges": bin_edges.tolist(),
                "bin_centers": bin_centers,
                "total_count": int(np.sum(counts)),
            }
        except Exception as e:
            raise ComputationError(f"Histogram creation failed: {str(e)}")

    async def test_normality(self, params: Dict[str, Any]) -> Dict[str, float]:
        """Test for normality using Shapiro-Wilk test.

        Args:
            params: Dictionary containing 'data' list

        Returns:
            Dictionary with test statistic and p-value
        """
        data = params.get("data")
        if data is None:
            raise ValidationError("Data is required for normality test")

        validated_data = self._validate_data(data)

        if len(validated_data) < 3:
            raise ValidationError("At least 3 data points are required for normality test")

        if len(validated_data) > 5000:
            raise ValidationError("Shapiro-Wilk test requires 5000 or fewer data points")

        try:
            statistic, p_value = stats.shapiro(validated_data)

            return {
                "statistic": float(statistic),
                "p_value": float(p_value),
                "is_normal": p_value > 0.05,  # Common significance level
            }
        except Exception as e:
            raise ComputationError(f"Normality test failed: {str(e)}")

    async def t_test(self, params: Dict[str, Any]) -> Dict[str, float]:
        """Perform t-test.

        Args:
            params: Dictionary containing test parameters

        Returns:
            Dictionary with test results
        """
        test_type = params.get("type", "one_sample")

        if test_type == "one_sample":
            return await self._one_sample_t_test(params)
        elif test_type == "two_sample":
            return await self._two_sample_t_test(params)
        else:
            raise ValidationError(f"Unknown t-test type: {test_type}")

    async def _one_sample_t_test(self, params: Dict[str, Any]) -> Dict[str, float]:
        """Perform one-sample t-test."""
        data = params.get("data")
        population_mean = params.get("population_mean", 0)

        if data is None:
            raise ValidationError("Data is required for one-sample t-test")

        validated_data = self._validate_data(data)

        if len(validated_data) < 2:
            raise ValidationError("At least 2 data points are required for t-test")

        try:
            statistic, p_value = stats.ttest_1samp(validated_data, population_mean)

            return {
                "statistic": float(statistic),
                "p_value": float(p_value),
                "degrees_of_freedom": len(validated_data) - 1,
            }
        except Exception as e:
            raise ComputationError(f"One-sample t-test failed: {str(e)}")

    async def _two_sample_t_test(self, params: Dict[str, Any]) -> Dict[str, float]:
        """Perform two-sample t-test."""
        data1 = params.get("data1")
        data2 = params.get("data2")
        equal_var = params.get("equal_var", True)

        if data1 is None or data2 is None:
            raise ValidationError("Both data1 and data2 are required for two-sample t-test")

        validated_data1 = self._validate_data(data1, "data1")
        validated_data2 = self._validate_data(data2, "data2")

        if len(validated_data1) < 2 or len(validated_data2) < 2:
            raise ValidationError("At least 2 data points are required in each group for t-test")

        try:
            statistic, p_value = stats.ttest_ind(
                validated_data1, validated_data2, equal_var=equal_var
            )

            return {
                "statistic": float(statistic),
                "p_value": float(p_value),
                "degrees_of_freedom": len(validated_data1) + len(validated_data2) - 2,
            }
        except Exception as e:
            raise ComputationError(f"Two-sample t-test failed: {str(e)}")

    async def chi_square_test(self, params: Dict[str, Any]) -> Dict[str, float]:
        """Perform chi-square test.

        Args:
            params: Dictionary containing observed frequencies

        Returns:
            Dictionary with test results
        """
        observed = params.get("observed")
        expected = params.get("expected")

        if observed is None:
            raise ValidationError("Observed frequencies are required for chi-square test")

        try:
            observed_array = np.array(observed)

            if expected is not None:
                expected_array = np.array(expected)
                statistic, p_value = stats.chisquare(observed_array, expected_array)
            else:
                statistic, p_value = stats.chisquare(observed_array)

            degrees_of_freedom = len(observed_array) - 1

            return {
                "statistic": float(statistic),
                "p_value": float(p_value),
                "degrees_of_freedom": degrees_of_freedom,
            }
        except Exception as e:
            raise ComputationError(f"Chi-square test failed: {str(e)}")

    async def anova_test(self, params: Dict[str, Any]) -> Dict[str, float]:
        """Perform one-way ANOVA test.

        Args:
            params: Dictionary containing groups of data

        Returns:
            Dictionary with ANOVA results
        """
        groups = params.get("groups")

        if groups is None or len(groups) < 2:
            raise ValidationError("At least 2 groups are required for ANOVA test")

        try:
            validated_groups = []
            for i, group in enumerate(groups):
                validated_group = self._validate_data(group, f"group_{i}")
                if len(validated_group) < 2:
                    raise ValidationError(f"Group {i} must have at least 2 data points")
                validated_groups.append(validated_group)

            statistic, p_value = stats.f_oneway(*validated_groups)

            # Calculate degrees of freedom
            k = len(validated_groups)  # number of groups
            n = sum(len(group) for group in validated_groups)  # total observations
            df_between = k - 1
            df_within = n - k

            return {
                "statistic": float(statistic),
                "p_value": float(p_value),
                "df_between": df_between,
                "df_within": df_within,
                "df_total": n - 1,
            }
        except Exception as e:
            raise ComputationError(f"ANOVA test failed: {str(e)}")

    async def descriptive_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive descriptive statistics.

        Args:
            params: Dictionary containing 'data' list

        Returns:
            Dictionary with comprehensive statistics
        """
        data = params.get("data")
        if data is None:
            raise ValidationError("Data is required for descriptive statistics")

        validated_data = self._validate_data(data)

        try:
            n = len(validated_data)
            mean_val = statistics.mean(validated_data)
            median_val = statistics.median(validated_data)

            # Calculate other statistics
            min_val = min(validated_data)
            max_val = max(validated_data)
            range_val = max_val - min_val

            if n >= 2:
                variance_val = statistics.variance(validated_data)
                std_dev_val = statistics.stdev(validated_data)
            else:
                variance_val = 0
                std_dev_val = 0

            # Quartiles
            if n >= 4:
                q1 = np.percentile(validated_data, 25)
                q3 = np.percentile(validated_data, 75)
                iqr = q3 - q1
            else:
                q1 = q3 = iqr = None

            # Skewness and kurtosis
            if n >= 3:
                skewness = float(stats.skew(validated_data))
                kurtosis = float(stats.kurtosis(validated_data))
            else:
                skewness = kurtosis = None

            result = {
                "count": n,
                "mean": mean_val,
                "median": median_val,
                "min": min_val,
                "max": max_val,
                "range": range_val,
                "variance": variance_val,
                "std_dev": std_dev_val,
            }

            if q1 is not None:
                result.update({"q1": float(q1), "q3": float(q3), "iqr": float(iqr)})

            if skewness is not None:
                result.update({"skewness": skewness, "kurtosis": kurtosis})

            return result

        except Exception as e:
            raise ComputationError(f"Descriptive statistics calculation failed: {str(e)}")
