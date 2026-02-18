from __future__ import annotations

import json
from pathlib import Path

from openshift_log_analyzer import analyze_log_file
from openshift_log_analyzer.ollama_agent import request_ollama_agent_analysis


class _FakeResponse:
    def __init__(self, payload: dict[str, str]) -> None:
        self._body = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False


def test_request_ollama_agent_analysis_uses_local_generate_endpoint(monkeypatch, tmp_path: Path) -> None:
    log_file = tmp_path / "cluster.log"
    log_file.write_text("ERROR namespace=foo kube-apiserver unavailable\n", encoding="utf-8")
    summary = analyze_log_file(log_file)

    seen: dict[str, str] = {}

    def fake_urlopen(req, timeout: int = 60):
        seen["url"] = req.full_url
        seen["method"] = req.get_method()
        seen["body"] = req.data.decode("utf-8")
        seen["timeout"] = str(timeout)
        return _FakeResponse({"response": "agent output"})

    monkeypatch.setattr("openshift_log_analyzer.ollama_agent.request.urlopen", fake_urlopen)

    output = request_ollama_agent_analysis(
        summary=summary,
        model="llama3.2",
        base_url="http://127.0.0.1:11434/",
    )

    assert output == "agent output"
    assert seen["url"] == "http://127.0.0.1:11434/api/generate"
    assert seen["method"] == "POST"
    assert seen["timeout"] == "60"
    body = json.loads(seen["body"])
    assert body["model"] == "llama3.2"
    assert body["stream"] is False
    assert "OpenShift SRE agent" in body["prompt"]


def test_request_ollama_agent_analysis_returns_helpful_error_when_ollama_unreachable(tmp_path: Path) -> None:
    log_file = tmp_path / "cluster.log"
    log_file.write_text("ERROR namespace=foo kube-apiserver unavailable\n", encoding="utf-8")
    summary = analyze_log_file(log_file)

    output = request_ollama_agent_analysis(
        summary=summary,
        model="llama3.2",
        base_url="http://127.0.0.1:1",
        timeout_seconds=1,
    )

    assert "Unable to reach Ollama" in output
