# Agenticness Assessment

Glytch now uses two lenses:
1. AI capability patterns (what behaviors exist)
2. Agentic workflow maturity (how autonomous the workflow is)

## Current state
- Levels 1-6 mostly demonstrate capability patterns.
- Level 7 is the strongest true agentic demo (bounded loop with explicit stop conditions).
- Level 8 is a simulated orchestration pattern, not production orchestration.

## What is genuinely agentic
- Action selection in a loop
- Tool-assisted steps
- Explicit stop conditions
- Trace visibility

## What is simulated
- Multi-agent orchestration is sequential and workshop-safe.
- No real concurrent worker runtime.

## Why this is a good teaching tool
- It shows the progression from prompting to bounded autonomy.
- It separates "can do" capability from operational maturity.

## Why this is not yet a true multi-agent orchestrator
- No persistent coordinator service
- No distributed worker lifecycle
- No production governance/policy engine

## Path to real orchestration
- Add persistent task state and retries
- Add parallel worker execution
- Add policy, audit logs, and rollback controls

## 2026-05 agenticness implementation update
- Level 3: upgraded to model-selected tool action with JSON action choice and visible tool trace.
- Level 4: upgraded with evidence source labels, sufficiency check, and answer support verifier.
- Level 5: upgraded to plan-execute-verify with conditional single revision.
- Level 6: upgraded to bounded critique loop (score gate, threshold, max revisions).
- Level 7: upgraded with explicit AgentPolicy, action budget visibility, tool-error counting, final verifier gate, and structured run summary.
- Level 8: upgraded to mini-orchestrator abstraction in `src/orchestrator.py` with planner/researcher/writer/critic workers plus verifier and merger, running in safe parallel mode with fallback.
- Added Yegge fields per level in `AGENTICNESS`: `closest_yegge_stage`, `yegge_alignment_score`, and `yegge_alignment_explanation`.
- Limitation: this remains workshop-safe and is not a production orchestrator (no external side effects, no deployment automation, limited policy depth).



## Why Yegge adoption increased by one point
- Before: Level 8 demonstrated parallel role orchestration with verifier and merger outputs.
- After: Level 8 now runs a taskboard-based orchestrator simulation with explicit task state, worker lifecycle transitions, retry handling, audit trail, verifier gate, approval gate, and merge policy.
- Score change: Yegge alignment for Level 8 increased from 8 to 9 (exactly +1) because these orchestration mechanics now exist in implementation.
- Still missing for production-level orchestration: persistent storage, real worker processes, repository side effects, deployment integration, and multi-run memory.

## Why Levels 1–6 were uplifted to 7/10
Levels 1–6 are no longer raw capability-only demos. Each now runs inside a workshop-safe agentic wrapper with an objective, policy, allowed actions, verification, stop condition, approval gate, audit trail, and final verdict. The original capability theme is preserved per level (supervised completion, permissioned instruction following, tool-action loop, grounded research, CLI-style single-agent planning run, and bounded evaluator loop). A 7/10 score here reflects bounded and inspectable agent workflow mechanics, not production-grade autonomy. The app still avoids real side effects (no shell execution, file writes, GitHub writes, or background jobs).
