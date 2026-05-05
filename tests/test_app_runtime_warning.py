from __future__ import annotations

import json
import threading
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer

from app import Handler


def _serve(server: ThreadingHTTPServer) -> None:
    server.serve_forever()


def _request(port: int, payload: dict):
    conn = HTTPConnection("127.0.0.1", port, timeout=5)
    conn.request(
        "POST",
        "/api/run",
        body=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    resp = conn.getresponse()
    data = resp.read()
    conn.close()
    return resp.status, json.loads(data)


def test_api_run_returns_structured_warning_when_model_calls_fail(monkeypatch):
    from src.ai_client import AIClientError

    class FakeAIClient:
        def __init__(self):
            self.model = "gpt-4.1-mini"
            self.base_url = "https://api.openai.com/v1"

        def available(self):
            return True

        def chat(self, *_args, **_kwargs):
            raise AIClientError(
                (
                    "Upstream AI provider returned an error for the configured model. "
                    "Check OPENAI_MODEL, model access, quota, and billing."
                ),
                code="upstream_http",
                status=502,
            )

    monkeypatch.setattr("app.AIClient", FakeAIClient)
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    t = threading.Thread(target=_serve, args=(server,), daemon=True)
    t.start()
    try:
        for level in range(1, 9):
            status, payload = _request(port=server.server_port, payload={"level": level})
            assert status == 200
            assert payload["lines"]
            assert payload["score_summary"]
            assert payload["theatre_steps"]
            assert payload["replay_steps"]
            assert payload["runtime_error"]["code"] == "upstream_http"
            assert payload["runtime_errors"]
            assert payload["approval_summary"]["approved"] is False
            assert payload["approval_summary"]["final_status"] == "needs_human_review"
            assert any("AI call failed safely" in step for step in payload["replay_steps"])
            blob = str(payload)
            assert "Authorization" not in blob
            assert "api_key" not in blob.lower()
    finally:
        server.shutdown()
        server.server_close()
