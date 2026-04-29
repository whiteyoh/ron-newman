from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent
WEB = ROOT / "web"

LEVELS = {
    1: {"name": "Autocomplete", "desc": "Pattern completion from short prompts."},
    2: {"name": "Instruction Following", "desc": "Maps explicit instructions to direct output."},
    3: {"name": "Tool Use", "desc": "Calls a helper tool (calculator) to solve structured tasks."},
    4: {"name": "Retrieval + Grounding", "desc": "Finds facts from a mini local knowledge base."},
    5: {"name": "Multi-step Reasoning", "desc": "Plans and executes a chained objective."},
    6: {"name": "Agentic Loop", "desc": "Observe-plan-act loops with reflection."},
    7: {"name": "Multi-agent Collaboration", "desc": "Specialized agents coordinate toward one output."},
    8: {"name": "Self-improving Workflow", "desc": "Evaluates, revises, and improves draft output."},
}


def demo_output(level: int):
    common = [f"Running Level {level}: {LEVELS[level]['name']}", LEVELS[level]["desc"]]
    traces = {
        1: ["Prompt: 'The sun rises in the'", "Completion: 'east.'", "Confidence: 0.97"],
        2: ["Instruction: Summarize in 7 words.", "Input: Long paragraph on climate.", "Output: 'Warming accelerates, adaptation requires urgent cooperation.'"],
        3: ["Task: 17 * 43", "Action: calculator_tool(17, 43)", "Result: 731", "Returned answer: 731"],
        4: ["Question: What port does Postgres use?", "Retrieve doc chunk: 'PostgreSQL default port is 5432.'", "Grounded answer: 5432"],
        5: ["Goal: Plan a 2-hour workshop", "Step 1: identify audience", "Step 2: choose modules", "Step 3: sequence agenda", "Produced agenda with timings."],
        6: ["Loop 1: Observe missing context", "Loop 1: Ask clarification", "Loop 2: Generate draft", "Loop 3: Critique and fix edge case", "Stop condition met."],
        7: ["ResearchAgent: gathered 4 constraints", "PlannerAgent: drafted architecture", "CriticAgent: found latency risk", "PlannerAgent: revised design", "Coordinator: finalized response."],
        8: ["Draft v1 score: 0.62", "Evaluator feedback: weak examples", "Revision v2 score: 0.79", "Evaluator feedback: clearer narrative", "Revision v3 score: 0.88", "Accepted best version."],
    }
    return {"level": level, "title": LEVELS[level]["name"], "lines": common + traces[level]}


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
                payload = demo_output(level)
            except Exception:
                self.send_error(400, "Invalid level")
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
