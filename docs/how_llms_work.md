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

# How AI Workflows Work (Simple)

## The key idea

A single AI answer and a controlled AI workflow are not the same thing.

Glytch helps learners see the difference.

---

## Prompt baseline

At Level 1, a user asks for help and gets one draft.

```text
Ask -> answer -> human decides what to do next
```

Useful for low-risk tasks, but weak for traceability and verification.

---

## What changes when structure is added

| Layer added | Why it matters |
|---|---|
| clearer instructions | reduces ambiguity |
| bounded tool use | gives checkable intermediate outputs |
| evidence grounding | ties claims to known material |
| critique and revision | improves weak first drafts |
| loop controls | prevents runaway processing |
| orchestration gates | adds review points before merge |

---

## What "workflow detail" means

Workflow detail is a readable trace of who did what and in which order.

It is not an extra question for the user to answer.

It helps learners inspect process, not just outcome.

---

## Why evidence matters

Without evidence, polished wording can still hide mistakes.

With evidence, the same claim can be checked against supplied facts.

```text
Claim without evidence: sounds right
Claim with evidence: can be reviewed
```

---

## Why human review still matters

Even with higher levels, AI can:

- misread context
- overstate confidence
- skip important nuance
- produce incomplete reasoning

Human judgement remains the final safety layer.

---

## Lowest safe level principle

Higher automation is not automatically better.

The right choice is the lowest level that safely handles the task with clear review checkpoints.

---

## FAQ

### Is Level 8 always best?

No. It adds structure and control, but may be unnecessary for simple tasks.

### Is a merged Level 8 result always correct?

No. Merge status is still a simulated workflow outcome that needs human review.

### Does better wording mean better truth?

No. Fluency is not proof.

### Should students use AI for everything?

No. AI should support learning, not replace thinking.

---

<p align="center">
  <a href="../README.md">Home</a> •
  <a href="first_lesson_walkthrough.md">First Lesson Walkthrough</a> •
  <a href="teacher_guide.md">Teacher Guide</a> •
  <a href="student_worksheet.md">Student Worksheet</a> •
  <a href="architecture.md">Architecture</a> •
  <a href="how_llms_work.md">How AI Workflows Work</a>
</p>
