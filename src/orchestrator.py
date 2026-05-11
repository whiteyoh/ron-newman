from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from datetime import datetime, timezone
from uuid import uuid4

from src.agent_models import (
    AgentTask,
    AgentWorker,
    OrchestratorRunState,
    OrchestratorTaskRecord,
    TaskStatus,
    WorkerStatus,
)
from src.types import AIChatClient


def run_mini_orchestrator(client: AIChatClient, task: AgentTask, parallel: bool = True) -> dict:
    max_worker_retries = 1
    require_verifier_supported = True
    require_human_approval_before_merge = True
    allow_parallel_workers = True
    policy = {
        "max_worker_retries": max_worker_retries,
        "require_verifier_supported": require_verifier_supported,
        "require_human_approval_before_merge": require_human_approval_before_merge,
        "allow_parallel_workers": allow_parallel_workers,
    }
    workers = [
        AgentWorker("planner", "planner", "Create an execution plan for the objective."),
        AgentWorker("researcher", "researcher", "Gather key evidence and constraints."),
        AgentWorker(
            "content_writer",
            "content_writer",
            "Draft user-ready content for the confirmed use case.",
        ),
        AgentWorker("critic", "critic", "Identify weaknesses and suggest improvements."),
    ]

    run_state = OrchestratorRunState(
        run_id=f"orch-{uuid4().hex[:8]}",
        objective=task.objective,
        mode="parallel" if parallel and allow_parallel_workers else "sequential",
        tasks=[],
    )

    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()  # noqa: UP017

    for w in workers:
        rec = OrchestratorTaskRecord(
            task_id=f"{run_state.run_id}-{w.name}",
            worker_name=w.name,
            worker_role=w.role,
            task=w.task,
        )
        run_state.tasks.append(rec)
        run_state.audit_log.append(f"created task: {rec.task_id} for worker {w.name}")

    tasks_by_worker = {r.worker_name: r for r in run_state.tasks}

    def run_worker(worker: AgentWorker) -> tuple[str, str]:
        rec = tasks_by_worker[worker.name]
        while rec.attempt <= max_worker_retries:
            rec.attempt += 1
            rec.status = TaskStatus.RUNNING
            rec.worker_status = WorkerStatus.RUNNING
            rec.started_at = _now()
            run_state.audit_log.append(f"started worker: {worker.name} attempt {rec.attempt}")
            try:
                output = client.chat(f"You are {worker.role}. {worker.task}", task.objective)
                rec.status = TaskStatus.COMPLETED
                rec.worker_status = WorkerStatus.COMPLETED
                rec.output = output
                rec.completed_at = _now()
                run_state.audit_log.append(f"completed worker: {worker.name} attempt {rec.attempt}")
                return worker.name, output
            except Exception as exc:
                rec.status = TaskStatus.FAILED
                rec.worker_status = WorkerStatus.FAILED
                rec.error = str(exc)
                rec.completed_at = _now()
                run_state.audit_log.append(
                    f"failed worker: {worker.name} attempt {rec.attempt}: {exc}"
                )
                if rec.attempt <= max_worker_retries:
                    rec.worker_status = WorkerStatus.RETRIED
                    run_state.audit_log.append(f"retried worker: {worker.name}")
                    continue
                raise
        raise RuntimeError(f"Worker {worker.name} exhausted retries")

    outputs: dict[str, str] = {}
    mode = run_state.mode
    if run_state.mode == "parallel":
        try:
            with ThreadPoolExecutor(max_workers=4) as pool:
                for name, out in pool.map(run_worker, workers):
                    outputs[name] = out
        except Exception:
            mode = "sequential"
            run_state.mode = mode
            run_state.audit_log.append("parallel execution failed; falling back to sequential")
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
    run_state.verifier_result = verifier
    run_state.audit_log.append("verifier completed")

    verifier_supported = "supported" in verifier.lower() and "unsupported" not in verifier.lower()
    run_state.approval_required = require_human_approval_before_merge
    run_state.approved_for_merge = verifier_supported
    run_state.audit_log.append(
        f"approval decision: {'approved' if run_state.approved_for_merge else 'rejected'}"
    )

    merger = "needs human review"
    if run_state.approved_for_merge:
        merger = client.chat(
            (
                "You are merger. Produce the user-requested output first "
                "and make it action-ready. "
                "Do not default to generic guidance. "
                "Avoid 'guidance for preparing' wording unless guidance was requested. "
                "Preserve known facts, clearly label assumptions, "
                "and include 'Check before use' where appropriate. "
                "Use plain English."
            ),
            f"Objective: {task.objective}\nVerifier: {verifier}\n\nOutputs:\n{verifier_input}",
        )
        run_state.audit_log.append("merge decision: merged")
        for rec in run_state.tasks:
            if rec.status == TaskStatus.COMPLETED:
                rec.status = TaskStatus.MERGED
    else:
        run_state.audit_log.append("merge decision: blocked; needs human review")
        for rec in run_state.tasks:
            if rec.status in {TaskStatus.COMPLETED, TaskStatus.FAILED}:
                rec.status = TaskStatus.NEEDS_HUMAN_REVIEW

    run_state.final_answer = merger

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
        "policy": policy,
        "trace": trace,
        "taskboard": [asdict(rec) for rec in run_state.tasks],
        "audit_log": run_state.audit_log,
        "run_id": run_state.run_id,
        "worker_outputs": outputs,
        "verifier_result": verifier,
        "merge_policy": "objective coverage > clarity > actionability",
        "approval_required": run_state.approval_required,
        "approved_for_merge": run_state.approved_for_merge,
        "status": (
            TaskStatus.MERGED.value
            if run_state.approved_for_merge
            else TaskStatus.NEEDS_HUMAN_REVIEW.value
        ),
        "final_answer": run_state.final_answer,
        "run_state": {
            "run_id": run_state.run_id,
            "objective": run_state.objective,
            "mode": run_state.mode,
            "tasks": [asdict(rec) for rec in run_state.tasks],
            "verifier_result": run_state.verifier_result,
            "merge_policy": run_state.merge_policy,
            "approval_required": run_state.approval_required,
            "approved_for_merge": run_state.approved_for_merge,
            "final_answer": run_state.final_answer,
            "audit_log": run_state.audit_log,
        },
        "limitation": "Workshop-safe orchestration only; no external side-effectful tools.",
    }
