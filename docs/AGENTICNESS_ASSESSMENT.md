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
