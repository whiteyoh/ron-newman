from src.ai_client import AIClientError
from src.constants import LEVELS
from src.levels import run_level
from src.runtime_client import CapturedAIClient


class FailingClient:
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


def test_levels_return_payload_when_ai_calls_fail_safely():
    for level in LEVELS:
        wrapper = CapturedAIClient(FailingClient())
        payload = run_level(level, wrapper)
        assert payload["lines"]
        assert payload["score_summary"]
        assert payload["theatre_steps"]
        assert payload["replay_steps"]
        assert wrapper.has_errors
        text = str(payload)
        assert "Authorization" not in text
        assert "api_key" not in text.lower()
