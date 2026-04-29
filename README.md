# Yegge AI Competence Ladder Demo

This repository was rebuilt as a focused educational demo for **8 levels of AI competence** inspired by Steve Yegge's framing.

## What this project does

- Runs a tiny local web app.
- Lets you execute 8 staged examples (one per competence level).
- Streams human-readable output to an HTML dashboard.
- Keeps each level isolated in its own folder with setup/install/usage docs.

## Quick start

```bash
python app.py
```

Open: <http://127.0.0.1:8000>

## Project layout

- `app.py` — lightweight web server + JSON endpoints
- `web/index.html` — dashboard UI
- `web/main.js` — runner + renderer for demo output
- `examples/level1` ... `examples/level8` — one folder per level, each with a clear README

## Notes

This is intentionally pedagogical, not benchmark science. The point is to provide
clear, demonstrable behavior at each level that a human can watch and understand.
