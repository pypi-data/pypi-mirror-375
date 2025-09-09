"""Custom exceptions for MBU RPA Core library with Pydantic validation.

This module contains custom exception classes for handling different types of
errors that may occur during RPA processes in the MBU department.
"""

from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class BaseRPAError(Exception):
    """Base class for all RPA exceptions with Pydantic validation."""

    message: str = Field(..., min_length=1)

    def __str__(self):
        """Return the error message."""
        return self.message

    def __repr__(self):
        """Return a string representation of the exception."""
        return f"{self.__class__.__name__}(message={repr(self.message)})"


class BusinessError(BaseRPAError):
    """Exception raised for business-related errors in the RPA process."""

    def __init__(self, message: str):
        """Initialize the BusinessError with a message."""
        super().__init__(message=message)


class ProcessError(BaseRPAError):
    """Exception raised for process-related errors in the RPA process."""

    def __init__(self, message: str):
        """Initialize the ProcessError with a message."""
        super().__init__(message=message)
