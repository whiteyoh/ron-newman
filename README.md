# Agentic AI Tool Builder

This project is a starter implementation of an **agentic AI tool that builds agentic AI tools** from a human-provided folder.

---

## What this app does

- Scans a target folder and summarizes file structure.
- Generates a tool blueprint with capabilities, architecture, and testing strategy.
- Drafts output as pull-request style content.
- Streams each artifact into a chat-style Streamlit UI.
- Narrates analysis live in plain English so you can see what the tool is doing step-by-step.
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

## 2) How to make it analyze a folder

Once the app is open:

1. In the **Folder path to analyze** field, enter the path to the project you want analyzed.
   - Example: `.` (current repo)
   - Example: `/absolute/path/to/your/project`
2. Click **Analyze Folder and Draft PR**.
3. Watch the **Live agent narration** panel while it runs. You will see human-readable progress updates (for example, when it is scanning files, planning architecture, or drafting the PR).
4. After completion, review:
   - **What I looked at**: top areas and largest files inspected for context
   - A folder summary with representative files
   - A proposed blueprint/plan
   - A PR-style draft output

### Good first folder to try

Use this repository itself by entering:

```text
.
```

This is a reliable first run because the app can inspect known files immediately.

---

## 3) Example: how to make it evolve

After the initial analysis finishes, add feedback in the chat input.

The system can create missing agents automatically (scanner/planner/PR/evolver) and then reuse them in later runs. You can always inspect current status in the **Agent registry** expander in the UI.

Example prompts you can paste directly:

- "Evolve this plan to prioritize test coverage first."
- "Refine the architecture to support plugin-based scanners."
- "Update the PR draft so phase 1 is a minimal MVP and phase 2 adds advanced features."
- "Improve the plan for a small team shipping in 2 weeks."

Each feedback entry is captured and used by the evolution loop to produce a revised proposal.

---

## 4) How to run the tests

From the repository root:

```bash
pytest
```

If you want verbose output:

```bash
pytest -v
```

---

## 5) Step-by-step guide to demonstrate it

Use this sequence for a quick demo (about 5-10 minutes):

1. **Start the app**
   - Run `streamlit run app.py`.
2. **Analyze a folder**
   - Enter `.` and click **Analyze Folder and Draft PR**.
3. **Walk through generated artifacts**
   - Show the folder summary, architecture/blueprint, and PR-style draft in the chat output.
4. **Submit evolution feedback**
   - Paste: "Evolve this plan to reduce scope and deliver a working prototype in one week."
5. **Review evolved output**
   - Compare the new plan to the initial plan and call out what changed.
6. **Run tests live (optional but recommended)**
   - In terminal: `pytest`
7. **Close with next steps**
   - Propose one additional iteration prompt (e.g., adding policy/security checks).

---

## Project structure

- `app.py` — chat window UI
- `src/agentic_builder/scanner.py` — folder inspection agent
- `src/agentic_builder/planner.py` — blueprint generation agent
- `src/agentic_builder/pr_manager.py` — PR draft generation
- `src/agentic_builder/evolver.py` — feedback-based evolution loop
- `src/agentic_builder/orchestrator.py` — high-level orchestration
- `tests/` — automated tests

## Planning artifacts

- `docs/architecture_overview.md` — high-level architecture and data-flow reference
- `docs/test_plan.md` — test scope, levels, and release exit criteria

## Suggested next iterations

- Replace rule-based planning with an LLM provider
- Add a git integration agent that opens real PRs automatically
- Add policy/security checks before proposing implementation changes

## Populate a GitHub Project with tickets

Use `project_tickets.csv` as a starter backlog and run:

```bash
GITHUB_TOKEN=YOUR_TOKEN REPO=YOUR_REPO ./scripts/populate_github_project.sh OWNER PROJECT_NUMBER ./project_tickets.csv
```

This creates issues in `OWNER/REPO` and adds them to GitHub Project (v2) number `PROJECT_NUMBER`.
