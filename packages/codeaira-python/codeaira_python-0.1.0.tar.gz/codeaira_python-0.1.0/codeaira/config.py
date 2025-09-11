from pydantic import ValidationError
from pydantic_settings import BaseSettings
from utils import setup_logger

logger = setup_logger(name="codeaira-config")


class CodeAiraConfig(BaseSettings):
    CODEAIRA_API_KEY: str
    CODEAIRA_BASE_URL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_config() -> CodeAiraConfig:
    try:
        logger.info("Loading configuration from environment variables")
        config = CodeAiraConfig()
        logger.info("Configuration loaded successfully")
        return config
    except ValidationError as e:
        logger.error(f"Invalid configuration: {e}")
        raise ValueError("Missing or invalid configuration settings")


config = get_config()
