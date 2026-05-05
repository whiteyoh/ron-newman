import io
from urllib.error import HTTPError, URLError

import pytest

import src.ai_client as ai
from src.ai_client import AIClient, AIClientError


def test_ai_client_default_model_when_unset(monkeypatch):
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    assert AIClient().model == "gpt-4.1-mini"


def test_ai_client_model_override_from_env(monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "gpt-5-mini")
    assert AIClient().model == "gpt-5-mini"


def test_build_chat_payload_shape():
    client = AIClient()
    client.model = "gpt-4.1-mini"

    payload = client._build_chat_payload("sys", "user", 0.2)

    assert payload["model"] == "gpt-4.1-mini"
    assert payload["temperature"] == 0.2
    assert payload["messages"] == [
        {"role": "system", "content": "sys"},
        {"role": "user", "content": "user"},
    ]
    assert "reasoning" not in payload


def test_ai_client_unavailable_raises(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(AIClientError, match="OPENAI_API_KEY"):
        AIClient().chat("s", "u")


def test_ai_client_http_error(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")

    def boom(*_args, **_kwargs):
        raise HTTPError("u", 500, "bad", {}, io.BytesIO(b'{"error":"bad"}'))

    monkeypatch.setattr(ai, "urlopen", boom)
    with pytest.raises(AIClientError) as err:
        AIClient().chat("s", "u")
    assert err.value.status == 502
    assert err.value.code == "upstream_http"
    assert "configured model" in err.value.message
    assert "OPENAI_MODEL" in err.value.message
    assert '{"error":"bad"}' not in err.value.message
    assert "sk-" not in err.value.message


def test_ai_client_connection_error(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setattr(
        ai, "urlopen", lambda *_a, **_k: (_ for _ in ()).throw(URLError("no route"))
    )
    with pytest.raises(AIClientError) as err:
        AIClient().chat("s", "u")
    assert err.value.code == "upstream_connection"


def test_ai_client_timeout(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setattr(
        ai, "urlopen", lambda *_a, **_k: (_ for _ in ()).throw(TimeoutError("late"))
    )
    with pytest.raises(AIClientError) as err:
        AIClient().chat("s", "u")
    assert err.value.code == "upstream_timeout"


def test_ai_client_invalid_json(monkeypatch):
    class Resp:
        def __enter__(self):
            return self

        def __exit__(self, *_a):
            return False

        def read(self):
            return b"not-json"

    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setattr(ai, "urlopen", lambda *_a, **_k: Resp())
    with pytest.raises(AIClientError) as err:
        AIClient().chat("s", "u")
    assert err.value.code == "upstream_json"


def test_ai_client_unexpected_schema(monkeypatch):
    class Resp:
        def __enter__(self):
            return self

        def __exit__(self, *_a):
            return False

        def read(self):
            return b"{}"

    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setattr(ai, "urlopen", lambda *_a, **_k: Resp())
    with pytest.raises(AIClientError) as err:
        AIClient().chat("s", "u")
    assert err.value.code == "upstream_schema"
