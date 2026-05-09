Glytch helps people understand AI beyond the chat box.

![Glytch logo](assets/glytch-logo.svg)

## Workshop Guide

This guide explains the purpose and flow of the Glytch workshop.

The workshop uses one set of scenario use cases across eight levels so participants can compare what changes as AI support becomes more structured and reviewable.

Reference scenarios: `examples/SCENARIO_USE_CASES.md`.

## Workshop objective

Participants should be able to:
- Explain what changes from Levels 1 through 8.
- Identify when a lower-complexity approach is sufficient.
- Recognize trade-offs in quality, reliability, and effort.
- Choose the lowest safe level of AI support for a real task.

## Level summary

1. **Level 1**: simple AI response.
2. **Level 2**: instruction-led response.
3. **Level 3**: response with tools and checks.
4. **Level 4**: response grounded in evidence.
5. **Level 5**: structured multi-step support.
6. **Level 6**: draft, review, then improve.
7. **Level 7**: bounded workflow with clear limits.
8. **Level 8**: orchestrated workflow with explicit review points.

## Suggested session structure

- Introduction and setup: 20 minutes
- Levels 1 to 4: 60 minutes
- Levels 5 to 8: 60 minutes
- Debrief and discussion: 30 to 60 minutes

Total: approximately 2.5 to 4 hours.

## Audience

Appropriate for:
- Students learning practical AI literacy.
- Individual builders learning workflow trade-offs.
- Teams comparing safe ways to use AI support.

Prerequisites: basic Python and web app familiarity.

## Quick start

```bash
export OPENAI_API_KEY="your_key_here"
python app.py
```

Then open <http://127.0.0.1:8000> and run through Levels 1 to 8.

## Using Glytch in schools

### Why this matters for schools

Schools need AI literacy that goes beyond asking questions in a chat box.

Glytch gives pupils, teachers and school leaders a safe way to see how AI-supported work changes when structure, evidence, checks and review points are added.

Glytch is not about encouraging pupils to outsource thinking. It helps people understand, question and check AI-supported work.

### Who the school workshop is for

The school workshop can be used with:
- teachers
- teaching assistants
- pupils
- sixth form students
- digital leads
- senior leadership teams
- governors
- careers and employability teams
- school support/admin teams

The same demo can be run at different depths depending on the audience.

### Learning outcomes

After a Glytch school workshop, participants should be able to explain:
- the difference between asking AI a question and using AI in a structured workflow
- why AI outputs need checking
- why evidence and source material matter
- where human review is needed
- why more automation is not always better
- what “lowest safe level” means
- how to compare simple prompting with checked and reviewable AI-supported work

### School-safe principles

For school workshops:
- Do not enter personal pupil data.
- Do not enter sensitive school data.
- Do not treat AI answers as automatically correct.
- A human should check outputs before they are used.
- AI should support learning, not replace thinking.
- The demo is simulated and workshop-safe.
- No real emails are sent.
- No files are changed.
- No real-world actions are taken.

Schools should follow their own policies and relevant safeguarding, data protection and AI guidance.

### Suggested 45–60 minute school workshop

- **0–5 mins**: Introduce the idea — AI beyond the chat box.
- **5–10 mins**: Ask what people currently use AI for.
- **10–20 mins**: Run Level 1 and discuss simple prompting.
- **20–30 mins**: Run Level 3 and discuss tools/checks.
- **30–40 mins**: Run Level 4 or Level 6 and discuss evidence/review.
- **40–50 mins**: Run Level 8 and discuss orchestration, limits and human judgement.
- **50–60 mins**: Reflection — when should we keep AI simple, and when do we need more control?

### Teacher discussion questions

- What changed between Level 1 and Level 3?
- Where could the AI make a mistake?
- What evidence would we need before trusting this?
- What should a person check?
- Which level is enough for this task?
- Where would using AI be inappropriate?
- How would we explain this to pupils?

### Pupil reflection questions

- Did the AI explain its work?
- What would you check before using the answer?
- What information did the AI need?
- What parts should still be your own thinking?
- When is AI helpful?
- When could AI make learning worse?
- What is the difference between help and copying?

### Example school scenarios

Examples that work well in Glytch:
- planning a revision timetable
- checking a paragraph for clarity
- creating quiz questions from teacher-provided notes
- comparing a simple answer with an evidence-based answer
- planning a careers research task
- preparing questions for a debate
- improving a draft explanation
- planning a safe school club activity

Keep all examples generic and avoid real pupil data.

### Suggested wording for a school leader

Glytch helps us build practical AI literacy safely. It shows staff and pupils how AI can move from simple answers into structured, checked and reviewable work. The aim is not to replace judgement, but to help people understand where judgement, evidence and human review still matter.

### What Glytch is not

Glytch is:
- not a homework machine
- not a replacement teacher
- not a safeguarding system
- not a production automation tool
- not tied to one AI company
- not a reason to skip human review

### Optional school workshop structure

**Short version: 20 minutes**
- show Level 1
- show Level 3
- discuss what changed

**Standard version: 45–60 minutes**
- use the main session plan

**Extended version: 90 minutes**
- include pupil reflection, group discussion and scenario design
