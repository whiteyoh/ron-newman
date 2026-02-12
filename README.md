# Agentic AI Tool Builder

This project is a local-first implementation of an **agent that creates and evolves other agents** from folder analysis.

The core idea: point it at a codebase, let it inspect structure and file makeup, and it will automatically assemble the right internal agents on the fly (scanner, planner, PR manager, evolver) without asking for manual confirmation.

---

## What this app does

- Scans a target folder and summarizes file structure, dominant file types, and high-signal areas.
- Dynamically creates missing internal agents at runtime and reuses existing ones in later runs.
- Generates a tool blueprint with capabilities, architecture, and testing strategy.
- Drafts output as pull-request style content.
- Streams each artifact into a chat-style Streamlit UI.
- Narrates analysis live in plain English so you can follow every step.
- Supports iterative evolution by turning feedback into a history of improvements.

---

## 1) Getting the app set up

### Prerequisites

- Python 3.10+
- `pip`
- `venv` support

### Install and run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
streamlit run app.py
```

When Streamlit starts, open the local URL shown in your terminal (usually `http://localhost:8501`).

---

## 2) How to create a new agent from folder analysis (local + on-the-fly)

This is the behavior you asked for: agent creation should happen locally and immediately during analysis.

### In the UI

1. Start the app with `streamlit run app.py`.
2. Enter a folder path in **Folder path to analyze**.
3. Click **Analyze Folder and Draft PR**.
4. Open **Agent registry** before and after the run.
   - Agents that were missing are auto-created during the run.
   - Agents that already existed are reused.
5. Read **New agents created this run** in the final output block.

### What happens internally

During `run_with_updates(...)`, the orchestrator:

1. Checks the in-memory agent registry.
2. Creates missing agents immediately via `_get_or_create_agent(...)`.
3. Scans the folder and builds insight data.
4. Chooses implementation focus based on dominant extension.
5. Builds a blueprint.
6. Produces a PR-style draft.
7. Reports which agents were created this run.

No network service is required for this flow; it is local process state in your running app session.

---

## 3) Features that are easy to miss (now documented)

If you only use the primary button, several capabilities can be overlooked:

- **Agent registry visibility**: You can inspect active vs idle agents in the UI.
- **Automatic agent lifecycle**: Missing agents are created without prompt; existing agents are reused.
- **Inspection scope narration**: Output includes top-level folders and largest files reviewed.
- **Decision engine**: Dominant extension influences recommended implementation focus.
- **Evolution loop**: Chat feedback is captured and transformed into the next prioritized improvement.
- **Programmatic API**: You can import and run the orchestrator directly in Python (without Streamlit).

### Programmatic usage example

```python
from agentic_builder import AgenticBuilder, EvolutionState

builder = AgenticBuilder()
result = builder.run(".")
print(result["pr_title"])

state = EvolutionState()
next_step = builder.evolve("Prioritize test coverage and reduce scope", state)
print(next_step)
```

---

## 4) How to run folder analysis effectively

1. Start with a small, representative repo for faster results.
2. Use absolute paths when analyzing folders outside the current working directory.
3. If the folder is huge, run once, review the decision and scope notes, then iterate with feedback.
4. Use evolution prompts to steer goals (speed, quality, architecture constraints, delivery timeline).

### Good first folder to try

Use this repository itself by entering:

```text
.
```

---

## 5) Example feedback prompts for evolution

- "Evolve this plan to prioritize test coverage first."
- "Refine the architecture to support plugin-based scanners."
- "Update the PR draft so phase 1 is a minimal MVP and phase 2 adds advanced features."
- "Improve the plan for a small team shipping in 2 weeks."

---

## 6) How to run the tests

From the repository root:

```bash
pytest
```

If you want verbose output:

```bash
pytest -v
```

---

## 7) Step-by-step demo (5–10 minutes)

1. **Start the app**
   - Run `streamlit run app.py`.
2. **Analyze a folder**
   - Enter `.` and click **Analyze Folder and Draft PR**.
3. **Show dynamic agent creation**
   - Open **Agent registry** and show newly active agents.
   - Point out **New agents created this run** in output.
4. **Walk through generated artifacts**
   - Show scope note, decision, blueprint summary, and PR-style draft.
5. **Submit evolution feedback**
   - Paste: "Evolve this plan to reduce scope and deliver a working prototype in one week."
6. **Review evolved output**
   - Compare next improvement candidate and evolution history.
7. **Run tests live (optional)**
   - In terminal: `pytest`

---

## Project structure

- `app.py` — Streamlit chat UI and live narration
- `src/agentic_builder/orchestrator.py` — dynamic agent registry + end-to-end flow
- `src/agentic_builder/scanner.py` — folder inspection agent
- `src/agentic_builder/planner.py` — blueprint generation agent
- `src/agentic_builder/pr_manager.py` — PR draft generation
- `src/agentic_builder/evolver.py` — feedback-based evolution engine
- `src/agentic_builder/models.py` — shared dataclasses and state
- `tests/` — automated tests

## Planning artifacts

- `docs/architecture_overview.md` — high-level architecture and data flow
- `docs/test_plan.md` — test scope, levels, and release criteria

## Populate a GitHub Project with tickets

Use `project_tickets.csv` as a starter backlog and run:

```bash
GITHUB_TOKEN=YOUR_TOKEN REPO=YOUR_REPO ./scripts/populate_github_project.sh OWNER PROJECT_NUMBER ./project_tickets.csv
```

This creates issues in `OWNER/REPO` and adds them to GitHub Project (v2) number `PROJECT_NUMBER`.
