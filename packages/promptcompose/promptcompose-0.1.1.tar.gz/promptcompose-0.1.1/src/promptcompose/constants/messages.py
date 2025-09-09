"""Error messages for the PromptCompose SDK."""

from typing import Callable


def _failed_to_fetch_prompt(prompt_id: str) -> str:
    """Generate failed to fetch prompt message."""
    return f"Failed to fetch prompt {prompt_id}"


def _failed_to_resolve_prompt(prompt_id: str) -> str:
    """Generate failed to resolve prompt message."""
    return f"Failed to resolve prompt {prompt_id}"


def _failed_to_fetch_ab_test(ab_test_id: str) -> str:
    """Generate failed to fetch A/B test message."""
    return f"Failed to fetch A/B test {ab_test_id}"


def _failed_to_report_ab_result(ab_test_id: str) -> str:
    """Generate failed to report A/B result message."""
    return f"Failed to report A/B test {ab_test_id} result"


def _missing_required_variables(variables: list[str]) -> str:
    """Generate missing required variables message."""
    return f"Missing required variable(s): {', '.join(variables)}"


messages = {
    "connect": "Connecting to PromptCompose API",
    "prompts": "Fetching prompts",
    "prompt": lambda prompt_id: f"Fetching prompt {prompt_id}",
    "resolvePrompt": lambda prompt_id: f"Resolving prompt {prompt_id}",
    "abTests": "Fetching A/B tests",
    "abTest": lambda ab_test_id: f"Fetching A/B test {ab_test_id}",
    "reportABResult": lambda ab_test_id: f"Reporting A/B test {ab_test_id} result",
    "apiKeyAndProjectIdRequired": "API key and project ID are required",
    "failedToInitializeSDK": "Failed to initialize SDK",
    "failedToFetchPrompts": "Failed to fetch prompts",
    "failedToFetchPrompt": _failed_to_fetch_prompt,
    "failedToResolvePrompt": _failed_to_resolve_prompt,
    "failedToFetchABTests": "Failed to fetch A/B tests",
    "failedToFetchABTest": _failed_to_fetch_ab_test,
    "failedToReportABResult": _failed_to_report_ab_result,
    "promptIdRequired": "Prompt ID is required",
    "statusAndVariantIdRequired": "Status and variantId are required",
    "variablesAreRequiredWhenResolvingPromptWithDynamicInputs": "Variables are required when resolving a prompt with dynamic inputs.",
    "missingRequiredVariables": _missing_required_variables,
} 