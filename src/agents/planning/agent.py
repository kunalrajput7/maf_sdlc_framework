"""
Planning Agent — creates project plan with epics, stories, tasks, and sprints.

Flow:
  1. Reads RequirementsDocument + ArchitectureDocument from ProjectContext
  2. Produces a complete ProjectPlan (epics, stories, tasks, sprint allocation)
  3. Can refine based on user feedback
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


class PlanningAgent:
    """
    Wraps an AutoGen AssistantAgent specialized in project planning.

    Usage:
        agent = PlanningAgent(model_client)
        plan = await agent.generate_plan(requirements_doc, architecture_doc)
    """

    def __init__(self, model_client):
        self.agent = AssistantAgent(
            name="PlanningAgent",
            model_client=model_client,
            system_message=SYSTEM_PROMPT,
        )

    async def generate_plan(
        self, requirements: RequirementsDocument, architecture: ArchitectureDocument
    ) -> ProjectPlan:
        """Generate a project plan from requirements and architecture."""
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
