"""
LLM client factory — creates Azure OpenAI model clients for each agent.

Each agent gets its own model client pointing to its specific deployment
in Azure AI Foundry. This allows using different models for different agents
(e.g., GPT-4o for complex reasoning, GPT-4o-mini for simpler tasks).
"""

from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from src.utils.config import Settings


def create_model_client(settings: Settings, deployment_name: str) -> AzureOpenAIChatCompletionClient:
    """
    Create an Azure OpenAI model client for a specific deployment.

    Args:
        settings: Application settings with Azure credentials
        deployment_name: The deployment name in Azure AI Foundry

    Returns:
        A model client ready to use with AutoGen agents
    """
    return AzureOpenAIChatCompletionClient(
        azure_deployment=deployment_name,
        model=deployment_name,
        api_key=settings.azure_openai_api_key,
        azure_endpoint=settings.azure_openai_endpoint,
        api_version=settings.azure_openai_api_version,
    )
