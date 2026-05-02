![Glytch logo](assets/glytch-logo.svg)

## Glytch Workshop Repository

This repository contains an 8-level workshop that demonstrates how application behavior changes as system capability increases from simple prompting to evaluated workflows.

The examples are aligned to explicit scenario use cases so each level has a clear purpose and measurable output shape.

## Start Here

- **Workshop guide:** [README_WORKSHOP_GUIDE.md](README_WORKSHOP_GUIDE.md)
- **8-layer model overview:** [README_8_LAYER_MODEL.md](README_8_LAYER_MODEL.md)
- **Scenario use cases (Given / When / Then):** [examples/SCENARIO_USE_CASES.md](examples/SCENARIO_USE_CASES.md)
- **Level-to-stage alignment details:** [examples/STAGES_ALIGNMENT_README.md](examples/STAGES_ALIGNMENT_README.md)

## Level READMEs

1. [Level 1 README](examples/level1/README.md)
2. [Level 2 README](examples/level2/README.md)
3. [Level 3 README](examples/level3/README.md)
4. [Level 4 README](examples/level4/README.md)
5. [Level 5 README](examples/level5/README.md)
6. [Level 6 README](examples/level6/README.md)
7. [Level 7 README](examples/level7/README.md)
8. [Level 8 README](examples/level8/README.md)

## Local Setup

### Prerequisites
- Python 3.11+
- pip

### Environment
```bash
export OPENAI_API_KEY="your_api_key_here"
export OPENAI_MODEL="gpt-4o-mini"               # optional
export OPENAI_BASE_URL="https://api.openai.com/v1" # optional
```

### Install and test
```bash
python -m pip install --upgrade pip
python -m pip install pytest
python -m pytest -q
```

### Run
```bash
python app.py
```
Open <http://127.0.0.1:8000>.

## Deployment (Render)

A `render.yaml` blueprint is included.

1. Push this repository to GitHub.
2. In Render, create a new **Blueprint** service from the repo.
3. Set `OPENAI_API_KEY` in Render environment variables.
4. Deploy.

Default build/start commands:
- Build: `pip install -r requirements.txt`
- Start: `python app.py`

## Notes on production readiness

Current baseline:
- Uses `PORT` for cloud compatibility.
- Returns structured JSON errors with request IDs.
- Includes timeout and upstream error handling in the OpenAI client.
- Includes API-level tests.

Recommended next steps:
- Add request rate limiting for `/api/run`.
- Add auth if exposed beyond workshop/demo usage.
- Pin dependency versions in `requirements.txt`.
- Add a dedicated `/healthz` endpoint if infra health should be separated from business checks.
