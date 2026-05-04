# Pipeline Checks

## 1) Overview

The `pre-merge-checks` pipeline is designed to keep frequent pull requests safe and predictable by:

- preventing regressions before merge,
- validating Python formatting, linting, typing, and tests,
- validating API safety paths (including structured errors),
- validating frontend module serving for ES module paths,
- avoiding real OpenAI calls in CI by running with `OPENAI_API_KEY` unset,
- catching dependency vulnerabilities and accidentally committed secrets.

## 2) Jobs

### `python-checks`

**What it checks**
- Runs `make check` on Python 3.11 and 3.12.
- `make check` includes format check, lint, mypy, and pytest.

**Why it matters**
- This is the primary quality gate and catches the most common regressions early.

**Run locally**
```bash
make install-dev
make check
```

### `smoke-test`

**What it checks**
- Starts the app locally and executes `bash scripts/smoke_test.sh`.
- Verifies health, metadata APIs, static entrypoints, ES module paths, and `/api/run` safety/validation responses.

**Why it matters**
- Confirms the app boots and serves core API/frontend paths as expected in a deterministic CI environment.

**Run locally**
```bash
make install-dev
bash scripts/smoke_test.sh
```

### `dependency-audit`

**What it checks**
- Runs `pip-audit -r requirements.txt -r requirements-dev.txt`.

**Why it matters**
- Surfaces known dependency vulnerabilities before merge.

**Run locally**
```bash
python -m pip install pip-audit
pip-audit -r requirements.txt -r requirements-dev.txt
```

### `secret-scan`

**What it checks**
- Runs Gitleaks to detect committed secrets and high-risk tokens.

**Why it matters**
- Helps prevent credential leaks in repository history.

**Run locally**
- CI uses `gitleaks/gitleaks-action@v2`.
- If needed locally, use Gitleaks CLI with your preferred install method.

## 3) Smoke test behaviour

The smoke test script intentionally validates safe demo behavior:

- `OPENAI_API_KEY` is explicitly unset.
- A valid `/api/run` request returns HTTP 200 and a safe fallback message (`AI backend not configured`) plus structured metadata fields like `backend` and `request_id`.
- Invalid `/api/run` payloads return structured HTTP 400 errors with `request_id`.
- Frontend ES modules under `web/js/*.js` must be reachable from `/js/<filename>`.

## 4) Troubleshooting

- **App fails to start**
  - Check `/tmp/glytch-smoke.log` output from the smoke script.
  - Verify dependencies are installed: `make install-dev`.

- **Port `8000` already in use**
  - Stop the conflicting process and rerun the smoke script.

- **Smoke test cannot reach `/healthz`**
  - Ensure startup did not crash; inspect `/tmp/glytch-smoke.log`.
  - Ensure local firewalls or environment restrictions are not blocking loopback access.

- **`pip-audit` advisory failure**
  - This is expected behavior for a blocking audit gate when vulnerabilities are found.
  - Triage and remediate vulnerable packages or explicitly document accepted risk in PR discussion.

- **Gitleaks failure**
  - Remove committed secrets, rotate compromised credentials, and rerun checks.
  - If a known false positive occurs, tune allowlisting carefully and transparently.

- **`actions/setup-python@v6` / `actions/checkout@v6` compatibility fallback**
  - If runner compatibility issues occur, pin fallback versions:
    - `actions/checkout@v4`
    - `actions/setup-python@v5`

## 5) Branch protection recommendations

For `main`, enable:

- Require a pull request before merging.
- Require status checks to pass:
  - `python-checks`
  - `smoke-test`
  - `dependency-audit` (if enabled as blocking)
  - `secret-scan` (if enabled as blocking)
- Require at least one approving review.
- Block direct pushes to `main`.
- Require branches to be up to date before merge.
