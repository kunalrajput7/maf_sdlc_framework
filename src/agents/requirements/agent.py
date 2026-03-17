"""
Requirements Agent — gathers and structures project requirements.

This is now a TRULY AGENTIC agent. It can:
  1. Search the web for similar products and market research
  2. Load NFR checklists to ensure completeness
  3. Read files from GitHub repos (for existing project analysis)
  4. Validate its own output before presenting to the user

Flow:
  1. Takes the user's project description
  2. Uses tools to research and gather information
  3. Generates clarifying questions
  4. Uses the user's answers + research to produce a RequirementsDocument
  5. Validates its output, fixes issues, then presents to the user
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
from src.tools.web_search_tool import web_search
from src.tools.template_tool import nfr_checklist_tool
from src.tools.validator_tool import requirements_validator


class RequirementsAgent:
    """
    Wraps an AutoGen AssistantAgent specialized in requirements gathering.

    Tools available:
      - search_web: Research similar products and market needs
      - load_nfr_checklist: Load comprehensive NFR category checklist
      - validate_requirements: Check output for completeness and consistency

    Optionally accepts GitHub MCP tools for reading existing repos.
    """

    def __init__(self, model_client, github_tools: list | None = None):
        # Combine custom tools + optional GitHub MCP tools
        tools = [web_search, nfr_checklist_tool, requirements_validator]
        if github_tools:
            tools.extend(github_tools)

        self.agent = AssistantAgent(
            name="RequirementsAgent",
            model_client=model_client,
            system_message=SYSTEM_PROMPT,
            tools=tools,
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
        """Generate a complete requirements document using tools for research and validation."""
        prompt = GENERATE_REQUIREMENTS_PROMPT.format(
            project_description=project_description,
            user_answers=user_answers,
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
