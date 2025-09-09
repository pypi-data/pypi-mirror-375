# PromptCompose SDK (Python)

Official Python SDK for integrating with the PromptCompose API to resolve and manage AI prompts with A/B testing capabilities.

## Installation

```bash
pip install promptcompose-sdk
```

## Quick Start

```python
from promptcompose import PromptCompose

# Initialize the SDK
prompt_compose = PromptCompose(
    api_key='your-api-key',
    project_id='your-project-id',
    debug=True
)

# Initialize connection
prompt_compose.init()

# Resolve a prompt with variables
result = prompt_compose.resolve_prompt(
    prompt_id='prompt-id',
    config={
        'version_id': 'v1',
        'ab_testing': {'enabled': False}
    },
    variables={
        'user_name': 'John',
        'product_name': 'Widget'
    }
)

print(result.content)
```

## Features

- **Prompt Resolution**: Resolve prompts with dynamic variable interpolation
- **A/B Testing**: Built-in support for A/B testing with multiple rollout strategies
- **Version Management**: Handle multiple prompt versions seamlessly
- **Type Hints**: Full type hints included with comprehensive docstrings
- **IntelliSense**: Complete IntelliSense support for all IDEs
- **Error Handling**: Comprehensive error handling with detailed messages

## API Reference

### Constructor

```python
PromptCompose(api_key: str, project_id: str, debug: bool = False)
```

### Methods

#### `init()`
Performs initial handshake with the API to verify credentials.

#### `list_prompts()`
Retrieves all prompts for the project.

#### `get_prompt(prompt_id: str)`
Retrieves a specific prompt by ID.

#### `resolve_prompt(prompt_id: str, config: Optional[PromptConfig] = None, variables: Optional[Dict[str, Union[str, int]]] = None)`
Resolves a prompt with optional A/B testing and variable interpolation.

#### `list_ab_tests()`
Retrieves all A/B tests for the project.

#### `get_ab_test(ab_test_id: str)`
Retrieves a specific A/B test by ID.

#### `report_ab_result(ab_test_id: str, result: ReportABResult)`
Reports A/B test results for analytics.

## A/B Testing

The SDK supports three A/B testing strategies:

- **Sequential**: Tests variants in order
- **Weighted**: Random selection with specified weights
- **Manual**: Explicit variant selection

```python
# Sequential A/B testing
result = prompt_compose.resolve_prompt('prompt-id', {
    'ab_testing': {
        'session_id': 'user-session-123'
    }
})

# Manual variant selection
result = prompt_compose.resolve_prompt('prompt-id', {
    'ab_testing': {
        'variant_id': 'variant-abc'
    }
})
```

## Error Handling

The SDK provides detailed error messages for various scenarios:

- `ValidationError`: Missing required variables or invalid configuration
- `APIError`: Network or server errors
- `SDKError`: General SDK errors

## IntelliSense Support

The SDK provides comprehensive IntelliSense support for all Python IDEs:

### Type Hints
- Full type definitions with comprehensive docstrings
- Autocomplete for all methods and properties
- Type checking for parameters and return values
- Import suggestions for all exported types

```python
from promptcompose import PromptCompose, PromptConfig, ResolvedPrompt

# Full IntelliSense support with docstrings
sdk = PromptCompose('api-key', 'project-id')

# IntelliSense will show autocomplete for config.ab_testing properties
config: PromptConfig = {
    'version_id': 'v1',
    'ab_testing': {
        'enabled': False,
        'variant_id': 'variant-123',
        'session_id': 'session-456'
    }
}

result: ResolvedPrompt = sdk.resolve_prompt('prompt-id', config)
```

## License

MIT 