# CodeAira Python Client
## Introduction
CodeAira Python Client is a powerful and easy-to-use library for interacting with the CodeAira API for text completion tasks. This library simplifies the process of making requests to the CodeAira API, handling responses, and managing errors.

## Installation
To install the CodeAira Python Client, use pip:
```bash
pip install codeaira-python
```
Configuration
Before using the library, you need to set up your CodeAira API key as an environment variable:
```bash
set CODEAIRA_API_KEY=your_api_key_here
```
Alternatively, you can use a .env file in your project directory:
```bash
CODEAIRA_API_KEY=your_api_key_here
```

## Usage
Here's a basic example of how to use the CodeAira Python Client:
```python
from codeaira import CodeAiraClient

client = CodeAiraClient()

response = client.complete_text(
    model_name="gpt-3.5-turbo",
    prompt="Translate the following English text to French: 'Hello, world!'",
    context="This is a translation task."
)

print(response.choices[0].text)
```
## API Reference
### CodeAiraClient
The main class for interacting with the CodeAira API.

Methods
```python
complete_text(model_name: str, prompt: str, context: str = None, app_id: str = None) -> CompletionResponse
```
Sends a text completion request to the CodeAira API.
```python
model_name: The name of the model to use for completion.
prompt: The text prompt for completion.
context (optional): Additional context for the completion task.
app_id (optional): An identifier for the application making the request.
Returns a CompletionResponse object.
```
### Data Models
* CodeAiraRequest: Represents the structure of a request to the CodeAira API.
* CompletionResponse: Represents the structure of a response from the CodeAira API.
* CompletionChoice: Represents a single completion choice in the API response.
### Error Handling
The library uses custom exceptions to handle various error scenarios:

* ConfigurationError: Raised when there's an issue with the API key configuration.
* APIError: Raised when the API returns an error response.
* NetworkError: Raised when there's a network-related issue.
* ValidationError: Raised when there's a data validation error.
Example of error handling:
```python
from codeaira import CodeAiraClient, APIError, NetworkError

client = CodeAiraClient()

try:
    response = client.complete_text(
        model_name="gpt-3.5-turbo",
        prompt="Generate a story about a robot."
    )
    print(response.choices[0].text)
except APIError as e:
    print(f"API Error: {e}")
except NetworkError as e:
    print(f"Network Error: {e}")
```
### Logging
The library uses Python's built-in logging module to provide informative logs. You can configure the logging level and format as needed in your application.

Example of configuring logging:
``` python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('codeaira')
```
## Compatibility
CodeAira Python Client supports Python 3.9 and above.

## Contributing
Contributions to the CodeAira Python Client are welcome! Please refer to the project's GitHub repository for guidelines on how to contribute.

## License
This project is licensed under the MIT License. See the LICENSE file for details