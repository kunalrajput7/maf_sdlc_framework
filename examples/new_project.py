"""
Example: Plan a new project from scratch.

This shows how to use the orchestrator programmatically
instead of the interactive CLI. Useful for testing or automation.

Usage:
    python examples/new_project.py
"""

import asyncio
from src.orchestrator.context import ProjectContext
from src.agents.requirements import RequirementsAgent
from src.agents.architecture import ArchitectureAgent
from src.agents.planning import PlanningAgent
from src.tools.file_tool import save_artifact
from src.utils.config import get_settings
from src.utils.llm import create_model_client


async def main():
    settings = get_settings()

    # ── Setup agents ──
    req_agent = RequirementsAgent(
        create_model_client(settings, settings.requirements_deployment)
    )
    arch_agent = ArchitectureAgent(
        create_model_client(settings, settings.architecture_deployment)
    )
    plan_agent = PlanningAgent(
        create_model_client(settings, settings.planning_deployment)
    )

    # ── Define the project ──
    description = """
    Build a campus food delivery app for college students.
    Students can order from campus restaurants and cafeterias.
    Delivery is done by other students who want to earn extra money.
    Payment via student meal plans and credit cards.
    """

    # ── Phase 1: Requirements ──
    print("Phase 1: Generating requirements...")
    questions = await req_agent.generate_questions(description)
    print(f"Questions the agent would ask:\n{questions}\n")

    # In this example, we provide pre-written answers
    answers = """
    Target users: college students (18-25), campus restaurants, student delivery drivers.
    Core features: ordering, real-time tracking, payment, ratings.
    Scale: single campus initially, ~5000 users.
    Platform: mobile app (iOS + Android) with web dashboard for restaurants.
    Payment: student meal plan integration + Stripe for cards.
    """

    requirements = await req_agent.generate_requirements(description, answers)
    save_artifact("requirements.md", requirements.to_markdown())
    print("Requirements saved to outputs/requirements.md\n")

    # ── Phase 2: Architecture ──
    print("Phase 2: Designing architecture...")
    architecture = await arch_agent.generate_architecture(requirements)
    save_artifact("architecture.md", architecture.to_markdown())
    print("Architecture saved to outputs/architecture.md\n")

    # ── Phase 3: Planning ──
    print("Phase 3: Creating project plan...")
    plan = await plan_agent.generate_plan(requirements, architecture)
    save_artifact("project_plan.md", plan.to_markdown())
    print("Project plan saved to outputs/project_plan.md\n")

    print("Done! Check the /outputs/ folder for all artifacts.")


if __name__ == "__main__":
    asyncio.run(main())
