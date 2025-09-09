"""Process completion states for MBU RPA Core library with Pydantic validation.

This module contains Pydantic models representing different completion states
of RPA processes in the MBU department, each with an associated message.
"""

from enum import Enum, auto
from pydantic import BaseModel, Field


class StateType(Enum):
    """Enumeration of possible process completion states."""
    COMPLETED = auto()
    COMPLETED_WITH_EXCEPTION = auto()


class CompletedState(BaseModel):
    """Pydantic model representing process completion states with associated messages."""

    state: StateType
    message: str = Field(..., min_length=1)

    def __str__(self):
        """Return a human-readable string representation of the state."""
        state_str = "Completed with exceptions" if self.state == StateType.COMPLETED_WITH_EXCEPTION else "Completed"
        return f"{state_str}: {self.message}"

    @classmethod
    def completed(cls, message: str) -> 'CompletedState':
        """Factory method for creating a Completed state.

        Args:
            message (str): Description of the completion.

        Returns:
            CompletedState: A CompletedState instance with Completed state
        """
        return cls(state=StateType.COMPLETED, message=message)

    @classmethod
    def completed_with_exception(cls, message: str) -> 'CompletedState':
        """Factory method for creating a CompletedWithException state.

        Args:
            message (str): Description of the completion.

        Returns:
            CompletedState: A CompletedState instance with CompletedWithException state
        """
        return cls(state=StateType.COMPLETED_WITH_EXCEPTION, message=message)
