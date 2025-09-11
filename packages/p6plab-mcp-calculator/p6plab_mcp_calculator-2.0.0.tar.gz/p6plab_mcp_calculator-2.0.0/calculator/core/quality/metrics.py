"""Code quality metrics collection and monitoring."""

import ast
import inspect
import time
from dataclasses import dataclass, field
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from loguru import logger


@dataclass
class QualityMetric:
    """Individual quality metric."""

    name: str
    value: float
    threshold: float
    passed: bool
    timestamp: float = field(default_factory=time.time)
    details: Optional[Dict[str, Any]] = None


@dataclass
class ModuleQualityReport:
    """Quality report for a module."""

    module_name: str
    file_path: str
    metrics: List[QualityMetric]
    overall_score: float
    passed: bool
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "module_name": self.module_name,
            "file_path": self.file_path,
            "metrics": [
                {
                    "name": m.name,
                    "value": m.value,
                    "threshold": m.threshold,
                    "passed": m.passed,
                    "details": m.details,
                }
                for m in self.metrics
            ],
            "overall_score": self.overall_score,
            "passed": self.passed,
            "timestamp": self.timestamp,
        }


class CodeQualityMetrics:
    """Code quality metrics calculator."""

    # Quality thresholds
    THRESHOLDS = {
        "cyclomatic_complexity": 10,
        "function_length": 50,
        "class_length": 500,
        "module_length": 800,
        "nesting_depth": 4,
        "parameter_count": 7,
        "cognitive_complexity": 15,
        "maintainability_index": 70,
        "documentation_coverage": 80,
        "type_hint_coverage": 90,
    }

    @staticmethod
    def calculate_cyclomatic_complexity(source_code: str) -> int:
        """Calculate cyclomatic complexity of source code.

        Args:
            source_code: Source code to analyze

        Returns:
            Cyclomatic complexity score
        """
        try:
            tree = ast.parse(source_code)
            complexity = 1  # Base complexity

            for node in ast.walk(tree):
                # Decision points that increase complexity
                if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                    complexity += 1
                elif isinstance(node, ast.ExceptHandler):
                    complexity += 1
                elif isinstance(node, (ast.And, ast.Or)):
                    complexity += 1
                elif isinstance(node, ast.comprehension):
                    complexity += 1

            return complexity

        except SyntaxError:
            return 0

    @staticmethod
    def calculate_function_metrics(func_node: ast.FunctionDef) -> Dict[str, int]:
        """Calculate metrics for a function.

        Args:
            func_node: AST function node

        Returns:
            Dictionary of function metrics
        """
        # Count lines (excluding empty lines and comments)
        lines = 0
        for node in ast.walk(func_node):
            if hasattr(node, "lineno"):
                lines = max(lines, node.lineno - func_node.lineno + 1)

        # Count parameters
        param_count = len(func_node.args.args)
        if func_node.args.vararg:
            param_count += 1
        if func_node.args.kwarg:
            param_count += 1

        # Calculate nesting depth
        max_depth = CodeQualityMetrics._calculate_nesting_depth(func_node)

        return {"length": lines, "parameter_count": param_count, "nesting_depth": max_depth}

    @staticmethod
    def _calculate_nesting_depth(node: ast.AST, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth."""
        max_depth = current_depth

        for child in ast.iter_child_nodes(node):
            if isinstance(
                child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.With, ast.AsyncWith, ast.Try)
            ):
                child_depth = CodeQualityMetrics._calculate_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = CodeQualityMetrics._calculate_nesting_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)

        return max_depth

    @staticmethod
    def calculate_documentation_coverage(source_code: str) -> float:
        """Calculate documentation coverage percentage.

        Args:
            source_code: Source code to analyze

        Returns:
            Documentation coverage percentage (0-100)
        """
        try:
            tree = ast.parse(source_code)

            total_items = 0
            documented_items = 0

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    total_items += 1

                    # Check if has docstring
                    if (
                        node.body
                        and isinstance(node.body[0], ast.Expr)
                        and isinstance(node.body[0].value, ast.Constant)
                        and isinstance(node.body[0].value.value, str)
                    ):
                        documented_items += 1

            if total_items == 0:
                return 100.0

            return (documented_items / total_items) * 100

        except SyntaxError:
            return 0.0

    @staticmethod
    def calculate_type_hint_coverage(source_code: str) -> float:
        """Calculate type hint coverage percentage.

        Args:
            source_code: Source code to analyze

        Returns:
            Type hint coverage percentage (0-100)
        """
        try:
            tree = ast.parse(source_code)

            total_functions = 0
            typed_functions = 0

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    total_functions += 1

                    # Check for return type annotation
                    has_return_type = node.returns is not None

                    # Check for parameter type annotations
                    has_param_types = all(arg.annotation is not None for arg in node.args.args)

                    if has_return_type and has_param_types:
                        typed_functions += 1

            if total_functions == 0:
                return 100.0

            return (typed_functions / total_functions) * 100

        except SyntaxError:
            return 0.0

    @staticmethod
    def calculate_maintainability_index(source_code: str) -> float:
        """Calculate maintainability index (simplified version).

        Args:
            source_code: Source code to analyze

        Returns:
            Maintainability index (0-100)
        """
        try:
            # Count lines of code
            lines = len([line for line in source_code.split("\n") if line.strip()])

            # Calculate cyclomatic complexity
            complexity = CodeQualityMetrics.calculate_cyclomatic_complexity(source_code)

            # Simplified maintainability index calculation
            # Based on Halstead volume (approximated) and cyclomatic complexity
            if lines == 0:
                return 100.0

            # Approximate Halstead volume
            halstead_volume = lines * 4.7  # Simplified approximation

            # Calculate maintainability index
            mi = max(
                0,
                (171 - 5.2 * (halstead_volume**0.23) - 0.23 * complexity - 16.2 * (lines**0.5))
                * 100
                / 171,
            )

            return min(100.0, mi)

        except (SyntaxError, ZeroDivisionError):
            return 0.0


class QualityChecker:
    """Code quality checker and monitor."""

    def __init__(self, custom_thresholds: Optional[Dict[str, float]] = None):
        """Initialize quality checker.

        Args:
            custom_thresholds: Custom quality thresholds
        """
        self.thresholds = CodeQualityMetrics.THRESHOLDS.copy()
        if custom_thresholds:
            self.thresholds.update(custom_thresholds)

        self.reports: List[ModuleQualityReport] = []
        self.max_reports = 1000

    def check_module_quality(self, module_path: str) -> ModuleQualityReport:
        """Check quality of a Python module.

        Args:
            module_path: Path to Python module

        Returns:
            Quality report for the module
        """
        try:
            with open(module_path, encoding="utf-8") as f:
                source_code = f.read()

            return self.check_source_quality(source_code, module_path)

        except Exception as e:
            logger.error(f"Failed to check quality of {module_path}: {str(e)}")
            return ModuleQualityReport(
                module_name=Path(module_path).stem,
                file_path=module_path,
                metrics=[],
                overall_score=0.0,
                passed=False,
            )

    def check_source_quality(
        self, source_code: str, module_path: str = "unknown"
    ) -> ModuleQualityReport:
        """Check quality of source code.

        Args:
            source_code: Source code to check
            module_path: Path to the module (for reporting)

        Returns:
            Quality report
        """
        metrics = []

        try:
            # Parse source code
            tree = ast.parse(source_code)

            # Module-level metrics
            module_lines = len([line for line in source_code.split("\n") if line.strip()])
            metrics.append(
                QualityMetric(
                    name="module_length",
                    value=module_lines,
                    threshold=self.thresholds["module_length"],
                    passed=module_lines <= self.thresholds["module_length"],
                )
            )

            # Cyclomatic complexity
            complexity = CodeQualityMetrics.calculate_cyclomatic_complexity(source_code)
            metrics.append(
                QualityMetric(
                    name="cyclomatic_complexity",
                    value=complexity,
                    threshold=self.thresholds["cyclomatic_complexity"],
                    passed=complexity <= self.thresholds["cyclomatic_complexity"],
                )
            )

            # Documentation coverage
            doc_coverage = CodeQualityMetrics.calculate_documentation_coverage(source_code)
            metrics.append(
                QualityMetric(
                    name="documentation_coverage",
                    value=doc_coverage,
                    threshold=self.thresholds["documentation_coverage"],
                    passed=doc_coverage >= self.thresholds["documentation_coverage"],
                )
            )

            # Type hint coverage
            type_coverage = CodeQualityMetrics.calculate_type_hint_coverage(source_code)
            metrics.append(
                QualityMetric(
                    name="type_hint_coverage",
                    value=type_coverage,
                    threshold=self.thresholds["type_hint_coverage"],
                    passed=type_coverage >= self.thresholds["type_hint_coverage"],
                )
            )

            # Maintainability index
            maintainability = CodeQualityMetrics.calculate_maintainability_index(source_code)
            metrics.append(
                QualityMetric(
                    name="maintainability_index",
                    value=maintainability,
                    threshold=self.thresholds["maintainability_index"],
                    passed=maintainability >= self.thresholds["maintainability_index"],
                )
            )

            # Function-level metrics
            function_metrics = self._check_function_quality(tree)
            metrics.extend(function_metrics)

            # Class-level metrics
            class_metrics = self._check_class_quality(tree)
            metrics.extend(class_metrics)

        except SyntaxError as e:
            logger.error(f"Syntax error in {module_path}: {str(e)}")
            metrics.append(
                QualityMetric(
                    name="syntax_error",
                    value=1,
                    threshold=0,
                    passed=False,
                    details={"error": str(e)},
                )
            )

        # Calculate overall score
        if metrics:
            passed_metrics = sum(1 for m in metrics if m.passed)
            overall_score = (passed_metrics / len(metrics)) * 100
            overall_passed = all(m.passed for m in metrics)
        else:
            overall_score = 0.0
            overall_passed = False

        # Create report
        report = ModuleQualityReport(
            module_name=Path(module_path).stem,
            file_path=module_path,
            metrics=metrics,
            overall_score=overall_score,
            passed=overall_passed,
        )

        # Store report
        self.reports.append(report)
        if len(self.reports) > self.max_reports:
            self.reports.pop(0)

        return report

    def _check_function_quality(self, tree: ast.AST) -> List[QualityMetric]:
        """Check quality of functions in the AST."""
        metrics = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_metrics = CodeQualityMetrics.calculate_function_metrics(node)

                # Function length
                metrics.append(
                    QualityMetric(
                        name=f"function_length_{node.name}",
                        value=func_metrics["length"],
                        threshold=self.thresholds["function_length"],
                        passed=func_metrics["length"] <= self.thresholds["function_length"],
                        details={"function_name": node.name},
                    )
                )

                # Parameter count
                metrics.append(
                    QualityMetric(
                        name=f"parameter_count_{node.name}",
                        value=func_metrics["parameter_count"],
                        threshold=self.thresholds["parameter_count"],
                        passed=func_metrics["parameter_count"]
                        <= self.thresholds["parameter_count"],
                        details={"function_name": node.name},
                    )
                )

                # Nesting depth
                metrics.append(
                    QualityMetric(
                        name=f"nesting_depth_{node.name}",
                        value=func_metrics["nesting_depth"],
                        threshold=self.thresholds["nesting_depth"],
                        passed=func_metrics["nesting_depth"] <= self.thresholds["nesting_depth"],
                        details={"function_name": node.name},
                    )
                )

        return metrics

    def _check_class_quality(self, tree: ast.AST) -> List[QualityMetric]:
        """Check quality of classes in the AST."""
        metrics = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Count class lines
                class_lines = 0
                for child in ast.walk(node):
                    if hasattr(child, "lineno"):
                        class_lines = max(class_lines, child.lineno - node.lineno + 1)

                metrics.append(
                    QualityMetric(
                        name=f"class_length_{node.name}",
                        value=class_lines,
                        threshold=self.thresholds["class_length"],
                        passed=class_lines <= self.thresholds["class_length"],
                        details={"class_name": node.name},
                    )
                )

        return metrics

    def get_quality_summary(self) -> Dict[str, Any]:
        """Get quality summary across all checked modules.

        Returns:
            Quality summary dictionary
        """
        if not self.reports:
            return {"no_reports": True}

        total_reports = len(self.reports)
        passed_reports = sum(1 for r in self.reports if r.passed)

        # Average scores
        avg_score = sum(r.overall_score for r in self.reports) / total_reports

        # Metric statistics
        metric_stats = {}
        for report in self.reports:
            for metric in report.metrics:
                if metric.name not in metric_stats:
                    metric_stats[metric.name] = {"values": [], "passed": 0, "total": 0}

                metric_stats[metric.name]["values"].append(metric.value)
                metric_stats[metric.name]["total"] += 1
                if metric.passed:
                    metric_stats[metric.name]["passed"] += 1

        # Calculate averages and pass rates
        for metric_name, stats in metric_stats.items():
            stats["average"] = sum(stats["values"]) / len(stats["values"])
            stats["pass_rate"] = (stats["passed"] / stats["total"]) * 100
            del stats["values"]  # Remove raw values to reduce size

        return {
            "total_modules_checked": total_reports,
            "modules_passed": passed_reports,
            "overall_pass_rate": (passed_reports / total_reports) * 100,
            "average_quality_score": avg_score,
            "metric_statistics": metric_stats,
            "recent_reports": [r.to_dict() for r in self.reports[-5:]],  # Last 5 reports
        }

    def check_directory_quality(self, directory_path: str) -> Dict[str, ModuleQualityReport]:
        """Check quality of all Python files in a directory.

        Args:
            directory_path: Path to directory

        Returns:
            Dictionary mapping file paths to quality reports
        """
        reports = {}
        directory = Path(directory_path)

        for py_file in directory.rglob("*.py"):
            if py_file.name.startswith("."):
                continue  # Skip hidden files

            try:
                report = self.check_module_quality(str(py_file))
                reports[str(py_file)] = report
            except Exception as e:
                logger.error(f"Failed to check {py_file}: {str(e)}")

        return reports


# Global quality checker instance
quality_metrics = QualityChecker()


def code_quality_decorator(threshold_score: float = 70.0):
    """Decorator to check code quality of functions.

    Args:
        threshold_score: Minimum quality score required
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get function source code
            try:
                source_code = inspect.getsource(func)

                # Check quality
                report = quality_metrics.check_source_quality(source_code, func.__name__)

                # Log quality issues
                if not report.passed or report.overall_score < threshold_score:
                    logger.warning(
                        f"Function {func.__name__} has quality issues",
                        quality_score=report.overall_score,
                        threshold=threshold_score,
                        failed_metrics=[m.name for m in report.metrics if not m.passed],
                    )

                # Execute function
                return func(*args, **kwargs)

            except Exception as e:
                logger.error(f"Quality check failed for {func.__name__}: {str(e)}")
                return func(*args, **kwargs)

        return wrapper

    return decorator
