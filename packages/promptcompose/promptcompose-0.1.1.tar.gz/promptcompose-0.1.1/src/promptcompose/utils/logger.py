"""Logging utility for the PromptCompose SDK."""

import logging
from typing import Any


class PromptComposeLogger:
    """Logger for the PromptCompose SDK."""
    
    def __init__(self) -> None:
        """Initialize the logger."""
        self._logger = logging.getLogger("promptcompose")
        self._logger.setLevel(logging.INFO)
        
        # Create console handler if none exists
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(name)s [%(levelname)s]: %(message)s"
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
    
    def log(self, message: str) -> None:
        """Log an info message."""
        self._logger.info(message)
    
    def error(self, message: str) -> None:
        """Log an error message."""
        self._logger.error(message)
    
    def warn(self, message: str) -> None:
        """Log a warning message."""
        self._logger.warning(message)
    
    def info(self, message: str) -> None:
        """Log an info message."""
        self._logger.info(message)
    
    def debug(self, message: str) -> None:
        """Log a debug message."""
        self._logger.debug(message)


logger = PromptComposeLogger() 