import os
import pytest
from unittest.mock import patch, MagicMock
from config import get_config, validate_api_key
from main import CodeAiraClient
from models import FullCompletionResponse
from codeaira.exceptions import (
    ConfigurationError, APIError, NetworkError, ValidationError)


@pytest.fixture
def mock_env_api_key(monkeypatch):
    monkeypatch.setenv("CODEAIRA_API_KEY", "test_api_key")


@pytest.fixture
def mock_requests_post():
    with patch("codeaira.main.requests.post") as mock_post:
        yield mock_post


def test_config_validation(mock_env_api_key):
    config = get_config()
    assert config.CODEAIRA_API_KEY == "test_api_key"


def test_config_validation_missing_key():
    with pytest.raises(ValueError):
        validate_api_key()


def test_client_initialization(mock_env_api_key):
    client = CodeAiraClient()
    assert client.api_key == "test_api_key"
    assert client.base_url == "https://codeaira.qdatalabs.com/api/application"


def test_client_initialization_error():
    with pytest.raises(ConfigurationError):
        CodeAiraClient()


def test_complete_text_success(mock_env_api_key, mock_requests_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": "test_id",
        "object": "text_completion",
        "created": 1234567890,
        "model": "test_model",
        "choices": [
            {
                "text": "Generated text",
                "index": 0,
                "logprobs": None,
                "finish_reason": "length"
            }
        ],
        "usage": {"prompt_tokens": 10,
                  "completion_tokens": 20, "total_tokens": 30}
    }
    mock_response.raise_for_status.return_value = None
    mock_requests_post.return_value = mock_response

    client = CodeAiraClient()
    response = client.complete_text("test_model", "Test prompt")

    assert isinstance(response, FullCompletionResponse)
    assert response.id == "test_id"
    assert response.choices[0].text == "Generated text"


def test_complete_text_api_error(mock_env_api_key, mock_requests_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {"error": "API Error"}
    mock_response.raise_for_status.side_effect = Exception("API Error")
    mock_requests_post.return_value = mock_response

    client = CodeAiraClient()
    with pytest.raises(APIError):
        client.complete_text("test_model", "Test prompt")


def test_complete_text_network_error(mock_env_api_key, mock_requests_post):
    mock_requests_post.side_effect = Exception("Network Error")

    client = CodeAiraClient()
    with pytest.raises(NetworkError):
        client.complete_text("test_model", "Test prompt")


def test_complete_text_validation_error(mock_env_api_key):
    client = CodeAiraClient()
    with pytest.raises(ValidationError):
        client.complete_text("", "")  # Empty model_name and prompt


@pytest.mark.integration
def test_integration_complete_text():
    api_key = os.getenv("CODEAIRA_API_KEY")
    if not api_key:
        pytest.skip("CODEAIRA_API_KEY not set for integration test")

    client = CodeAiraClient()
    response = client.complete_text("gpt-3.5-turbo", "Hello, world!")

    assert isinstance(response, FullCompletionResponse)
    assert response.choices[0].text
    assert response.model == "gpt-3.5-turbo"
