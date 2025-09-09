"""Prompt type definitions for the PromptCompose SDK."""

from datetime import datetime
from typing import Dict, List, Optional, TypedDict, Union

from .ab_test import ABTest, Variant, Version


class Prompt(TypedDict):
    """Represents a prompt configuration with all its metadata, versions, and variables."""
    id: str
    name: str
    createdAt: datetime
    updatedAt: datetime
    createdBy: str
    updatedBy: str
    versions: List[dict]  # Contains version information
    publicId: str
    projectId: str


class PromptConfig(TypedDict, total=False):
    """Configuration object for prompt resolution, including version selection and A/B testing options."""
    versionId: str
    abTesting: Dict[str, Union[bool, str]]


class ResolvedPrompt(TypedDict):
    """The resolved prompt result containing the final content and metadata about the source."""
    content: str
    source: str
    publicId: str
    variant: Optional[Variant]
    version: Optional[Version]
    abTest: Optional[ABTest]
    projectId: str 