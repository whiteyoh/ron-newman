Glytch has two lenses: AI capability patterns and agentic workflow maturity.

![Glytch logo](assets/glytch-logo.svg)

## Workshop Guide

This guide explains the purpose and flow of the Glytch workshop.

The workshop uses one set of scenario use cases across eight levels so participants can compare output quality, reliability, and operational complexity at each stage.

Reference scenarios: `examples/SCENARIO_USE_CASES.md`.

## Workshop objective

Participants should be able to:
- Explain what changes from Levels 1 through 8.
- Identify when a lower-complexity approach is sufficient.
- Recognize trade-offs in quality, latency, and cost.
- Choose an implementation level appropriate for a real use case.

## Level summary

1. **Autocomplete**: continuation-style output.
2. **Instruction Following**: constrained response formatting.
3. **Tool Use**: model + external tool for exact operations.
4. **Retrieval + Grounding**: answers constrained by retrieved evidence.
5. **Multi-step Reasoning**: plan then execute.
6. **Critique + Revision**: one critique pass followed by one revision pass.
7. **Constrained Agent Loop**: bounded observe/act/replan cycle with allowed tools and stop conditions.
8. **Self-improving Workflow**: evaluate candidates and choose the stronger result.

## Suggested session structure

- Introduction and setup: 20 minutes
- Levels 1 to 4: 60 minutes
- Levels 5 to 8: 60 minutes
- Debrief and architecture discussion: 30 to 60 minutes

Total: approximately 2.5 to 4 hours.

## Audience

Appropriate for:
- Students learning modern application patterns.
- Individual builders learning system design trade-offs.
- Teams evaluating architecture choices before production.

Prerequisites: basic Python and web app familiarity.

## Quick start

```bash
export OPENAI_API_KEY="your_key_here"
python app.py
```

Then open <http://127.0.0.1:8000> and run through Levels 1 to 8.

## Why Levels 1–6 were uplifted to 7/10
Levels 1–6 are no longer raw capability-only demos. Each now runs inside a workshop-safe agentic wrapper with an objective, policy, allowed actions, verification, stop condition, approval gate, audit trail, and final verdict. The original capability theme is preserved per level (supervised completion, permissioned instruction following, tool-action loop, grounded research, CLI-style single-agent planning run, and bounded evaluator loop). A 7/10 score here reflects bounded and inspectable agent workflow mechanics, not production-grade autonomy. The app still avoids real side effects (no shell execution, file writes, GitHub writes, or background jobs).

## WOW but honest update
Glytch now includes Agentic Theatre, a maturity ladder, score explanations, and a Level 8 taskboard dashboard. It remains a workshop-safe simulated orchestration environment with human approval gates and no external side effects.

## Yegge alignment update
This demo now presents **capability vs Yegge stage** with high-fidelity workshop simulations, explicit human approval gates, and clear non-production limits.
