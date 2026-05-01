![Glitch logo](assets/glitch-logo.svg)

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

### 6) Agentic Loop
- Repeats observe/act/review cycles until conditions are met.
- Strength: iterative improvement.
- Limitation: requires robust stop conditions and safeguards.

### 7) Multi-agent Collaboration
- Uses specialized roles that contribute to a final synthesis.
- Strength: improves quality via specialization.
- Limitation: increased coordination overhead.

### 8) Self-improving Workflow
- Evaluates outputs and selects or updates based on defined criteria.
- Strength: measurable quality improvement over time.
- Limitation: requires governance and safe update controls.

## Practical guidance

Use the lowest layer that consistently meets your use-case requirements.

For this repository, layer behavior is demonstrated in:
- `examples/SCENARIO_USE_CASES.md`
- `examples/level1` through `examples/level8`
