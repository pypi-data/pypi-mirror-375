"""API error class for the PromptCompose SDK."""

from typing import Any, Optional

from .sdk_error import SDKError


class APIError(SDKError):
    """Exception raised when API communication fails."""
    
    def __init__(
        self,
        message: str = "An error occurred while communicating with the PromptCompose API.",
        status: Optional[int] = None,
        response_data: Optional[Any] = None
    ) -> None:
        """
        Initialize the API error.
        
        Args:
            message: Error message
            status: HTTP status code
            response_data: Response data from the API
        """
        super().__init__(message, "API_ERROR", status)
        self.response_data = response_data 