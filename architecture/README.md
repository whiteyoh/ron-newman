# Architecture diagrams

This folder contains the architecture diagram generator for Glytch’s eight levels.

The generated diagrams are conceptual. They show how each level is presented in the workshop-safe Glytch demo. They are not production deployment diagrams.

## Generate diagrams

Run:

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

## Notes

- The diagrams are generated from a small Python data structure.
- Generated SVG files are intentionally not committed in the first PR.
- Keep generated outputs small and reviewable if they are committed later.
- Glytch remains a workshop-safe simulation with no real external action.
