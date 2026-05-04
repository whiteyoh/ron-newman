Glytch has two lenses: AI capability patterns and agentic workflow maturity.

![Glytch logo](assets/glytch-logo.svg)

## Glytch Workshop Repository

8-level Glytch workshop demo with a stdlib Python API and static frontend.


## Reading the output

New to Glytch? Start with [Reading Glytch output](docs/READING_GLYTCH_OUTPUT.md). It explains the scores, trace, Agentic Theatre, replay, and Level 8 taskboard.

## Architecture

Architecture diagram generation lives in [`architecture/`](architecture/README.md). The diagrams are generated from `scripts/generate_architecture_diagrams.py` and describe the workshop-safe flow for each Glytch level.

## Local development

### Prerequisites
- Python 3.11+

### Environment
```bash
export OPENAI_API_KEY="your_api_key_here"   # optional for demo fallback
export OPENAI_MODEL="gpt-4.1-mini"
export OPENAI_BASE_URL="https://api.openai.com/v1"
```

### Install dev dependencies
```bash
make install-dev
```

### Run quality checks
```bash
make check
```

### Run app
```bash
make run
```
Open <http://127.0.0.1:8000>.

## Pre-merge checks

Pull requests should pass the GitHub Actions workflow `pre-merge-checks`.

- `python-checks` runs `make check` (format, lint, type checks, tests) on Python 3.11 and 3.12.
- `smoke-test` starts the app locally and verifies health endpoints, API endpoints, and frontend module serving paths.
- `dependency-audit` runs `pip-audit` against runtime and dev requirements.
- `secret-scan` runs Gitleaks to detect accidentally committed secrets.

Local equivalents:

```bash
make check
bash scripts/smoke_test.sh
pip-audit -r requirements.txt -r requirements-dev.txt
```

## API endpoints
- `GET /healthz` -> `{ "status": "ok" }`
- `GET /api/levels`
- `GET /api/use-cases`
- `POST /api/run` with JSON body like `{ "level": 1 }`

If `OPENAI_API_KEY` is missing, `/api/run` returns a graceful non-crashing demo response.

## Deployment (Render)
- Build: `pip install -r requirements.txt`
- Start: `python app.py`
- Health check path: `/healthz`
- Keep `OPENAI_API_KEY` in Render env vars.

## Troubleshooting
- **Missing `OPENAI_API_KEY`**: expected in local demo mode; API returns fallback lines.
- **Quota / upstream errors**: API returns structured errors with `request_id`, `error`, and `code`.

## 2026-05 agenticness implementation update
- Level 3: upgraded to model-selected tool action with JSON action choice and visible tool trace.
- Level 4: upgraded with evidence source labels, sufficiency check, and answer support verifier.
- Level 5: upgraded to plan-execute-verify with conditional single revision.
- Level 6: upgraded to bounded critique loop (score gate, threshold, max revisions).
- Level 7: upgraded with explicit AgentPolicy, action budget visibility, tool-error counting, final verifier gate, and structured run summary.
- Level 8: upgraded to mini-orchestrator abstraction in `src/orchestrator.py` with planner/researcher/writer/critic workers plus verifier and merger, running in safe parallel mode with fallback.
- Added Yegge fields per level in `AGENTICNESS`: `closest_yegge_stage`, `yegge_alignment_score`, and `yegge_alignment_explanation`.
- Limitation: this remains workshop-safe and is a workshop-safe simulation, not a production system (no external side effects, no deployment automation, limited policy depth).



## Why Yegge adoption increased by one point
- Before: Level 8 demonstrated parallel role orchestration with verifier and merger outputs.
- After: Level 8 now runs a request-scoped taskboard-based orchestrator simulation with explicit task state, worker lifecycle transitions, retry handling, audit trail, verifier gate, approval gate, and merge policy.
- Score change: Yegge alignment for Level 8 increased from 8 to 9 (exactly +1) because these orchestration mechanics now exist in implementation.
- Still missing for production-level orchestration: persistent storage, real worker processes, repository side effects, deployment integration, and multi-run memory.

## Why Levels 1–6 were uplifted to 7/10
Levels 1–6 are no longer raw capability-only demos. Each now runs inside a workshop-safe agentic wrapper with an objective, policy, allowed actions, verification, stop condition, approval gate, audit trail, and final verdict. The original capability theme is preserved per level (supervised completion, permissioned instruction following, tool-action loop, grounded research, CLI-style single-agent planning run, and bounded evaluator loop). A 7/10 score here reflects bounded and inspectable agent workflow mechanics, not production-grade autonomy. The app still avoids real side effects (no shell execution, file writes, GitHub writes, or background jobs).

## WOW but honest update
Glytch now includes Agentic Theatre, a maturity ladder, score explanations, and a Level 8 taskboard dashboard. It remains a workshop-safe simulated orchestration environment with human approval gates and no external side effects.

## Yegge alignment update
This demo now presents **capability vs Yegge stage** with high-fidelity workshop simulations, explicit human approval gates, and clear non-production limits.


## Workshop simulation fidelity updates

All 8 levels now include a Yegge workflow simulation object. These are high-fidelity workshop simulations, not production autonomous agents. Level 8 taskboard uses real orchestrator run state and theatre/replay views now derive from actual run data.


## Rate limiting note

Rate limiting is intentionally lightweight and in-memory for this workshop/demo app. It is not a distributed production rate limiter.
