Glytch has two lenses: AI capability patterns and agentic workflow maturity.

![Glytch logo](assets/glytch-logo.svg)

## 8-Layer Capability Model

This document describes the eight capability layers used in this repository and links them to the workshop scenarios.

## Why this model is used

The model provides a consistent way to compare:
- response quality,
- factual reliability,
- latency,
- implementation complexity,
- and operational cost.

It is intended to support architecture decisions, not to imply every use case needs the highest layer.

## Two lenses used in Glytch

| Lens | What it measures |
|---|---|
| AI capability patterns | What app behavior is demonstrated (autocomplete, tool use, retrieval, loops, orchestration patterns). |
| Agentic workflow maturity | How autonomous the human/agent workflow is in practice (who chooses actions, when tools are used, whether loops run independently). |

Prompt-only use is useful, but it is low agenticness because the AI does not choose actions, use tools, loop, or operate independently.

## Layer definitions

### 1) Autocomplete
- Predicts likely continuation text.
- Strength: fluent output.
- Limitation: weak consistency and factual control.

### 2) Instruction Following
- Applies explicit constraints (format, length, style).
- Strength: improved output structure.
- Limitation: still may produce unsupported facts.

### 3) Tool Use
- Calls external tools such as calculators or lookups.
- Strength: better precision for tool-compatible tasks.
- Limitation: orchestration and error handling become important.

### 4) Retrieval + Grounding
- Uses retrieved evidence and constrains answers to that evidence.
- Strength: reduced hallucination risk.
- Limitation: dependent on retrieval quality.

### 5) Multi-step Reasoning
- Separates planning and execution steps.
- Strength: better handling of complex tasks.
- Limitation: increased latency and workflow complexity.

### 6) Critique + Revision
- Performs one critique pass and one revision pass on a draft.
- Strength: iterative quality improvement in a simple controlled pattern.
- Limitation: not yet a fully autonomous action loop.

### 7) Constrained Agent Loop
- Runs a bounded objective -> action -> tool -> observation -> next action cycle.
- Strength: adaptive behavior with explicit safeguards and transparent traces.
- Limitation: still needs careful action constraints and iteration limits.

### 8) Mini Orchestrator / Self-improving Workflow
- Workshop-safe simulation of orchestrating planner, critic, teacher-resource-writer, and verifier roles.
- Strength: demonstrates role-based coordination and verification in one flow.
- Limitation: simulation only, not a production orchestrator.

## Practical guidance

Use the lowest layer that consistently meets your use-case requirements.

For this repository, layer behavior is demonstrated in:
- `examples/SCENARIO_USE_CASES.md`
- `examples/level1` through `examples/level8`
