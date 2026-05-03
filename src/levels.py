from typing import Any

from src.agent_models import AgentPolicy, AgentTask

# ruff: noqa: E501
from src.agent_runtime import run_constrained_agent_loop
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
    intro = [
        f"Running Level {level}: {LEVELS[level]['name']}",
        LEVELS[level]["desc"],
        f"Nourishment: {LEVELS[level]['nourishment']}",
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
            "title": LEVELS[level]["name"],
            "lines": intro
            + [
                "AI backend not configured.",
                "Set OPENAI_API_KEY (and optionally OPENAI_BASE_URL, OPENAI_MODEL), then retry.",
            ],
        }

    if level == 1:
        prompt = use_case_prompt(
            "The teacher begins the lesson: 'Today we're mastering key ideas by'", use_case
        )
        completion = client.chat("Continue the text naturally in one short phrase.", prompt)
        lines = [f"Prompt: {prompt}", f"Model completion: {completion}"]
    elif level == 2:
        user_prompt = use_case_prompt(
            "Summarize this in exactly 7 words: We reduced reply time while keeping quality high.",
            use_case,
        )
        completion = client.chat("Follow user constraints precisely.", user_prompt)
        lines = [f"Instruction: {user_prompt}", f"Model output: {completion}"]
    elif level == 3:
        expression = "17*43"
        chooser = client.chat(
            'Return strict JSON only: {"action":"answer_directly|use_calculator","tool_input":"string","final_answer":"string"}.',
            use_case_prompt(
                f"Question: What is {expression}? Allowed actions: answer_directly, use_calculator.",
                use_case,
            ),
        )
        action = "answer_directly"
        tool_input = expression
        tool_result = "n/a"
        final_answer = ""
        try:
            import json

            parsed = json.loads(chooser)
            action = str(parsed.get("action", "answer_directly"))
            tool_input = str(parsed.get("tool_input", expression))
            final_answer = str(parsed.get("final_answer", ""))
        except Exception:
            action = "answer_directly"
            final_answer = "Fallback: unable to parse model JSON."
        if action == "use_calculator":
            tool_result = calculator_tool(tool_input)
            final_answer = client.chat(
                "Use tool result to provide final answer.", f"tool_result={tool_result}"
            )
        elif not final_answer:
            final_answer = client.chat("Answer directly in one line.", f"What is {expression}?")
        lines = [
            f"Task expression: {expression}",
            f"Model selected action: {action}",
            f"Tool input: {tool_input}",
            f"Tool result: {tool_result}",
            f"Final answer: {final_answer}",
        ]
    elif level == 4:
        question = "What is a SMART learning objective?"
        evidence = retrieve_local_facts(question)
        sufficiency = client.chat(
            "Is this evidence sufficient for the question? Return sufficient/insufficient and one reason.",
            f"Question: {question}\nEvidence: {evidence}",
        )
        answer = client.chat(
            "Answer only from evidence. If insufficient, clearly note limits.",
            use_case_prompt(
                f"Question: {question}\nEvidence(source=local_kb): {evidence}\nSufficiency: {sufficiency}",
                use_case,
            ),
        )
        support = client.chat(
            "Is this answer fully supported by the supplied evidence? Return supported/unsupported and one reason.",
            f"Evidence: {evidence}\nAnswer: {answer}",
        )
        lines = [
            f"Question: {question}",
            f"Retrieved evidence: {evidence}",
            "Evidence source: local_kb",
            f"Sufficiency check: {sufficiency}",
            f"Grounded answer: {answer}",
            f"Support verifier: {support}",
        ]
    elif level == 5:
        goal = use_case_prompt("Design a 2-hour Year 10 revision workshop.", use_case)
        plan = client.chat("Create a concise numbered plan.", goal)
        execution = client.chat("Execute this plan into a timed agenda with bullets.", plan)
        verification = client.chat(
            "Verify against objective. Return strong/weak/unsupported/incomplete and one reason.",
            f"Objective: {goal}\nOutput: {execution}",
        )
        revise = (
            "revise"
            if any(tag in verification.lower() for tag in ["weak", "unsupported", "incomplete"])
            else "keep"
        )
        final = (
            execution
            if revise == "keep"
            else client.chat(
                "Revise to fix verification weakness.",
                f"Objective:{goal}\nPlan:{plan}\nExecution:{execution}\nVerification:{verification}",
            )
        )
        lines = [
            f"Goal: {goal}",
            "Plan:",
            plan,
            "Execution:",
            execution,
            f"Verification result: {verification}",
            f"Revision decision: {revise}",
            "Final answer:",
            final,
        ]
    elif level == 6:
        objective = use_case_prompt(
            "Write a short lesson-summary note with one clear learner benefit.", use_case
        )
        current = client.chat("Draft initial answer.", objective)
        lines = ["Bounded critique loop:"]
        threshold = 80
        selected = current
        for attempt in range(1, 4):
            critique = client.chat("Critique this draft and provide one improvement.", current)
            score_raw = client.chat("Score this draft 0-100 as integer only.", current)
            try:
                score = int("".join(ch for ch in score_raw if ch.isdigit()) or "0")
            except Exception:
                score = 0
            decision = "revise" if attempt < 3 and score < threshold else "select"
            lines.extend(
                [
                    f"Attempt number: {attempt}",
                    f"Score: {score}",
                    f"Critique: {critique}",
                    f"Decision: {decision}",
                ]
            )
            selected = current
            if decision == "revise":
                current = client.chat(
                    "Revise using critique.", f"Draft:{current}\nCritique:{critique}"
                )
            else:
                break
        lines.extend(["Selected final answer:", selected])
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
            "Orchestration trace:",
            f"orchestration mode: {orch['mode']}",
        ]
        for item in orch["trace"]:
            lines.extend(
                [
                    f"worker name: {item['worker']}",
                    f"worker task: {item['task']}",
                    f"worker output summary: {item['output_summary']}",
                ]
            )
        lines.extend(
            [
                f"verifier result: {orch['verifier_result']}",
                f"merge policy: {orch['merge_policy']}",
                "final answer:",
                orch["final_answer"],
                f"honest limitation note: {orch['limitation']}",
            ]
        )

    return {
        "level": level,
        "title": LEVELS[level]["name"],
        "lines": intro + lines,
        "agenticness": AGENTICNESS[level],
    }
