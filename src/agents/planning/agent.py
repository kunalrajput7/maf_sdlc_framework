"""
Planning Agent — creates project plan with epics, stories, tasks, and sprints.

This is now a TRULY AGENTIC agent. It can:
  1. Load risk category checklists to ensure comprehensive risk assessment
  2. Validate its plan for consistency (point totals, dependencies, sprint loads)
  3. Self-correct before presenting to the user

Flow:
  1. Reads RequirementsDocument + ArchitectureDocument from ProjectContext
  2. Uses tools to load checklists and validate output
  3. Produces a complete ProjectPlan
  4. Validates consistency, fixes issues, then presents
"""

import json

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken

from src.agents.planning.prompts import (
    SYSTEM_PROMPT,
    GENERATE_PLAN_PROMPT,
    REFINE_PROMPT,
)
from src.models.artifacts import RequirementsDocument, ArchitectureDocument, ProjectPlan
from src.tools.template_tool import risk_checklist_tool
from src.tools.validator_tool import plan_validator


class PlanningAgent:
    """
    Wraps an AutoGen AssistantAgent specialized in project planning.

    Tools available:
      - load_risk_checklist: Load risk categories for comprehensive assessment
      - validate_plan: Check output for consistent IDs, points, and dependencies
    """

    def __init__(self, model_client):
        self.agent = AssistantAgent(
            name="PlanningAgent",
            model_client=model_client,
            system_message=SYSTEM_PROMPT,
            tools=[risk_checklist_tool, plan_validator],
        )

    async def generate_plan(
        self, requirements: RequirementsDocument, architecture: ArchitectureDocument
    ) -> ProjectPlan:
        """Generate a project plan, using tools for checklists and validation."""
        prompt = GENERATE_PLAN_PROMPT.format(
            requirements_json=requirements.model_dump_json(indent=2),
            architecture_json=architecture.model_dump_json(indent=2),
        )
        response = await self.agent.on_messages(
            [TextMessage(content=prompt, source="user")],
            CancellationToken(),
        )
        raw = response.chat_message.content
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
        data = json.loads(raw)
        return ProjectPlan(**data)

    async def refine(
        self, current_plan: ProjectPlan, feedback: str
    ) -> ProjectPlan:
        """Refine the plan based on user feedback."""
        prompt = REFINE_PROMPT.format(
            current_plan=current_plan.model_dump_json(indent=2),
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
        return ProjectPlan(**data)
