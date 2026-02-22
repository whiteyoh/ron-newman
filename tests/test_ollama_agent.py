from __future__ import annotations

import json
from pathlib import Path

from openshift_log_analyzer import analyze_log_file
from openshift_log_analyzer.ollama_agent import (
    AgentPolicy,
    ExecutionMode,
    IncidentCase,
    WorkflowStep,
    get_tool_interface_schemas,
    request_ollama_agent_analysis,
    run_incident_replay,
)


class _FakeResponse:
    def __init__(self, payload: dict[str, str]) -> None:
        self._body = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False


def test_request_ollama_agent_analysis_runs_workflow_and_emits_observability(monkeypatch, tmp_path: Path) -> None:
    log_file = tmp_path / "cluster.log"
    log_file.write_text("ERROR namespace=foo kube-apiserver unavailable\n", encoding="utf-8")
    summary = analyze_log_file(log_file)

    seen: dict[str, str] = {}

    def fake_urlopen(req, timeout: int = 60):
        seen["url"] = req.full_url
        seen["method"] = req.get_method()
        seen["body"] = req.data.decode("utf-8")
        seen["timeout"] = str(timeout)
        return _FakeResponse({"response": "agent diagnosis"})

    monkeypatch.setattr("openshift_log_analyzer.ollama_agent.request.urlopen", fake_urlopen)

    output = request_ollama_agent_analysis(
        summary=summary,
        model="llama3.2",
        base_url="http://127.0.0.1:11434/",
        mode=ExecutionMode.PROPOSE_CHANGES,
    )

    assert "agent diagnosis" in output
    assert "Human approval gate active" in output
    assert "Observability traces" in output
    for step in WorkflowStep:
        assert step.value in output

    assert seen["url"] == "http://127.0.0.1:11434/api/generate"
    assert seen["method"] == "POST"
    assert seen["timeout"] == "60"
    body = json.loads(seen["body"])
    assert body["model"] == "llama3.2"
    assert body["stream"] is False


def test_request_ollama_agent_analysis_enforces_policy(tmp_path: Path) -> None:
    log_file = tmp_path / "cluster.log"
    log_file.write_text("ERROR namespace=foo kube-apiserver unavailable\n", encoding="utf-8")
    summary = analyze_log_file(log_file)

    output = request_ollama_agent_analysis(
        summary=summary,
        model="llama3.2",
        base_url="http://127.0.0.1:11434",
        policy=AgentPolicy(tenant="acme", namespace="dev", allowed_tools={"ollama.generate": ["other:ns"]}),
    )

    assert "Policy denied ollama.generate" in output


def test_tool_schema_and_replay_harness(tmp_path: Path) -> None:
    log_file = tmp_path / "cluster.log"
    log_file.write_text("ERROR namespace=foo kube-apiserver unavailable\n", encoding="utf-8")
    summary = analyze_log_file(log_file)

    schemas = get_tool_interface_schemas()
    assert "ollama.generate.request" in schemas
    assert schemas["ollama.generate.request"]["type"] == "object"

    report = run_incident_replay(
        incidents=[IncidentCase(name="incident-1", summary=summary)],
        model="llama3.2",
        base_url="http://127.0.0.1:1",
        timeout_seconds=1,
    )
    assert report.total_cases == 1
    assert report.passed_cases == 1
    assert report.failed_cases == 0
