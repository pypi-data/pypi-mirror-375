import requests
import logging
from pydantic import ValidationError
from config import config
from models import (CodeAiraRequest,
                    FullCompletionResponse,
                    DataOnlyResponse)
from exceptions import (
    handle_request_exception,
    handle_api_error,
    handle_validation_error,
    ConfigurationError)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeAiraClient:
    def __init__(self):
        try:
            self.api_key = config.CODEAIRA_API_KEY
            self.base_url = config.CODEAIRA_BASE_URL
        except ValueError as e:
            logger.error(f"Configuration error: {str(e)}")
            raise ConfigurationError(str(e))

    def complete_text(self,
                      model_name: str,
                      prompt: str,
                      context: str = None,
                      app_id: str = None,
                      response_only: bool = True):
        try:
            request_data = CodeAiraRequest(
                model_name=model_name,
                prompt=prompt,
                context=context,
                app_id=app_id
            )
        except ValidationError as e:
            handle_validation_error(e)

        payload = request_data.model_dump(exclude_none=True)
        payload["api_token"] = self.api_key

        try:
            response = requests.post(self.base_url, json=payload)
            response.raise_for_status()
            response_json = response.json()

            if not response_json["success"]:
                logger.error(f"API error: {response_json["error"]}")
                handle_api_error(response.status_code, response_json)
            if response_only:
                return DataOnlyResponse(**response_json)
            else:
                return FullCompletionResponse(**response_json)
        except requests.RequestException as e:
            handle_request_exception(e)

    def __repr__(self):
        return f"CodeAiraClient(base_url={self.base_url})"
