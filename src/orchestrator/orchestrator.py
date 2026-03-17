"""
Orchestrator — the meta-agent that coordinates the entire SDLC flow.

This is the main engine. It:
  1. Creates all agent instances with their respective model clients
  2. Runs agents in sequence: Requirements → Architecture → Planning
  3. Manages human gates (review & approve) between each phase
  4. Maintains the shared ProjectContext across all phases
  5. Saves artifacts to the /outputs/ directory
"""

import asyncio

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from src.agents.requirements import RequirementsAgent
from src.agents.architecture import ArchitectureAgent
from src.agents.planning import PlanningAgent
from src.orchestrator.context import ProjectContext
from src.orchestrator.prompts import WELCOME_MESSAGE, PHASE_HEADERS, COMPLETION_MESSAGE
from src.tools.file_tool import save_artifact
from src.utils.config import get_settings
from src.utils.llm import create_model_client

console = Console()


class Orchestrator:
    """
    Coordinates the 3-phase SDLC flow with human-in-the-loop gates.

    Usage:
        orchestrator = Orchestrator()
        await orchestrator.run()
    """

    def __init__(self):
        settings = get_settings()

        # Create model clients — each agent can use a different deployment
        req_client = create_model_client(settings, settings.requirements_deployment)
        arch_client = create_model_client(settings, settings.architecture_deployment)
        plan_client = create_model_client(settings, settings.planning_deployment)

        # Create agents
        self.requirements_agent = RequirementsAgent(req_client)
        self.architecture_agent = ArchitectureAgent(arch_client)
        self.planning_agent = PlanningAgent(plan_client)

        # Shared context
        self.context = ProjectContext()

    async def run(self):
        """Run the full 3-phase SDLC flow."""
        console.print(WELCOME_MESSAGE)

        # Get project description from user
        console.print("[bold]Describe your project idea:[/bold]")
        self.context.project_description = input("\n> ").strip()

        if not self.context.project_description:
            console.print("[red]No project description provided. Exiting.[/red]")
            return

        # Phase 1: Requirements
        await self._run_requirements_phase()

        # Phase 2: Architecture
        await self._run_architecture_phase()

        # Phase 3: Planning
        await self._run_planning_phase()

        # Done!
        console.print(COMPLETION_MESSAGE)

    # ──────────────────────────────────────────────────────
    # Phase 1: Requirements
    # ──────────────────────────────────────────────────────

    async def _run_requirements_phase(self):
        console.print(PHASE_HEADERS["requirements"])

        # Step 1: Generate clarifying questions
        console.print("[bold]Generating clarifying questions...[/bold]\n")
        questions = await self.requirements_agent.generate_questions(
            self.context.project_description
        )
        console.print(Panel(questions, title="Clarifying Questions"))

        # Step 2: Get user's answers
        console.print("\n[bold]Answer the questions above (type your answers):[/bold]")
        self.context.clarifying_answers = input("\n> ").strip()

        # Step 3: Generate requirements document
        console.print("\n[bold]Generating requirements document...[/bold]\n")
        self.context.requirements = await self.requirements_agent.generate_requirements(
            self.context.project_description,
            self.context.clarifying_answers,
        )

        # Step 4: Show to user and get approval
        markdown = self.context.requirements.to_markdown()
        console.print(Markdown(markdown))

        approved = await self._human_gate("requirements")
        if not approved:
            return

        # Save artifact
        save_artifact("requirements.md", markdown)
        self.context.mark_phase_complete("requirements")
        console.print("[green]Requirements phase complete. Artifact saved.[/green]\n")

    # ──────────────────────────────────────────────────────
    # Phase 2: Architecture
    # ──────────────────────────────────────────────────────

    async def _run_architecture_phase(self):
        if self.context.requirements is None:
            console.print("[red]Cannot run architecture phase without requirements.[/red]")
            return

        console.print(PHASE_HEADERS["architecture"])
        console.print("[bold]Designing system architecture...[/bold]\n")

        self.context.architecture = await self.architecture_agent.generate_architecture(
            self.context.requirements
        )

        markdown = self.context.architecture.to_markdown()
        console.print(Markdown(markdown))

        approved = await self._human_gate("architecture")
        if not approved:
            return

        save_artifact("architecture.md", markdown)
        self.context.mark_phase_complete("architecture")
        console.print("[green]Architecture phase complete. Artifact saved.[/green]\n")

    # ──────────────────────────────────────────────────────
    # Phase 3: Planning
    # ──────────────────────────────────────────────────────

    async def _run_planning_phase(self):
        if self.context.requirements is None or self.context.architecture is None:
            console.print("[red]Cannot run planning phase without requirements and architecture.[/red]")
            return

        console.print(PHASE_HEADERS["planning"])
        console.print("[bold]Creating project plan...[/bold]\n")

        self.context.project_plan = await self.planning_agent.generate_plan(
            self.context.requirements,
            self.context.architecture,
        )

        markdown = self.context.project_plan.to_markdown()
        console.print(Markdown(markdown))

        approved = await self._human_gate("planning")
        if not approved:
            return

        save_artifact("project_plan.md", markdown)
        self.context.mark_phase_complete("planning")
        console.print("[green]Planning phase complete. Artifact saved.[/green]\n")

    # ──────────────────────────────────────────────────────
    # Human Gate — review & approve between phases
    # ──────────────────────────────────────────────────────

    async def _human_gate(self, phase: str) -> bool:
        """
        Pause for human review. User can:
          - 'yes' / 'approve' → proceed to next phase
          - 'no' / 'reject'  → stop the flow
          - anything else     → treated as feedback, agent refines output
        """
        while True:
            console.print(
                f"\n[bold yellow]Review the {phase} output above.[/bold yellow]"
            )
            console.print("  Type [green]'yes'[/green] to approve and continue")
            console.print("  Type [red]'no'[/red] to stop")
            console.print("  Or type your [cyan]feedback[/cyan] to refine\n")

            response = input("> ").strip().lower()

            if response in ("yes", "approve", "y"):
                return True

            if response in ("no", "reject", "n"):
                console.print("[red]Flow stopped by user.[/red]")
                return False

            # User gave feedback — refine
            console.print(f"\n[bold]Refining {phase} based on your feedback...[/bold]\n")

            if phase == "requirements" and self.context.requirements:
                self.context.requirements = await self.requirements_agent.refine(
                    self.context.requirements, response
                )
                console.print(Markdown(self.context.requirements.to_markdown()))

            elif phase == "architecture" and self.context.architecture:
                self.context.architecture = await self.architecture_agent.refine(
                    self.context.architecture, response
                )
                console.print(Markdown(self.context.architecture.to_markdown()))

            elif phase == "planning" and self.context.project_plan:
                self.context.project_plan = await self.planning_agent.refine(
                    self.context.project_plan, response
                )
                console.print(Markdown(self.context.project_plan.to_markdown()))
