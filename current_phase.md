# MAF SDLC Platform — Current Phase (MVP)

This document explains exactly how the system works right now — every step, every tool call, every decision.

---

## What This MVP Does

You describe a software project idea. 3 AI agents produce:

1. **Requirements Document** — personas, user stories, functional & non-functional requirements
2. **Architecture Document** — tech stack, components, APIs, database schema
3. **Project Plan** — epics, stories, tasks, estimates, sprint allocation

You review and approve each phase. Agents use tools to research, validate, and self-correct.

---

## The Complete Flow

### Step 0: Startup

```
$ python main.py

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

Connecting to GitHub MCP server...
GitHub MCP connected — 22 tools available

What type of project?
  [1] New project from scratch
  [2] Enhance an existing project (GitHub repo)

> 1

Describe your project idea:

> I want to build a campus food delivery app where students can order
  from campus restaurants and other students deliver
```

What happens behind the scenes:

```
Orchestrator.__init__()
│
├── Loads .env file → validates all required credentials exist
│   ├── AZURE_OPENAI_ENDPOINT     ← required (crash-safe error if missing)
│   ├── AZURE_OPENAI_API_KEY      ← required
│   ├── Deployment names          ← have defaults (gpt-4o, gpt-4o-mini)
│   ├── GITHUB_TOKEN              ← optional (agents work without it)
│   └── BING_SEARCH_API_KEY       ← optional (agents use built-in knowledge)
│
├── Creates 3 model clients (one per agent, pointing to Azure AI Foundry)
│   ├── req_client  → "gpt-4o" deployment
│   ├── arch_client → "gpt-4o" deployment
│   └── plan_client → "gpt-4o-mini" deployment
│
├── Connects to GitHub MCP server (if token configured)
│   ├── Spawns: npx @modelcontextprotocol/server-github
│   ├── Gets 22 tools (get_file_contents, search_code, etc.)
│   └── If no token: skips gracefully, agents work without it
│
└── Creates agents with their tools:
    ├── RequirementsAgent  → [search_web, nfr_checklist, validator, github_mcp_tools]
    ├── ArchitectureAgent  → [search_web, api_checklist, validator, github_mcp_tools]
    └── PlanningAgent      → [risk_checklist, validator]
```

---

### Phase 1: Requirements Agent

**Role:** Senior Business Analyst
**Tools:** search_web, load_nfr_checklist, validate_requirements, [GitHub MCP tools]

#### Step 1A: Clarifying Questions

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PHASE 1: REQUIREMENTS GATHERING
  Agent: Requirements Agent (Senior Business Analyst)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Generating clarifying questions...
(Agent may search the web for similar products first)
```

What happens inside:

```
RequirementsAgent.generate_questions(project_description)
│
├── Sends to GPT-4o on Azure:
│   ├── System: "You are a Senior Business Analyst... You have tools..."
│   └── Task: "Generate 5-8 clarifying questions. Use search_web first."
│
├── GPT-4o DECIDES to call a tool (this is the agentic part):
│   └── TOOL CALL: search_web("campus food delivery apps features 2026")
│       │
│       ├── IF Bing key configured → calls Bing API → real results
│       └── IF no key → returns "Web search unavailable, using built-in knowledge"
│
├── GPT-4o receives search results, generates INFORMED questions:
│   └── Returns text:
│       "1. Should students pay with campus meal plans or cards?
│        2. Do you need real-time GPS tracking?
│        3. What delivery radius from campus?
│        4. Should restaurants manage their own menus?
│        5. Do you need ratings and reviews?
│        6. Mobile apps (iOS/Android) or web only?
│        7. What payment provider (Stripe, PayPal)?"
│
└── Orchestrator displays questions in a panel, waits for user input
```

Terminal shows:

```
┌───────────────────── Clarifying Questions ─────────────────────┐
│ 1. Should students pay with campus meal plans or cards?        │
│ 2. Do you need real-time GPS tracking?                         │
│ 3. What delivery radius from campus?                           │
│ ...                                                            │
└────────────────────────────────────────────────────────────────┘

Answer the questions above (type your answers):

> Meal plans + Stripe. Yes GPS. 2km radius. Restaurant dashboard
  for menus. Yes ratings. Mobile iOS + Android. ~5000 students.
```

#### Step 1B: Generating Requirements Document

```
Generating requirements document...
(Agent is researching, loading checklists, and validating...)
```

What happens inside — the agent makes MULTIPLE tool calls in sequence:

```
RequirementsAgent.generate_requirements(description, user_answers)
│
├── Sends to GPT-4o:
│   ├── System: "You are a Senior Business Analyst... USE TOOLS proactively"
│   └── Task: "Before generating, you MUST:
│              1. Use search_web to research similar products
│              2. Use load_nfr_checklist
│              3. Generate JSON
│              4. Use validate_requirements"
│
│   HOW DOES GPT-4o DECIDE WHICH TOOLS TO USE?
│   ─────────────────────────────────────────────
│   The prompt explicitly says "you MUST use these tools."
│   GPT-4o reads that instruction and returns tool calls.
│   AutoGen executes them and sends results back.
│   The LLM keeps calling tools until it has enough info,
│   then returns the final text response.
│
│   AutoGen's internal loop:
│   ┌───────────────────────────────────┐
│   │  LLM receives message             │
│   │  ├── Returns tool_call?           │
│   │  │   YES → AutoGen runs the tool  │──→ result sent back to LLM
│   │  │         LLM sees the result    │←─┘
│   │  │         Loop continues         │
│   │  │   NO  → Returns final text     │──→ Done
│   │  └───────────────────────────────┘
│
├── TOOL CALL 1: search_web
│   query: "food delivery app requirements best practices 2026"
│   → Returns real search results (or "unavailable" message)
│
├── TOOL CALL 2: load_nfr_checklist
│   → Returns the full checklist:
│     "### Performance - Response time targets...
│      ### Security - Authentication method...
│      ### Scalability - Concurrent users..."
│   (This is a curated template stored in template_tool.py)
│
├── GPT-4o generates complete JSON with all this context:
│   {
│     "project_name": "Campus Eats",
│     "personas": [...],
│     "user_stories": [12 stories with acceptance criteria],
│     "functional_requirements": [10 FRs],
│     "non_functional_requirements": [6 NFRs informed by checklist]
│   }
│
├── TOOL CALL 3: validate_requirements
│   Sends the JSON it just generated to the validator.
│   │
│   │  validator_tool.py checks:
│   │  ├── All IDs unique?                    ✓
│   │  ├── At least 5 user stories?           ✓ (found 12)
│   │  ├── At least 5 functional reqs?        ✓ (found 10)
│   │  ├── At least 3 NFRs?                   ✓ (found 6)
│   │  ├── All priorities valid?              ✓
│   │  ├── >60% marked "high"?               ✗ 8/12 are "high"
│   │  └── All stories have acceptance criteria? ✓
│   │
│   └── Returns: "ISSUES FOUND:
│                  - 8/12 items are 'high' priority. Be more realistic."
│
├── GPT-4o reads validation result and SELF-CORRECTS:
│   "Too many items are high priority. Let me rebalance."
│   → Regenerates JSON with 4 high, 5 medium, 3 low
│
└── Our code parses the final JSON → RequirementsDocument (Pydantic model)
```

Terminal shows the rendered markdown:

```
# Requirements Document: Campus Eats

## Project Summary
A mobile food delivery platform for college campuses enabling students
to order from campus restaurants with peer-to-peer delivery...

## User Personas

### Hungry Student (Student Customer)
Goals: Order food quickly, track delivery, use meal plan
Pain Points: Long cafeteria lines, limited late-night options

### Delivery Runner (Student Courier)
Goals: Earn extra money, flexible schedule
Pain Points: Inconsistent income, no existing campus gig platform
...

## User Stories

### US-001: As a student, I want to browse nearby restaurant menus
So that: I can find food I want to eat
Priority: high
Acceptance Criteria:
  - Can see restaurant list sorted by distance
  - Can filter by cuisine type
  - Can see estimated delivery time
  - Menu shows prices and item descriptions
...

(12 user stories, 10 functional requirements, 6 NFRs displayed)
```

#### Step 1C: Human Gate

```
Review the requirements output above.
  Type 'yes' to approve and continue
  Type 'no' to stop
  Or type your feedback to refine

> Add group ordering — students often order together for the same class
```

If user types feedback:

```
Refining requirements based on your feedback...

RequirementsAgent.refine(current_doc, feedback)
│
├── Sends current JSON + "Add group ordering" to GPT-4o
├── GPT-4o adds US-013: group ordering story + updates FRs
├── TOOL CALL: validate_requirements → "VALID"
└── Returns updated doc → displayed again → asks for approval again

> yes
Requirements phase complete. Artifact saved.
```

RequirementsDocument is now:
- Stored in `ProjectContext.requirements` (in memory)
- Saved to `outputs/requirements.md` (on disk)

---

### Phase 2: Architecture Agent

**Role:** Senior Software Architect
**Tools:** search_web, load_api_design_checklist, validate_architecture, [GitHub MCP tools]

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PHASE 2: ARCHITECTURE DESIGN
  Agent: Architecture Agent (Senior Software Architect)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Designing system architecture...
(Agent is researching tech stacks, loading API checklist, and validating...)
```

What happens inside:

```
ArchitectureAgent.generate_architecture(requirements)
│
├── Receives: the FULL RequirementsDocument from Phase 1
│   (All personas, stories, FRs, NFRs — the agent reads everything)
│
├── TOOL CALL 1: search_web
│   query: "best mobile backend framework 2026 real-time food delivery"
│   → Returns: tech comparisons, benchmarks
│
├── TOOL CALL 2: load_api_design_checklist
│   → Returns curated checklist:
│     "### Core Patterns
│      - RESTful naming: /users, /orders
│      - Pagination for list endpoints
│      ### Commonly Missed
│      - Health check: GET /api/v1/health
│      - File upload endpoints
│      - Webhook endpoints"
│
├── [IF EXISTING PROJECT with GitHub MCP]:
│   ├── TOOL CALL: get_file_contents("user/repo", "package.json")
│   │   → Returns actual dependencies
│   ├── TOOL CALL: search_code("user/repo", "router.post")
│   │   → Returns existing API endpoints
│   └── Agent designs architecture that FITS the existing code
│
├── GPT-4o generates architecture JSON:
│   ├── Tech Stack: React Native, FastAPI, PostgreSQL, AWS
│   │   └── Reasoning references actual search results
│   ├── Components: API Gateway, Order Service, Delivery Tracker...
│   ├── 15 API endpoints (informed by checklist — includes health check)
│   ├── 7 database tables with relationships
│   └── Architecture notes on WebSocket for real-time tracking
│
├── TOOL CALL 3: validate_architecture(architecture, requirements)
│   │
│   │  Checks:
│   │  ├── Tech stack complete?           ✓
│   │  ├── At least 3 components?         ✓ (6)
│   │  ├── At least 5 endpoints?          ✓ (15)
│   │  ├── At least 3 tables?             ✓ (7)
│   │  ├── Valid HTTP methods?            ✓
│   │  └── API coverage vs requirements?  ✓
│   │
│   └── Returns: "VALID"
│
└── Returns ArchitectureDocument → displayed → human gate → saved
```

---

### Phase 3: Planning Agent

**Role:** Senior Engineering Manager
**Tools:** load_risk_checklist, validate_plan

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PHASE 3: PROJECT PLANNING
  Agent: Planning Agent (Senior Engineering Manager)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Creating project plan...
(Agent is loading risk checklist and validating plan consistency...)
```

What happens inside:

```
PlanningAgent.generate_plan(requirements, architecture)
│
├── Receives: BOTH RequirementsDocument AND ArchitectureDocument
│   (Knows WHAT to build and HOW it's designed)
│
├── TOOL CALL 1: load_risk_checklist
│   → Returns risk categories:
│     "### Technical Risks - New technology, complex integrations...
│      ### Resource Risks - Skill gaps, key person dependency...
│      ### Schedule Risks - Underestimated complexity...
│      ### Business Risks - Changing requirements, competition..."
│
├── GPT-4o generates project plan:
│   ├── Epic E-001: Project Setup (repo, CI/CD, dev environment)
│   ├── Epic E-002: Core Ordering (browse, cart, checkout)
│   ├── Epic E-003: Delivery System (matching, tracking, notifications)
│   ├── Epic E-004: Payment Integration (Stripe, meal plans)
│   ├── 15 Stories across epics, each with 2-4 tasks
│   ├── Story points on each task (Fibonacci: 1,2,3,5,8,13)
│   ├── 6 Sprints (2 weeks each = 12 weeks total)
│   ├── 5 Risks (informed by the checklist)
│   └── 4 Assumptions
│
├── TOOL CALL 2: validate_plan
│   │
│   │  Checks:
│   │  ├── All IDs unique?                     ✓
│   │  ├── Story points sum correctly?
│   │  │   ├── S-001: declared 8, tasks = 3+5 = 8     ✓
│   │  │   ├── S-002: declared 13, tasks = 5+3+3 = 11 ✗
│   │  │   └── ...
│   │  ├── Sprint loads reasonable (15-35)?
│   │  │   ├── Sprint 1: 22 pts ✓
│   │  │   ├── Sprint 3: 42 pts ✗ TOO HEAVY
│   │  │   └── ...
│   │  ├── Sprint stories all exist?           ✓
│   │  └── Task dependencies valid?            ✓
│   │
│   └── Returns: "ISSUES FOUND:
│                  - S-002 declared 13 but tasks sum to 11
│                  - Sprint 3 has 42 points — too heavy"
│
├── GPT-4o SELF-CORRECTS:
│   ├── Fixes S-002: declared total → 11
│   ├── Moves 2 stories from Sprint 3 to Sprint 4
│   └── Recalculates totals
│
└── Returns corrected ProjectPlan → displayed → human gate → saved
```

---

### Completion

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ALL PHASES COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your project artifacts have been saved to the /outputs/ folder:

  - requirements.md    → Full requirements document
  - architecture.md    → System architecture design
  - project_plan.md    → Sprint plan with estimates

Review these files and use them to kickstart your development!
```

---

## New Project vs Existing Project

### New Project Flow

```
User selects: [1] New project from scratch

User types: "I want to build a campus food delivery app"

→ Requirements Agent: generates everything from scratch
→ Architecture Agent: recommends tech stack from scratch
→ Planning Agent: creates full project plan
```

### Existing Project Flow

```
User selects: [2] Enhance an existing project

User provides: GitHub repo URL + what they want to change

→ Requirements Agent:
  ├── Uses GitHub MCP to READ the actual codebase
  │   ├── get_file_contents("package.json") → knows React 18, Express
  │   ├── get_file_contents("prisma/schema.prisma") → knows the DB schema
  │   └── search_code("router.post") → knows existing API endpoints
  ├── Generates requirements for the NEW feature only
  └── Requirements are scoped to fit the existing system

→ Architecture Agent:
  ├── Uses GitHub MCP to understand current architecture
  ├── Designs the new feature to FIT existing patterns
  └── Won't recommend React if the project uses Vue

→ Planning Agent:
  ├── Knows it's enhancement, not greenfield
  ├── Estimates based on existing codebase complexity
  └── Includes migration/integration tasks
```

---

## Where Every Tool Lives

```
src/tools/
│
├── web_search_tool.py          1 tool:  search_web
│   └── Calls Bing Search API for current web results
│   └── Graceful fallback if no API key configured
│
├── template_tool.py            3 tools: load_nfr_checklist
│   │                                    load_api_design_checklist
│   │                                    load_risk_checklist
│   └── Returns curated best-practice checklists (stored as strings)
│   └── No API key needed — always available
│
├── validator_tool.py           3 tools: validate_requirements
│   │                                    validate_architecture
│   │                                    validate_plan
│   └── Checks output for consistency (IDs, points, coverage)
│   └── No API key needed — always available
│
├── github_mcp.py               20+ tools from GitHub MCP Server:
│   │                                    get_file_contents
│   │                                    search_code
│   │                                    search_repositories
│   │                                    list_commits
│   │                                    create_issue
│   │                                    ... etc
│   └── Connects to external MCP server process
│   └── Requires GITHUB_TOKEN + Node.js installed
│
└── file_tool.py                1 tool:  save_artifact
    └── Saves markdown files to outputs/ folder
    └── Used by orchestrator, not by agents directly
```

---

## User Interaction Points

The user interacts at exactly these moments:

```
1. PROJECT TYPE    → Choose [1] New or [2] Existing
2. DESCRIBE        → Type project idea (+ GitHub URL if existing)
3. ANSWER          → Answer 5-8 clarifying questions
4. APPROVE PHASE 1 → "yes" / "no" / feedback
5. APPROVE PHASE 2 → "yes" / "no" / feedback
6. APPROVE PHASE 3 → "yes" / "no" / feedback
```

Everything else is autonomous — agents decide which tools to use, how to use them, and how to fix their own mistakes.
