# Yegge AI Competence Ladder Demo

This project provides an interactive, **real-LLM-backed** demonstration of 8 AI competence levels.

## Quick start

```bash
export OPENAI_API_KEY="your_key_here"
# optional
# export OPENAI_BASE_URL="https://api.openai.com/v1"
# export OPENAI_MODEL="gpt-4.1-mini"
python app.py
```

Open: <http://127.0.0.1:8000>

## What this project does

- Runs a local web dashboard.
- Executes eight distinct AI workflows (one per level).
- Shows trace output so you can inspect the behavior.
- Demonstrates practical AI usage patterns from completion to iterative improvement.

## Project layout

- `app.py` — HTTP server + level workflow implementations.
- `web/index.html` — dashboard UI.
- `web/main.js` — level runner and output renderer.
- `examples/level1` ... `examples/level8` — per-level notes and expected AI behavior.

## Note

If `OPENAI_API_KEY` is missing, each level returns a clear configuration message rather than fake output.
