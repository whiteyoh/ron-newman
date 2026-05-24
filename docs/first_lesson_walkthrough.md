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

# First Lesson Walkthrough

## Goal

Run one complete learning loop: prompt baseline -> added checks -> evidence-aware run -> orchestration comparison -> reflection.

By the end, learners should be able to explain:

- why a fluent answer is not automatically a trustworthy answer
- why evidence and review checkpoints matter
- why the lowest safe level is usually the best starting point

---

## Session setup

- Launch the demo with `python app.py`
- Open `http://127.0.0.1:8000`
- Choose one safe scenario for the whole lesson

Suggested scenario:

```text
Plan a one-week revision timetable for three subjects with realistic breaks.
```

---

## What success looks like

- Learners can identify what changed at each level.
- Learners can point to at least one place where human review is still required.
- Learners can justify why a lower or higher level was appropriate for the task.

### Comparison table

| Stage | What you run | What learners should notice |
|---|---|---|
| Baseline | Level 1 | Fast draft, hidden assumptions, weak traceability |
| Checked | Level 3 | Better structure and check points |
| Grounded or revised | Level 4 or 6 | Evidence links or visible improvement loop |
| Orchestrated | Level 8 | Worker split, gates, and merge decision pressure |

---

## Step 1 - Run Level 1

Prompt learners with these questions:

- What is useful right away?
- What could be wrong?
- What would you check before using this?

Record notes in plain language.

---

## Step 2 - Run Level 3

Keep the same scenario. Ask learners:

- What changed from Level 1?
- Which parts are now easier to verify?
- What is still risky?

---

## Step 3 - Run Level 4 or Level 6

If you pick Level 4, focus on evidence grounding.

If you pick Level 6, focus on critique and revision quality.

Ask learners to locate one concrete improvement and one remaining risk.

---

## Step 4 - Run Level 8

Use this step as a control and responsibility lesson, not a "higher is always better" lesson.

Inspect together:

- taskboard entries
- verifier result
- approval gate
- merge decision
- final status

---

## Step 5 - Use workflow detail for debrief

Open workflow detail and replay the run.

Ask:

- Where did the process become safer?
- Where did complexity increase?
- Which step should always involve a person?

---

## Exit ticket

Each learner completes:

```text
The lowest safe level for this scenario was...
because...
```

And:

```text
One check I would always do before using an AI output is...
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
