from typing import Any

# ruff: noqa: E501
from src.agent_runtime import run_constrained_agent_loop
from src.constants import AGENTICNESS, DEFAULT_USE_CASE_KEY, LEVELS, USE_CASE_OPTIONS
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
        tool_result = calculator_tool(expression)
        answer = client.chat(
            "You can call a calculator. Return final numeric answer only.",
            use_case_prompt(
                f"Use calculator result {tool_result} for expression {expression}.", use_case
            ),
        )
        lines = [
            f"Task expression: {expression}",
            f"calculator_tool => {tool_result}",
            f"Model final answer: {answer}",
        ]
    elif level == 4:
        question = "What is a SMART learning objective?"
        evidence = retrieve_local_facts(question)
        answer = client.chat(
            "Answer only from supplied evidence. If missing, say unknown.",
            use_case_prompt(f"Question: {question}\nEvidence: {evidence}", use_case),
        )
        lines = [
            f"Question: {question}",
            f"Retrieved evidence: {evidence}",
            f"Grounded answer: {answer}",
        ]
    elif level == 5:
        goal = use_case_prompt("Design a 2-hour Year 10 revision workshop.", use_case)
        plan = client.chat("Create a concise numbered plan.", goal)
        agenda = client.chat("Execute the plan into a timed agenda with bullet points.", plan)
        lines = [f"Goal: {goal}", "Plan:", plan, "Executed agenda:", agenda]
    elif level == 6:
        draft = client.chat(
            "Write a short lesson-summary note with one clear learner benefit.",
            use_case_prompt("Students can now self-test using spaced retrieval prompts.", use_case),
        )
        critique = client.chat("Critique this draft in two bullets.", draft)
        improved = client.chat(
            "Revise the draft using this critique.", f"Draft:\n{draft}\n\nCritique:\n{critique}"
        )
        lines = ["Initial draft:", draft, "Critique:", critique, "Improved draft:", improved]
    elif level == 7:
        objective = use_case_prompt(
            "Design a practical support workflow for teachers creating lessons and revision plans.",
            use_case,
        )
        run = run_constrained_agent_loop(
            client=client,
            objective=objective,
            retrieve_fn=retrieve_local_facts,
            calculate_fn=calculator_tool,
            max_iterations=5,
        )
        lines = ["Objective:", objective, "Agent loop timeline:"]
        for step in run["trace"]:
            lines.extend(
                [
                    f"Iteration {step.iteration}",
                    f"Chosen action: {step.action}",
                    f"Tool input: {step.tool_input}",
                    f"Observation: {step.observation}",
                    f"Decision reason: {step.reason}",
                ]
            )
        stop = (
            "stop condition met: finish action"
            if run["stopped_on_finish"]
            else "stop condition met: max iterations"
        )
        lines.extend([f"Stop condition: {stop}", "Final answer:", run["final_answer"]])
    else:
        seed = use_case_prompt(
            "Draft guidance for writing effective lesson and revision plans.", use_case
        )
        planner = client.chat("You are planner. Return a short execution plan.", seed)
        critic = client.chat("You are critic. Identify two risks and two improvements.", planner)
        writer = client.chat(
            "You are teacher-resource-writer. Produce classroom-ready guidance using plan and critique.",
            f"Plan:\n{planner}\n\nCritique:\n{critic}",
        )
        verifier = client.chat(
            "You are verifier. Score 0-100 for clarity/actionability and give one-line verdict.",
            writer,
        )
        final = client.chat(
            "Merge planner, critic, writer, and verifier into one concise final answer.",
            f"Planner:\n{planner}\n\nCritic:\n{critic}\n\nWriter:\n{writer}\n\nVerifier:\n{verifier}",
        )
        lines = [
            "Simulated orchestration note: This is not a full production orchestrator. It is a workshop-safe miniature showing the pattern.",
            "Orchestration trace:",
            "Worker: planner",
            planner,
            "Worker: critic",
            critic,
            "Worker: teacher-resource-writer",
            writer,
            "Worker: verifier",
            verifier,
            "Final merged answer:",
            final,
        ]

    return {
        "level": level,
        "title": LEVELS[level]["name"],
        "lines": intro + lines,
        "agenticness": AGENTICNESS[level],
    }
