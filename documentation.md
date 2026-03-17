# MAF SDLC Platform — Documentation

## What Is This?

MAF is an **AI-powered SDLC (Software Development Lifecycle) orchestration platform** that uses multiple specialized AI agents to help you plan software projects from idea to sprint-ready backlog.

Instead of one generic AI chatbot, MAF uses **3 specialized agents** — each an expert in their domain — coordinated by an orchestrator that maintains context across the entire flow.

Each agent is **truly agentic**: they have tools to search the web, read GitHub repos, load best-practice checklists, and validate their own output before presenting it to you.

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
┌─────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR                            │
│          Coordinates agents, manages context                 │
│          Handles human-in-the-loop gates                     │
└────────┬──────────────┬──────────────┬──────────────────────┘
         │              │              │
         ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Requirements │ │ Architecture │ │   Planning   │
│    Agent     │ │    Agent     │ │    Agent     │
│              │ │              │ │              │
│ Tools:       │ │ Tools:       │ │ Tools:       │
│ • Web Search │ │ • Web Search │ │ • Risk       │
│ • NFR Check  │ │ • API Check  │ │   Checklist  │
│ • Validator  │ │ • Validator  │ │ • Validator  │
│ • GitHub MCP │ │ • GitHub MCP │ │              │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       ▼                ▼                ▼
┌──────────────────────────────────────────────────────────────┐
│                  Azure AI Foundry                             │
│           GPT-4o / GPT-4o-mini deployments                   │
└──────────────────────────────────────────────────────────────┘
```

### What Makes This Agentic (Not Just LLM Calls)

Simple LLM pipelines just send prompts and get text back. Our agents are different:

| Capability | Simple Pipeline | MAF Agents |
|---|---|---|
| **Research** | Uses training data only | Searches the web for current tech benchmarks |
| **Codebase awareness** | User describes the project | Reads actual code from GitHub via MCP |
| **Best practices** | Relies on LLM memory | Loads curated checklists before generating |
| **Self-correction** | Presents raw output | Validates output, fixes issues, then presents |
| **Decision-making** | Follows fixed prompts | Decides which tools to use based on context |

### The 3-Phase Flow

**Phase 1: Requirements Gathering**
- The Requirements Agent (acting as a Senior Business Analyst) takes your project idea
- It **searches the web** for similar products to inform its questions
- It asks clarifying questions to understand scope
- It **loads the NFR checklist** to ensure complete coverage
- It **validates its output** for consistency before showing you
- It produces a structured requirements document with personas, user stories, and requirements
- **You review and approve** before moving to the next phase

**Phase 2: Architecture Design**
- The Architecture Agent (acting as a Senior Software Architect) reads the approved requirements
- It **searches the web** for technology benchmarks and comparisons
- It **loads the API design checklist** to follow best practices
- If a GitHub repo was provided, it **reads the actual codebase** via MCP
- It **validates coverage** against requirements before showing you
- It produces a complete architecture document with tech stack, APIs, and database schema
- **You review and approve** before moving to the next phase

**Phase 3: Project Planning**
- The Planning Agent (acting as a Senior Engineering Manager) reads requirements + architecture
- It **loads the risk categories checklist** for comprehensive risk assessment
- It **validates plan consistency** (point totals, dependencies, sprint loads)
- It produces a project plan with epics, stories, tasks, estimates, and sprints
- **You review and approve** to finalize

### Key Design Decisions

1. **Sequential flow with human gates** — Each phase must be approved before the next starts. AI proposes, you decide.

2. **Shared ProjectContext** — A context object flows between agents, carrying all accumulated knowledge. This means the Architecture Agent has full access to requirements, and the Planning Agent knows both requirements AND architecture.

3. **Structured output** — Agents produce typed, validated data (Pydantic models), not raw text. This makes agent-to-agent handoffs reliable.

4. **Each agent is independent** — Agents don't talk to each other directly. The Orchestrator coordinates everything. This makes it easy to add, replace, or test agents individually.

5. **Tools make it agentic** — Agents use web search, checklists, validators, and GitHub MCP to gather information and verify their work, not just generate text from prompts.

---

## Agent Tools

### Custom Tools (built into the project)

| Tool | Used By | Purpose |
|---|---|---|
| `search_web` | Requirements, Architecture | Search the web for tech benchmarks, competitor analysis, best practices |
| `load_nfr_checklist` | Requirements | Load NFR categories (security, performance, scalability, etc.) |
| `load_api_design_checklist` | Architecture | Load API design patterns (REST conventions, common endpoints) |
| `load_risk_checklist` | Planning | Load risk categories (technical, resource, schedule, business) |
| `validate_requirements` | Requirements | Check for unique IDs, priority balance, acceptance criteria |
| `validate_architecture` | Architecture | Check tech stack completeness, API coverage, component count |
| `validate_plan` | Planning | Check point totals, sprint loads, dependency consistency |

### MCP Tools (via GitHub MCP Server)

When `GITHUB_TOKEN` is configured, agents get access to GitHub tools:

| Tool | Purpose |
|---|---|
| `get_file_contents` | Read files from any GitHub repo |
| `search_code` | Search code across repositories |
| `search_repositories` | Find similar projects for research |
| `list_commits` | View recent changes to understand project activity |

These tools are provided by the [official GitHub MCP server](https://github.com/modelcontextprotocol/servers/tree/main/src/github). The agents decide when to use them based on context.

### How MCP Works

MCP (Model Context Protocol) is a standard that lets AI agents connect to external services through a unified protocol. Instead of writing custom API integration code, you connect to an MCP server that exposes tools.

```
Without MCP:  Agent → Custom GitHub API code → GitHub
With MCP:     Agent → MCP Protocol → GitHub MCP Server → GitHub
```

Benefits:
- No custom integration code to maintain
- Any MCP server works with any MCP-compatible agent
- The GitHub MCP server handles auth, pagination, error handling
- Future: plug in Jira MCP, Slack MCP, Linear MCP the same way

---

## Project Structure

```
MAF/
├── main.py                         # Entry point — run this
├── pyproject.toml                  # Dependencies and project config
├── .env.example                    # Template for credentials
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
│   │   │   ├── agent.py            # Requirements Agent + tools
│   │   │   └── prompts.py          # System & task prompts
│   │   ├── architecture/
│   │   │   ├── agent.py            # Architecture Agent + tools
│   │   │   └── prompts.py          # System & task prompts
│   │   └── planning/
│   │       ├── agent.py            # Planning Agent + tools
│   │       └── prompts.py          # System & task prompts
│   │
│   ├── models/                     # Shared data structures
│   │   ├── project.py              # Core models (UserStory, Task, etc.)
│   │   └── artifacts.py            # Document models with to_markdown()
│   │
│   ├── tools/                      # Agent tools
│   │   ├── file_tool.py            # Save artifacts to disk
│   │   ├── github_mcp.py           # GitHub MCP server connection
│   │   ├── web_search_tool.py      # Bing web search integration
│   │   ├── validator_tool.py       # Output validation (IDs, points, coverage)
│   │   └── template_tool.py        # Best-practice checklists (NFR, API, risks)
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
3. **`src/tools/`** — See what tools agents have (web search, validators, checklists, GitHub MCP)
4. **`src/orchestrator/context.py`** — Understand the shared state between agents
5. **`src/agents/requirements/prompts.py`** — See how we instruct agents to use their tools
6. **`src/agents/requirements/agent.py`** — See how an agent wraps AutoGen with tools
7. **`src/orchestrator/orchestrator.py`** — See how everything is coordinated
8. **`main.py`** — The entry point that ties it all together

---

## Technology Stack

| Technology | Purpose |
|---|---|
| **AutoGen 0.4+** | Multi-agent orchestration framework (by Microsoft) |
| **Azure AI Foundry** | Hosts the LLM deployments (GPT-4o, GPT-4o-mini) |
| **MCP (Model Context Protocol)** | Standard protocol for agent-to-service communication |
| **GitHub MCP Server** | Provides GitHub tools (read files, search code, etc.) |
| **Pydantic v2** | Data validation and structured output |
| **Rich** | Beautiful terminal output |
| **httpx** | Async HTTP client for web search |
| **Python 3.10+** | Language runtime |

### Why AutoGen?

AutoGen (part of Microsoft's Agent Framework) provides:
- Agent abstractions (`AssistantAgent`) with built-in message handling and tool use
- Model client connectors for Azure OpenAI
- MCP client support for connecting to any MCP server
- Support for structured output, tool use, and handoffs
- Active development with strong community support

We use AutoGen's agent primitives but orchestrate them with our own sequential flow (not group chat), because our 3-phase pipeline with human gates is simpler and more predictable than a dynamic group chat.

---

## Setup Guide

### Prerequisites

- Python 3.10 or higher
- An Azure subscription with Azure AI Foundry access
- (Optional) Node.js 18+ for GitHub MCP server
- (Optional) GitHub Personal Access Token for repo reading
- (Optional) Azure Bing Search resource for web search

### Step 1: Azure AI Foundry Setup (Required)

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
git clone https://github.com/kunalrajput7/maf_sdlc_framework.git
cd maf_sdlc_framework

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

Open `.env` and fill in the required values:

```bash
# REQUIRED — Azure AI Foundry
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_API_VERSION=2024-10-21
ORCHESTRATOR_DEPLOYMENT=gpt-4o
REQUIREMENTS_DEPLOYMENT=gpt-4o
ARCHITECTURE_DEPLOYMENT=gpt-4o
PLANNING_DEPLOYMENT=gpt-4o-mini

# OPTIONAL — GitHub MCP (enables repo reading)
GITHUB_TOKEN=ghp_your_github_token_here

# OPTIONAL — Bing Search (enables web search tool)
BING_SEARCH_API_KEY=your-bing-key-here
```

### Step 4: (Optional) Install GitHub MCP Server

If you want agents to read GitHub repos:

```bash
npm install -g @modelcontextprotocol/server-github
```

The orchestrator will automatically connect to it when `GITHUB_TOKEN` is set.

### Step 5: Run

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
4. Create any new tools in `src/tools/` if the agent needs them
5. Add a field to `ProjectContext` in `src/orchestrator/context.py`
6. Add the phase to `orchestrator.py`

The modular structure means adding a new agent doesn't change existing code — you just plug it in.

### Adding a New MCP Server

To connect agents to a new service (e.g., Jira, Slack, Linear):

1. Find or install the MCP server (check [MCP servers directory](https://github.com/modelcontextprotocol/servers))
2. Create a connection file in `src/tools/` (similar to `github_mcp.py`)
3. Pass the tools to the relevant agent in the orchestrator

### Adding a New Custom Tool

1. Create a function in `src/tools/` that does the work
2. Wrap it with `FunctionTool` from `autogen_core.tools`
3. Add it to the relevant agent's tool list in `agent.py`

### Changing the LLM

To use a different model (e.g., GPT-4o-mini for all agents), just change the deployment names in `.env`. No code changes needed.

---

## FAQ

**Q: Do I need all the optional tools (GitHub, Bing)?**
No. The system works with just the Azure AI Foundry credentials. Without GitHub MCP, agents won't read repos but still work. Without Bing, agents use built-in knowledge instead of web search. The validators and checklists are always available (no API keys needed).

**Q: Do I need RAG (Retrieval Augmented Generation)?**
No. For Phase 1 MVP, the agents reason directly from the project description, their tool results, and each other's outputs. RAG would be useful later for searching past project data.

**Q: Can I use OpenAI directly instead of Azure?**
Not in this version. The codebase uses `AzureOpenAIChatCompletionClient`. Swapping to direct OpenAI would require changing `src/utils/llm.py` to use `OpenAIChatCompletionClient` instead.

**Q: What if an agent produces bad output?**
Agents now validate their own output before presenting it. But if something still looks wrong, type your feedback at the approval step and the agent will refine. You can iterate as many times as needed.

**Q: How much does it cost to run?**
A full 3-phase run with tool use typically uses ~15,000-30,000 tokens. With Azure GPT-4o pricing (~$5/1M input, $15/1M output tokens), that's roughly $0.10-0.25 per run.

**Q: What is MCP?**
MCP (Model Context Protocol) is an open standard for connecting AI agents to external services. Instead of writing custom API code, agents connect to MCP servers that expose tools through a standard protocol. Think of it as "USB for AI tools" — one standard plug that works with any service.
