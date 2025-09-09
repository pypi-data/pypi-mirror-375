"""
PromptCompose SDK for Python

Official Python SDK for integrating with the PromptCompose API to resolve and manage AI prompts.
"""

from .prompt_compose import PromptCompose
from .types import *
from .errors import SDKError, APIError, ValidationError

__version__ = "0.1.1"
__all__ = [
    "PromptCompose",
    # Types
    "Prompt",
    "PromptConfig", 
    "ResolvedPrompt",
    "ABTest",
    "Variant",
    "Version",
    "Variable",
    "ReportABResult",
    "RolloutStrategy",
    "Status",
    "Conversion",
    # Errors
    "SDKError",
    "APIError", 
    "ValidationError",
] 