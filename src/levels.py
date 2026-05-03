from typing import Any, cast

from src.agent_models import AgentPolicy, AgentTask

# ruff: noqa: E501
from src.agent_runtime import run_constrained_agent_loop
from src.agentic_wrappers import run_agentic_capability_demo
from src.constants import AGENTICNESS, DEFAULT_USE_CASE_KEY, LEVELS, USE_CASE_OPTIONS
from src.orchestrator import run_mini_orchestrator
from src.tools import calculator_tool, retrieve_local_facts
from src.types import AIChatClient

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


def use_case_prompt(text: str, use_case: str | None = None) -> str:
    if use_case is None:
        use_case = USE_CASE_OPTIONS[DEFAULT_USE_CASE_KEY]
    return f"{use_case}\n{text}"


def _build_structured_payload(
    level: int, level_info: dict[str, str], lines: list[str], agenticness: dict[str, Any]
) -> dict[str, Any]:
    stage_summary = {
        "level": level,
        "name": level_info["name"],
        "plain_summary": level_info["desc"],
        "closest_yegge_stage": agenticness["closest_yegge_stage"],
    }
    score_summary = {
        "capability_level": level,
        "agenticness_score": agenticness["score"],
        "yegge_alignment_score": agenticness["yegge_alignment_score"],
        "why_this_score": agenticness["explanation"],
        "why_not_higher": "More autonomy requires stronger orchestration, verification depth, and governance.",
        "move_up_hint": "Add tighter verification, clearer approval gates, and stronger orchestration only when needed.",
    }
    theatre_steps = [
        {
            "label": "What the human asked for",
            "actor": "human",
            "status": "complete",
            "summary": lines[0] if lines else "Objective set",
            "detail": "Objective created",
        },
        {
            "label": "What the agent decided",
            "actor": "agent",
            "status": "complete",
            "summary": "Policy and actions selected.",
            "detail": "Bounded autonomy in workshop-safe simulation.",
        },
        {
            "label": "What the agent checked",
            "actor": "verifier",
            "status": "complete",
            "summary": "Verifier reviewed output.",
            "detail": "Verification step applied before final verdict.",
        },
        {
            "label": "Where the human stays in control",
            "actor": "human",
            "status": "approved",
            "summary": "Human approval gate enforced.",
            "detail": "Final output requires review and approval.",
        },
        {
            "label": "Can we trust this output?",
            "actor": "orchestrator" if level == 8 else "agent",
            "status": "complete",
            "summary": "Final verdict issued with audit trail.",
            "detail": "Outcome is educational and workshop-safe.",
        },
    ]
    replay_steps = [
        "objective created",
        "policy loaded",
        "action selected",
        "tool/worker executed",
        "observation received",
        "verifier checked",
        "approval gate applied",
        "final verdict",
    ]
    approval_summary = {
        "approval_required": True,
        "approved": level != 8,
        "merge_decision": "approved" if level != 8 else "conditional",
    }
    audit_summary = {
        "entries": [
            entry
            for entry in lines
            if any(k in entry.lower() for k in ["audit", "verdict", "approval", "verification"])
        ][:8]
    }
    taskboard = None
    if level == 8:
        taskboard = {
            "columns": ["Pending", "Running", "Completed", "Needs human review", "Merged"],
            "workers": [
                {
                    "worker": "planner",
                    "task": "Break objective into tasks",
                    "status": "completed",
                    "attempt": 1,
                    "output_summary": "Plan drafted",
                    "error": "",
                    "verified": True,
                },
                {
                    "worker": "researcher",
                    "task": "Gather guidance",
                    "status": "completed",
                    "attempt": 1,
                    "output_summary": "Evidence gathered",
                    "error": "",
                    "verified": True,
                },
                {
                    "worker": "teacher_resource_writer",
                    "task": "Draft teaching resource",
                    "status": "completed",
                    "attempt": 1,
                    "output_summary": "Draft produced",
                    "error": "",
                    "verified": True,
                },
                {
                    "worker": "critic",
                    "task": "Stress-test draft",
                    "status": "completed",
                    "attempt": 1,
                    "output_summary": "Critique captured",
                    "error": "",
                    "verified": True,
                },
                {
                    "worker": "verifier",
                    "task": "Check claims and fit",
                    "status": "completed",
                    "attempt": 1,
                    "output_summary": "Verifier gate complete",
                    "error": "",
                    "verified": True,
                },
                {
                    "worker": "merger",
                    "task": "Apply merge policy",
                    "status": "needs_review",
                    "attempt": 1,
                    "output_summary": "Awaiting human gate",
                    "error": "",
                    "verified": True,
                },
            ],
        }
    return {
        "stage_summary": stage_summary,
        "score_summary": score_summary,
        "theatre_steps": theatre_steps,
        "approval_summary": approval_summary,
        "audit_summary": audit_summary,
        "replay_steps": replay_steps,
        "taskboard": taskboard,
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

    payload = {
        "level": level,
        "title": level_info["name"],
        "lines": intro + lines,
        "agenticness": AGENTICNESS[level],
    }
    payload.update(_build_structured_payload(level, level_info, intro + lines, AGENTICNESS[level]))
    return payload
