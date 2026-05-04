from typing import Any, cast

from src.agent_models import AgentPolicy, AgentTask

# ruff: noqa: E501
from src.agent_runtime import run_constrained_agent_loop
from src.agentic_wrappers import run_agentic_capability_demo
from src.constants import AGENTICNESS, DEFAULT_USE_CASE_KEY, LEVELS, USE_CASE_OPTIONS
from src.orchestrator import run_mini_orchestrator
from src.tools import calculator_tool, retrieve_local_facts
from src.types import AIChatClient
from src.yegge_workflows import build_yegge_simulation

LEVEL_ADVANCEMENT_REASONS = {
    2: (
        "It advances beyond Level 1 by obeying explicit instructions and constraints "
        "instead of only predicting likely next words."
    ),
    3: (
        "It advances beyond Level 2 by taking external actions (tool calls) to get exact "
        "results, not just following text-only instructions."
    ),
    4: (
        "It advances beyond Level 3 by grounding answers in retrieved evidence, so "
        "responses can be tied to provided facts."
    ),
    5: (
        "It advances beyond Level 4 by planning and executing multiple connected steps "
        "toward a concrete goal."
    ),
    6: (
        "It advances beyond Level 5 by evaluating and revising its own draft using "
        "critique feedback."
    ),
    7: (
        "It advances beyond Level 6 by running a bounded agent loop with explicit "
        "observe-act-replan iterations and stop conditions."
    ),
    8: (
        "It advances beyond Level 7 by scoring multiple candidate outputs and selecting "
        "the best improved result."
    ),
}

LEVEL_CONTEXT_TIP_TEMPLATES = {
    1: "Starter tip: for {topic}, write one clear next sentence you can immediately use.",
    2: (
        "Constraint tip: for {topic}, force your prompt to include a word limit and "
        "exact output format."
    ),
    3: (
        "Tool tip: for {topic}, use a concrete check (dates, marks, timings, formulas) "
        "before finalizing."
    ),
    4: "Evidence tip: for {topic}, anchor your answer to at least two specific facts or examples.",
    5: (
        "Planning tip: for {topic}, split work into timed blocks with a clear result for "
        "each block."
    ),
    6: (
        "Revision tip: for {topic}, run one critique pass focused on clarity and learner "
        "usefulness."
    ),
    7: (
        "Agent tip: for {topic}, iterate in short cycles (observe -> act -> review) with "
        "a stop condition."
    ),
    8: (
        "Optimization tip: for {topic}, compare multiple drafts and keep the one with "
        "the strongest actionability."
    ),
}


def _topic_from_context(use_case_context: str | None, use_case: str) -> str:
    if use_case_context and use_case_context.strip():
        return use_case_context.strip()
    if "revision" in use_case.lower():
        return "revision"
    if "lesson" in use_case.lower():
        return "lesson planning"
    return "your current topic"


def _contextual_tip(level: int, use_case_context: str | None, use_case: str) -> str:
    topic = _topic_from_context(use_case_context, use_case)
    template = LEVEL_CONTEXT_TIP_TEMPLATES[level]
    return template.format(topic=topic)


def _clip_text(value: Any, limit: int = 140) -> str:
    text = str(value or "")
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _normalized_status(raw: Any) -> str:
    value = str(raw or "pending").lower().replace("taskstatus.", "").strip()
    if "needs human review" in value or "needs_human_review" in value or "needs review" in value:
        return "needs_human_review"
    if "merge" in value:
        return "merged"
    if "run" in value:
        return "running"
    if "complete" in value:
        return "completed"
    if "approve" in value:
        return "approved"
    if "block" in value:
        return "blocked"
    if "fail" in value:
        return "failed"
    return "pending"


def use_case_prompt(text: str, use_case: str | None = None) -> str:
    if use_case is None:
        use_case = USE_CASE_OPTIONS[DEFAULT_USE_CASE_KEY]
    return f"{use_case}\n{text}"


def _build_structured_payload(
    level: int,
    level_info: dict[str, str],
    lines: list[str],
    agenticness: dict[str, Any],
    yegge_simulation: dict[str, Any],
    run_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    run_data = run_data or {}
    stage_summary = {
        "level": level,
        "name": level_info["name"],
        "plain_summary": level_info["desc"],
        "closest_yegge_stage": agenticness["closest_yegge_stage"],
    }
    score_summary = {
        "capability_level": level,
        "capability_score": agenticness.get("capability_score", level),
        "agenticness_score": agenticness.get("agenticness_score", agenticness["score"]),
        "yegge_alignment_score": agenticness["yegge_alignment_score"],
        "why_this_score": agenticness["yegge_alignment_explanation"],
        "why_not_higher": agenticness.get(
            "yegge_alignment_limit", "Workshop-safe simulation limits autonomy."
        ),
    }
    theatre_steps = []
    if level <= 6 and run_data:
        theatre_steps = [
            {
                "label": "Demo request",
                "actor": "human",
                "status": "completed",
                "summary": run_data.get("objective", "Objective set"),
                "detail": "Human objective provided.",
            },
            {
                "label": "Policy loaded",
                "actor": "agent",
                "status": "completed",
                "summary": run_data.get("policy", "Policy loaded"),
                "detail": "Bounded policy applied.",
            },
            {
                "label": "Action selected",
                "actor": "agent",
                "status": "completed",
                "summary": (run_data.get("actions") or ["Action selected"])[0],
                "detail": "Agent selected a bounded action.",
            },
            {
                "label": "Observation received",
                "actor": "tool",
                "status": "completed",
                "summary": (run_data.get("observations") or ["Observation received"])[0],
                "detail": "Tool/simulation returned observation.",
            },
            {
                "label": "Verification performed",
                "actor": "verifier",
                "status": "completed",
                "summary": run_data.get("verification_result", "Verifier check complete"),
                "detail": "Verification executed before verdict.",
            },
            {
                "label": "Human approval gate",
                "actor": "human",
                "status": "approved"
                if run_data.get("approved_for_final", True)
                else "needs_human_review",
                "summary": f"Approval required: {run_data.get('approval_required', True)}",
                "detail": f"Approved: {run_data.get('approved_for_final', False)}",
            },
            {
                "label": "Final verdict",
                "actor": "agent",
                "status": "completed",
                "summary": run_data.get("final_verdict", "Final verdict issued"),
                "detail": "Workshop-safe simulation outcome.",
            },
        ]
    elif level == 7 and run_data:
        loop = run_data.get("trace", [])
        theatre_steps = [
            {
                "label": "Demo request",
                "actor": "human",
                "status": "completed",
                "summary": run_data.get("objective", "Objective set"),
                "detail": "Bounded agent loop started.",
            }
        ]
        for step in loop[:5]:
            theatre_steps.append(
                {
                    "label": "Action selected",
                    "actor": "agent",
                    "status": "running",
                    "summary": f"Iteration {step.get('iteration', '?')}: {step.get('action', step.get('chosen_action', 'action'))}",
                    "detail": f"Tool input: {step.get('tool_input', 'n/a')} · Observation: {step.get('observation', 'n/a')} · Reason: {step.get('reason', 'n/a')} · Stop: {step.get('stop_condition', 'continue')} · Verifier: {step.get('verifier_result', 'pending')}",
                }
            )
        theatre_steps += [
            {
                "label": "Verification performed",
                "actor": "verifier",
                "status": "completed",
                "summary": run_data.get("final_verifier", "Verifier complete"),
                "detail": "Final verifier reviewed bounded loop.",
            },
            {
                "label": "Final verdict",
                "actor": "agent",
                "status": "completed",
                "summary": run_data.get("final_verdict", "Final verdict issued"),
                "detail": run_data.get("stop_condition", "Stop condition reached"),
            },
        ]
    elif level == 8 and run_data:
        orch = run_data
        taskboard = orch.get("taskboard", [])
        theatre_steps = [
            {
                "label": "Orchestrator run created",
                "actor": "orchestrator",
                "status": "completed",
                "summary": f"Run id: {orch.get('run_id', 'unknown')}",
                "detail": f"Request-scoped orchestration mode: {orch.get('mode', 'parallel')}",
            },
            {
                "label": "Policy loaded",
                "actor": "orchestrator",
                "status": "completed",
                "summary": _clip_text(orch.get("policy", "Workshop-safe policy loaded")),
                "detail": "Bounded workflow policy prepared for simulation.",
            },
            {
                "label": "Worker tasks created",
                "actor": "orchestrator",
                "status": "completed",
                "summary": f"{len(taskboard)} worker tasks created",
                "detail": "Taskboard initialized for simulated agentic workflow.",
            },
        ]
        for record in taskboard:
            worker = record.get("worker_name") or record.get("worker") or "worker"
            attempt = record.get("attempt", 1)
            status = _normalized_status(record.get("status"))
            task = _clip_text(record.get("task", "No task description"))
            output = _clip_text(
                record.get("output")
                or record.get("output_summary")
                or record.get("summary")
                or "No output yet"
            )
            error = _clip_text(record.get("error", ""))
            detail = f"Task: {task} · Output: {output}"
            if error:
                detail += f" · Error: {error}"
            theatre_steps.append(
                {
                    "label": "Worker completed",
                    "actor": "orchestrator",
                    "status": status,
                    "summary": f"{worker} completed attempt {attempt}",
                    "detail": detail,
                }
            )
        theatre_steps.extend(
            [
                {
                    "label": "Verification performed",
                    "actor": "verifier",
                    "status": "completed",
                    "summary": _clip_text(orch.get("verifier_result", "Verifier result pending")),
                    "detail": "Verifier checked objective coverage before merge decision.",
                },
                {
                    "label": "Human approval gate",
                    "actor": "human",
                    "status": "approved"
                    if orch.get("approved_for_merge")
                    else "needs_human_review",
                    "summary": f"Approval required: {orch.get('approval_required', True)}",
                    "detail": f"Approved for merge: {orch.get('approved_for_merge', False)}",
                },
                {
                    "label": "Merge decision",
                    "actor": "orchestrator",
                    "status": "merged" if orch.get("approved_for_merge") else "blocked",
                    "summary": _clip_text(orch.get("status", "needs_human_review")),
                    "detail": _clip_text(orch.get("merge_policy", "Workshop-safe merge policy")),
                },
                {
                    "label": "Final verdict",
                    "actor": "orchestrator",
                    "status": "merged" if orch.get("approved_for_merge") else "needs_human_review",
                    "summary": _clip_text(orch.get("status", "needs_human_review")),
                    "detail": _clip_text(orch.get("final_answer", "Needs human review")),
                },
            ]
        )
    replay_steps = [f"{s['label']}: {s['summary']}" for s in theatre_steps]
    merge_decision = (
        "approved"
        if run_data.get("approved_for_merge")
        else run_data.get("status", "needs_human_review")
    )
    if level == 8:
        final_status = run_data.get("status")
        if not final_status:
            if run_data.get("approved_for_merge"):
                final_status = "merged"
            elif run_data.get("approval_required", True) and not run_data.get(
                "approved_for_merge", False
            ):
                final_status = "needs_human_review"
            else:
                final_status = "unknown"
    else:
        final_status = run_data.get("final_verdict", "completed")
    approval_summary = {
        "approval_required": run_data.get("approval_required", True),
        "approved": run_data.get("approved_for_merge", run_data.get("approved_for_final", False)),
        "merge_decision": merge_decision,
        "verifier_result": run_data.get(
            "verifier_result", run_data.get("verification_result", "Available after run")
        ),
        "merge_policy": run_data.get("merge_policy", "Workshop-safe merge policy"),
        "final_status": final_status,
    }
    audit_summary = {"entries": run_data.get("audit_log") or []}
    taskboard = run_data.get("taskboard")
    workflow_preview = {
        "workflow_name": yegge_simulation["workflow_name"],
        "simulated_environment": yegge_simulation["simulated_environment"],
        "human_role": yegge_simulation["human_role"],
        "agent_role": yegge_simulation["agent_role"],
    }
    return {
        "stage_summary": stage_summary,
        "score_summary": score_summary,
        "theatre_steps": theatre_steps,
        "approval_summary": approval_summary,
        "audit_summary": audit_summary,
        "replay_steps": replay_steps,
        "taskboard": taskboard,
        "yegge_simulation": yegge_simulation,
        "yegge_score_summary": score_summary,
        "permission_flow": yegge_simulation.get("permissions"),
        "diff_preview": yegge_simulation.get("previewed_changes"),
        "command_preview": yegge_simulation.get("command_preview"),
        "parallel_agents": yegge_simulation.get("agent_instances"),
        "swarm_summary": run_data.get(
            "swarm_summary", {"total_agents": len(yegge_simulation.get("agent_instances", []))}
        ),
        "review_gate": yegge_simulation.get("review_gate"),
        "workflow_preview": workflow_preview,
        "why_not_production": yegge_simulation.get("why_not_production"),
        "lines": lines,
        "agenticness": agenticness,
    }


def run_level(
    level: int,
    client: AIChatClient,
    use_case_key: str = DEFAULT_USE_CASE_KEY,
    use_case_context: str | None = None,
) -> dict[str, Any]:
    use_case = USE_CASE_OPTIONS.get(use_case_key, USE_CASE_OPTIONS[DEFAULT_USE_CASE_KEY])
    if use_case_context and use_case_context.strip():
        use_case = (
            f"{use_case}\n"
            f"Confirmed context from user: {use_case_context.strip()}\n"
            "Use this confirmed context directly and do not ask clarifying questions."
        )
    level_info = cast(dict[str, str], LEVELS[level])
    intro = [
        f"Running Level {level}: {level_info['name']}",
        level_info["desc"],
        f"Nourishment: {level_info['nourishment']}",
        f"Topic tip: {_contextual_tip(level, use_case_context, use_case)}",
    ]
    if level > 1:
        intro.append(
            f"Why this is more advanced than Level {level - 1}: {LEVEL_ADVANCEMENT_REASONS[level]}"
        )
    intro.append(use_case)
    simulation = build_yegge_simulation(level, level_info["name"], use_case).to_dict()
    run_data: dict[str, Any] = {}

    if not client.available():
        return {
            "level": level,
            "title": level_info["name"],
            "lines": intro
            + [
                "AI backend not configured.",
                "Set OPENAI_API_KEY (and optionally OPENAI_BASE_URL, OPENAI_MODEL), then retry.",
            ],
        }

    if level == 1:
        objective = use_case_prompt("Produce a useful one-line continuation.", use_case)
        prompt = "The teacher begins the lesson: 'Today we're mastering key ideas by'"
        allowed = ["draft_completion", "verify_completion", "revise_completion", "finish"]

        def exec_l1(action: str, _state: dict[str, Any]) -> tuple[str, str]:
            if action == "draft_completion":
                draft = client.chat("Continue the text naturally in one short phrase.", prompt)
                return draft, f"drafted continuation: {draft}"
            if action == "verify_completion":
                verdict = client.chat(
                    "Verify if this continuation is useful, specific, and safe. Return strong/weak plus reason.",
                    f"prompt={prompt}",
                )
                return "", f"verification: {verdict}"
            if action == "revise_completion":
                revised = client.chat(
                    "Revise the completion to be more useful and specific.", prompt
                )
                return revised, f"revised completion: {revised}"
            return "", "finish selected"

        run = run_agentic_capability_demo(
            client,
            1,
            objective,
            "Supervised completion agent",
            allowed,
            "draft_completion",
            exec_l1,
            "Final verifier: is the continuation classroom-useful and safe?",
        )
        lines = [
            f"Objective: {run['objective']}",
            f"Policy: {run['policy']}",
            f"Allowed actions: {', '.join(allowed)}",
            f"Action trace: {run['actions']}",
            f"Verification: {run['verification_result']}",
            "Approval gate: simulated human approval required before final use.",
            f"Final verdict: {run['final_verdict']}",
            "Audit trail:",
            *run["audit_log"],
            f"Final answer: {run['final_answer']}",
        ]
        run_data = run
    elif level == 2:
        objective = use_case_prompt("Follow instruction contract with permission gate.", use_case)
        instruction = (
            "Summarize this in exactly 7 words: We reduced reply time while keeping quality high."
        )
        permission = "Request permission to apply instruction output in IDE"
        allowed = ["draft_completion", "verify_completion", "revise_completion", "finish"]

        def exec_l2(action: str, _state: dict[str, Any]) -> tuple[str, str]:
            if action == "draft_completion":
                out = client.chat(
                    "Follow user constraints precisely and respond as JSON with output field.",
                    instruction,
                )
                return out, f"structured output drafted: {out}"
            if action == "verify_completion":
                check = client.chat(
                    "Check exact 7-word constraint and return pass/fail with reason.", instruction
                )
                return "", f"constraint verifier: {check}"
            if action == "revise_completion":
                revised = client.chat("Revise to satisfy exact 7-word constraint.", instruction)
                return revised, f"revision produced: {revised}"
            return "", "finish selected"

        run = run_agentic_capability_demo(
            client,
            2,
            objective,
            "Permissioned instruction-following agent",
            allowed,
            "draft_completion",
            exec_l2,
            "Final verifier: does output satisfy instruction contract exactly?",
        )
        lines = [
            f"Instruction: {instruction}",
            f"Permission requested: {permission}",
            "Permission granted simulation: yes (workshop-safe)",
            f"Constraint verifier result: {run['verification_result']}",
            f"Revision decision: {'revise once then finish' if 'weak' in run['verification_result'].lower() or 'fail' in run['verification_result'].lower() else 'finish'}",
            f"Policy: {run['policy']}",
            f"Action trace: {run['actions']}",
            f"Approval gate: {'required' if run['approval_required'] else 'not required'}",
            f"Final approved output: {run['final_answer']}",
            f"Final verdict: {run['final_verdict']}",
            "Audit trail:",
            *run["audit_log"],
        ]
        run_data = run
    elif level == 3:
        objective = use_case_prompt(
            "Solve arithmetic with model-selected tool action loop.", use_case
        )
        expression = "17*43"
        allowed = [
            "answer_directly",
            "use_calculator",
            "verify_with_calculator",
            "revise_answer",
            "finish",
        ]

        def exec_l3(action: str, _state: dict[str, Any]) -> tuple[str, str]:
            if action == "answer_directly":
                ans = client.chat("Answer directly in one line.", f"What is {expression}?")
                return ans, "selected action=answer_directly"
            if action == "use_calculator":
                result = calculator_tool(expression)
                ans = client.chat("Use calculator output to answer.", result)
                return ans, f"tool input={expression}; tool result={result}"
            if action == "verify_with_calculator":
                v = calculator_tool(expression)
                return "", f"independent verification={v}"
            if action == "revise_answer":
                rev = client.chat("Revise answer to match verified calculator result.", expression)
                return rev, "answer revised"
            return "", "finish selected"

        run = run_agentic_capability_demo(
            client,
            3,
            objective,
            "Tool-action loop",
            allowed,
            "use_calculator",
            exec_l3,
            "Final verifier: is final answer numerically correct and safe?",
        )
        lines = [
            f"Task expression: {expression}",
            f"Selected action trace: {run['actions']}",
            f"Tool result / observations: {run['observations']}",
            f"Independent verification: {calculator_tool(expression)}",
            f"Approval decision: {'approved' if run['approved_for_final'] else 'denied'}",
            f"Final answer: {run['final_answer']}",
            f"Final verdict: {run['final_verdict']}",
            "Policy:",
            str(run["policy"]),
            "Audit trail:",
            *run["audit_log"],
        ]
        run_data = run
    elif level == 4:
        objective = use_case_prompt("Answer using retrieved evidence only.", use_case)
        question = "What is a SMART learning objective?"
        evidence = retrieve_local_facts(question)
        allowed = ["retrieve_evidence", "verify_completion", "revise_completion", "finish"]

        def exec_l4(action: str, _state: dict[str, Any]) -> tuple[str, str]:
            if action == "retrieve_evidence":
                answer = client.chat(
                    "Answer only from supplied evidence.", f"Q:{question}\nEvidence:{evidence}"
                )
                return answer, f"evidence source=local_kb; evidence={evidence}"
            if action == "verify_completion":
                support = client.chat(
                    "Check whether answer is fully supported by evidence.", f"Evidence:{evidence}"
                )
                return "", f"support verification={support}"
            if action == "revise_completion":
                revised = client.chat(
                    "Revise and mark limits if unsupported.", f"Evidence:{evidence}"
                )
                return revised, "revised for evidence support"
            return "", "finish selected"

        run = run_agentic_capability_demo(
            client,
            4,
            objective,
            "Grounded research agent",
            allowed,
            "retrieve_evidence",
            exec_l4,
            "Final verifier: supported/unsupported based on evidence only.",
        )
        lines = [
            f"Research objective: {objective}",
            "Retrieval plan: query local_kb then answer from evidence only.",
            f"Evidence source: {evidence}",
            f"Evidence sufficiency: {client.chat('Is evidence sufficient? Return sufficient/insufficient.', evidence)}",
            f"Answer: {run['final_answer']}",
            f"Support verification: {run['verification_result']}",
            f"Human approval gate: {'required' if run['approval_required'] else 'none'}",
            f"Final verdict: {run['final_verdict']}",
            "Policy:",
            str(run["policy"]),
            "Audit trail:",
            *run["audit_log"],
        ]
        run_data = run
    elif level == 5:
        objective = use_case_prompt("Design a 2-hour Year 10 revision workshop.", use_case)
        allowed = ["plan", "verify_completion", "revise_completion", "finish"]

        def exec_l5(action: str, _state: dict[str, Any]) -> tuple[str, str]:
            if action == "plan":
                plan = client.chat(
                    "Create concise numbered plan, then execute as timed agenda.", objective
                )
                return plan, f"plan_execute_output={plan}"
            if action == "verify_completion":
                ver = client.chat(
                    "Verify against objective. Return strong/weak/incomplete and one reason.",
                    objective,
                )
                return "", f"final verifier={ver}"
            if action == "revise_completion":
                revised = client.chat("Revise to fix verifier weaknesses.", objective)
                return revised, "revision generated"
            return "", "finish selected"

        run = run_agentic_capability_demo(
            client,
            5,
            objective,
            "CLI-style single-agent run",
            allowed,
            "plan",
            exec_l5,
            "Final verifier: objective fit, practical sequencing, and safety.",
            max_iterations=3,
        )
        lines = [
            f"Run id: {run['run_id']}",
            f"Objective: {objective}",
            f"Action budget: {run['policy']['max_iterations']}",
            f"Step trace: {run['actions']}",
            f"Stop condition: {run['stop_condition']}",
            f"Final verifier: {run['verification_result']}",
            f"Approved for use: {'yes' if run['approved_for_final'] else 'no'}",
            f"Final verdict: {run['final_verdict']}",
            "Policy:",
            str(run["policy"]),
            "Structured run summary:",
            f"stop_condition={run['stop_condition']}",
            "Audit trail:",
            *run["audit_log"],
            "Final answer:",
            run["final_answer"],
        ]
        run_data = run
    elif level == 6:
        objective = use_case_prompt(
            "Write a short lesson-summary note with one clear learner benefit.", use_case
        )
        allowed = ["draft_completion", "critique", "revise_completion", "finish"]
        attempts: list[tuple[int, int, str]] = []

        def exec_l6(action: str, state: dict[str, Any]) -> tuple[str, str]:
            if action == "draft_completion":
                draft = client.chat("Draft initial answer.", objective)
                return draft, "attempt 1 drafted"
            if action == "critique":
                critique = client.chat(
                    "Critique this draft and provide one improvement.", state.get("current", "")
                )
                score_raw = client.chat(
                    "Score this draft 0-100 as integer only.", state.get("current", "")
                )
                score = int("".join(ch for ch in score_raw if ch.isdigit()) or "0")
                attempts.append((state["iteration"], score, critique))
                return "", f"attempt={state['iteration']} score={score} critique={critique}"
            if action == "revise_completion":
                revised = client.chat("Revise using critique.", state.get("current", ""))
                return revised, "revision created"
            return "", "finish selected"

        run = run_agentic_capability_demo(
            client,
            6,
            objective,
            "Bounded evaluator agent",
            allowed,
            "draft_completion",
            exec_l6,
            "Final verifier: does final note meet objective with clear learner benefit?",
            max_iterations=3,
        )
        lines = [
            "Bounded evaluator loop:",
            *[f"Attempt number: {a[0]} | Score: {a[1]} | Critique: {a[2]}" for a in attempts],
            f"Best candidate: {run['final_answer']}",
            f"Final verifier: {run['verification_result']}",
            f"Approval gate: {'required' if run['approval_required'] else 'none'}",
            f"Final verdict: {run['final_verdict']}",
            "Policy:",
            str(run["policy"]),
            "Audit trail:",
            *run["audit_log"],
        ]
        run_data = run
    elif level == 7:
        objective = use_case_prompt(
            "Design a practical support workflow for teachers creating lessons and revision plans.",
            use_case,
        )
        policy = AgentPolicy(
            allowed_actions=["research", "calculate", "draft", "finish"],
            max_iterations=5,
            max_tool_errors=1,
            require_final_verification=True,
        )
        run = run_constrained_agent_loop(
            client=client,
            objective=objective,
            retrieve_fn=retrieve_local_facts,
            calculate_fn=calculator_tool,
            max_iterations=policy.max_iterations,
        )
        tool_errors = sum(1 for s in run["trace"] if "tool error" in s.observation)
        verified = True
        verifier = (
            client.chat(
                "Verify final answer for objective fit. Return safe/unsafe and one reason.",
                f"Objective:{objective}\nAnswer:{run['final_answer']}",
            )
            if policy.require_final_verification
            else "verification skipped"
        )
        if "unsafe" in verifier.lower():
            verified = False
        lines = [
            "Objective:",
            objective,
            "Agent policy:",
            f"allowed_actions={policy.allowed_actions}",
            f"max_iterations={policy.max_iterations}",
            f"max_tool_errors={policy.max_tool_errors}",
            f"require_final_verification={policy.require_final_verification}",
            "Agent loop timeline:",
        ]
        for step in run["trace"]:
            lines.extend(
                [
                    f"Iteration {step.iteration}",
                    f"Chosen action: {step.action}",
                    f"Action budget remaining: {max(policy.max_iterations - step.iteration, 0)}",
                    f"Tool input: {step.tool_input}",
                    f"Observation: {step.observation}",
                    f"Decision reason: {step.reason}",
                    f"Tool error count: {tool_errors}",
                ]
            )
        lines.extend(
            [
                f"Stop condition: {'finish action' if run['stopped_on_finish'] else 'max iterations budget'}",
                f"Final verifier step: {verifier}",
                f"safe to use?: {'yes' if verified else 'no'}",
                "Structured run summary:",
                f"stopped_on_finish: {run['stopped_on_finish']}",
                f"stopped_on_budget: {not run['stopped_on_finish']}",
                f"tool_errors: {tool_errors}",
                f"verified: {verified}",
                f"final_verdict: {'safe' if verified else 'needs review'}",
                "Final answer:",
                run["final_answer"],
            ]
        )
        agent_instances = simulation.get("agent_instances", [])
        run_data = {
            "trace": [s.__dict__ for s in run["trace"]],
            "swarm_summary": {
                "total_agents": len(agent_instances),
                "running": sum(
                    1 for a in agent_instances if str(a.get("status", "")).lower() == "running"
                ),
                "ready": sum(
                    1
                    for a in agent_instances
                    if str(a.get("status", "")).lower() in {"ready", "pending"}
                ),
                "completed": sum(
                    1 for a in agent_instances if "complete" in str(a.get("status", "")).lower()
                ),
                "coordination_pressure": "High — many agent contexts need manual review",
                "pressure_points": [
                    "duplicate work",
                    "conflicting outputs",
                    "manual prioritisation",
                    "review bottleneck",
                ],
                "why_orchestration_matters": "As agent count rises, manual prioritisation and review bottlenecks make orchestration necessary.",
            },
        }
    else:
        task = AgentTask(
            objective=use_case_prompt(
                "Draft guidance for writing effective lesson and revision plans.", use_case
            )
        )
        orch = run_mini_orchestrator(client, task, parallel=True)
        lines = [
            "Simulated orchestration note: This remains workshop-safe and is not a production orchestrator.",
            f"Orchestrator run id: {orch['run_id']}",
            f"orchestration mode: {orch['mode']}",
            "Policy:",
            f"max worker retries: {orch['policy']['max_worker_retries']}",
            f"verifier required: {orch['policy']['require_verifier_supported']}",
            f"human approval required: {orch['policy']['require_human_approval_before_merge']}",
            "Taskboard:",
        ]
        for item in orch["taskboard"]:
            lines.extend(
                [
                    f"worker: {item['worker_name']}",
                    f"task: {item['task']}",
                    f"status: {item['status']}",
                    f"attempt: {item['attempt']}",
                ]
            )
        lines.extend(
            [
                "Audit trail:",
                *orch["audit_log"],
                f"verifier result: {orch['verifier_result']}",
                "Approval gate:",
                f"approval required: {'yes' if orch['approval_required'] else 'no'}",
                f"approved for merge: {'yes' if orch['approved_for_merge'] else 'no'}",
                f"merge policy: {orch['merge_policy']}",
                ("final answer:" if orch["approved_for_merge"] else "needs human review:"),
                orch["final_answer"],
                "honest limitation note: This is still a workshop-safe orchestrator simulation. It does not execute repository changes, manage real background jobs, or persist state outside the request.",
            ]
        )
        run_data = orch

    payload = {
        "level": level,
        "title": level_info["name"],
        "lines": intro + lines,
        "agenticness": AGENTICNESS[level],
    }
    payload.update(
        _build_structured_payload(
            level, level_info, intro + lines, AGENTICNESS[level], simulation, run_data
        )
    )
    return payload
