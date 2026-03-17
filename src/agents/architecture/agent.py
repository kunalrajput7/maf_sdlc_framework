"""
Architecture Agent — designs system architecture from requirements.

Flow:
  1. Reads the RequirementsDocument from ProjectContext
  2. Produces a complete ArchitectureDocument (tech stack, components, APIs, DB schema)
  3. Can refine based on user feedback
"""

import json

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken

from src.agents.architecture.prompts import (
    SYSTEM_PROMPT,
    GENERATE_ARCHITECTURE_PROMPT,
    REFINE_PROMPT,
)
from src.models.artifacts import RequirementsDocument, ArchitectureDocument


class ArchitectureAgent:
    """
    Wraps an AutoGen AssistantAgent specialized in system architecture design.

    Usage:
        agent = ArchitectureAgent(model_client)
        doc = await agent.generate_architecture(requirements_doc)
    """

    def __init__(self, model_client):
        self.agent = AssistantAgent(
            name="ArchitectureAgent",
            model_client=model_client,
            system_message=SYSTEM_PROMPT,
        )

    async def generate_architecture(
        self, requirements: RequirementsDocument
    ) -> ArchitectureDocument:
        """Generate architecture from requirements."""
        prompt = GENERATE_ARCHITECTURE_PROMPT.format(
            requirements_json=requirements.model_dump_json(indent=2),
        )
        response = await self.agent.on_messages(
            [TextMessage(content=prompt, source="user")],
            CancellationToken(),
        )
        raw = response.chat_message.content
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
        data = json.loads(raw)
        return ArchitectureDocument(**data)

    async def refine(
        self, current_doc: ArchitectureDocument, feedback: str
    ) -> ArchitectureDocument:
        """Refine architecture based on user feedback."""
        prompt = REFINE_PROMPT.format(
            current_architecture=current_doc.model_dump_json(indent=2),
            feedback=feedback,
        )
        response = await self.agent.on_messages(
            [TextMessage(content=prompt, source="user")],
            CancellationToken(),
        )
        raw = response.chat_message.content
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
        data = json.loads(raw)
        return ArchitectureDocument(**data)
