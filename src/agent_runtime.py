from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from src.types import AIChatClient

ALLOWED_ACTIONS = {"research", "calculate", "draft", "finish"}


@dataclass
class AgentDecision:
    action: str
    input: str
    reason: str
    final: str


@dataclass
class AgentStep:
    iteration: int
    action: str
    reason: str
    tool_input: str
    observation: str


def _safe_draft_decision() -> AgentDecision:
    return AgentDecision(
        action="draft",
        input="Provide a concise best-effort response using prior observations.",
        reason="Fallback after invalid model JSON.",
        final="",
    )


def _parse_decision(raw: str) -> AgentDecision | None:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return None

    if not isinstance(parsed, dict):
        return None

    action = str(parsed.get("action", "")).strip().lower()
    tool_input = str(parsed.get("input", ""))
    reason = str(parsed.get("reason", ""))
    final = str(parsed.get("final", ""))

    return AgentDecision(action=action, input=tool_input, reason=reason, final=final)


def choose_next_action(
    client: AIChatClient, objective: str, trace: list[AgentStep], last_observation: str
) -> AgentDecision:
    trace_lines = [
        (
            f"#{step.iteration} action={step.action} reason={step.reason} "
            f"input={step.tool_input} observation={step.observation}"
        )
        for step in trace
    ]
    prompt = (
        "You are a constrained agent controller. Choose exactly one next action. "
        "Return strict JSON only with schema: "
        '{"action":"research|calculate|draft|finish","input":"string",'
        '"reason":"short human-readable reason",'
        '"final":"string only when action is finish"}. '
        "Do not include markdown or extra keys."
    )
    context = (
        f"Objective: {objective}\n"
        f"Last observation: {last_observation or 'none'}\n"
        f"Current trace:\n" + ("\n".join(trace_lines) if trace_lines else "(empty)")
    )

    raw = client.chat(prompt, context)
    decision = _parse_decision(raw)
    if decision is None:
        correction_prompt = (
            "Your last response was invalid JSON. "
            "Return only valid JSON using this schema exactly: "
            '{"action":"research|calculate|draft|finish","input":"string",'
            '"reason":"short human-readable reason",'
            '"final":"string only when action is finish"}.'
        )
        raw_retry = client.chat(
            correction_prompt, f"Objective: {objective}\nTrace:\n" + "\n".join(trace_lines)
        )
        decision = _parse_decision(raw_retry)

    if decision is None:
        return _safe_draft_decision()

    return decision


def run_constrained_agent_loop(
    client: AIChatClient,
    objective: str,
    retrieve_fn: Callable[[str], str],
    calculate_fn: Callable[[str], str],
    max_iterations: int = 5,
) -> dict[str, Any]:
    trace: list[AgentStep] = []
    last_observation = ""

    for iteration in range(1, max_iterations + 1):
        decision = choose_next_action(client, objective, trace, last_observation)

        if decision.action not in ALLOWED_ACTIONS:
            observation = (
                f"Unknown action '{decision.action}'. Choose one of: "
                "research, calculate, draft, finish."
            )
            trace.append(
                AgentStep(
                    iteration=iteration,
                    action=decision.action,
                    reason=decision.reason,
                    tool_input=decision.input,
                    observation=observation,
                )
            )
            last_observation = observation
            continue

        if decision.action == "finish":
            final_answer = (
                decision.final or decision.input or "Best effort final answer not provided."
            )
            trace.append(
                AgentStep(
                    iteration=iteration,
                    action=decision.action,
                    reason=decision.reason,
                    tool_input=decision.input,
                    observation=f"Final answer selected: {final_answer}",
                )
            )
            return {"trace": trace, "final_answer": final_answer, "stopped_on_finish": True}

        if decision.action == "research":
            observation = retrieve_fn(decision.input)
        elif decision.action == "calculate":
            try:
                observation = calculate_fn(decision.input)
            except Exception as err:  # defensive tool execution
                observation = f"tool error: {err}"
        else:
            observation = client.chat("Draft a concise response for the objective.", decision.input)

        trace.append(
            AgentStep(
                iteration=iteration,
                action=decision.action,
                reason=decision.reason,
                tool_input=decision.input,
                observation=observation,
            )
        )
        last_observation = observation

    best_effort = client.chat(
        "Max iterations reached. Produce a best-effort final answer from the observations.",
        "\n".join(
            [
                (
                    f"#{step.iteration} action={step.action} input={step.tool_input} "
                    f"observation={step.observation}"
                )
                for step in trace
            ]
        ),
    )
    return {"trace": trace, "final_answer": best_effort, "stopped_on_finish": False}
