"""
Application configuration — loads settings from .env file.

All Azure AI Foundry credentials and deployment names are configured here.
Copy .env.example to .env and fill in your values before running.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings are loaded from environment variables or .env file.
    See .env.example for all required values.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Azure OpenAI connection
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_api_version: str = "2024-10-21"

    # Deployment names (as created in Azure AI Foundry)
    orchestrator_deployment: str = "gpt-4o"
    requirements_deployment: str = "gpt-4o"
    architecture_deployment: str = "gpt-4o"
    planning_deployment: str = "gpt-4o-mini"


def get_settings() -> Settings:
    """Load and return application settings."""
    return Settings()
