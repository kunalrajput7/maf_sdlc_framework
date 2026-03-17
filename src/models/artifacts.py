"""
Artifact models — the final documents produced by each agent.

Each artifact is a complete, self-contained document that:
  1. Gets stored in ProjectContext for cross-agent communication
  2. Gets saved to /outputs/ as a markdown file for human review
"""

from pydantic import BaseModel, Field
from src.models.project import (
    UserPersona,
    UserStory,
    FunctionalRequirement,
    NonFunctionalRequirement,
    TechStack,
    APIEndpoint,
    DatabaseTable,
    Component,
    Epic,
    Sprint,
)


class RequirementsDocument(BaseModel):
    """Complete requirements output from the Requirements Agent."""

    project_name: str
    project_summary: str = Field(description="2-3 sentence summary of the project")
    personas: list[UserPersona]
    user_stories: list[UserStory]
    functional_requirements: list[FunctionalRequirement]
    non_functional_requirements: list[NonFunctionalRequirement]

    def to_markdown(self) -> str:
        """Convert to a readable markdown document."""
        lines = [
            f"# Requirements Document: {self.project_name}\n",
            f"## Project Summary\n{self.project_summary}\n",
            "## User Personas\n",
        ]
        for p in self.personas:
            lines.append(f"### {p.name} ({p.role})")
            lines.append(f"**Goals:** {', '.join(p.goals)}")
            lines.append(f"**Pain Points:** {', '.join(p.pain_points)}\n")

        lines.append("## User Stories\n")
        for s in self.user_stories:
            lines.append(f"### {s.id}: As a {s.as_a}, I want {s.i_want}")
            lines.append(f"**So that:** {s.so_that}")
            lines.append(f"**Priority:** {s.priority}")
            lines.append("**Acceptance Criteria:**")
            for ac in s.acceptance_criteria:
                lines.append(f"  - {ac}")
            lines.append("")

        lines.append("## Functional Requirements\n")
        for fr in self.functional_requirements:
            lines.append(f"- **{fr.id} - {fr.title}** [{fr.priority}]: {fr.description}")

        lines.append("\n## Non-Functional Requirements\n")
        for nfr in self.non_functional_requirements:
            metric = f" (Target: {nfr.target_metric})" if nfr.target_metric else ""
            lines.append(f"- **{nfr.id} [{nfr.category}]**: {nfr.description}{metric}")

        return "\n".join(lines)


class ArchitectureDocument(BaseModel):
    """Complete architecture output from the Architecture Agent."""

    overview: str = Field(description="High-level architecture overview")
    tech_stack: TechStack
    components: list[Component]
    api_endpoints: list[APIEndpoint]
    database_tables: list[DatabaseTable]
    architecture_notes: str = Field(default="", description="Additional architecture decisions and trade-offs")

    def to_markdown(self) -> str:
        """Convert to a readable markdown document."""
        lines = [
            "# Architecture Document\n",
            f"## Overview\n{self.overview}\n",
            "## Tech Stack\n",
            f"- **Frontend:** {self.tech_stack.frontend}",
            f"- **Backend:** {self.tech_stack.backend}",
            f"- **Database:** {self.tech_stack.database}",
            f"- **Infrastructure:** {self.tech_stack.infrastructure}",
            f"- **Reasoning:** {self.tech_stack.reasoning}\n",
            "## System Components\n",
        ]
        for c in self.components:
            lines.append(f"### {c.name}")
            lines.append(f"{c.description}")
            lines.append(f"**Responsibility:** {c.responsibility}")
            if c.dependencies:
                lines.append(f"**Dependencies:** {', '.join(c.dependencies)}")
            lines.append("")

        lines.append("## API Endpoints\n")
        lines.append("| Method | Path | Description |")
        lines.append("|--------|------|-------------|")
        for ep in self.api_endpoints:
            lines.append(f"| {ep.method} | `{ep.path}` | {ep.description} |")

        lines.append("\n## Database Schema\n")
        for t in self.database_tables:
            lines.append(f"### {t.name}")
            lines.append(f"{t.description}")
            lines.append("```")
            for col in t.columns:
                lines.append(f"  {col}")
            lines.append("```")
            if t.relationships:
                lines.append(f"**Relationships:** {', '.join(t.relationships)}")
            lines.append("")

        if self.architecture_notes:
            lines.append(f"## Architecture Notes\n{self.architecture_notes}\n")

        return "\n".join(lines)


class ProjectPlan(BaseModel):
    """Complete project plan output from the Planning Agent."""

    epics: list[Epic]
    sprints: list[Sprint]
    total_story_points: int
    estimated_weeks: int
    risks: list[str] = Field(description="Identified project risks")
    assumptions: list[str] = Field(default_factory=list, description="Planning assumptions made")

    def to_markdown(self) -> str:
        """Convert to a readable markdown document."""
        lines = [
            "# Project Plan\n",
            f"**Total Story Points:** {self.total_story_points}",
            f"**Estimated Duration:** {self.estimated_weeks} weeks\n",
            "## Epics & Stories\n",
        ]
        for epic in self.epics:
            lines.append(f"### {epic.id}: {epic.title}")
            lines.append(f"{epic.description}\n")
            for story in epic.stories:
                lines.append(f"#### {story.id}: {story.title} ({story.total_points} pts)")
                lines.append(f"{story.description}")
                lines.append("| Task | Points | Priority | Dependencies |")
                lines.append("|------|--------|----------|--------------|")
                for task in story.tasks:
                    deps = ", ".join(task.dependencies) if task.dependencies else "None"
                    lines.append(f"| {task.id}: {task.title} | {task.story_points} | {task.priority} | {deps} |")
                lines.append("")

        lines.append("## Sprint Plan\n")
        for sprint in self.sprints:
            lines.append(f"### Sprint {sprint.number}: {sprint.goal}")
            lines.append(f"**Stories:** {', '.join(sprint.story_ids)}")
            lines.append(f"**Total Points:** {sprint.total_points}\n")

        lines.append("## Risks\n")
        for risk in self.risks:
            lines.append(f"- {risk}")

        if self.assumptions:
            lines.append("\n## Assumptions\n")
            for a in self.assumptions:
                lines.append(f"- {a}")

        return "\n".join(lines)
