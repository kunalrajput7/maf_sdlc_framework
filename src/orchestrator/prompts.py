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

PROJECT_TYPE_PROMPT = """
[bold]What type of project?[/bold]

  [cyan][1][/cyan] New project from scratch
  [cyan][2][/cyan] Enhance an existing project (provide GitHub repo URL)
"""

MISSING_ENV_MESSAGE = """
[bold red]Missing required configuration![/bold red]

MAF needs Azure AI Foundry credentials to run. Please:

  1. Copy the environment template:
     [cyan]cp .env.example .env[/cyan]

  2. Fill in your Azure AI Foundry values in [cyan].env[/cyan]:
     - AZURE_OPENAI_ENDPOINT
     - AZURE_OPENAI_API_KEY

  3. Run again:
     [cyan]python main.py[/cyan]

See [cyan]documentation.md[/cyan] for the full setup guide.
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
