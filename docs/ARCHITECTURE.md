# Architecture

- **Frontend (`web/`)**: static HTML/CSS/JS UI for use case selection and level execution.
- **API handler (`app.py`)**: stdlib `ThreadingHTTPServer` exposing `/healthz`, `/api/levels`, `/api/use-cases`, and `/api/run`.
- **Level runner (`src/levels.py`)**: orchestrates the 8-step workshop flow while preserving response shape.
- **Tool layer (`src/tools.py`)**: constrained calculator and local fact retrieval.
- **OpenAI client (`src/ai_client.py`)**: stdlib `urllib` based client with explicit error mapping.

## Trust boundaries

- Browser input is untrusted and validated in `POST /api/run`.
- Request size, content type, JSON schema, and level range are validated.
- Rate limiting is in-memory and demo scoped.
- Upstream error details are truncated to avoid secret leakage.
