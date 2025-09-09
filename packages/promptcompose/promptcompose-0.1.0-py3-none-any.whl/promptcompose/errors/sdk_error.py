"""Base error class for the PromptCompose SDK."""

from typing import Optional


class SDKError(Exception):
    """Base exception class for all SDK errors."""
    
    def __init__(
        self, 
        message: str = "An error occurred in the PromptCompose SDK.",
        code: str = "SDK_ERROR",
        status: Optional[int] = None
    ) -> None:
        """
        Initialize the SDK error.
        
        Args:
            message: Error message
            code: Error code
            status: HTTP status code if applicable
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status
        self.name = self.__class__.__name__ 