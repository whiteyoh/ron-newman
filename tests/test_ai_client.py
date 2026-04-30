import pytest
from urllib.error import URLError

import src.ai_client as ai
from src.ai_client import AIClient, AIClientError


def test_ai_client_unavailable_raises(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = AIClient()
    with pytest.raises(AIClientError) as err:
        client.chat("s", "u")
    assert err.value.status == 503


def test_ai_client_connection_error(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "x")

    def boom(*_args, **_kwargs):
        raise URLError("no route")

    monkeypatch.setattr(ai, "urlopen", boom)
    client = AIClient()
    with pytest.raises(AIClientError) as err:
        client.chat("s", "u")
    assert err.value.code == "upstream_connection"
