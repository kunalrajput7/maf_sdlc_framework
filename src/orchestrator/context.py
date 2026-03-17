"""
ProjectContext — the shared state that flows between all agents.

This is the KEY piece that makes cross-phase intelligence work.
When one agent produces output, it's stored here. The next agent
reads from here, maintaining full context across the entire SDLC.

Think of it as the "project memory" that every agent can access.
"""

from dataclasses import dataclass, field
from src.models.artifacts import (
    RequirementsDocument,
    ArchitectureDocument,
    ProjectPlan,
)


@dataclass
class ProjectContext:
    """
    Shared context that accumulates as agents complete their phases.

    Flow:
      1. User provides project_description
      2. Requirements Agent fills in: requirements
      3. Architecture Agent fills in: architecture
      4. Planning Agent fills in: project_plan

    Each agent reads the context from previous phases and adds its own output.
    """

    # Input from user
    project_description: str = ""
    clarifying_answers: str = ""

    # Phase 1 output (Requirements Agent)
    requirements: RequirementsDocument | None = None

    # Phase 2 output (Architecture Agent)
    architecture: ArchitectureDocument | None = None

    # Phase 3 output (Planning Agent)
    project_plan: ProjectPlan | None = None

    # Tracks which phases are complete
    completed_phases: list[str] = field(default_factory=list)

    def mark_phase_complete(self, phase: str):
        """Mark a phase as completed."""
        if phase not in self.completed_phases:
            self.completed_phases.append(phase)

    @property
    def current_phase(self) -> str:
        """Determine the current phase based on what's completed."""
        if "planning" in self.completed_phases:
            return "done"
        if "architecture" in self.completed_phases:
            return "planning"
        if "requirements" in self.completed_phases:
            return "architecture"
        return "requirements"
