# Improvement Suggestions

This document captures practical next steps to improve this project's reliability, safety, and usability.

## Completed in this iteration

1. Replaced calculator `eval` execution with a safe `ast`-based evaluator and added malformed/div-by-zero/large-input tests.
2. Added explicit OpenAI client failure handling with structured `AIClientError` responses.
3. Added a `POST /api/run` endpoint and improved API error/status mapping with request IDs.
4. Expanded typing discipline in touched modules and added broader tests for levels/API/client failure paths.
5. Added `.env.example` and a single `make test` entrypoint for local verification consistency.
6. Added baseline observability with structured request logs, timing, selected level, status, and request IDs.

## New suggestions (next wave)

## 1) Add real static type checking in CI
- Add `mypy` configuration (strict for `src/`, lenient for tests at first).
- Gate pull requests on `mypy` + `pytest` in CI.
- Add stub packages where needed for `http.server` interactions.

## 2) Introduce request validation objects
- For `POST /api/run`, validate payload via a small schema layer (e.g., dataclass validator or `pydantic`).
- Return machine-readable validation errors (`field`, `message`, `code`) for client UX.

## 3) Harden calculator resource limits
- Add max AST depth / max exponent size limits to prevent expensive arithmetic operations.
- Add fuzz tests against pathological arithmetic payloads.

## 4) Add API integration tests with a live test server
- Start the HTTP server in-process during tests and assert full request/response behavior.
- Cover `/api/levels`, `/api/run/<level>`, and `POST /api/run` with invalid and valid payloads.

## 5) Add architecture and boundaries docs
- Add a one-page architecture diagram showing frontend ↔ API ↔ level runner ↔ tool layer ↔ model API.
- Document trust boundaries and which components handle untrusted input.

## 6) Add per-level limitations and expected behavior docs
- For each level README, add a short "What this level does not solve" section.
- Include one failure example and one success example per level.

## 7) Add lightweight metrics hooks
- Track success/error counters per endpoint and level.
- Add a simple `/api/health` + `/api/metrics` endpoint (even if text-only) for local debugging.

## 8) Improve developer experience
- Add a `make run` target and `make lint` target.
- Add a concise troubleshooting section in README with common errors and fixes.
