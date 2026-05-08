# Glytch

Most people use AI like search. Glytch shows what comes next.

Glytch is an 8-level, workshop-safe demo that shows how simple prompts become tools, checks, review points and controlled workflows.

![Glytch logo](assets/glytch-logo.svg)

## What Glytch is

Glytch is a plain-English AI maturity demo with a static frontend and a stdlib Python API.

It is built as a workshop-safe simulation. No real external action is taken.

It helps users compare:
- basic prompting
- bounded tool use
- evidence grounding
- planning and revision
- controlled workflow loops
- simulated orchestration

## The 8 levels

| Level | Focus | What it shows |
|---:|---|---|
| 1 | Autocomplete | One prompt, one draft, human decides next |
| 2 | Instruction following | Clearer instructions, format and constraints |
| 3 | Tool use | Bounded tool use with a checkable result |
| 4 | Retrieval + grounding | Output tied to retrieved evidence |
| 5 | Planning | Broad work split into visible steps |
| 6 | Critique + revision | Draft, critique and improve before review |
| 7 | Constrained agent loop | Bounded observe-act-check loop with stop conditions |
| 8 | Mini orchestrator | Multiple simulated workers, verifier, review gate and merge decision |

## Reading the output

New to Glytch? Start with [Reading Glytch output](docs/READING_GLYTCH_OUTPUT.md). It explains the scores, read-only simulation trace, workflow detail, replay and Level 8 taskboard.

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

The default model is gpt-4.1-mini because the current implementation uses Chat Completions. You can override OPENAI_MODEL for any model your provider supports.

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
