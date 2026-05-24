<p align="center">
  <img src="assets/glytch-logo.svg" alt="Glytch logo" width="640"/>
</p>

<p align="center">
  <a href="../README.md">Home</a> •
  <a href="first_lesson_walkthrough.md">First Lesson Walkthrough</a> •
  <a href="teacher_guide.md">Teacher Guide</a> •
  <a href="student_worksheet.md">Student Worksheet</a> •
  <a href="architecture.md">Architecture</a> •
  <a href="how_llms_work.md">How AI Workflows Work</a>
</p>

---

# Teacher Guide

## Lesson goal

Help learners understand AI beyond the chat box by comparing levels of structure, evidence, and human control.

---

## Before-lesson checklist

- Python environment is ready.
- Demo launches locally with `python app.py`.
- One safe scenario is chosen in advance.
- School-safe rules are visible.
- A fallback screenshot set is available in case connectivity fails.

Quick preflight:

```bash
python -m compileall src tests
python app.py
```

---

## Quick-reference classroom flow

| Section | Suggested timing | Teacher move | Student outcome |
|---|---:|---|---|
| 1. Frame the goal | 5 min | Explain "lowest safe level" | Learners know what to compare |
| 2. Baseline run | 10 min | Run Level 1 and question claims | Learners separate fluency from reliability |
| 3. Add checks | 10 min | Run Level 3 | Learners see structured control |
| 4. Add evidence/revision | 10 min | Run Level 4 or 6 | Learners see quality lift and limits |
| 5. Orchestrate carefully | 10 min | Run Level 8 | Learners see gates and review burden |
| 6. Reflect | 5 min | Exit ticket | Learners justify level choice |

---

## Suggested classroom pacing

### 45-minute version

1. Context and rules (5)
2. Level 1 baseline (10)
3. Level 3 checks (10)
4. Level 4 or 6 (10)
5. Reflection (10)

### 90-minute version

1. Context and rules (10)
2. Levels 1 to 4 comparison (25)
3. Levels 6 and 8 comparison (25)
4. Group scenario design (20)
5. Debrief and action planning (10)

---

## Facilitation tips

- Keep one scenario fixed across levels.
- Ask for evidence, not opinions, when comparing outputs.
- Avoid treating Level 8 as "best" by default.
- Keep reminding that AI support should not replace thinking.
- Use workflow detail replay to slow down and inspect process.

---

## Common misconceptions and Q&A guidance

### Misconception: "If it sounds confident, it is probably right."

Teacher response: confidence is style, not proof.

### Misconception: "Better prompts solve everything."

Teacher response: some tasks need evidence, checks, and explicit review gates.

### Misconception: "Higher level means better answer."

Teacher response: higher level means more workflow structure; usefulness depends on task risk.

### Misconception: "If it merged, we can trust it completely."

Teacher response: merge status in Glytch still requires human judgement before real-world use.

---

## Teacher gotchas

| Gotcha | What it means | What to do |
|---|---|---|
| Learners jump to tool debate | Session focus drifts to vendor names | Bring it back to task, evidence, checks |
| Level 8 feels "too much" | Complexity may exceed task need | Use it as a lesson in overengineering |
| Learners treat trace as an instruction | They think they must answer trace text | Clarify trace is run history only |
| AI wording sounds polished | Learners over-trust style | Ask them to name concrete verification steps |

---

## Example teacher script

- "Today we are not testing which tool is coolest; we are testing which level is safest for this task."
- "We are looking for where checks happen, not just what answer appears."
- "If we cannot explain why we trust it, we should not use it yet."

---

## Printable materials

Markdown sources are in `docs/` and printable PDFs are in `docs/printable/`.

To regenerate printables:

```bash
pip install reportlab
python tools/pdf/generate_printables.py
python tools/pdf/generate_tech_i_can_glytch_book.py
```

For US Letter output:

```bash
python tools/pdf/generate_printables.py letter
```

---

<p align="center">
  <a href="../README.md">Home</a> •
  <a href="first_lesson_walkthrough.md">First Lesson Walkthrough</a> •
  <a href="teacher_guide.md">Teacher Guide</a> •
  <a href="student_worksheet.md">Student Worksheet</a> •
  <a href="architecture.md">Architecture</a> •
  <a href="how_llms_work.md">How AI Workflows Work</a>
</p>
