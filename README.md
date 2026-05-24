<p align="center">
  <img src="assets/glytch-readme-banner.png" alt="Glytch banner" width="900"/>
</p>

<p align="center">
  <strong>Helping people understand AI beyond the chat box.</strong>
</p>

<p align="center">
  <a href="README.md">Home</a> • <a href="STEP_BY_STEP.md">Step-by-Step</a> • <a href="docs/first_lesson_walkthrough.md">First Lesson</a> • <a href="docs/teacher_guide.md">Teacher Guide</a> • <a href="docs/student_worksheet.md">Student Worksheet</a> • <a href="docs/architecture.md">Architecture</a> • <a href="docs/how_llms_work.md">How AI Workflows Work</a>
</p>

---

# Glytch

Glytch is a workshop-safe demo for teaching AI judgement in plain language.

It shows how AI support can move from a simple prompt into structured workflow with evidence, checks, review gates, and human decision points.

The goal is not tool-chasing. The goal is better judgement.

Repository: [whiteyoh/glytch](https://github.com/whiteyoh/glytch)

---

## Why Glytch?

Many people only see AI as a chat response.

Glytch makes the hidden process visible:

- what task the AI was asked to do
- where checks happened
- where evidence was used
- where human review is still required
- when complexity helps and when it does not

---

## Core principle

Use the lowest safe level that gets the task done.

Higher levels can add control and traceability, but they can also add overhead.

---

## What you will see

- score panel summaries of behavior and control
- simulation trace for readable run context
- workflow detail that breaks each run into visible steps
- Level 8 taskboard summaries with verifier and approval states

---

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
export OPENAI_API_KEY="your_key_here"
python app.py
```

Open `http://127.0.0.1:8000`.

---

## Documentation map

### Canonical docs

- [Step-by-Step guide](STEP_BY_STEP.md)
- [First lesson walkthrough](docs/first_lesson_walkthrough.md)
- [Teacher guide](docs/teacher_guide.md)
- [Student worksheet](docs/student_worksheet.md)
- [Architecture](docs/architecture.md)
- [How AI workflows work](docs/how_llms_work.md)
- [Edition 1 release gate](docs/edition1_release_gate.md)

### Book

- [Tech I Can: Glytch (manuscript)](docs/tech_i_can_glytch_book.md)
- [Tech I Can: Glytch (PDF)](docs/printable/Tech_I_Can_Glytch_Book.pdf)

### School and workshop pack

- [Glytch for Schools](README_SCHOOLS.md)
- [Facilitator guide](FACILITATOR_GUIDE.md)
- [Student activity sheet](STUDENT_ACTIVITY_SHEET.md)
- [Safe use in schools](SAFE_USE_IN_SCHOOLS.md)
- [Workshop guide](README_WORKSHOP_GUIDE.md)
- [Pilot plan](PILOT_PLAN.md)

### Output interpretation

- [Reading Glytch output](docs/READING_GLYTCH_OUTPUT.md)

### Visual references

- [Architecture flowchart](docs/assets/simple-architecture-flowchart.svg)
- [Level comparison map](docs/assets/level-comparison-map.svg)
- [Human review gate](docs/assets/human-review-gate.svg)

---

## Printables

Generate classroom PDFs:

```bash
pip install reportlab
python tools/pdf/generate_printables.py
python tools/pdf/generate_tech_i_can_glytch_book.py
```

For US Letter:

```bash
python tools/pdf/generate_printables.py letter
```

Generated files are written to `docs/printable/`.

---

## Safety reminder

Glytch is a learning simulation. It does not perform real-world external actions.

Outputs should be treated as draft material that requires human review.

---

## Policy references

See [SECURITY.md](SECURITY.md) and [SAFE_USE_IN_SCHOOLS.md](SAFE_USE_IN_SCHOOLS.md) for safety and policy framing.
