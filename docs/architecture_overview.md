# Architecture Overview

## System context

The application is a local, Streamlit-based "agentic builder" that helps a user inspect a folder and produce an implementation-oriented PR draft. The user provides a folder path and optional feedback through a chat UI, while the backend modules orchestrate scanning, planning, PR drafting, and iterative evolution.

## Main components

1. **UI layer (`app.py`)**
   - Hosts the Streamlit chat experience.
   - Captures the folder path to analyze.
   - Triggers orchestration and renders generated artifacts.

2. **Orchestration layer (`src/agentic_builder/orchestrator.py`)**
   - Coordinates end-to-end workflow.
   - Calls scanner, planner, PR manager, and evolver in sequence.
   - Returns a single coherent result that can be displayed in chat.

3. **Domain agents (`src/agentic_builder/*.py`)**
   - `scanner.py`: inspects file structure and summarizes content.
   - `planner.py`: builds a blueprint including capabilities and testing strategy.
   - `pr_manager.py`: converts blueprint output into a PR-style narrative.
   - `evolver.py`: translates user feedback into incremental improvement history.

4. **Shared models (`src/agentic_builder/models.py`)**
   - Defines shared dataclasses used to move data between modules.
   - Keeps module boundaries explicit and minimizes ad hoc dictionaries.

5. **Tests (`tests/test_agentic_builder.py`)**
   - Validates scanning and orchestration behavior.
   - Protects feedback evolution and PR draft expectations.

## Data flow

```text
User input (folder path + feedback)
      |
      v
Streamlit UI (app.py)
      |
      v
Orchestrator
  ├─> Scanner      -> folder summary
  ├─> Planner      -> tool blueprint
  ├─> PR Manager   -> PR-style draft
  └─> Evolver      -> updated roadmap from feedback
      |
      v
Chat-visible artifacts
```

## Dependencies and boundaries

- **Runtime**: Python 3.11+
- **UI framework**: Streamlit
- **Testing**: Pytest
- **Packaging**: `pyproject.toml` with editable install support

The architecture intentionally favors lightweight, deterministic module behavior so it can later be replaced or augmented with provider-backed LLM calls without redesigning top-level flow.
