from __future__ import annotations

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).parent
WEB = ROOT / "web"

LEVELS = {
    1: {
        "name": "Autocomplete",
        "desc": "Predicts likely next text from a short prompt.",
    },
    2: {
        "name": "Instruction Following",
        "desc": "Follows explicit constraints in a prompt.",
    },
    3: {
        "name": "Tool Use",
        "desc": "Selects and uses a calculator tool for exact arithmetic.",
    },
    4: {
        "name": "Retrieval + Grounding",
        "desc": "Reads local facts, then answers using retrieved context.",
    },
    5: {
        "name": "Multi-step Reasoning",
        "desc": "Builds and executes a structured plan for a concrete goal.",
    },
    6: {
        "name": "Agentic Loop",
        "desc": "Iterates with critique + revision until quality target is met.",
    },
    7: {
        "name": "Multi-agent Collaboration",
        "desc": "Uses role-specialized agents to produce one final result.",
    },
    8: {
        "name": "Self-improving Workflow",
        "desc": "Scores outputs and keeps the best improved candidate.",
    },
}


class AIClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    def available(self) -> bool:
        return bool(self.api_key)

    def chat(self, system: str, user: str, temperature: float = 0.2) -> str:
        if not self.available():
            raise RuntimeError("OPENAI_API_KEY is not set")

        payload = {
            "model": self.model,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        data = json.dumps(payload).encode("utf-8")
        request = Request(
            url=f"{self.base_url}/chat/completions",
            data=data,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        with urlopen(request, timeout=30) as response:
            body = json.loads(response.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"].strip()


def calculator_tool(expression: str) -> str:
    allowed = set("0123456789+-*/(). ")
    if any(c not in allowed for c in expression):
        raise ValueError("unsupported characters in expression")
    return str(eval(expression, {"__builtins__": {}}, {}))


def retrieve_local_facts(question: str) -> str:
    kb = {
        "postgres": "PostgreSQL default port is 5432.",
        "redis": "Redis default port is 6379.",
        "nginx": "Nginx commonly serves HTTP on port 80.",
    }
    lower_question = question.lower()
    for key, value in kb.items():
        if key in lower_question:
            return value
    return "No matching fact found in local knowledge base."


def run_level(level: int, client: AIClient) -> dict[str, Any]:
    intro = [f"Running Level {level}: {LEVELS[level]['name']}", LEVELS[level]["desc"]]

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
        prompt = "The sun rises in the"
        completion = client.chat("Continue the text naturally in one short phrase.", prompt)
        lines = [f"Prompt: {prompt}", f"Model completion: {completion}"]
    elif level == 2:
        user_prompt = "Summarize this in exactly 7 words: AI systems transform routine office workflows."
        completion = client.chat("Follow user constraints precisely.", user_prompt)
        lines = [f"Instruction: {user_prompt}", f"Model output: {completion}"]
    elif level == 3:
        expression = "17*43"
        tool_result = calculator_tool(expression)
        answer = client.chat(
            "You can call a calculator. Return final numeric answer only.",
            f"Use calculator result {tool_result} for expression {expression}.",
        )
        lines = [f"Task expression: {expression}", f"calculator_tool => {tool_result}", f"Model final answer: {answer}"]
    elif level == 4:
        question = "What is the default port for Postgres?"
        evidence = retrieve_local_facts(question)
        answer = client.chat(
            "Answer only from supplied evidence. If missing, say unknown.",
            f"Question: {question}\nEvidence: {evidence}",
        )
        lines = [f"Question: {question}", f"Retrieved evidence: {evidence}", f"Grounded answer: {answer}"]
    elif level == 5:
        goal = "Design a 2-hour onboarding workshop for new software engineers."
        plan = client.chat("Create a concise numbered plan.", goal)
        agenda = client.chat("Execute the plan into a timed agenda with bullet points.", plan)
        lines = [f"Goal: {goal}", "Plan:", plan, "Executed agenda:", agenda]
    elif level == 6:
        draft = client.chat("Write a short release note with one clear benefit.", "We shipped faster search.")
        critique = client.chat("Critique this draft in two bullets.", draft)
        improved = client.chat("Revise the draft using this critique.", f"Draft:\n{draft}\n\nCritique:\n{critique}")
        lines = ["Initial draft:", draft, "Critique:", critique, "Improved draft:", improved]
    elif level == 7:
        prompt = "Propose a secure, low-cost internal FAQ assistant for a 30-person startup."
        researcher = client.chat("You are ResearchAgent. List constraints and risks.", prompt)
        planner = client.chat("You are PlannerAgent. Propose architecture using research notes.", researcher)
        critic = client.chat("You are CriticAgent. Find weaknesses and improvements.", planner)
        final = client.chat("You are Coordinator. Produce final recommendation.", f"Plan:\n{planner}\n\nCritique:\n{critic}")
        lines = ["ResearchAgent:", researcher, "PlannerAgent:", planner, "CriticAgent:", critic, "Coordinator output:", final]
    else:
        seed = "Draft guidance for writing effective bug reports."
        v1 = client.chat("Write a first draft.", seed)
        score1 = client.chat("Score this from 0-100 for clarity and actionability, return only integer.", v1)
        v2 = client.chat("Improve this draft to increase clarity and actionability.", v1)
        score2 = client.chat("Score this from 0-100 for clarity and actionability, return only integer.", v2)
        best = v2 if int(score2) >= int(score1) else v1
        lines = ["Draft v1:", v1, f"Score v1: {score1}", "Draft v2:", v2, f"Score v2: {score2}", "Selected best version:", best]

    return {"level": level, "title": LEVELS[level]["name"], "lines": intro + lines}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB), **kwargs)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/levels":
            body = json.dumps(LEVELS).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path.startswith("/api/run/"):
            try:
                level = int(path.split("/")[-1])
                if level not in LEVELS:
                    raise ValueError("out of range")
                payload = run_level(level, AIClient())
            except Exception as err:
                self.send_error(400, f"Invalid level or execution error: {err}")
                return
            body = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        return super().do_GET()


if __name__ == "__main__":
    host, port = "127.0.0.1", 8000
    print(f"Serving demo at http://{host}:{port}")
    ThreadingHTTPServer((host, port), Handler).serve_forever()
