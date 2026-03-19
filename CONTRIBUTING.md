# Contributing to APEX

Thank you for your interest in contributing to APEX! This guide will help you get started.

## How Can You Contribute?

- **Report bugs** — Found something broken? Open an issue
- **Suggest features** — Have an idea? Open a feature request
- **Fix bugs** — Browse open issues and submit a fix
- **Add features** — Pick up a feature request and implement it
- **Improve docs** — Fix typos, add examples, clarify explanations
- **Write tests** — Help improve test coverage

## Getting Started

### 1. Fork the Repository

Click the "Fork" button on GitHub. This creates your own copy of the repo.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR-USERNAME/APEX.git
cd APEX
```

### 3. Set Up the Development Environment

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# or: venv\Scripts\activate     # Windows

# Install with dev dependencies
pip install -e ".[dev]"

# Copy the env template
cp .env.example .env
# Fill in your Azure AI Foundry credentials
```

### 4. Create a Branch

Always create a new branch for your work. Never commit directly to `main`.

```bash
# Create a branch with a descriptive name
git checkout -b feature/add-testing-agent
# or
git checkout -b fix/requirements-parsing-error
```

**Branch naming convention:**
- `feature/description` — for new features
- `fix/description` — for bug fixes
- `docs/description` — for documentation changes
- `refactor/description` — for code refactoring

### 5. Make Your Changes

- Write clean, readable code
- Add docstrings to new functions and classes
- Follow the existing code style (see Code Style below)
- Add tests for new functionality

### 6. Run Tests

```bash
pytest tests/
```

Make sure all tests pass before submitting.

### 7. Commit Your Changes

Write clear, descriptive commit messages:

```bash
# Good commit messages
git commit -m "Add testing agent with unit test generation"
git commit -m "Fix JSON parsing error in requirements agent"
git commit -m "Update documentation with setup troubleshooting"

# Bad commit messages
git commit -m "fix stuff"
git commit -m "updates"
```

### 8. Push and Open a Pull Request

```bash
git push origin feature/add-testing-agent
```

Then go to GitHub and click "Compare & pull request". Fill in the PR template.

## Code Style

- **Python 3.10+** — use modern Python features (type hints, `match` statements, `|` unions)
- **Pydantic v2** — all data models use Pydantic `BaseModel`
- **Docstrings** — every module, class, and public function needs a docstring
- **No magic strings** — prompts go in `prompts.py`, not inline in agent code
- **Keep agents independent** — agents should not import from other agents

## Project Architecture

If you're adding a new agent, follow this pattern:

```
src/agents/your_agent/
├── __init__.py          # Export the agent class
├── agent.py             # Agent logic (wraps AutoGen AssistantAgent)
└── prompts.py           # System prompt + task prompts
```

Then:
1. Add output models to `src/models/project.py`
2. Add a document model to `src/models/artifacts.py` (with `to_markdown()`)
3. Add a field to `ProjectContext` in `src/orchestrator/context.py`
4. Add the phase to `src/orchestrator/orchestrator.py`

## Pull Request Guidelines

- Keep PRs focused — one feature or fix per PR
- Update documentation if your change affects how users interact with the tool
- Add tests for new functionality
- Make sure all existing tests still pass
- Describe WHAT you changed and WHY in the PR description

## Reporting Bugs

When opening a bug report, include:
1. What you expected to happen
2. What actually happened
3. Steps to reproduce
4. Your Python version and OS
5. Any error messages or logs

## Questions?

Open a discussion on GitHub if you have questions about contributing. We're happy to help newcomers!
