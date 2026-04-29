# AI Competence Ladder Workshop

This repository can be run as a **hands-on workshop** to teach people how AI systems evolve from simple prompting to agentic and self-improving workflows.

The workshop uses one shared scenario throughout all activities:

> **Improving customer support response quality for a SaaS product.**

---

## Workshop outcomes

By the end of this workshop, participants will be able to:

- Explain the difference between Levels 1–8 of AI capability.
- Observe how adding tools, retrieval, planning, and agents changes output quality.
- Diagnose common failure modes (hallucination, brittle steps, over-tooling).
- Propose practical production guardrails for each level.

---

## Audience and timing

- **Audience:** Product managers, engineers, analysts, or technical educators.
- **Prerequisites:** Basic comfort with Python and web apps.
- **Recommended length:** 2.5–4 hours.
  - Intro + setup: 20 min
  - Levels 1–4: 60 min
  - Levels 5–8: 60 min
  - Debrief + design exercise: 30–60 min

---

## Facilitator prep

1. Clone this repo and verify Python works locally.
2. Set your OpenAI credentials.
3. Run the app and click each level once.
4. Decide if attendees will run locally or pair at shared stations.
5. Print/share the discussion prompts section below.

---

## Quick start

```bash
export OPENAI_API_KEY="your_key_here"
# optional
# export OPENAI_BASE_URL="https://api.openai.com/v1"
# export OPENAI_MODEL="gpt-4.1-mini"
python app.py
```

Open: <http://127.0.0.1:8000>

> If `OPENAI_API_KEY` is missing, each level returns a configuration message instead of model output.

---

## Workshop run-of-show

### 1) Framing (10 minutes)

Teach this mental model:

- **Level 1–2:** Better prompting.
- **Level 3–4:** Tooling and grounding.
- **Level 5–6:** Planning and iterative execution.
- **Level 7–8:** Teams of agents and feedback loops.

### 2) Live walkthrough of all levels (60–90 minutes)

For each level:

1. Ask participants to predict what will improve from the previous level.
2. Click the level button in UI.
3. Review trace output.
4. Discuss: quality, latency, cost, and risk trade-offs.

Buttons in UI:

- **Level 1** Autocomplete
- **Level 2** Instruction Following
- **Level 3** Tool Use
- **Level 4** Retrieval + Grounding
- **Level 5** Multi-step Reasoning
- **Level 6** Agentic Loop
- **Level 7** Multi-agent Collaboration
- **Level 8** Self-improving Workflow

### 3) Group exercise (30–45 minutes)

Break attendees into small groups and assign:

- One target level to productionize.
- A reliability goal (e.g., less hallucination, faster response, lower token cost).
- A guardrail strategy (fallbacks, confidence checks, human review).

Each group presents:

- Why they chose that level.
- What they would add/remove.
- Their top operational risk.

### 4) Debrief (15 minutes)

Use these prompts:

- Which level delivered the best value/complexity ratio?
- Where did quality improve most?
- Which level felt hardest to make reliable?
- What monitoring would you need in production?

---

## Hands-on participant tasks

Have participants complete these in order:

1. Run Level 2 and rewrite instructions for clearer tone constraints.
2. Run Level 3 and inspect tool choice behavior.
3. Run Level 4 and discuss what grounding changed.
4. Run Level 6 and identify where loop termination could fail.
5. Run Level 8 and propose one safe self-improvement boundary.

Optional challenge:

- Add a new support policy input and compare behavior at Levels 4, 6, and 8.

---

## Repository map (for teaching)

- `app.py` — HTTP server and API routes.
- `web/index.html`, `web/main.js` — workshop dashboard and controls.
- `src/constants.py` — level labels and shared use-case text.
- `src/ai_client.py` — model client wiring.
- `src/tools.py` — pure tool functions used by level workflows.
- `src/levels.py` — implementation for each level.
- `tests/test_tools.py` — unit tests for deterministic helpers.
- `examples/level1` ... `examples/level8` — level-specific notes.

---

## Suggested evaluation rubric

Score each level (1–5) on:

- Output quality
- Factual reliability
- Latency
- Token/cost efficiency
- Ease of debugging
- Production readiness

This makes trade-offs explicit and creates a reusable framework for future AI project reviews.

---

## Troubleshooting

- **Port in use:** change the port in `app.py` or stop the existing process.
- **No model output:** verify `OPENAI_API_KEY` is set in your current shell.
- **Unexpected responses:** pin `OPENAI_MODEL` to a known model during workshop delivery for consistency.

---

## License and usage

Use this repo freely for internal training, bootcamps, and education sessions. If you adapt the workshop, consider adding your own domain-specific use case and risk controls.
