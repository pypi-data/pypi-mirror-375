import logging
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


class CodeAiraException(Exception):
    """Base exception for CodeAira client library"""


class ConfigurationError(CodeAiraException):
    """Raised when there's an issue with the configuration"""


class APIError(CodeAiraException):
    """Raised when the API returns an error response"""

    def __init__(self, status_code, error_message):
        self.status_code = status_code
        self.error_message = error_message
        super().__init__(f"API Error (Status {status_code}): {error_message}")


class NetworkError(CodeAiraException):
    """Raised when there's a network-related issue"""


class ValidationError(CodeAiraException):
    """Raised when there's a data validation error"""


def handle_request_exception(e: RequestException):
    if isinstance(e, RequestException):
        logger.error(f"Network error occurred: {str(e)}")
        raise NetworkError(f"Network error: {str(e)}")
    else:
        logger.error(f"Unexpected error occurred: {str(e)}")
        raise CodeAiraException(f"Unexpected error: {str(e)}")


def handle_api_error(status_code: int, response_json: dict):
    error_message = response_json.get('error', 'Unknown API error')
    logger.error(f"API error (Status {status_code}): {error_message}")
    raise APIError(status_code, error_message)


def handle_validation_error(e: Exception):
    logger.error(f"Validation error: {str(e)}")
    raise ValidationError(f"Data validation error: {str(e)}")
