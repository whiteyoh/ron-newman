from __future__ import annotations

from dataclasses import dataclass, field


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
