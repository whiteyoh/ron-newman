from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


@dataclass
class AgentTask:
    objective: str
    context: str = ""
    task_id: str = "workshop-task"


@dataclass
class AgentWorker:
    name: str
    role: str
    task: str


@dataclass
class AgentAction:
    actor: str
    action: str
    input: str
    reason: str


@dataclass
class AgentObservation:
    source: str
    content: str
    success: bool = True


@dataclass
class VerificationResult:
    status: str
    reason: str
    score: int = 0


@dataclass
class AgentPolicy:
    allowed_actions: list[str] = field(default_factory=list)
    max_iterations: int = 5
    max_tool_errors: int = 1
    require_final_verification: bool = True


@dataclass
class AgentRunResult:
    final_answer: str
    trace: list[str]
    stopped_on_finish: bool
    stopped_on_budget: bool
    tool_errors: int
    verified: bool
    final_verdict: str


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"
    MERGED = "merged"
    NEEDS_HUMAN_REVIEW = "needs_human_review"


class WorkerStatus(str, Enum):
    WAITING = "waiting"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRIED = "retried"


@dataclass
class OrchestratorTaskRecord:
    task_id: str
    worker_name: str
    worker_role: str
    task: str
    status: TaskStatus = TaskStatus.PENDING
    attempt: int = 0
    output: str = ""
    error: str = ""
    started_at: str = ""
    completed_at: str = ""
    worker_status: WorkerStatus = WorkerStatus.WAITING


@dataclass
class OrchestratorRunState:
    run_id: str
    objective: str
    mode: str
    tasks: list[OrchestratorTaskRecord]
    verifier_result: str = ""
    merge_policy: str = "objective coverage > clarity > actionability"
    approval_required: bool = True
    approved_for_merge: bool = False
    final_answer: str = ""
    audit_log: list[str] = field(default_factory=list)
