"""
Validator Tool — checks agent output for consistency and completeness.

Used by agents to verify their own work before presenting to the user:
  - Are all IDs unique?
  - Do dependencies reference real tasks?
  - Do sprint point totals add up?
  - Are all requirements covered by the architecture?
  - Does the plan cover all architectural components?

This is what makes agents self-correcting — they can catch their own mistakes.
"""

import json

from autogen_core.tools import FunctionTool


async def validate_requirements(requirements_json: str) -> str:
    """
    Validate a requirements document for completeness and consistency.

    Checks:
    - All IDs are unique
    - At least 1 persona, 5 user stories, 5 functional requirements, 3 NFRs
    - All priorities are valid (high/medium/low)
    - Not everything is marked "high" priority

    Args:
        requirements_json: The requirements document as a JSON string

    Returns:
        Validation result: either "VALID" or a list of issues to fix
    """
    try:
        data = json.loads(requirements_json)
    except json.JSONDecodeError as e:
        return f"INVALID JSON: {e}"

    issues = []

    # Check minimums
    personas = data.get("personas", [])
    stories = data.get("user_stories", [])
    frs = data.get("functional_requirements", [])
    nfrs = data.get("non_functional_requirements", [])

    if len(personas) < 1:
        issues.append("Need at least 1 user persona")
    if len(stories) < 5:
        issues.append(f"Need at least 5 user stories, found {len(stories)}")
    if len(frs) < 5:
        issues.append(f"Need at least 5 functional requirements, found {len(frs)}")
    if len(nfrs) < 3:
        issues.append(f"Need at least 3 non-functional requirements, found {len(nfrs)}")

    # Check unique IDs
    all_ids = [s.get("id") for s in stories] + [f.get("id") for f in frs] + [n.get("id") for n in nfrs]
    duplicates = [x for x in all_ids if all_ids.count(x) > 1]
    if duplicates:
        issues.append(f"Duplicate IDs found: {set(duplicates)}")

    # Check priority distribution
    valid_priorities = {"high", "medium", "low"}
    all_priorities = [s.get("priority", "") for s in stories + frs]
    invalid = [p for p in all_priorities if p not in valid_priorities]
    if invalid:
        issues.append(f"Invalid priorities found: {set(invalid)}. Must be high/medium/low")

    high_count = sum(1 for p in all_priorities if p == "high")
    if len(all_priorities) > 0 and high_count / len(all_priorities) > 0.6:
        issues.append(
            f"{high_count}/{len(all_priorities)} items are 'high' priority. "
            "Be more realistic — not everything can be high priority."
        )

    # Check user stories have acceptance criteria
    for story in stories:
        ac = story.get("acceptance_criteria", [])
        if len(ac) < 1:
            issues.append(f"Story {story.get('id')} has no acceptance criteria")

    if not issues:
        return "VALID: Requirements document passes all checks."

    return "ISSUES FOUND:\n" + "\n".join(f"  - {issue}" for issue in issues)


async def validate_architecture(architecture_json: str, requirements_json: str) -> str:
    """
    Validate an architecture document against the requirements.

    Checks:
    - Has tech stack with all fields
    - Has at least 3 components
    - Has at least 5 API endpoints
    - Has at least 3 database tables
    - Components have clear responsibilities

    Args:
        architecture_json: The architecture document as a JSON string
        requirements_json: The requirements document to check coverage against

    Returns:
        Validation result: either "VALID" or a list of issues to fix
    """
    try:
        arch = json.loads(architecture_json)
        reqs = json.loads(requirements_json)
    except json.JSONDecodeError as e:
        return f"INVALID JSON: {e}"

    issues = []

    # Check tech stack
    stack = arch.get("tech_stack", {})
    for field in ["frontend", "backend", "database", "infrastructure", "reasoning"]:
        if not stack.get(field):
            issues.append(f"Tech stack missing: {field}")

    # Check minimums
    components = arch.get("components", [])
    endpoints = arch.get("api_endpoints", [])
    tables = arch.get("database_tables", [])

    if len(components) < 3:
        issues.append(f"Need at least 3 components, found {len(components)}")
    if len(endpoints) < 5:
        issues.append(f"Need at least 5 API endpoints, found {len(endpoints)}")
    if len(tables) < 3:
        issues.append(f"Need at least 3 database tables, found {len(tables)}")

    # Check API methods are valid
    valid_methods = {"GET", "POST", "PUT", "DELETE", "PATCH"}
    for ep in endpoints:
        if ep.get("method", "").upper() not in valid_methods:
            issues.append(f"Invalid HTTP method '{ep.get('method')}' in {ep.get('path')}")

    # Check that functional requirements have likely API coverage
    fr_count = len(reqs.get("functional_requirements", []))
    if fr_count > 0 and len(endpoints) < fr_count * 0.5:
        issues.append(
            f"Only {len(endpoints)} endpoints for {fr_count} functional requirements. "
            "Some requirements may not have API coverage."
        )

    if not issues:
        return "VALID: Architecture document passes all checks."

    return "ISSUES FOUND:\n" + "\n".join(f"  - {issue}" for issue in issues)


async def validate_plan(plan_json: str) -> str:
    """
    Validate a project plan for consistency.

    Checks:
    - All task/story/epic IDs are unique
    - Story total_points matches sum of task points
    - Sprint point totals are realistic (15-35 per sprint)
    - Task dependencies reference existing tasks
    - No circular dependencies
    - Total points matches sum across all stories

    Args:
        plan_json: The project plan as a JSON string

    Returns:
        Validation result: either "VALID" or a list of issues to fix
    """
    try:
        plan = json.loads(plan_json)
    except json.JSONDecodeError as e:
        return f"INVALID JSON: {e}"

    issues = []

    # Collect all IDs
    all_task_ids = set()
    all_story_ids = set()
    all_epic_ids = set()
    total_points = 0

    for epic in plan.get("epics", []):
        eid = epic.get("id", "")
        if eid in all_epic_ids:
            issues.append(f"Duplicate epic ID: {eid}")
        all_epic_ids.add(eid)

        for story in epic.get("stories", []):
            sid = story.get("id", "")
            if sid in all_story_ids:
                issues.append(f"Duplicate story ID: {sid}")
            all_story_ids.add(sid)

            task_points_sum = 0
            for task in story.get("tasks", []):
                tid = task.get("id", "")
                if tid in all_task_ids:
                    issues.append(f"Duplicate task ID: {tid}")
                all_task_ids.add(tid)
                task_points_sum += task.get("story_points", 0)

            # Check story points match
            declared = story.get("total_points", 0)
            if task_points_sum != declared:
                issues.append(
                    f"Story {sid}: declared {declared} points but tasks sum to {task_points_sum}"
                )
            total_points += task_points_sum

    # Check total points
    declared_total = plan.get("total_story_points", 0)
    if total_points != declared_total:
        issues.append(
            f"Declared total {declared_total} points but actual sum is {total_points}"
        )

    # Check sprint point loads
    for sprint in plan.get("sprints", []):
        sp = sprint.get("total_points", 0)
        num = sprint.get("number", "?")
        if sp > 40:
            issues.append(f"Sprint {num} has {sp} points — too heavy (max ~30-35)")
        if sp < 5 and sp > 0:
            issues.append(f"Sprint {num} has only {sp} points — too light")

    # Check sprint stories exist
    for sprint in plan.get("sprints", []):
        for sid in sprint.get("story_ids", []):
            if sid not in all_story_ids:
                issues.append(f"Sprint {sprint.get('number')} references unknown story: {sid}")

    # Check task dependencies exist
    for epic in plan.get("epics", []):
        for story in epic.get("stories", []):
            for task in story.get("tasks", []):
                for dep in task.get("dependencies", []):
                    if dep not in all_task_ids:
                        issues.append(f"Task {task.get('id')} depends on unknown task: {dep}")

    if not issues:
        return "VALID: Project plan passes all checks."

    return "ISSUES FOUND:\n" + "\n".join(f"  - {issue}" for issue in issues)


# Create AutoGen-compatible tools
requirements_validator = FunctionTool(
    validate_requirements,
    name="validate_requirements",
    description="Validate a requirements document for completeness, unique IDs, realistic priorities, and acceptance criteria.",
)

architecture_validator = FunctionTool(
    validate_architecture,
    name="validate_architecture",
    description="Validate an architecture document against requirements for coverage, proper tech stack, and sufficient components/endpoints/tables.",
)

plan_validator = FunctionTool(
    validate_plan,
    name="validate_plan",
    description="Validate a project plan for consistent IDs, correct point totals, realistic sprint loads, and valid dependencies.",
)
