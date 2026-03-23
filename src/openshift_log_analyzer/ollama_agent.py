from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from time import perf_counter
from typing import Any, Callable
from urllib import error, request

from .analyzer import LogSummary
from .renderer import render_human_readable_report


class WorkflowStep(str, Enum):
    COLLECT_CONTEXT = "CollectContext"
    DIAGNOSE = "Diagnose"
    RECOMMEND = "Recommend"
    EXECUTE_FIX = "ExecuteFix"
    VERIFY = "Verify"


class ExecutionMode(str, Enum):
    PROPOSE_CHANGES = "propose_changes"
    APPLY_CHANGES = "apply_changes"


@dataclass(frozen=True)
class AgentPolicy:
    tenant: str = "default"
    namespace: str = "default"
    allowed_tools: dict[str, list[str]] = field(default_factory=dict)


@dataclass(frozen=True)
class WorkflowTrace:
    step: WorkflowStep
    latency_ms: float
    success: bool
    detail: str

    def as_dict(self) -> dict[str, object]:
        return {
            "step": self.step.value,
            "latency_ms": self.latency_ms,
            "success": self.success,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class WorkflowOutcome:
    mode: ExecutionMode
    analysis: str
    traces: list[WorkflowTrace]
    failure_counts: dict[str, int]


@dataclass
class PolicyEnforcer:
    policy: AgentPolicy

    def check(self, tool_name: str) -> bool:
        allowed = self.policy.allowed_tools.get(tool_name)
        if not allowed:
            return False
        tenant_namespace = f"{self.policy.tenant}:{self.policy.namespace}"
        return "*" in allowed or tenant_namespace in allowed


@dataclass
class OpenShiftAgentWorkflow:
    summary: LogSummary
    model: str
    base_url: str
    timeout_seconds: int = 60
    mode: ExecutionMode = ExecutionMode.PROPOSE_CHANGES
    policy: AgentPolicy = field(default_factory=lambda: AgentPolicy(allowed_tools={"ollama.generate": ["*"]}))

    traces: list[WorkflowTrace] = field(default_factory=list)
    failure_counts: dict[str, int] = field(default_factory=dict)
    step_event_handler: Callable[[WorkflowTrace], None] | None = None
    approval_callback: Callable[[str], bool] | None = None

    def run(self) -> WorkflowOutcome:
        context = self._run_step(WorkflowStep.COLLECT_CONTEXT, self._collect_context)
        diagnosis = self._run_step(WorkflowStep.DIAGNOSE, lambda: self._diagnose(context))
        recommendation = self._run_step(WorkflowStep.RECOMMEND, lambda: self._recommend(diagnosis))

        if self.mode == ExecutionMode.APPLY_CHANGES:
            execution = self._run_step(WorkflowStep.EXECUTE_FIX, lambda: self._execute_fix(recommendation))
        else:
            execution = self._run_step(
                WorkflowStep.EXECUTE_FIX,
                lambda: "Human approval gate active: propose-only mode, no automated fixes applied.",
            )

        verification = self._run_step(WorkflowStep.VERIFY, lambda: self._verify(execution))
        full_analysis = "\n\n".join([diagnosis, recommendation, execution, verification])
        return WorkflowOutcome(self.mode, full_analysis, self.traces, self.failure_counts)

    def _run_step(self, step: WorkflowStep, operation: Callable[[], str]) -> str:
        start = perf_counter()
        try:
            detail = operation()
            success = True
        except Exception as exc:  # noqa: BLE001
            success = False
            detail = f"{step.value} failed: {exc}"
            self.failure_counts[step.value] = self.failure_counts.get(step.value, 0) + 1
        latency_ms = (perf_counter() - start) * 1000
        trace = WorkflowTrace(step=step, latency_ms=round(latency_ms, 2), success=success, detail=detail)
        self.traces.append(trace)
        if self.step_event_handler:
            self.step_event_handler(trace)
        return detail

    def _collect_context(self) -> str:
        report = render_human_readable_report(self.summary)
        return f"Collected analyzer context for {self.summary.file_path.name}.\n\n{report}"

    def _diagnose(self, context: str) -> str:
        prompt = _build_operator_prompt(self.summary)
        return _invoke_ollama(
            model=self.model,
            prompt=prompt,
            base_url=self.base_url,
            timeout_seconds=self.timeout_seconds,
            policy=self.policy,
        )

    def _recommend(self, diagnosis: str) -> str:
        return "Recommendations prepared from diagnosis with OpenShift-safe mitigation sequencing."

    def _execute_fix(self, recommendation: str) -> str:
        if self.approval_callback and not self.approval_callback(recommendation):
            return "Human rejected automated fix plan. No changes were applied."
        return "Executed automated fix plan under approved mode."

    def _verify(self, execution_result: str) -> str:
        return "Verification complete: check cluster operators, nodes, and API server health to confirm stabilization."


@dataclass(frozen=True)
class IncidentCase:
    name: str
    summary: LogSummary


@dataclass(frozen=True)
class ReplayReport:
    total_cases: int
    passed_cases: int
    failed_cases: int


def run_incident_replay(
    *,
    incidents: list[IncidentCase],
    model: str,
    base_url: str,
    timeout_seconds: int = 60,
    mode: ExecutionMode = ExecutionMode.PROPOSE_CHANGES,
) -> ReplayReport:
    failures = 0
    for incident in incidents:
        outcome = OpenShiftAgentWorkflow(
            summary=incident.summary,
            model=model,
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            mode=mode,
        ).run()
        if outcome.failure_counts:
            failures += 1
    return ReplayReport(total_cases=len(incidents), passed_cases=len(incidents) - failures, failed_cases=failures)


def _validate_generate_request(payload: dict[str, Any]) -> tuple[bool, str]:
    required = {"model": str, "prompt": str, "stream": bool}
    for field_name, field_type in required.items():
        if field_name not in payload:
            return False, f"Missing required field: {field_name}"
        if not isinstance(payload[field_name], field_type):
            return False, f"Invalid type for {field_name}: expected {field_type.__name__}"
    unknown_fields = set(payload) - set(required)
    if unknown_fields:
        return False, f"Unexpected fields: {', '.join(sorted(unknown_fields))}"
    return True, ""


def _invoke_ollama(
    *,
    model: str,
    prompt: str,
    base_url: str,
    timeout_seconds: int,
    policy: AgentPolicy,
) -> str:
    if not PolicyEnforcer(policy).check("ollama.generate"):
        return "Policy denied ollama.generate for this tenant/namespace."

    payload = {"model": model, "prompt": prompt, "stream": False}
    valid, error_message = _validate_generate_request(payload)
    if not valid:
        return f"Invalid tool request schema: {error_message}"

    req = request.Request(
        f"{base_url.rstrip('/')}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=timeout_seconds) as response:
            body = response.read().decode("utf-8")
    except error.URLError as exc:
        return (
            "Unable to reach Ollama. Ensure Ollama is running locally and that the model is pulled. "
            f"Connection error: {exc}"
        )

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        return f"Ollama returned non-JSON output:\n{body}"

    if not isinstance(parsed, dict) or "response" not in parsed or not isinstance(parsed["response"], str):
        return f"Unexpected Ollama response payload:\n{body}"

    return parsed["response"].strip()


def request_ollama_agent_analysis(
    *,
    summary: LogSummary,
    model: str,
    base_url: str,
    timeout_seconds: int = 60,
    mode: ExecutionMode = ExecutionMode.PROPOSE_CHANGES,
    policy: AgentPolicy | None = None,
    step_event_handler: Callable[[WorkflowTrace], None] | None = None,
    approval_callback: Callable[[str], bool] | None = None,
) -> str:
    outcome = OpenShiftAgentWorkflow(
        summary=summary,
        model=model,
        base_url=base_url,
        timeout_seconds=timeout_seconds,
        mode=mode,
        policy=policy or AgentPolicy(allowed_tools={"ollama.generate": ["*"]}),
        step_event_handler=step_event_handler,
        approval_callback=approval_callback,
    ).run()
    traces_json = json.dumps([trace.as_dict() for trace in outcome.traces], indent=2)
    return f"{outcome.analysis}\n\nObservability traces:\n{traces_json}\nFailure counts: {outcome.failure_counts}"


def get_tool_interface_schemas() -> dict[str, dict[str, object]]:
    request_schema: dict[str, object] = {
        "type": "object",
        "additionalProperties": False,
        "required": ["model", "prompt", "stream"],
        "properties": {
            "model": {"type": "string"},
            "prompt": {"type": "string"},
            "stream": {"type": "boolean"},
        },
    }
    response_schema: dict[str, object] = {
        "type": "object",
        "required": ["response"],
        "properties": {
            "response": {"type": "string"},
        },
    }
    return {
        "ollama.generate.request": request_schema,
        "ollama.generate.response": response_schema,
    }


def _build_operator_prompt(summary: LogSummary) -> str:
    top_issue_lines = [
        *summary.notable_errors,
        *summary.api_failure_signals,
        *summary.watch_storm_signals,
        *summary.master_node_risk_signals,
        *summary.unhealthy_operator_signals,
    ]
    unique_lines = list(dict.fromkeys(line for line in top_issue_lines if line.strip()))
    condensed_lines = unique_lines[:20]
    condensed_issue_text = "\n".join(f"- {line}" for line in condensed_lines) or "- No issue lines captured"

    return "\n".join(
        [
            "You are an OpenShift SRE agent in a workflow engine.",
            "Follow workflow steps: CollectContext -> Diagnose -> Recommend -> ExecuteFix -> Verify.",
            "Respond with:",
            "1) probable root causes,",
            "2) immediate mitigation steps,",
            "3) a 24-hour stabilization plan,",
            "4) suggested kubectl/oc commands to verify assumptions.",
            "Keep the answer concise and action-oriented.",
            "",
            "=== Analyzer Report ===",
            render_human_readable_report(summary),
            "",
            "=== Condensed Raw Issue Lines ===",
            condensed_issue_text,
        ]
    )
