from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from src.agent_models import AgentTask, AgentWorker
from src.types import AIChatClient


def run_mini_orchestrator(client: AIChatClient, task: AgentTask, parallel: bool = True) -> dict:
    workers = [
        AgentWorker("planner", "planner", "Create an execution plan for the objective."),
        AgentWorker("researcher", "researcher", "Gather key evidence and constraints."),
        AgentWorker(
            "teacher_resource_writer",
            "teacher_resource_writer",
            "Draft classroom-ready resource text.",
        ),
        AgentWorker("critic", "critic", "Identify weaknesses and suggest improvements."),
    ]

    def run_worker(worker: AgentWorker) -> tuple[str, str]:
        output = client.chat(f"You are {worker.role}. {worker.task}", task.objective)
        return worker.name, output

    outputs: dict[str, str] = {}
    mode = "parallel" if parallel else "sequential"
    if parallel:
        try:
            with ThreadPoolExecutor(max_workers=4) as pool:
                for name, out in pool.map(run_worker, workers):
                    outputs[name] = out
        except Exception:
            mode = "sequential"
            for worker in workers:
                name, out = run_worker(worker)
                outputs[name] = out
    else:
        for worker in workers:
            name, out = run_worker(worker)
            outputs[name] = out

    verifier_input = "\n\n".join(f"{k}:\n{v}" for k, v in outputs.items())
    verifier = client.chat(
        "You are verifier. Check objective coverage. Return supported/unsupported with one reason.",
        f"Objective: {task.objective}\n\nOutputs:\n{verifier_input}",
    )
    merger = client.chat(
        (
            "You are merger. Merge outputs using policy: prioritize objective "
            "coverage, then clarity, then actionability."
        ),
        f"Objective: {task.objective}\nVerifier: {verifier}\n\nOutputs:\n{verifier_input}",
    )

    trace = []
    for w in workers:
        trace.append(
            {
                "worker": w.name,
                "task": w.task,
                "output_summary": outputs.get(w.name, "")[:180],
            }
        )

    return {
        "mode": mode,
        "trace": trace,
        "worker_outputs": outputs,
        "verifier_result": verifier,
        "merge_policy": "objective coverage > clarity > actionability",
        "final_answer": merger,
        "limitation": "Workshop-safe orchestration only; no external side-effectful tools.",
    }
