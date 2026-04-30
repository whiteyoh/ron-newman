# Improvement Suggestions

This document captures practical next steps to improve this project's reliability, safety, and usability.

## 1) Remove `eval` from the calculator tool
- `src/tools.py` currently evaluates expressions with `eval`, even with restricted builtins.
- Replace it with a safe expression parser (for example `ast.parse` with strict node allowlisting) or a small math expression library.
- Add tests for edge cases like power operator use, malformed expressions, division by zero, and very large inputs.

## 2) Add robust error handling for OpenAI API calls
- `src/ai_client.py` uses `urllib` directly and assumes a successful response shape.
- Handle common failure modes explicitly:
  - Non-2xx HTTP status codes
  - Timeouts and connection errors
  - Missing/changed response fields
- Return structured errors to callers so `app.py` can map failures to clean API responses.

## 3) Improve API endpoint design and status codes
- `app.py` uses GET for `/api/run/<level>` even though it triggers model execution.
- Consider switching execution to POST (`/api/run`) with JSON payload `{ "level": n }`.
- Return clear status codes:
  - 400 for bad input
  - 503 when AI client is unavailable (missing key)
  - 500 for internal errors

## 4) Add type hints and static checks across modules
- Several modules have partial typing; tighten all public functions.
- Add a static checker (e.g., `mypy` or `pyright`) and enforce it in CI.
- This will reduce runtime surprises, especially around JSON payload handling.

## 5) Expand test coverage beyond unit utility functions
- Current tests focus on tools and one prompt utility.
- Add tests for:
  - `run_level` behavior across all levels
  - API handler behavior for `/api/levels` and `/api/run/*`
  - AI client failure-path behavior with mocked HTTP responses

## 6) Add developer onboarding + quickstart consistency checks
- Add a short "local setup" section with exact commands and expected output.
- Include `.env.example` documenting `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `OPENAI_MODEL`.
- Add a single `make test` or `just test` entrypoint for consistent local verification.

## 7) Improve observability
- Add structured logging for incoming requests, selected level, execution time, and errors.
- Add request IDs in responses for easier debugging.
- Avoid logging secrets or user prompt content by default.

## 8) Optional: package polish for educational use
- Add architecture diagram(s) showing the flow among frontend, app server, level runner, tools, and model API.
- Add a short "limitations" section for each level so readers know what each stage intentionally does *not* solve.
