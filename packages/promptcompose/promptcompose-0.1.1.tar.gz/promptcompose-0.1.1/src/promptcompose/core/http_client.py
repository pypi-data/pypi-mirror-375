"""HTTP client configuration for the PromptCompose SDK."""

import os
from typing import Dict

import requests


def create_http_client(project_id: str, api_key: str) -> requests.Session:
    """
    Create a configured HTTP client for the PromptCompose API.
    
    Args:
        project_id: The project ID for authentication
        api_key: The API key for authentication
        
    Returns:
        Configured requests.Session instance
    """
    api_base_url = os.getenv("PROMPT_COMPOSE_API_URL", "https://api.promptcompose.ai/v1")
    
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "x-project-id": project_id,
    })
    
    # Store base URL for later use
    session._base_url = api_base_url
    
    return session 