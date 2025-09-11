"""Abstract base class for validators."""

from abc import ABC, abstractmethod
from typing import Any, List


class BaseValidator(ABC):
    """Abstract base class for input validators.

    Validators ensure that input data meets the requirements for
    mathematical operations and provide clear error messages.
    """

    @abstractmethod
    def validate(self, value: Any) -> bool:
        """Validate a value.

        Args:
            value: Value to validate

        Returns:
            True if value is valid

        Raises:
            ValidationError: If value is invalid
        """
        pass

    @abstractmethod
    def get_validation_errors(self, value: Any) -> List[str]:
        """Get detailed validation error messages.

        Args:
            value: Value to validate

        Returns:
            List of error messages (empty if valid)
        """
        pass

    def get_suggestions(self, value: Any) -> List[str]:
        """Get suggestions for fixing validation errors.

        Args:
            value: Invalid value

        Returns:
            List of suggestions for fixing the value
        """
        return []

    def is_valid(self, value: Any) -> bool:
        """Check if a value is valid without raising exceptions.

        Args:
            value: Value to check

        Returns:
            True if valid, False otherwise
        """
        try:
            return self.validate(value)
        except Exception:
            return False
