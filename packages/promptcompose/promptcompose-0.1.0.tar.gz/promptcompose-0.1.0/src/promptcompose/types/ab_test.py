"""A/B test type definitions for the PromptCompose SDK."""

from datetime import datetime
from typing import List, Literal, TypedDict, Union


# Type aliases
RolloutStrategy = Literal["weighted", "manual", "sequential"]
Status = Literal["active", "paused", "completed", "cancelled"]


class Variable(TypedDict):
    """Defines a variable that can be interpolated into a prompt."""
    name: str
    label: str
    type: str
    required: bool
    defaultValue: Union[str, int, float, bool, None]
    options: List[str]
    description: str


class Version(TypedDict):
    """Represents a specific version of a prompt with its content and variables."""
    title: str
    content: str
    deployMessage: str
    tags: List[str]
    variables: List[Variable]
    createdAt: datetime


class Conversion(TypedDict):
    """Represents a conversion event for A/B test tracking."""
    sessionId: str
    timestamp: datetime
    status: str


class Variant(TypedDict):
    """Represents a variant in an A/B test with its content and performance metrics."""
    _id: str
    publicId: str
    name: str
    content: str
    weight: int
    variables: List[Variable]
    impressions: int
    conversions: List[Conversion]


class ABTest(TypedDict):
    """Represents an A/B test configuration with variants and rollout strategy."""
    _id: str
    name: str
    projectId: str
    publicId: str
    prompt: dict[str, str]  # Contains publicId and name
    rolloutStrategy: RolloutStrategy
    status: Status
    variants: List[Variant]
    startDate: datetime
    endDate: datetime
    rotationIndex: int


class ReportABResult(TypedDict):
    """Result data for reporting A/B test outcomes."""
    variantId: str
    sessionId: str
    status: Literal["success", "fail", "skipped", "timeout", "error"] 