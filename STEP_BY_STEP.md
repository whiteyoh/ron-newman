# Glytch Step-by-Step Guide

**Move from prompt-only AI use to controlled, reviewable workflow thinking.**

This is the fastest full path through Glytch for a classroom, staff briefing, or workshop.

---

## 1. Set up Glytch

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

If your session uses live model responses, set your key:

```bash
export OPENAI_API_KEY="your_key_here"
```

---

## 2. Start the workshop-safe demo

```bash
python app.py
```

Open `http://127.0.0.1:8000`.

---

## 3. Run Level 1 (prompt baseline)

Use a simple scenario such as:

- planning a revision timetable
- improving a paragraph for clarity
- building questions from teacher notes

Look for:

- quick draft quality
- missing assumptions
- what still needs checking

---

## 4. Run Level 3 (tool and checks)

Run the same scenario at Level 3.

Compare with Level 1:

- which parts became easier to verify
- what still needs human judgement
- whether added structure helped or overcomplicated the task

---

## 5. Run Level 4 or Level 6 (evidence and revision)

Use Level 4 to discuss grounding to supplied facts.

Use Level 6 to discuss draft-critique-revise flow.

Capture evidence:

- what source material was used
- what changed after critique
- what claims still need human validation

---

## 6. Run Level 8 (orchestration)

Use the same scenario once at Level 8.

Inspect:

- worker task split
- verifier status
- approval gate
- merge decision
- final status

Core lesson: more structure can increase control, but it also increases responsibility.

---

## 7. Read the outputs clearly

Use these views in order:

1. score panel
2. simulation trace
3. workflow detail
4. taskboard (Level 8)

Guide: [`docs/READING_GLYTCH_OUTPUT.md`](docs/READING_GLYTCH_OUTPUT.md)

---

## 8. Capture reflection before closing

Ask participants to answer:

- When was Level 1 enough?
- When was evidence required?
- Where did human review change the outcome?
- Which level was the lowest safe level for this scenario?

---

## 9. Use the classroom pack and printables

Classroom pack:

- [`docs/teacher_guide.md`](docs/teacher_guide.md)
- [`docs/student_worksheet.md`](docs/student_worksheet.md)
- [`docs/first_lesson_walkthrough.md`](docs/first_lesson_walkthrough.md)
- [`docs/tech_i_can_glytch_book.md`](docs/tech_i_can_glytch_book.md)

Generate printables:

```bash
pip install reportlab
python tools/pdf/generate_printables.py
python tools/pdf/generate_tech_i_can_glytch_book.py
```

Use US Letter if needed:

```bash
python tools/pdf/generate_printables.py letter
```

---

## 10. Next steps

- Repeat the same scenario across multiple levels to build comparison evidence.
- Add one new safe scenario from your setting.
- Run a short pilot and collect before-and-after confidence signals.
