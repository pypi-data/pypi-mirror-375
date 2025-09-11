"""Abstract base class for all mathematical operations."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pydantic import BaseModel


class BaseOperation(ABC):
    """Abstract base class for all mathematical operations.

    This class defines the standard interface that all mathematical operations
    must implement, ensuring consistency across the calculator system.
    """

    def __init__(self, config=None, cache=None):
        """Initialize the operation with optional configuration and cache.

        Args:
            config: Configuration service instance
            cache: Cache repository instance
        """
        self.config = config
        self.cache = cache

    @abstractmethod
    async def execute(self, params: BaseModel) -> Dict[str, Any]:
        """Execute the mathematical operation.

        Args:
            params: Validated input parameters

        Returns:
            Dictionary containing the operation result and metadata

        Raises:
            ValidationError: If input parameters are invalid
            ComputationError: If the mathematical computation fails
        """
        pass

    @abstractmethod
    def validate_input(self, params: BaseModel) -> bool:
        """Validate input parameters for the operation.

        Args:
            params: Input parameters to validate

        Returns:
            True if parameters are valid

        Raises:
            ValidationError: If parameters are invalid
        """
        pass

    def format_result(
        self, result: Any, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Format operation result consistently.

        Args:
            result: The computed result
            metadata: Optional metadata about the computation

        Returns:
            Standardized result dictionary
        """
        return {"result": result, "metadata": metadata or {}, "operation": self.__class__.__name__}

    def get_cache_key(self, params: BaseModel) -> str:
        """Generate a cache key for the operation and parameters.

        Args:
            params: Input parameters

        Returns:
            String cache key
        """
        operation_name = self.__class__.__name__
        params_str = str(sorted(params.dict().items()))
        return f"{operation_name}:{hash(params_str)}"
