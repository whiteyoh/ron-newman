![Glitch logo](../assets/glitch-logo.svg)

# Scenario Use Cases (Given / When / Then)

This document describes what people will see in each scenario using simple behavior-driven language.

## Scenario 1 — Autocomplete (`examples/level1`)

**Given** a partially written customer support sentence,
**When** the model is asked to continue it naturally,
**Then** people will see a short text continuation with no strict formatting, tools, or evidence checks.

## Scenario 2 — Instruction Following (`examples/level2`)

**Given** a response task with a strict output constraint,
**When** the model is told to follow that constraint exactly,
**Then** people will see a compliant answer (for example, exactly seven words) that prioritizes instruction precision.

## Scenario 3 — Tool Use (`examples/level3`)

**Given** a task that includes arithmetic requiring exactness,
**When** the workflow calls a calculator tool and passes the result back to the model,
**Then** people will see a precise final answer produced through model-and-tool cooperation.

## Scenario 4 — Retrieval + Grounding (`examples/level4`)

**Given** a factual question and a local evidence retrieval step,
**When** the model is constrained to answer only from retrieved facts,
**Then** people will see grounded responses tied to evidence (or an explicit unknown if evidence is missing).

## Scenario 5 — Multi-step Reasoning (`examples/level5`)

**Given** a planning-style request,
**When** the model first creates a numbered plan and then executes that plan,
**Then** people will see structured, stepwise output rather than a single one-pass response.

## Scenario 6 — Agentic Loop (`examples/level6`)

**Given** an initial draft response,
**When** the model critiques the draft and then revises it,
**Then** people will see an iterative improvement loop (draft → critique → revised draft).

## Scenario 7 — Multi-agent Collaboration (`examples/level7`)

**Given** multiple role-specialized agents (Research, Planner, Critic, Coordinator),
**When** each role contributes and the coordinator synthesizes the result,
**Then** people will see a combined final answer that reflects distinct expert perspectives.

## Scenario 8 — Self-improving Workflow (`examples/level8`)

**Given** multiple candidate drafts and explicit scoring criteria,
**When** the workflow scores each candidate and selects the stronger one,
**Then** people will see a quality-optimized final output chosen by measurable evaluation.
