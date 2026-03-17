"""
Core data models used across all agents.

These Pydantic models define the structured data that flows between agents
through the shared ProjectContext. Each agent produces and consumes these models.
"""

from pydantic import BaseModel, Field


# ──────────────────────────────────────────────────────────────
# Requirements Models (produced by Requirements Agent)
# ──────────────────────────────────────────────────────────────


class UserPersona(BaseModel):
    """A target user of the system being built."""

    name: str = Field(description="Persona name (e.g., 'College Student')")
    role: str = Field(description="What role this persona plays")
    goals: list[str] = Field(description="What this persona wants to achieve")
    pain_points: list[str] = Field(description="Current frustrations or problems")


class UserStory(BaseModel):
    """A user story in standard format: As a [role], I want [goal], so that [benefit]."""

    id: str = Field(description="Unique ID like US-001")
    as_a: str = Field(description="The user role")
    i_want: str = Field(description="The desired action")
    so_that: str = Field(description="The expected benefit")
    acceptance_criteria: list[str] = Field(description="Conditions for this story to be 'done'")
    priority: str = Field(description="high / medium / low")


class FunctionalRequirement(BaseModel):
    """A specific functional capability the system must have."""

    id: str = Field(description="Unique ID like FR-001")
    title: str
    description: str
    priority: str = Field(description="high / medium / low")


class NonFunctionalRequirement(BaseModel):
    """A quality attribute or constraint (performance, security, etc.)."""

    id: str = Field(description="Unique ID like NFR-001")
    category: str = Field(description="e.g., Performance, Security, Scalability")
    description: str
    target_metric: str = Field(default="", description="Measurable target if applicable")


# ──────────────────────────────────────────────────────────────
# Architecture Models (produced by Architecture Agent)
# ──────────────────────────────────────────────────────────────


class TechStack(BaseModel):
    """Recommended technology stack with reasoning."""

    frontend: str = Field(description="Frontend framework/library")
    backend: str = Field(description="Backend framework/language")
    database: str = Field(description="Database technology")
    infrastructure: str = Field(description="Hosting/cloud setup")
    reasoning: str = Field(description="Why this stack was chosen")


class APIEndpoint(BaseModel):
    """A single API endpoint definition."""

    method: str = Field(description="HTTP method: GET, POST, PUT, DELETE")
    path: str = Field(description="URL path like /api/v1/users")
    description: str
    request_body: str = Field(default="", description="Expected request payload description")
    response_body: str = Field(default="", description="Expected response payload description")


class DatabaseTable(BaseModel):
    """A database table/collection definition."""

    name: str = Field(description="Table name")
    description: str
    columns: list[str] = Field(description="Column definitions like 'id: UUID PRIMARY KEY'")
    relationships: list[str] = Field(default_factory=list, description="Foreign key relationships")


class Component(BaseModel):
    """A system component or service."""

    name: str
    description: str
    responsibility: str = Field(description="What this component is responsible for")
    dependencies: list[str] = Field(default_factory=list, description="Other components it depends on")


# ──────────────────────────────────────────────────────────────
# Planning Models (produced by Planning Agent)
# ──────────────────────────────────────────────────────────────


class Task(BaseModel):
    """A single development task within a story."""

    id: str = Field(description="Unique ID like T-001")
    title: str
    description: str
    story_points: int = Field(description="Estimated effort (1, 2, 3, 5, 8, 13)")
    priority: str = Field(description="high / medium / low")
    dependencies: list[str] = Field(default_factory=list, description="IDs of tasks this depends on")


class Story(BaseModel):
    """A development story containing multiple tasks."""

    id: str = Field(description="Unique ID like S-001")
    title: str
    description: str
    tasks: list[Task]
    total_points: int = Field(description="Sum of all task story points")


class Epic(BaseModel):
    """A large body of work broken into stories."""

    id: str = Field(description="Unique ID like E-001")
    title: str
    description: str
    stories: list[Story]


class Sprint(BaseModel):
    """A time-boxed iteration (typically 2 weeks)."""

    number: int = Field(description="Sprint number (1, 2, 3...)")
    goal: str = Field(description="What this sprint aims to achieve")
    story_ids: list[str] = Field(description="IDs of stories included in this sprint")
    total_points: int
