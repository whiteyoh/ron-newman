# Yegge Alignment

| Glytch capability level | Yegge-style stage alignment | Notes |
|---|---|---|
| 1-2 | 1-2 | Prompting and supervised usage; low autonomy |
| 3-4 | 2-4 | Tool/retrieval capability, still mostly supervised |
| 5-6 | 4-5 | Structured planning and revision, limited autonomy |
| 7 | 5 | Closest alignment: bounded CLI-like agent loop |
| 8 | 6-8 (partial) | Simulated orchestration pattern only |

## Recommended wording
Use: "Glytch has two lenses: AI capability patterns and agentic workflow maturity."  
Avoid: "These 8 capability levels are exactly Yegge's 8 stages."

## Where they align
- Agent loops and bounded autonomy concepts
- Workflow progression from manual to orchestrated patterns

## Where they do not
- Capability ladder is pedagogical, not an operational maturity ladder by itself
- Full multi-agent orchestration is only simulated in this workshop demo

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
