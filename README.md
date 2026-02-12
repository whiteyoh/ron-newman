# Agentic AI Tool Builder

This project is a starter implementation of an **agentic AI tool that builds agentic AI tools** from human-provided folders.

## What it does

- Scans a target folder and summarizes file structure.
- Generates a tool blueprint with capabilities, architecture, and testing strategy.
- Drafts work as a pull-request style document.
- Streams outputs into a chat-style UI so humans can observe each generation.
- Supports natural evolution by turning feedback into improvement history.

## Why this matches your goals

1. **Agentic creation loop**: scanner + planner + PR draft manager + evolution engine.
2. **Chat-first output**: every generated artifact appears in the Streamlit chat window.
3. **Natural evolution**: user feedback is preserved and converted into actionable next steps.
4. **PR-first delivery**: generated implementation plan is framed directly as PR content.
5. **Tests included**: unit tests validate scanning, orchestration, and evolution behavior.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
streamlit run app.py
```

Then open the shown local URL and:

1. Enter a folder path to analyze.
2. Click **Analyze Folder and Draft PR**.
3. Provide feedback in the chat input to evolve the tool.

## Project structure

- `app.py` — chat window UI.
- `src/agentic_builder/scanner.py` — folder inspection agent.
- `src/agentic_builder/planner.py` — blueprint generation agent.
- `src/agentic_builder/pr_manager.py` — PR draft generation.
- `src/agentic_builder/evolver.py` — feedback-based evolution loop.
- `src/agentic_builder/orchestrator.py` — high-level orchestration.
- `tests/` — automated tests.

## Run tests

```bash
pytest
```

## Suggested next iterations

- Replace rule-based planning with an LLM provider.
- Add a git integration agent that opens real PRs automatically.
- Add policy/security checks before proposing implementation changes.

## Populate a GitHub Project with Tickets

Use `project_tickets.csv` as a starter backlog and run:

```bash
GITHUB_TOKEN=YOUR_TOKEN REPO=YOUR_REPO ./scripts/populate_github_project.sh OWNER PROJECT_NUMBER ./project_tickets.csv
```

This will create issues in `OWNER/REPO` and add them to GitHub Project (v2) number `PROJECT_NUMBER`.
