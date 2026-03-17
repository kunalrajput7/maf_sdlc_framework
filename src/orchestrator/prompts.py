"""
Prompts for the Orchestrator.

The Orchestrator is the meta-agent that coordinates the entire flow.
It manages phase transitions, user interactions, and human gates.
"""

WELCOME_MESSAGE = """
╔══════════════════════════════════════════════════════════════╗
║             MAF — AI-Powered SDLC Platform                  ║
║                     Phase 1 MVP                             ║
╠══════════════════════════════════════════════════════════════╣
║                                                             ║
║  This tool will help you plan your software project using   ║
║  3 specialized AI agents:                                   ║
║                                                             ║
║    1. Requirements Agent  → Gathers & structures needs      ║
║    2. Architecture Agent  → Designs system architecture     ║
║    3. Planning Agent      → Creates sprint plan & estimates ║
║                                                             ║
║  You'll review and approve each phase before moving on.     ║
║                                                             ║
╚══════════════════════════════════════════════════════════════╝
"""

PHASE_HEADERS = {
    "requirements": """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PHASE 1: REQUIREMENTS GATHERING
  Agent: Requirements Agent (Senior Business Analyst)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
    "architecture": """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PHASE 2: ARCHITECTURE DESIGN
  Agent: Architecture Agent (Senior Software Architect)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
    "planning": """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PHASE 3: PROJECT PLANNING
  Agent: Planning Agent (Senior Engineering Manager)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
}

COMPLETION_MESSAGE = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ALL PHASES COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your project artifacts have been saved to the /outputs/ folder:

  - requirements.md    → Full requirements document
  - architecture.md    → System architecture design
  - project_plan.md    → Sprint plan with estimates

Review these files and use them to kickstart your development!
"""
