"""Validation utilities for the PromptCompose SDK."""

from typing import Any, Dict, Union

from ..errors import ValidationError
from ..constants.messages import messages


def validate_variables(
    prompt_source: Dict[str, Any],
    variables: Dict[str, Union[str, int]]
) -> None:
    """
    Validate that all required variables are provided.
    
    Args:
        prompt_source: The prompt source (variant or version) containing variable definitions
        variables: The variables provided by the user
        
    Raises:
        ValidationError: If required variables are missing
    """
    if not prompt_source:
        return
        
    expected_variables = prompt_source.get("variables", [])
    
    # Check for required variables
    if expected_variables:
        if not variables:
            raise ValidationError(
                messages["variablesAreRequiredWhenResolvingPromptWithDynamicInputs"]
            )
        
        missing = [
            var["name"] for var in expected_variables 
            if var.get("required", False) and var["name"] not in variables
        ]
        
        if missing:
            missing_vars_message = messages["missingRequiredVariables"]
            if callable(missing_vars_message):
                raise ValidationError(missing_vars_message(missing))
            else:
                raise ValidationError(str(missing_vars_message)) 