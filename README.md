Glytch has two lenses: AI capability patterns and agentic workflow maturity.

![Glytch logo](assets/glytch-logo.svg)

## Glytch Workshop Repository

8-level Glytch workshop demo with a stdlib Python API and static frontend.

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
