"""
Architecture Agent — designs system architecture from requirements.

This is now a TRULY AGENTIC agent. It can:
  1. Search the web for technology comparisons and benchmarks
  2. Load API design checklists to ensure best practices
  3. Read files from GitHub repos (for existing project analysis)
  4. Validate its architecture against the requirements

Flow:
  1. Reads the RequirementsDocument from ProjectContext
  2. Uses tools to research technologies and load best practices
  3. Produces a complete ArchitectureDocument
  4. Validates coverage against requirements before presenting
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
from src.tools.web_search_tool import web_search
from src.tools.template_tool import api_checklist_tool
from src.tools.validator_tool import architecture_validator


class ArchitectureAgent:
    """
    Wraps an AutoGen AssistantAgent specialized in system architecture design.

    Tools available:
      - search_web: Research technology benchmarks and comparisons
      - load_api_design_checklist: Load API design best practices
      - validate_architecture: Check output for coverage and consistency

    Optionally accepts GitHub MCP tools for reading existing codebases.
    """

    def __init__(self, model_client, github_tools: list | None = None):
        tools = [web_search, api_checklist_tool, architecture_validator]
        if github_tools:
            tools.extend(github_tools)

        self.agent = AssistantAgent(
            name="ArchitectureAgent",
            model_client=model_client,
            system_message=SYSTEM_PROMPT,
            tools=tools,
        )

    async def generate_architecture(
        self, requirements: RequirementsDocument
    ) -> ArchitectureDocument:
        """Generate architecture from requirements, using tools for research and validation."""
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
