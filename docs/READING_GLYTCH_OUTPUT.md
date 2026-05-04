# Reading Glytch output

After you run a Glytch level, the app shows several views of the same run. This guide explains what each part means and what to look for.

## How to use this guide

Start with the score panel, then read the trace. If you want to understand the run visually, use Agentic Theatre. If you ran Level 8, use the taskboard to see how the simulated orchestration ended.

## Quick version

- Start with the score panel.
- Read the simulation trace.
- Use Agentic Theatre for the step-by-step flow.
- Check the Level 8 taskboard when orchestration is shown.
- Use the lowest useful level; higher is not always better.

## The score panel

The score panel separates what behavior was shown from how much workflow control surrounded it.

| Score | What it tells you |
|---|---|
| Capability | What AI behaviour is being shown |
| Agenticness | How much workflow surrounds it |
| Yegge alignment | How closely it matches the maturity stage |

A score of 10 does **not** mean a level is more autonomous or more powerful.  
For example, Level 1 can score highly when it is a clean prompt-only baseline with a clear human decision point.

## The read-only simulation trace

The simulation trace is a text record of what happened during the run. It is not asking the user a hidden question, and there is nothing to answer in the trace.

If it looks like a question, read it as part of the demo trace, not as something you need to respond to.

## Agentic Theatre

Agentic Theatre presents the run as a visual step-by-step sequence.

Each step includes:
- actor
- status
- summary
- detail

| Actor | Meaning |
|---|---|
| Human | The person setting direction or approving work |
| Agent | The AI behaviour being demonstrated |
| Tool | A bounded helper such as calculator or retrieval |
| Verifier | A check before accepting the result |
| Orchestrator | The Level 8 controller coordinating work |

## Replay

Replay shows the same theatre steps again. It does not rerun the AI.

It is useful for teaching or presenting the flow.

## Level 8 taskboard

The Level 8 taskboard records specialist worker activity and how orchestration finished.

It shows:
- taskboard records
- specialist workers
- status
- attempts
- output summary
- verifier result
- approval gate
- merge decision
- final status

| Field | Meaning |
|---|---|
| Worker | The role handling part of the task |
| Task | What that worker was asked to do |
| Status | Where the task ended up |
| Attempt | How many tries were used |
| Output | Short summary of what the worker produced |
| Error | Any issue seen during the simulated run |

## Approval and merge summary

This summary explains the final control points:
- verifier result
- approval required
- approved for merge
- merge decision
- final status

Plain-English examples:
- “Merged” means the simulated checks passed.
- “Needs human review” means the run should not be treated as complete.
- “Blocked” means the verifier or approval gate stopped the merge.

## Common misreadings

- The trace is not asking you to answer.
- Higher level does not always mean better.
- Merged does not mean production-ready.
- Needs human review is a useful outcome, not a failure.
- Replay does not rerun the AI.

## What to take away by level

| Levels | Main idea |
|---|---|
| 1–2 | Asking and guiding |
| 3–4 | Tools and evidence |
| 5–6 | Planning and improving |
| 7 | Controlled agent loops and coordination pressure |
| 8 | Orchestration with taskboard, verifier and approval gate |

## What Glytch is not doing

Glytch does not:
- execute real shell commands
- write real files
- create GitHub changes
- run background jobs
- perform production orchestration
- remove the need for human judgement

## Final takeaway

Glytch is there to make AI maturity visible. The output is not just an answer; it is a guided view of how the answer was produced, checked and controlled.
