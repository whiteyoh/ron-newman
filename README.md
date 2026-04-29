# Yegge AI Competence Ladder Demo

An interactive web app that demonstrates 8 AI capability levels with a **single shared business use case**:

> **Improving customer support response quality for a SaaS product.**

## Quick start

```bash
export OPENAI_API_KEY="your_key_here"
# optional
# export OPENAI_BASE_URL="https://api.openai.com/v1"
# export OPENAI_MODEL="gpt-4.1-mini"
python app.py
```

Open: <http://127.0.0.1:8000>

## Triggering each use case

All examples run through the same UI flow:

1. Start the app (`python app.py`).
2. Open <http://127.0.0.1:8000>.
3. Click one button:
   - **Level 1** Autocomplete
   - **Level 2** Instruction Following
   - **Level 3** Tool Use
   - **Level 4** Retrieval + Grounding
   - **Level 5** Multi-step Reasoning
   - **Level 6** Agentic Loop
   - **Level 7** Multi-agent Collaboration
   - **Level 8** Self-improving Workflow
4. Read the trace output panel.

## What changed in this version

- Code is split into focused function files under `src/` for cleaner structure.
- Pure helper functions now have unit tests under `tests/`.
- Every level includes the same cross-cutting customer-support use case while preserving each original level behavior.

## Project layout

- `app.py` — HTTP server and API routes.
- `src/ai_client.py` — LLM client.
- `src/constants.py` — level metadata and global use case text.
- `src/tools.py` — pure tool functions.
- `src/levels.py` — per-level workflow implementations.
- `tests/test_tools.py` — unit tests for pure functions.
- `web/index.html`, `web/main.js` — dashboard UI.
- `examples/level1` ... `examples/level8` — level-specific walkthroughs.

## Note

If `OPENAI_API_KEY` is missing, each level returns a clear configuration message rather than fake output.
