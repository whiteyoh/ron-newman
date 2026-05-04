# Architecture diagrams

This folder documents the conceptual flow for each Glytch level. The diagrams are generated from a small Python data structure so they stay consistent and easy to update.

## What these diagrams show

These diagrams show the conceptual flow per level and how the demo presents each level.

They do not describe production deployment architecture.

## Generate diagrams

```bash
python scripts/generate_architecture_diagrams.py
```

Output:

```text
architecture/generated/level-1.svg
...
architecture/generated/level-8.svg
```

## Levels covered

| Level | Diagram focus |
|---:|---|
| 1 | Autocomplete |
| 2 | Instruction following |
| 3 | Tool use |
| 4 | Retrieval + grounding |
| 5 | Planning |
| 6 | Review loop |
| 7 | Swarm / multi-agent coordination |
| 8 | Custom orchestrator |

## Output files

Generated SVGs are ignored by default. Commit them only when they have been reviewed and are small enough for the repo.

## Safety model

These diagrams show the workshop-safe Glytch demo. They do not describe production deployment, real shell execution, real file writes or external side effects.
