"""API endpoints for the PromptCompose SDK."""

from typing import Callable


def _prompt_endpoint(prompt_id: str) -> str:
    """Generate prompt endpoint URL."""
    return f"/prompts/{prompt_id}"


def _ab_test_endpoint(ab_test_id: str) -> str:
    """Generate A/B test endpoint URL."""
    return f"/ab-tests/{ab_test_id}"


def _report_ab_result_endpoint(ab_test_id: str) -> str:
    """Generate report A/B result endpoint URL."""
    return f"/ab-tests/{ab_test_id}/report"


endpoints = {
    "connect": "/connect",
    "prompts": "/prompts",
    "prompt": _prompt_endpoint,
    "resolvePrompt": "/prompts/resolve",
    "abTests": "/ab-tests",
    "abTest": _ab_test_endpoint,
    "reportABResult": _report_ab_result_endpoint,
} 