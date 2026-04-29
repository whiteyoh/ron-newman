# Examples-to-Stages Alignment Guide

This document explains how each example (`examples/level1` through `examples/level8`) maps to the workshop's eight stages of AI capability.

## Stage 1 — Autocomplete (`examples/level1`)

- **Core behavior:** Continues a partially written sentence naturally.
- **Why this satisfies Stage 1:** The flow is pure next-text continuation with no explicit planning, no external tools, and no grounding source.
- **Implementation signal:** Level 1 asks the model to "Continue the text naturally in one short phrase" after a short support-response prefix.

## Stage 2 — Instruction Following (`examples/level2`)

- **Core behavior:** Obeys explicit output constraints.
- **Why this satisfies Stage 2:** The task emphasizes compliance with a strict format requirement (exactly seven words), which demonstrates controlled prompting over simple continuation.
- **Implementation signal:** Level 2 supplies a direct constraint and a system instruction to "Follow user constraints precisely."

## Stage 3 — Tool Use (`examples/level3`)

- **Core behavior:** Uses a deterministic helper for precise computation.
- **Why this satisfies Stage 3:** The workflow calls `calculator_tool` for exact arithmetic and then asks the model to produce the final answer, showing model+tool cooperation.
- **Implementation signal:** Level 3 computes `17*43` through `calculator_tool` and passes the result into the model context.

## Stage 4 — Retrieval + Grounding (`examples/level4`)

- **Core behavior:** Retrieves evidence and constrains answers to that evidence.
- **Why this satisfies Stage 4:** The model must answer a factual question using retrieved local facts only (or say unknown), reducing unsupported claims.
- **Implementation signal:** Level 4 runs `retrieve_local_facts(question)` and prompts "Answer only from supplied evidence."

## Stage 5 — Multi-step Reasoning (`examples/level5`)

- **Core behavior:** Separates planning from execution.
- **Why this satisfies Stage 5:** The model first generates a numbered plan, then executes that plan into a timed agenda, demonstrating decomposed reasoning.
- **Implementation signal:** Level 5 performs two sequential calls: plan creation, then plan execution.

## Stage 6 — Agentic Loop (`examples/level6`)

- **Core behavior:** Iterative draft → critique → revise cycle.
- **Why this satisfies Stage 6:** The model evaluates its own output (via critique prompt) and performs a guided revision pass, forming a bounded feedback loop.
- **Implementation signal:** Level 6 creates an initial draft, requests a two-bullet critique, then revises using that critique.

## Stage 7 — Multi-agent Collaboration (`examples/level7`)

- **Core behavior:** Role-specialized agents collaborate to produce a final answer.
- **Why this satisfies Stage 7:** Separate agent roles (Research, Planner, Critic, Coordinator) contribute distinct perspectives before synthesis.
- **Implementation signal:** Level 7 runs sequential role prompts and consolidates into a coordinator output.

## Stage 8 — Self-improving Workflow (`examples/level8`)

- **Core behavior:** Generates alternatives, scores them, and retains the better candidate.
- **Why this satisfies Stage 8:** The process includes explicit evaluation metrics (clarity + actionability score) and selection logic, which operationalizes quality improvement.
- **Implementation signal:** Level 8 compares `score1` and `score2` and programmatically selects the higher-scoring draft.

## Quick matrix

| Stage | Example folder | Distinguishing capability |
|---|---|---|
| 1 | `examples/level1` | Natural continuation |
| 2 | `examples/level2` | Strict instruction compliance |
| 3 | `examples/level3` | Deterministic tool integration |
| 4 | `examples/level4` | Retrieval-grounded factual response |
| 5 | `examples/level5` | Plan then execute |
| 6 | `examples/level6` | Critique-and-revision loop |
| 7 | `examples/level7` | Role-based multi-agent pipeline |
| 8 | `examples/level8` | Score-driven self-improvement |

## Suggested use in workshops

- Ask participants to compare adjacent stages (e.g., 4 → 5, 6 → 7) and identify what new control mechanism is introduced.
- Have participants evaluate trade-offs for each stage: quality, latency, cost, and operational complexity.
