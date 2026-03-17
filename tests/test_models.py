"""
Tests for data models and artifact serialization.

These tests verify that our Pydantic models work correctly
and that to_markdown() produces readable output.

Run with: pytest tests/
"""

from src.models.project import UserPersona, UserStory, Task, Story, Epic, Sprint
from src.models.artifacts import RequirementsDocument, ArchitectureDocument, ProjectPlan
from src.models.project import (
    FunctionalRequirement,
    NonFunctionalRequirement,
    TechStack,
    APIEndpoint,
    DatabaseTable,
    Component,
)


def test_user_story_creation():
    """User stories should be created with all required fields."""
    story = UserStory(
        id="US-001",
        as_a="student",
        i_want="to order food from my phone",
        so_that="I don't have to wait in line",
        acceptance_criteria=["Can browse menu", "Can add items to cart"],
        priority="high",
    )
    assert story.id == "US-001"
    assert story.priority == "high"
    assert len(story.acceptance_criteria) == 2


def test_requirements_document_to_markdown():
    """RequirementsDocument should produce readable markdown."""
    doc = RequirementsDocument(
        project_name="Test Project",
        project_summary="A test project for unit testing.",
        personas=[
            UserPersona(
                name="Developer",
                role="Software Engineer",
                goals=["Write clean code"],
                pain_points=["Too many meetings"],
            )
        ],
        user_stories=[
            UserStory(
                id="US-001",
                as_a="developer",
                i_want="to run tests",
                so_that="I know my code works",
                acceptance_criteria=["Tests pass"],
                priority="high",
            )
        ],
        functional_requirements=[
            FunctionalRequirement(
                id="FR-001",
                title="Test Runner",
                description="System must run tests",
                priority="high",
            )
        ],
        non_functional_requirements=[
            NonFunctionalRequirement(
                id="NFR-001",
                category="Performance",
                description="Tests must run in under 10 seconds",
                target_metric="<10s",
            )
        ],
    )
    md = doc.to_markdown()
    assert "# Requirements Document: Test Project" in md
    assert "US-001" in md
    assert "FR-001" in md
    assert "NFR-001" in md


def test_architecture_document_to_markdown():
    """ArchitectureDocument should produce readable markdown."""
    doc = ArchitectureDocument(
        overview="A simple test architecture.",
        tech_stack=TechStack(
            frontend="React",
            backend="FastAPI",
            database="PostgreSQL",
            infrastructure="AWS",
            reasoning="Standard modern stack",
        ),
        components=[
            Component(
                name="API Server",
                description="Handles HTTP requests",
                responsibility="Request routing and validation",
                dependencies=[],
            )
        ],
        api_endpoints=[
            APIEndpoint(
                method="GET",
                path="/api/v1/health",
                description="Health check endpoint",
            )
        ],
        database_tables=[
            DatabaseTable(
                name="users",
                description="User accounts",
                columns=["id: UUID PRIMARY KEY", "email: VARCHAR(255) UNIQUE"],
            )
        ],
    )
    md = doc.to_markdown()
    assert "# Architecture Document" in md
    assert "React" in md
    assert "/api/v1/health" in md


def test_project_plan_to_markdown():
    """ProjectPlan should produce readable markdown."""
    plan = ProjectPlan(
        epics=[
            Epic(
                id="E-001",
                title="Core Setup",
                description="Initial project setup",
                stories=[
                    Story(
                        id="S-001",
                        title="Project scaffolding",
                        description="Set up the project structure",
                        tasks=[
                            Task(
                                id="T-001",
                                title="Init repo",
                                description="Initialize the repository",
                                story_points=1,
                                priority="high",
                            )
                        ],
                        total_points=1,
                    )
                ],
            )
        ],
        sprints=[
            Sprint(number=1, goal="MVP skeleton", story_ids=["S-001"], total_points=1)
        ],
        total_story_points=1,
        estimated_weeks=1,
        risks=["Tight timeline"],
        assumptions=["Team of 2 developers"],
    )
    md = plan.to_markdown()
    assert "# Project Plan" in md
    assert "E-001" in md
    assert "Sprint 1" in md


def test_project_context_phase_tracking():
    """ProjectContext should track completed phases correctly."""
    from src.orchestrator.context import ProjectContext

    ctx = ProjectContext()
    assert ctx.current_phase == "requirements"

    ctx.mark_phase_complete("requirements")
    assert ctx.current_phase == "architecture"

    ctx.mark_phase_complete("architecture")
    assert ctx.current_phase == "planning"

    ctx.mark_phase_complete("planning")
    assert ctx.current_phase == "done"
