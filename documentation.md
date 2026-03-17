# MAF SDLC Platform — Documentation

## What Is This?

MAF is an **AI-powered SDLC (Software Development Lifecycle) orchestration platform** that uses multiple specialized AI agents to help you plan software projects from idea to sprint-ready backlog.

Instead of one generic AI chatbot, MAF uses **3 specialized agents** — each an expert in their domain — coordinated by an orchestrator that maintains context across the entire flow.

---

## The Problem We Solve

Today's AI coding tools (Copilot, Cursor, Devin) are great at writing code, but nobody covers the **planning phases** that come before writing code:

- **Requirements gathering** — What exactly should we build?
- **Architecture design** — How should we structure the system?
- **Project planning** — What tasks, in what order, with what effort?

Teams spend 40%+ of their time on these activities, yet no AI tool addresses them in a structured, connected way. MAF fills this gap.

---

## How It Works

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR                         │
│         Coordinates agents, manages context              │
│         Handles human-in-the-loop gates                  │
└────────┬──────────────┬──────────────┬──────────────────┘
         │              │              │
         ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Requirements │ │ Architecture │ │   Planning   │
│    Agent     │ │    Agent     │ │    Agent     │
│              │ │              │ │              │
│ Business     │ │ Software     │ │ Engineering  │
│ Analyst      │ │ Architect    │ │ Manager      │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       ▼                ▼                ▼
┌──────────────────────────────────────────────────────────┐
│                  Azure AI Foundry                         │
│           GPT-4o / GPT-4o-mini deployments               │
└──────────────────────────────────────────────────────────┘
```

### The 3-Phase Flow

**Phase 1: Requirements Gathering**
- The Requirements Agent (acting as a Senior Business Analyst) takes your project idea
- It asks clarifying questions to understand scope
- It produces a structured requirements document with:
  - User personas
  - User stories with acceptance criteria
  - Functional requirements
  - Non-functional requirements
- **You review and approve** before moving to the next phase

**Phase 2: Architecture Design**
- The Architecture Agent (acting as a Senior Software Architect) reads the approved requirements
- It produces a complete architecture document with:
  - Tech stack recommendation with reasoning
  - System component breakdown
  - API endpoint definitions
  - Database schema design
  - Architecture decisions and trade-offs
- **You review and approve** before moving to the next phase

**Phase 3: Project Planning**
- The Planning Agent (acting as a Senior Engineering Manager) reads requirements + architecture
- It produces a project plan with:
  - Epics broken into stories
  - Stories broken into tasks
  - Story point estimates (Fibonacci scale)
  - Sprint allocation (2-week sprints)
  - Risk assessment
- **You review and approve** to finalize

### Key Design Decisions

1. **Sequential flow with human gates** — Each phase must be approved before the next starts. AI proposes, you decide.

2. **Shared ProjectContext** — A context object flows between agents, carrying all accumulated knowledge. This means the Architecture Agent has full access to requirements, and the Planning Agent knows both requirements AND architecture.

3. **Structured output** — Agents produce typed, validated data (Pydantic models), not raw text. This makes agent-to-agent handoffs reliable.

4. **Each agent is independent** — Agents don't talk to each other directly. The Orchestrator coordinates everything. This makes it easy to add, replace, or test agents individually.

---

## Project Structure

```
MAF/
├── main.py                         # Entry point — run this
├── pyproject.toml                  # Dependencies and project config
├── .env.example                    # Template for Azure credentials
├── documentation.md                # This file
│
├── src/
│   ├── orchestrator/               # The brain — coordinates everything
│   │   ├── orchestrator.py         # Main orchestration logic
│   │   ├── context.py              # Shared state between agents
│   │   └── prompts.py              # CLI display messages
│   │
│   ├── agents/                     # One folder per SDLC agent
│   │   ├── requirements/
│   │   │   ├── agent.py            # Requirements Agent logic
│   │   │   └── prompts.py          # System & task prompts
│   │   ├── architecture/
│   │   │   ├── agent.py            # Architecture Agent logic
│   │   │   └── prompts.py          # System & task prompts
│   │   └── planning/
│   │       ├── agent.py            # Planning Agent logic
│   │       └── prompts.py          # System & task prompts
│   │
│   ├── models/                     # Shared data structures
│   │   ├── project.py              # Core models (UserStory, Task, etc.)
│   │   └── artifacts.py            # Document models with to_markdown()
│   │
│   ├── tools/                      # Utilities agents can use
│   │   └── file_tool.py            # Save artifacts to disk
│   │
│   └── utils/                      # Configuration and LLM setup
│       ├── config.py               # Loads settings from .env
│       └── llm.py                  # Creates Azure OpenAI model clients
│
├── outputs/                        # Generated artifacts land here
├── examples/                       # Example usage scripts
│   ├── new_project.py              # Plan a new project from scratch
│   └── existing_project.py         # Plan changes to an existing project
│
└── tests/                          # Unit tests
    └── test_models.py              # Tests for models and serialization
```

### How to Read the Code

If you're new to this codebase, read in this order:

1. **`src/models/project.py`** — Understand the data structures (UserStory, Task, Epic, etc.)
2. **`src/models/artifacts.py`** — See how documents are structured and converted to markdown
3. **`src/orchestrator/context.py`** — Understand the shared state between agents
4. **`src/agents/requirements/prompts.py`** — See how we instruct the AI (this is where the magic is)
5. **`src/agents/requirements/agent.py`** — See how an agent wraps AutoGen
6. **`src/orchestrator/orchestrator.py`** — See how everything is coordinated
7. **`main.py`** — The entry point that ties it all together

---

## Technology Stack

| Technology | Purpose |
|---|---|
| **AutoGen 0.4+** | Multi-agent orchestration framework (by Microsoft) |
| **Azure AI Foundry** | Hosts the LLM deployments (GPT-4o, GPT-4o-mini) |
| **Pydantic v2** | Data validation and structured output |
| **Rich** | Beautiful terminal output |
| **Python 3.10+** | Language runtime |

### Why AutoGen?

AutoGen (part of Microsoft's Agent Framework) provides:
- Agent abstractions (`AssistantAgent`) with built-in message handling
- Model client connectors for Azure OpenAI
- Support for structured output, tool use, and handoffs
- Active development with strong community support

We use AutoGen's agent primitives but orchestrate them with our own sequential flow (not group chat), because our 3-phase pipeline with human gates is simpler and more predictable than a dynamic group chat.

---

## Setup Guide

### Prerequisites

- Python 3.10 or higher
- An Azure subscription with Azure AI Foundry access

### Step 1: Azure AI Foundry Setup

1. Go to [Azure AI Foundry](https://ai.azure.com)
2. Create a **Hub** (or use an existing one)
3. Create a **Project** inside the hub
4. Deploy the following models:
   - **GPT-4o** — for Requirements, Architecture, and Orchestrator agents
   - **GPT-4o-mini** — for the Planning agent (cheaper, still capable)
5. Note down:
   - **Endpoint URL** (looks like `https://your-resource.openai.azure.com/`)
   - **API Key** (from the Keys section)
   - **Deployment names** (the names you gave each deployment)

### Step 2: Project Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd MAF

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# or: venv\Scripts\activate     # Windows

# Install dependencies
pip install -e ".[dev]"

# Copy environment template and fill in your credentials
cp .env.example .env
# Edit .env with your Azure values
```

### Step 3: Configure .env

Open `.env` and fill in these 6 values:

```
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_API_VERSION=2024-10-21
ORCHESTRATOR_DEPLOYMENT=gpt-4o
REQUIREMENTS_DEPLOYMENT=gpt-4o
ARCHITECTURE_DEPLOYMENT=gpt-4o
PLANNING_DEPLOYMENT=gpt-4o-mini
```

### Step 4: Run

```bash
# Interactive mode (recommended)
python main.py

# Or run an example
python examples/new_project.py

# Run tests
pytest tests/
```

---

## How to Extend

### Adding a New Agent (e.g., Testing Agent)

1. Create `src/agents/testing/` with `__init__.py`, `agent.py`, `prompts.py`
2. Define output schemas in `src/models/project.py` (e.g., `TestCase`, `TestSuite`)
3. Add a document model in `src/models/artifacts.py` (e.g., `TestPlanDocument`)
4. Add a field to `ProjectContext` in `src/orchestrator/context.py`
5. Add the phase to `orchestrator.py`

The modular structure means adding a new agent doesn't change existing code — you just plug it in.

### Changing the LLM

To use a different model (e.g., GPT-4o-mini for all agents), just change the deployment names in `.env`. No code changes needed.

---

## FAQ

**Q: Do I need RAG (Retrieval Augmented Generation)?**
No. For Phase 1 MVP, the agents reason directly from the project description and each other's outputs. RAG would be useful later for searching past project data.

**Q: Can I use OpenAI directly instead of Azure?**
Not in this version. The codebase uses `AzureOpenAIChatCompletionClient`. Swapping to direct OpenAI would require changing `src/utils/llm.py` to use `OpenAIChatCompletionClient` instead.

**Q: What if an agent produces bad output?**
That's what the human gates are for. Type your feedback at any approval step, and the agent will refine its output. You can iterate as many times as needed.

**Q: How much does it cost to run?**
A full 3-phase run typically uses ~10,000-20,000 tokens total. With Azure GPT-4o pricing (~$5/1M input, $15/1M output tokens), that's roughly $0.05-0.15 per run.
