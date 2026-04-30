import json

from app import Handler
from src.ai_client import AIClientError
from src.constants import LEVELS
from src.levels import run_level


class DummyClient:
    def __init__(self, available=True, fail=False):
        self._available = available
        self._fail = fail

    def available(self):
        return self._available

    def chat(self, *_args, **_kwargs):
        if self._fail:
            raise AIClientError("down", code="x", status=503)
        if "return only integer" in (_args[0] if _args else ""):
            return "80"
        return "ok"


def test_run_level_all_levels_with_mock_client():
    for level in LEVELS:
        payload = run_level(level, DummyClient(available=True))
        assert payload["level"] == level
        assert "lines" in payload and payload["lines"]


def test_run_level_when_client_unavailable():
    payload = run_level(1, DummyClient(available=False))
    assert any("AI backend not configured" in line for line in payload["lines"])


def test_api_levels_shape_contains_request_id():
    class TestHandler(Handler):
        def __init__(self):
            pass

    h = TestHandler()
    captured = {}
    h.send_response = lambda code: captured.setdefault("code", code)
    h.send_header = lambda *_args: None
    h.end_headers = lambda: None
    h.wfile = type("W", (), {"write": lambda _self, b: captured.setdefault("body", b)})()
    h._send_json(200, {"request_id": "abc", "levels": LEVELS})
    body = json.loads(captured["body"].decode("utf-8"))
    assert captured["code"] == 200
    assert "request_id" in body
