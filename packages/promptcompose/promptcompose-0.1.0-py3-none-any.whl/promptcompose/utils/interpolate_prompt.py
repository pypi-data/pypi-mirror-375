"""Prompt interpolation utility for the PromptCompose SDK."""

import re
from typing import Dict, Union


def interpolate_prompt(
    content: str, 
    variables: Dict[str, Union[str, int]]
) -> str:
    """
    Inject variables into a prompt content string using double curly syntax (e.g. {{variableName}}).
    
    Args:
        content: The raw prompt content containing variable placeholders
        variables: A key-value map of variables to inject
        
    Returns:
        The interpolated prompt with all variable placeholders replaced
        
    Example:
        >>> interpolate_prompt("Hello, {{name}}!", {"name": "Mahmoud"})
        "Hello, Mahmoud!"
    """
    def replace_variable(match: re.Match) -> str:
        key = match.group(1).strip()
        return str(variables.get(key, f"{{{{{key}}}}}"))
    
    return re.sub(r"{{\s*([\w.-]+)\s*}}", replace_variable, content) 