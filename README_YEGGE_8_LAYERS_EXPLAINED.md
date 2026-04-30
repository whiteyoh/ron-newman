# Yegge’s 8 Layers of AI — A Beginner-Friendly Guide

If you’re new to AI systems, think of **Yegge’s 8 layers** like levels in a game:

- You start with a model that just predicts text.
- Then you gradually add instructions, tools, memory, planning, and teamwork.
- By Layer 8, the system can improve itself (safely) over time.

This guide explains each layer in plain language with practical workshop context.

---

## Why these 8 layers matter

Most teams ask:

- “Why does this AI answer feel unreliable?”
- “When should we add tools or retrieval?”
- “Do we really need agents?”

The 8-layer model helps answer those questions by showing a **step-by-step maturity path** from basic prompting to robust, production-friendly workflows.

---

## The 8 layers in simple terms

## 1) Autocomplete

The model continues text based on patterns.

- **Good at:** fluent language.
- **Weak at:** consistency and factual reliability.
- **Analogy:** a smart sentence finisher.

## 2) Instruction Following

You give clearer rules (tone, format, constraints), and it follows them better.

- **Good at:** structured responses.
- **Weak at:** still can invent facts.
- **Analogy:** an intern who follows a detailed checklist.

## 3) Tool Use

The model can call tools (calculator, policy checker, database lookup).

- **Good at:** accuracy on tool-friendly tasks.
- **Weak at:** tool orchestration can get messy.
- **Analogy:** an intern who can use verified systems, not just memory.

## 4) Retrieval + Grounding

The model is given relevant documents and asked to answer from them.

- **Good at:** reducing hallucinations.
- **Weak at:** depends on document quality and retrieval logic.
- **Analogy:** answering with an open-book policy manual.

## 5) Multi-step Reasoning

The system breaks work into stages (plan → execute → synthesize).

- **Good at:** complex tasks.
- **Weak at:** more latency and complexity.
- **Analogy:** solving a problem with a step-by-step worksheet.

## 6) Agentic Loop

The system iterates: observe, plan, act, check, repeat until done.

- **Good at:** handling uncertainty and difficult tasks.
- **Weak at:** risk of loops if stop conditions are poor.
- **Analogy:** a worker who revises drafts until quality criteria are met.

## 7) Multi-agent Collaboration

Multiple specialized agents collaborate (researcher, writer, critic).

- **Good at:** higher quality through specialization.
- **Weak at:** coordination overhead and cost.
- **Analogy:** a small project team with defined roles.

## 8) Self-improving Workflow

The system reviews outcomes, learns from feedback, and updates prompts/rules/workflows with guardrails.

- **Good at:** continuous improvement.
- **Weak at:** needs strong governance and safety boundaries.
- **Analogy:** a team that runs retrospectives and upgrades its process each week.

---

## Quick mental model

- **Layers 1–2:** Better prompting.
- **Layers 3–4:** Better truth via tools and grounding.
- **Layers 5–6:** Better execution via planning and loops.
- **Layers 7–8:** Better system performance via collaboration and feedback.

---

## When to stop climbing

You don’t always need Layer 8.

A smart production strategy is to use the **lowest layer that reliably meets your goals** for quality, cost, and risk.

---

## Workshop tie-in

In this workshop, all layers are demonstrated using one shared scenario:

> Improving customer support response quality for a SaaS product.

That makes it easier to compare trade-offs at each layer:

- Output quality
- Factual reliability
- Latency
- Cost
- Operational risk

