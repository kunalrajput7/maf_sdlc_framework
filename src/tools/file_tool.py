"""
File Tool — saves generated artifacts to the /outputs/ directory.

Each run of the orchestrator produces markdown files that serve as
the deliverable documents for human review.
"""

import os
from pathlib import Path

# Output directory (relative to project root)
OUTPUTS_DIR = Path(__file__).parent.parent.parent / "outputs"


def save_artifact(filename: str, content: str) -> str:
    """
    Save a generated artifact to the outputs directory.

    Args:
        filename: Name of the file (e.g., 'requirements.md')
        content: The markdown content to save

    Returns:
        The full path where the file was saved
    """
    OUTPUTS_DIR.mkdir(exist_ok=True)
    filepath = OUTPUTS_DIR / filename
    filepath.write_text(content, encoding="utf-8")
    return str(filepath)
