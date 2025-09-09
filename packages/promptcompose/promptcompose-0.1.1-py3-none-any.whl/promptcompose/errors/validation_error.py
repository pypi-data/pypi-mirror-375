"""Validation error class for the PromptCompose SDK."""

from .sdk_error import SDKError


class ValidationError(SDKError):
    """Exception raised when input validation fails."""
    
    def __init__(self, message: str = "Invalid or missing input provided.") -> None:
        """
        Initialize the validation error.
        
        Args:
            message: Error message
        """
        super().__init__(message, "VALIDATION_ERROR", 400) 