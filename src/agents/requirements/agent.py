"""
Requirements Agent — gathers and structures project requirements.

Flow:
  1. Takes the user's project description
  2. Generates clarifying questions
  3. Uses the user's answers to produce a full RequirementsDocument
  4. Can refine based on user feedback
"""

import json

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken

from src.agents.requirements.prompts import (
    SYSTEM_PROMPT,
    CLARIFYING_QUESTIONS_PROMPT,
    GENERATE_REQUIREMENTS_PROMPT,
    REFINE_PROMPT,
)
from src.models.artifacts import RequirementsDocument


class RequirementsAgent:
    """
    Wraps an AutoGen AssistantAgent specialized in requirements gathering.

    Usage:
        agent = RequirementsAgent(model_client)
        questions = await agent.generate_questions("Build a food delivery app")
        # ... user answers questions ...
        doc = await agent.generate_requirements("Build a food delivery app", user_answers)
    """

    def __init__(self, model_client):
        self.agent = AssistantAgent(
            name="RequirementsAgent",
            model_client=model_client,
            system_message=SYSTEM_PROMPT,
        )

    async def generate_questions(self, project_description: str) -> str:
        """Generate clarifying questions about the project."""
        prompt = CLARIFYING_QUESTIONS_PROMPT.format(project_description=project_description)
        response = await self.agent.on_messages(
            [TextMessage(content=prompt, source="user")],
            CancellationToken(),
        )
        return response.chat_message.content

    async def generate_requirements(
        self, project_description: str, user_answers: str
    ) -> RequirementsDocument:
        """Generate a complete requirements document."""
        prompt = GENERATE_REQUIREMENTS_PROMPT.format(
            project_description=project_description,
            user_answers=user_answers,
        )
        response = await self.agent.on_messages(
            [TextMessage(content=prompt, source="user")],
            CancellationToken(),
        )

        # Parse the JSON response into our structured model
        raw = response.chat_message.content
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
        data = json.loads(raw)
        return RequirementsDocument(**data)

    async def refine(
        self, current_doc: RequirementsDocument, feedback: str
    ) -> RequirementsDocument:
        """Refine requirements based on user feedback."""
        prompt = REFINE_PROMPT.format(
            current_requirements=current_doc.model_dump_json(indent=2),
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
        return RequirementsDocument(**data)
