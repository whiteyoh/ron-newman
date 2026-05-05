# Glytch

Glytch is an 8-level workshop demo that helps people understand AI capability, agentic workflow maturity and what changes as AI moves beyond simple prompting.

![Glytch logo](assets/glytch-logo.svg)

## What Glytch is

Glytch is a plain-English AI maturity demo with a static frontend and a stdlib Python API.

It is built as a workshop-safe simulation: no real external action is taken.

## The 8 levels

| Level | Focus | What it shows |
|---:|---|---|
| 1 | Autocomplete | Simple prompt and response |
| 2 | Instruction following | Clearer instruction and human approval |
| 3 | Tool use | Bounded tool path |
| 4 | Retrieval + grounding | Evidence-backed output |
| 5 | Planning | Plan, execute, verify |
| 6 | Review loop | Critique and revision |
| 7 | Agent loop | Coordination pressure and controlled autonomy |
| 8 | Orchestration | Taskboard, verifier, approval gate and merge decision |

## Reading the output

New to Glytch? Start with [Reading Glytch output](docs/READING_GLYTCH_OUTPUT.md). It explains the scores, simulation trace, Agentic Theatre, replay and Level 8 taskboard.

## Guided first run

New users can start with **Try your first Glytch run**, which walks through a simple scenario, recommends Level 1 first, explains the output panels, and suggests comparing the same task at Level 3.

Scenario setup supports preset examples, custom use cases, and two “Surprise me” examples. Custom use cases are request-scoped and are not stored.

## Architecture

Architecture notes live in [architecture/](architecture/README.md). The diagrams are generated from `scripts/generate_architecture_diagrams.py` and describe the conceptual flow for each Glytch level.

## Run it locally

```bash
make install-dev
make run
```

Open <http://127.0.0.1:8000>.

### Optional AI backend

Glytch runs without an API key and shows a safe fallback. To use a live OpenAI-compatible backend, set:

```bash
export OPENAI_API_KEY="your_api_key_here"
export OPENAI_MODEL="gpt-4.1-mini"
export OPENAI_BASE_URL="https://api.openai.com/v1"
```

## Checks

```bash
make check
bash scripts/smoke_test.sh
```

## Pre-merge checks

GitHub Actions runs the `pre-merge-checks` workflow with Python checks, a smoke test, a dependency audit and a secret scan.

See [docs/PIPELINE_CHECKS.md](docs/PIPELINE_CHECKS.md) for details.

## API

- `GET /healthz`
- `GET /api/levels`
- `GET /api/use-cases`
- `GET /api/agentic-maturity`
- `POST /api/run`

If `OPENAI_API_KEY` is missing, `/api/run` returns a safe fallback rather than crashing.

## Deployment

Render settings:
- Build: `pip install -r requirements.txt`
- Start: `python app.py`
- Health check: `/healthz`

## Safety model

- workshop-safe simulation
- no real shell execution
- no real file writes
- no GitHub writes
- no background jobs
- no real external side effects
- Level 8 is request-scoped orchestration, not production orchestration
- rate limiting is lightweight and in-memory, not a distributed production limiter
