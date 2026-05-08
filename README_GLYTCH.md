# Glytch

Most people use AI like search. Glytch shows what comes next.

Glytch is an 8-level, workshop-safe demo that helps people understand how simple prompts become tools, checks, review points and controlled workflows.

![Glytch logo](assets/glytch-logo.svg)

## What is Glytch?

Glytch is a practical, plain-English AI fluency demo.

Glytch teaches AI capability, not AI products.

It is a workshop-safe simulation that helps people see how work changes from:
- one prompt and one draft
- to structured instructions
- to tool use and evidence checks
- to a controlled workflow with human review

It does this without requiring people to commit to one specific vendor or interface.

## Why use Glytch?

Glytch helps people see what usually stays hidden when they use AI:
- what the task is
- what the AI is doing
- whether evidence was used
- whether anything was checked
- where human review is needed
- whether the work should stay simple or become more structured

The aim is not to teach one specific AI tool. The aim is to build practical judgement that works across many tools.

## Who Glytch is for

Glytch is not only for developers. It is for people who need clear, practical AI understanding:

- students learning how AI can support study and problem solving
- teachers explaining AI capability safely
- public sector teams exploring safe AI use
- non-technical managers trying to understand what AI can and cannot do
- small businesses looking for practical AI workflow ideas
- job seekers building AI confidence
- teams that need shared language before choosing tools

## What Glytch teaches

The capability pattern is more durable than any single AI app:

Prompt → instruction → tool use → evidence → planning → critique → loop → orchestration

| Stage | Plain English idea |
|---|---|
| Prompt | Ask AI for a response |
| Instruction | Give clearer rules and format |
| Tool | Use a bounded helper such as a calculator |
| Evidence | Ground the answer in supplied facts |
| Plan | Break broad work into visible steps |
| Improve | Critique and revise before use |
| Loop | Observe, act, check and stop safely |
| Orchestrate | Coordinate multiple simulated workers with review gates |

Higher levels are not automatically better. The best AI use is the lowest level that safely gets the job done.

## The 8 Glytch levels

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

## How Glytch avoids tool chasing

AI tools change quickly. Glytch focuses on the mental model underneath them.

Whether someone uses ChatGPT, Gemini, Claude, Copilot or another AI tool, the same questions matter:
- what am I asking it to do?
- what information is it using?
- what should be checked?
- what should the human decide?
- is this simple prompting or a controlled workflow?

## Reading the output

New to Glytch? Start with [Reading Glytch output](docs/READING_GLYTCH_OUTPUT.md). It explains the scores, read-only simulation trace, workflow detail, replay and Level 8 taskboard.

## Guided first run

Try your first Glytch run to see the model in action.

- Start with Level 1.
- Compare the same scenario at Level 3.
- Use Level 8 to see orchestration with review gates.
- Custom use cases are request-scoped and are not stored.

## Architecture

Architecture notes live in [architecture/](architecture/README.md). The diagrams are generated from `scripts/generate_architecture_diagrams.py` and describe the conceptual flow for each Glytch level.

## Run it locally

```bash
make install-dev
make run
```

Open http://127.0.0.1:8000.

## Optional AI backend

Glytch runs without an API key and shows a safe fallback. To use a live OpenAI-compatible backend, set the variables above.

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

## What Glytch does not do

Glytch is a workshop-safe simulation. It does not perform real-world side effects.

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
