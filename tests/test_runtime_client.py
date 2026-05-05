from src.ai_client import AIClientError
from src.runtime_client import SAFE_PLACEHOLDER, CapturedAIClient


class InnerOK:
    def __init__(self):
        self.called = 0

    def available(self):
        return True

    def chat(self, *_args, **_kwargs):
        self.called += 1
        return "hello"


class InnerAIError:
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


class InnerBoom:
    def available(self):
        return True

    def chat(self, *_args, **_kwargs):
        raise RuntimeError("Authorization: Bearer sk-secret")


def test_captured_client_delegates_available_and_success_chat():
    inner = InnerOK()
    client = CapturedAIClient(inner)
    assert client.available() is True
    assert client.chat("sys", "user") == "hello"
    assert inner.called == 1
    assert not client.has_errors


def test_captured_client_handles_ai_client_error_safely():
    client = CapturedAIClient(InnerAIError())
    assert client.chat("sys", "user") == SAFE_PLACEHOLDER
    assert client.has_errors
    assert client.errors[0].code == "upstream_http"
    assert client.errors[0].status == 502


def test_captured_client_handles_unexpected_error_safely_and_redacts_secret_text():
    client = CapturedAIClient(InnerBoom())
    assert client.chat("sys", "user") == SAFE_PLACEHOLDER
    assert client.has_errors
    assert client.errors[0].message == "Unexpected AI runtime error during model call."
    blob = str(client.errors[0]).lower()
    assert "authorization" not in blob
    assert "api_key" not in blob
