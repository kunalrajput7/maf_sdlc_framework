# MAF — AI-Powered SDLC Platform

An AI multi-agent system that helps you plan software projects from idea to sprint-ready backlog.

## What It Does

Describe your project idea in plain English, and 3 specialized AI agents will produce:

1. **Requirements Document** — personas, user stories, functional & non-functional requirements
2. **Architecture Document** — tech stack, components, API design, database schema
3. **Project Plan** — epics, stories, tasks, estimates, sprint allocation

You review and approve each phase before moving on. AI proposes, you decide.

## Quick Start

```bash
# Install
pip install -e .

# Configure (add your Azure AI Foundry credentials)
cp .env.example .env
# Edit .env with your values

# Run
python main.py
```

## Tech Stack

- **AutoGen 0.4+** — Multi-agent orchestration
- **Azure AI Foundry** — GPT-4o / GPT-4o-mini model hosting
- **Pydantic v2** — Structured agent output
- **Rich** — Terminal UI

See [documentation.md](documentation.md) for the full guide.
