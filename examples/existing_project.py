"""
Example: Plan enhancements for an existing project.

This shows how to describe an existing project and get a plan
for adding new features to it.

Usage:
    python examples/existing_project.py
"""

import asyncio
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

    # ── Describe the existing project + desired changes ──
    description = """
    I have an existing e-commerce platform built with:
    - Frontend: React + TypeScript
    - Backend: Node.js + Express
    - Database: PostgreSQL
    - Deployed on AWS (ECS + RDS)

    I want to add a payment gateway integration (Stripe) to replace our
    current manual invoice system. This should include:
    - Checkout flow with card payments
    - Subscription/recurring payment support
    - Invoice generation
    - Refund handling
    - Webhook processing for payment events
    """

    answers = """
    Current users: ~2000 active merchants, ~50,000 end customers.
    Transaction volume: ~1000 orders/day, average $45/order.
    Must keep existing API contracts — new payment endpoints only.
    Timeline: need this in production within 6 weeks.
    Compliance: PCI-DSS compliance required — we'll use Stripe Elements (no raw card data).
    """

    # ── Run the pipeline ──
    print("Phase 1: Generating requirements...")
    requirements = await req_agent.generate_requirements(description, answers)
    save_artifact("requirements.md", requirements.to_markdown())

    print("Phase 2: Designing architecture...")
    architecture = await arch_agent.generate_architecture(requirements)
    save_artifact("architecture.md", architecture.to_markdown())

    print("Phase 3: Creating project plan...")
    plan = await plan_agent.generate_plan(requirements, architecture)
    save_artifact("project_plan.md", plan.to_markdown())

    print("\nDone! Check the /outputs/ folder for all artifacts.")


if __name__ == "__main__":
    asyncio.run(main())
