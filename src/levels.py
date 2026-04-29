from typing import Any

from src.constants import GLOBAL_USE_CASE, LEVELS
from src.tools import calculator_tool, retrieve_local_facts


def use_case_prompt(text: str) -> str:
    return f"{GLOBAL_USE_CASE}\n{text}"


def run_level(level: int, client) -> dict[str, Any]:
    intro = [f"Running Level {level}: {LEVELS[level]['name']}", LEVELS[level]["desc"], GLOBAL_USE_CASE]

    if not client.available():
        return {
            "level": level,
            "title": LEVELS[level]["name"],
            "lines": intro + [
                "AI backend not configured.",
                "Set OPENAI_API_KEY (and optionally OPENAI_BASE_URL, OPENAI_MODEL), then retry.",
            ],
        }

    if level == 1:
        prompt = use_case_prompt("The support agent replies: 'I understand your issue, and I can'")
        completion = client.chat("Continue the text naturally in one short phrase.", prompt)
        lines = [f"Prompt: {prompt}", f"Model completion: {completion}"]
    elif level == 2:
        user_prompt = use_case_prompt("Summarize this in exactly 7 words: We reduced reply time while keeping quality high.")
        completion = client.chat("Follow user constraints precisely.", user_prompt)
        lines = [f"Instruction: {user_prompt}", f"Model output: {completion}"]
    elif level == 3:
        expression = "17*43"
        tool_result = calculator_tool(expression)
        answer = client.chat("You can call a calculator. Return final numeric answer only.", use_case_prompt(f"Use calculator result {tool_result} for expression {expression}."))
        lines = [f"Task expression: {expression}", f"calculator_tool => {tool_result}", f"Model final answer: {answer}"]
    elif level == 4:
        question = "What is the default port for Postgres?"
        evidence = retrieve_local_facts(question)
        answer = client.chat("Answer only from supplied evidence. If missing, say unknown.", use_case_prompt(f"Question: {question}\nEvidence: {evidence}"))
        lines = [f"Question: {question}", f"Retrieved evidence: {evidence}", f"Grounded answer: {answer}"]
    elif level == 5:
        goal = use_case_prompt("Design a 2-hour training workshop for support agents.")
        plan = client.chat("Create a concise numbered plan.", goal)
        agenda = client.chat("Execute the plan into a timed agenda with bullet points.", plan)
        lines = [f"Goal: {goal}", "Plan:", plan, "Executed agenda:", agenda]
    elif level == 6:
        draft = client.chat("Write a short release note with one clear benefit.", use_case_prompt("We shipped faster support search."))
        critique = client.chat("Critique this draft in two bullets.", draft)
        improved = client.chat("Revise the draft using this critique.", f"Draft:\n{draft}\n\nCritique:\n{critique}")
        lines = ["Initial draft:", draft, "Critique:", critique, "Improved draft:", improved]
    elif level == 7:
        prompt = use_case_prompt("Propose a secure, low-cost internal support assistant for a 30-person startup.")
        researcher = client.chat("You are ResearchAgent. List constraints and risks.", prompt)
        planner = client.chat("You are PlannerAgent. Propose architecture using research notes.", researcher)
        critic = client.chat("You are CriticAgent. Find weaknesses and improvements.", planner)
        final = client.chat("You are Coordinator. Produce final recommendation.", f"Plan:\n{planner}\n\nCritique:\n{critic}")
        lines = ["ResearchAgent:", researcher, "PlannerAgent:", planner, "CriticAgent:", critic, "Coordinator output:", final]
    else:
        seed = use_case_prompt("Draft guidance for writing effective support ticket updates.")
        v1 = client.chat("Write a first draft.", seed)
        score1 = client.chat("Score this from 0-100 for clarity and actionability, return only integer.", v1)
        v2 = client.chat("Improve this draft to increase clarity and actionability.", v1)
        score2 = client.chat("Score this from 0-100 for clarity and actionability, return only integer.", v2)
        best = v2 if int(score2) >= int(score1) else v1
        lines = ["Draft v1:", v1, f"Score v1: {score1}", "Draft v2:", v2, f"Score v2: {score2}", "Selected best version:", best]

    return {"level": level, "title": LEVELS[level]["name"], "lines": intro + lines}
