"""Main PromptCompose SDK class."""

from typing import Any, Dict, List, Optional, Union

import requests

from .constants.endpoints import endpoints
from .constants.messages import messages
from .core.http_client import create_http_client
from .errors import APIError, ValidationError
from .types import (
    ABTest,
    Prompt,
    PromptConfig,
    ReportABResult,
    ResolvedPrompt,
)
from .utils.interpolate_prompt import interpolate_prompt
from .utils.logger import logger
from .utils.validate import validate_variables


class PromptCompose:
    """
    Main SDK class for interacting with the PromptCompose API.
    
    This class provides methods for resolving prompts, managing A/B tests,
    and handling variable interpolation.
    """
    
    def __init__(
        self,
        api_key: str,
        project_id: str,
        debug: bool = False
    ) -> None:
        """
        Initialize the PromptCompose SDK instance.
        
        Args:
            api_key: The secret API key associated with your project
            project_id: The public ID of your project
            debug: Enable debug logging
            
        Raises:
            ValidationError: If api_key or project_id are missing
        """
        if not api_key or not project_id:
            raise ValidationError(str(messages["apiKeyAndProjectIdRequired"]))
        
        self.api_key = api_key
        self.project_id = project_id
        self.http_client = create_http_client(self.project_id, self.api_key)
        self.debug = debug
        
        if self.debug:
            logger.log("Initialized PromptCompose SDK in debug mode")
    
    def init(self) -> Dict[str, str]:
        """
        Perform initial handshake with the PromptCompose API.
        
        Returns:
            Success message if connection is valid
            
        Raises:
            APIError: If connection fails
        """
        try:
            if self.debug:
                logger.log("Initializing PromptCompose SDK")
            
            response = self.http_client.get(f"{self.http_client._base_url}{endpoints['connect']}")
            response.raise_for_status()
            
            if self.debug:
                logger.log("Connected to PromptCompose API")
            
            response_data = response.json()
            return response_data.get("data", response_data)
        except requests.RequestException as error:
            raise APIError(
                str(messages["failedToInitializeSDK"]),
                getattr(error.response, 'status_code', None),
                getattr(error.response, 'json', lambda: None)()
            )
    
    def list_prompts(self) -> List[Prompt]:
        """
        Retrieve all prompt configurations for the project.
        
        Returns:
            List of prompt objects
            
        Raises:
            APIError: If the request fails
        """
        try:
            if self.debug:
                logger.log("Fetching prompts")
            
            response = self.http_client.get(f"{self.http_client._base_url}{endpoints['prompts']}")
            response.raise_for_status()
            
            if self.debug:
                logger.log("Fetched prompts successfully")
            
            response_data = response.json()
            return response_data.get("data", response_data)
        except requests.RequestException as error:
            raise APIError(
                str(messages["failedToFetchPrompts"]),
                getattr(error.response, 'status_code', None),
                getattr(error.response, 'json', lambda: None)()
            )
    
    def get_prompt(self, prompt_id: str) -> Prompt:
        """
        Retrieve a specific prompt by its public ID.
        
        Args:
            prompt_id: The public ID of the prompt to retrieve
            
        Returns:
            Prompt object containing metadata and configuration
            
        Raises:
            ValidationError: If prompt_id is not provided
            APIError: If the request fails
        """
        try:
            if not prompt_id:
                raise ValidationError(messages["promptIdRequired"])
            
            if self.debug:
                logger.log(f"Fetching prompt {prompt_id}")
            
            endpoint_func = endpoints['prompt']
            url = endpoint_func(prompt_id) if callable(endpoint_func) else str(endpoint_func)
            response = self.http_client.get(f"{self.http_client._base_url}{url}")
            response.raise_for_status()
            
            if self.debug:
                logger.log(f"Fetched prompt {prompt_id} successfully")
            
            response_data = response.json()
            return response_data.get("data", response_data)
        except requests.RequestException as error:
            msg_func = messages["failedToFetchPrompt"]
            error_msg = msg_func(prompt_id) if callable(msg_func) else str(msg_func)
            raise APIError(
                error_msg,
                getattr(error.response, 'status_code', None),
                getattr(error.response, 'json', lambda: None)()
            )
    
    def resolve_prompt(
        self,
        prompt_id: str,
        config: Optional[PromptConfig] = None,
        variables: Optional[Dict[str, Union[str, int]]] = None
    ) -> ResolvedPrompt:
        """
        Resolve the final content of a prompt with variable interpolation.
        
        This is the primary method for retrieving a finalized and usable prompt string.
        It handles A/B test resolution, version selection, and variable interpolation.
        
        Args:
            prompt_id: The public ID of the prompt to resolve
            config: Configuration for versioning and A/B testing
            variables: Key-value map of variables to inject into the prompt
            
        Returns:
            The final resolved prompt object with interpolated content
            
        Raises:
            ValidationError: If required variables are missing
            APIError: If resolution fails
        """
        try:
            if self.debug:
                logger.log(f"Resolving prompt {prompt_id}")
            
            payload = {"promptId": prompt_id}
            if config:
                payload.update(config)
            
            response = self.http_client.post(f"{self.http_client._base_url}{endpoints['resolvePrompt']}", json=payload)
            response.raise_for_status()
            
            response_data = response.json()
            data = response_data.get("data", response_data)
            prompt_source = data.get("variant") or data.get("version")
            
            if not prompt_source:
                raise APIError(
                    messages["failedToResolvePrompt"](prompt_id),
                    404,
                    "Prompt source not found"
                )
            
            if self.debug:
                logger.log(f"Prompt source: {prompt_source}")
                logger.log("Validating variables...")
            
            # Validate variables
            validate_variables(prompt_source, variables or {})
            
            if self.debug:
                logger.log("Variables validated successfully")
                logger.log("Interpolating content...")
            
            # Interpolate the content
            interpolated_content = interpolate_prompt(
                prompt_source.get("content", ""),
                variables or {}
            )
            
            if self.debug:
                logger.log("Content interpolated successfully")
            
            return {**data, "content": interpolated_content}
        except requests.RequestException as error:
            raise APIError(
                messages["failedToResolvePrompt"](prompt_id),
                getattr(error.response, 'status_code', None),
                getattr(error.response, 'json', lambda: None)()
            )
    
    def list_ab_tests(self) -> List[ABTest]:
        """
        Retrieve all A/B tests for the project.
        
        Returns:
            List of A/B test objects
            
        Raises:
            APIError: If the request fails
        """
        try:
            if self.debug:
                logger.log("Fetching A/B tests")
            
            response = self.http_client.get(f"{self.http_client._base_url}{endpoints['abTests']}")
            response.raise_for_status()
            
            if self.debug:
                logger.log("Fetched A/B tests successfully")
            
            response_data = response.json()
            return response_data.get("data", response_data)
        except requests.RequestException as error:
            raise APIError(
                messages["failedToFetchABTests"],
                getattr(error.response, 'status_code', None),
                getattr(error.response, 'json', lambda: None)()
            )
    
    def get_ab_test(self, ab_test_id: str) -> ABTest:
        """
        Retrieve a specific A/B test by its ID.
        
        Args:
            ab_test_id: The unique identifier of the A/B test
            
        Returns:
            Complete A/B test object with all metadata
            
        Raises:
            APIError: If the request fails
        """
        try:
            if self.debug:
                logger.log(f"Fetching A/B test {ab_test_id}")
            
            response = self.http_client.get(f"{self.http_client._base_url}{endpoints['abTest'](ab_test_id)}")
            response.raise_for_status()
            
            if self.debug:
                logger.log(f"Fetched A/B test {ab_test_id} successfully")
            
            response_data = response.json()
            return response_data.get("data", response_data)
        except requests.RequestException as error:
            raise APIError(
                messages["failedToFetchABTest"](ab_test_id),
                getattr(error.response, 'status_code', None),
                getattr(error.response, 'json', lambda: None)()
            )
    
    def report_ab_result(
        self,
        ab_test_id: str,
        result: ReportABResult
    ) -> ReportABResult:
        """
        Report the result of an A/B test execution.
        
        Args:
            ab_test_id: The unique ID of the A/B test
            result: The report payload with variantId, status, and optional sessionId
            
        Returns:
            The confirmed report data as recorded by the backend
            
        Raises:
            ValidationError: If variantId or status is missing
            APIError: If the request fails
        """
        try:
            if self.debug:
                logger.log(f"Reporting A/B test {ab_test_id} result")
            
            if not result.get("status") or not result.get("variantId"):
                raise ValidationError(messages["statusAndVariantIdRequired"])
            
            payload = {
                "status": result["status"],
                "variantId": result["variantId"],
                "sessionId": result.get("sessionId"),
            }
            
            response = self.http_client.post(
                f"{self.http_client._base_url}{endpoints['reportABResult'](ab_test_id)}",
                json=payload
            )
            response.raise_for_status()
            
            if self.debug:
                logger.log(f"Reported A/B test {ab_test_id} result successfully")
            
            response_data = response.json()
            return response_data.get("data", response_data)
        except requests.RequestException as error:
            raise APIError(
                messages["failedToReportABResult"](ab_test_id),
                getattr(error.response, 'status_code', None),
                getattr(error.response, 'json', lambda: None)()
            ) 