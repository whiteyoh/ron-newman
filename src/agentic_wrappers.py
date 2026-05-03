from __future__ import annotations

from collections.abc import Callable
from typing import Any
from uuid import uuid4

from src.types import AIChatClient

ExecuteActionFn = Callable[[str, dict[str, Any]], tuple[str, str]]


def run_agentic_capability_demo(
    client: AIChatClient,
    level: int,
    objective: str,
    capability_name: str,
    allowed_actions: list[str],
    initial_action: str,
    execute_action_fn: ExecuteActionFn,
    verifier_prompt: str,
    max_iterations: int = 2,
    require_human_approval: bool = True,
) -> dict[str, Any]:
    run_id = f"lvl{level}-{uuid4().hex[:8]}"
    policy = {
        "allowed_actions": allowed_actions,
        "max_iterations": max_iterations,
        "safe_mode": "no side effects",
        "approval_gate": require_human_approval,
    }

    actions: list[str] = []
    observations: list[str] = []
    audit_log: list[str] = [
        f"run_id={run_id}",
        f"capability={capability_name}",
        f"objective={objective}",
    ]

    current_action = initial_action
    final_answer = ""
    stop_condition = "iteration budget reached"

    for iteration in range(1, max_iterations + 1):
        if current_action not in allowed_actions:
            current_action = "finish" if "finish" in allowed_actions else allowed_actions[-1]

        actions.append(current_action)
        answer, observation = execute_action_fn(
            current_action, {"iteration": iteration, "current": final_answer}
        )
        observations.append(observation)
        audit_log.append(f"iteration={iteration} action={current_action} observation={observation}")

        if answer:
            final_answer = answer

        if current_action == "finish":
            stop_condition = "finish action selected"
            break

        if current_action in {"verify_completion", "verify_with_calculator"}:
            current_action = "finish"
        elif current_action in {"revise_completion", "revise_answer"}:
            current_action = "finish"
        elif current_action in {
            "draft_completion",
            "answer_directly",
            "use_calculator",
            "retrieve_evidence",
            "plan",
        }:
            if "critique" in allowed_actions:
                current_action = "critique"
            else:
                current_action = (
                    "verify_completion"
                    if "verify_completion" in allowed_actions
                    else (
                        "verify_with_calculator"
                        if "verify_with_calculator" in allowed_actions
                        else "finish"
                    )
                )
        elif current_action == "critique":
            current_action = (
                "revise_completion" if "revise_completion" in allowed_actions else "finish"
            )
        else:
            current_action = "finish"

    verification_result = client.chat(
        verifier_prompt, f"Objective:{objective}\nCandidate answer:{final_answer}"
    )
    approved_for_final = not require_human_approval or "deny" not in verification_result.lower()
    final_verdict = "approved" if approved_for_final else "needs_human_review"
    audit_log.append(f"verification={verification_result}")
    audit_log.append(f"approval_required={require_human_approval}")
    audit_log.append(f"approved_for_final={approved_for_final}")

    return {
        "run_id": run_id,
        "objective": objective,
        "capability_name": capability_name,
        "policy": policy,
        "actions": actions,
        "observations": observations,
        "verification_result": verification_result,
        "approval_required": require_human_approval,
        "approved_for_final": approved_for_final,
        "stop_condition": stop_condition,
        "final_answer": final_answer,
        "final_verdict": final_verdict,
        "audit_log": audit_log,
    }
