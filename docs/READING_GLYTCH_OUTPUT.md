# Reading Glytch output

After you run a Glytch level, the app shows a few different views of the same run. This guide explains what each part means and what to look for.

## Quick version

- Start with the score panel to understand what kind of run you just saw.
- Read the simulation trace for a plain-English record of the flow.
- Use Agentic Theatre to follow the run step by step.
- If you ran Level 8, check the taskboard for orchestration details.
- Use the lowest useful level for the job; higher is not always better.

## The score panel

The score panel helps you separate three different questions: what the model did, how controlled the workflow was, and how closely the run matches the intended maturity stage.

### Capability score

Capability score describes the kind of AI behavior being demonstrated.

Examples include:
- simple answering
- tool use
- evidence grounding
- planning
- review loops
- orchestration

### Agenticness score

Agenticness score describes how much workflow control surrounds the model.

A higher score usually means more structure, more steps, more checks, and more autonomy inside clear boundaries.

### Yegge alignment score

Yegge alignment score shows how closely the run simulates the matching Yegge-style maturity stage.

This is about workflow maturity, not production autonomy. Some early levels can score well because they accurately represent early-stage AI usage.

| Score | What it tells you |
|---|---|
| Capability | What behavior is being shown |
| Agenticness | How much workflow surrounds it |
| Yegge alignment | How closely it matches the maturity stage |

## The read-only simulation trace

The simulation trace is the text record of what happened during the run. It is not asking you a hidden question, and you do not need to answer anything there.

Use it to check the output in plain English.

If it looks like a question, read it as part of the demo trace, not as something you need to respond to.

## Agentic Theatre

Agentic Theatre turns the same run into a visual sequence.

Each step usually includes:
- actor
- status
- summary
- detail

Common actors:
- human
- agent
- tool
- verifier
- orchestrator

Common statuses:
- pending
- running
- completed
- approved
- blocked
- needs human review
- merged
- failed

| Actor | Meaning |
|---|---|
| Human | The person setting direction or approving work |
| Agent | The AI behavior being demonstrated |
| Tool | A bounded helper such as a calculator or retrieval step |
| Verifier | A check before accepting the result |
| Orchestrator | The Level 8 controller coordinating work |

## Replay

Replay shows the same theatre steps again. It does not rerun the AI.

Use replay when you want to teach or present the flow, or when you want to re-check the order of events.

## Level 8 taskboard

Level 8 includes an extra view because it simulates request-scoped orchestration.

The taskboard tracks:
- taskboard records
- specialist workers
- worker status
- attempts
- output summary
- verifier result
- approval gate
- merge decision
- final status

The taskboard is the most detailed view of a Level 8 run.

| Field | Meaning |
|---|---|
| Worker | The role handling part of the task |
| Task | What that worker was asked to do |
| Status | Where the task ended up |
| Attempt | How many tries were used |
| Output | Short summary of what the worker produced |
| Error | Any issue seen during the simulated run |

## Approval and merge summary

The approval and merge area explains how the run ended:
- verifier result shows whether the output passed checks
- approval required shows whether human approval was part of the flow
- approved for merge shows whether the result was allowed forward
- merge decision shows whether the output was merged or blocked
- final status shows the end state of the run

Plain-English examples:
- “Merged” means the simulated checks passed.
- “Needs human review” means the run should not be treated as complete.
- “Blocked” means the verifier or approval gate stopped the merge.

## What to take away by level

| Levels | Main idea |
|---|---|
| 1–2 | Asking and guiding |
| 3–4 | Tools and evidence |
| 5–6 | Planning and improving |
| 7 | Controlled agent loops and coordination pressure |
| 8 | Orchestration with taskboard, verifier and approval gate |

Lower levels are not worse. They are often the right choice.

The goal is to use the lowest useful level for the job.

## How to read a result safely

- What level did I run?
- What behavior was demonstrated?
- Was evidence or a tool used?
- Was there a verification step?
- Did anything need human review?
- Would a lower level have been enough?

## What Glytch is not doing

Glytch does not:
- execute real shell commands
- write real files
- create GitHub changes
- run background jobs
- perform production orchestration
- remove the need for human judgment

## Final takeaway

Glytch is there to make AI maturity visible. The output is not just an answer; it is a guided view of how the answer was produced, checked, and controlled.
