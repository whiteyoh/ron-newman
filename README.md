![Glitch logo](assets/glitch-logo.svg)

## Meet Glitch

![Robotic person mascot](assets/robotic-person.svg)

The world is full of advice on how you *should* use AI—what tools to use, why your approach is wrong, and what you should pick instead.

If I’m honest, none of that matters as much as this: understanding the layers of AI, and how **you** can use those principles to change the world around you.

You don’t need to be a genius to start. You just need curiosity:

- Curiosity about how AI works
- Curiosity about how it makes decisions
- Curiosity about how to apply it in real life

Worried you aren’t clever enough?
Wondering where to begin?

Here’s the truth: you *are* clever enough. That’s exactly why this repository is laid out in **8 clear stages**, with practical examples at every step.

This Glitch pack is designed to take your AI understanding to the next level, showing you eight layers of applied AI in a way that’s tangible and useful.

By the end, you’ll have:

- A stronger mental model for how AI systems mature
- A framework to test your own understanding
- A practical way to assess the maturity of AI systems you work with

Good luck—you’ve got this.

---

## Start Here

- **Workshop overview (main guide):** [README_WORKSHOP_FUN.md](README_WORKSHOP_FUN.md)
- **Yegge’s 8 layers explained (beginner-friendly):** [README_YEGGE_8_LAYERS_EXPLAINED.md](README_YEGGE_8_LAYERS_EXPLAINED.md)
- **How examples align to capability stages:** [examples/STAGES_ALIGNMENT_README.md](examples/STAGES_ALIGNMENT_README.md)

---

## The 8 Example Chapters

Follow the climb level-by-level in the shared customer support scenario:

1. [Level 1 README](examples/level1/README.md)
2. [Level 2 README](examples/level2/README.md)
3. [Level 3 README](examples/level3/README.md)
4. [Level 4 README](examples/level4/README.md)
5. [Level 5 README](examples/level5/README.md)
6. [Level 6 README](examples/level6/README.md)
7. [Level 7 README](examples/level7/README.md)
8. [Level 8 README](examples/level8/README.md)


---

## Local Run + OpenAI Token Setup

### 1) Prerequisites
- Python 3.11+ installed
- `pip` available

### 2) Create an OpenAI API token
1. Sign in to the OpenAI platform.
2. Open the API keys page and create a new secret key.
3. Copy the key and store it securely (you will not be able to view the full key again later).

### 3) Configure environment variables
Use your shell profile (`~/.bashrc`, `~/.zshrc`, etc.) or export in your current terminal:

```bash
export OPENAI_API_KEY="your_api_key_here"
export OPENAI_MODEL="gpt-4.1-mini"   # optional override
export OPENAI_BASE_URL="https://api.openai.com/v1"   # optional override
```

### 4) Install test/runtime tooling
```bash
python -m pip install --upgrade pip
python -m pip install pytest
```

### 5) Run checks before starting the app
```bash
python -m pytest -q
```

### 6) Run the app
```bash
python app.py
```
Then open `http://127.0.0.1:8000`.

### 7) What GitHub Actions runs
The CI workflow (`.github/workflows/ci.yml`) runs the same sequence automatically:
1. Checkout code
2. Set up Python
3. Install dependencies
4. Run tests
5. Launch `app.py` and verify `GET /api/levels` responds
6. If `OPENAI_API_KEY` is set in repository secrets, call `GET /api/run/1` and print the model completion line in Actions logs
