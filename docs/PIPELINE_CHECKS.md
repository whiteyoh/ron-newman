# Pipeline checks

This repository uses GitHub Actions pre-merge checks in `.github/workflows/pre-merge-checks.yml`.

## Jobs and purpose

## 1) `python-checks`
- Runs on PRs and pushes to `main`.
- Uses a Python matrix (`3.11`, `3.12`).
- Installs dev dependencies with `make install-dev`.
- Runs `make check` (`ruff format --check`, `ruff check`, `mypy`, `pytest`).

Why it exists:
- Keeps style, typing, and tests consistently enforced before merge.

## 2) `smoke-test`
- Runs after `python-checks` succeeds.
- Uses Python `3.12`.
- Runs `bash scripts/smoke_test.sh`.
- Validates app startup and key endpoints:
  - `/`
  - `/healthz`
  - `/api/levels`
  - `/api/use-cases`
  - `/api/agentic-maturity`
  - `/main.js`
  - all `web/js/*.js` served as `/js/<file>`
- Explicitly unsets `OPENAI_API_KEY` to verify safe no-key behavior.
- Valid no-key `/api/run` request must return HTTP 200 and include an "AI backend not configured" message.
- Invalid `/api/run` payload (`{"level":"bad"}`) must return HTTP 400 and include both `invalid_field` and `request_id`.

Why it exists:
- Protects the runnable workshop demo behavior and static module serving.

## 3) `dependency-audit`
- Uses Python `3.12`.
- Installs and runs `pip-audit` against `requirements.txt` and `requirements-dev.txt`.

Why it exists:
- Provides lightweight vulnerability scanning for known Python dependency advisories.

## 4) `secret-scan`
- Runs Gitleaks via `gitleaks/gitleaks-action@v2`.

Why it exists:
- Prevents accidental secret commits.

## Run equivalent checks locally

```bash
make install-dev
make check
bash scripts/smoke_test.sh
python -m pip install pip-audit
pip-audit -r requirements.txt -r requirements-dev.txt
```

## Troubleshooting failures

- `python-checks` failed:
  - Run `make check` locally and fix format/lint/type/test output.
- `smoke-test` failed:
  - Run `bash scripts/smoke_test.sh` locally.
  - Confirm port `8000` is free.
  - The script prints server log output for request failures.
- `dependency-audit` failed:
  - Review advisories and either upgrade/pin dependencies or document accepted risk.
- `secret-scan` failed:
  - Remove leaked secret material and rotate any exposed credential.

## Expected API behavior in smoke tests

- Missing `OPENAI_API_KEY`:
  - `/api/run` should return a safe, non-crashing workshop response and include a message like `AI backend not configured`.
- Invalid API payload:
  - `/api/run` with malformed schema (for example `{"level":"bad"}`) should return HTTP 400 with structured fields including `request_id` and `code=invalid_field`.

## Branch protection recommendation

For `main`, configure GitHub branch protection to:
- Require a pull request before merge.
- Require status checks:
  - `python-checks`
  - `smoke-test`
  - `dependency-audit` (if kept enabled)
  - `secret-scan` (if kept enabled)
- Block direct pushes to `main`.
- Require at least one approving review.
