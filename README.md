# Yegge AI Competence Ladder Demo

This project provides an interactive, **real-LLM-backed** demonstration of 8 AI competence layers.

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

## How to trigger each layer

After starting the app, click the matching **Level N** button in the UI:

1. **Level 1: Autocomplete**
   - Trigger: click **Level 1**.
   - Handles: next-text continuation from a short prompt (example: finishing “The sun rises in the ...”).
   - Real-world job example: a **journalist** starting a news intro and using AI to suggest the next sentence quickly.
2. **Level 2: Instruction Following**
   - Trigger: click **Level 2**.
   - Handles: strict prompt constraints (example: exactly 7-word summary output).
   - Real-world job example: a **social media manager** asking for a caption that must fit a strict word limit.
3. **Level 3: Tool Use**
   - Trigger: click **Level 3**.
   - Handles: deterministic arithmetic by combining model output with a calculator tool.
   - Real-world job example: a **shop manager** checking totals, discounts, and VAT with AI + calculator accuracy.
4. **Level 4: Retrieval + Grounding**
   - Trigger: click **Level 4**.
   - Handles: fact lookup from a local knowledge base and grounded answers only from retrieved evidence.
   - Real-world job example: a **nurse or GP receptionist** pulling answers only from trusted NHS guidance, not guesses.
5. **Level 5: Multi-step Reasoning**
   - Trigger: click **Level 5**.
   - Handles: planning then execution (example: build a workshop plan, then generate a timed agenda).
   - Real-world job example: an **event organiser** planning a school careers fair step by step (rooms, timings, staffing).
6. **Level 6: Agentic Loop**
   - Trigger: click **Level 6**.
   - Handles: draft → critique → revise cycles to improve quality.
   - Real-world job example: a **marketing assistant** creating an advert, reviewing it, then improving it before publishing.
7. **Level 7: Multi-agent Collaboration**
   - Trigger: click **Level 7**.
   - Handles: role-based collaboration (researcher, planner, critic, coordinator) to produce a final recommendation.
   - Real-world job example: a **project manager** using specialist AI roles like a mini team to plan a product launch.
8. **Level 8: Self-improving Workflow**
   - Trigger: click **Level 8**.
   - Handles: generate variants, score each one, and keep the best candidate.
   - Real-world job example: a **teacher** generating multiple quiz versions, scoring clarity, and choosing the best one for class.

## Project layout

- `app.py` — HTTP server + level workflow implementations.
- `web/index.html` — dashboard UI.
- `web/main.js` — level runner and output renderer.
- `examples/level1` ... `examples/level8` — per-level notes and expected AI behavior.

## Note

If `OPENAI_API_KEY` is missing, each level returns a clear configuration message rather than fake output.
