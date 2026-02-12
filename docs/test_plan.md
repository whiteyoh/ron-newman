# Test Plan

## Goals

This plan validates that the agentic builder remains reliable as it analyzes folders, drafts implementation plans, and evolves based on feedback.

## Scope

In scope:

- Unit-level behavior for scanner, planner, PR manager, evolver, and orchestrator.
- Integration behavior for the end-to-end orchestration path.
- Regression checks for chat-facing output formatting and feedback history.

Out of scope (for now):

- Browser automation and visual UI assertions.
- External API / LLM provider integration.
- Performance benchmarking at scale.

## Test levels

### 1) Unit tests

- **Scanner**
  - Returns deterministic summaries for folders with mixed files.
  - Handles missing or empty directories gracefully.
- **Planner**
  - Produces capabilities, architecture notes, and testing strategy sections.
- **PR manager**
  - Converts planning output into a coherent PR-style draft.
- **Evolver**
  - Adds user feedback to improvement history in order.
- **Orchestrator**
  - Correctly wires component outputs and preserves data contracts.

### 2) Integration tests

- Run full flow from folder input to final PR draft payload.
- Assert intermediate artifacts are represented in final output.
- Verify feedback cycles produce additive (non-destructive) evolution history.

### 3) Manual smoke checks

Before release:

1. Launch Streamlit app.
2. Analyze a representative folder.
3. Submit at least one feedback iteration.
4. Confirm artifacts are readable and logically connected.

## Test data strategy

- Use small fixture directories with controlled file names and contents.
- Include edge fixtures:
  - Empty folder
  - Nested folders
  - Mixed extensions
  - Hidden/system-style files

## Tooling and execution

- Primary command: `pytest`
- Optional quality gates (future): linting and type checks
- CI recommendation: run tests on each PR and block merges on failures

## Exit criteria

A change is releasable when:

- Existing tests pass.
- New behavior is covered by tests where feasible.
- No regressions in end-to-end orchestration output.
- Manual smoke check passes for the Streamlit flow.
