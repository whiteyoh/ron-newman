from src.constants import LEVELS
from src.levels import run_level


class DummyClient:
    def available(self):
        return True

    def chat(self, *_args, **_kwargs):
        return "ok"


def test_structured_fields_and_scores():
    for level in LEVELS:
        payload = run_level(level, DummyClient())
        assert payload["lines"]
        assert payload["agenticness"]["score"] <= 7 or level in {1, 7, 8}
        assert "score_summary" in payload
        assert "theatre_steps" in payload
        assert "replay_steps" in payload
        if level == 1:
            text = "\n".join(payload["lines"]).lower()
            for k in ["prompt-only baseline", "one model continuation", "human decides next"]:
                assert k in text
        elif level <= 6:
            text = "\n".join(payload["lines"]).lower()
            for k in ["policy", "verification", "approval", "audit", "final verdict"]:
                assert k in text
        if level == 8:
            assert payload["taskboard"] is not None
            text = "\n".join(payload["lines"]).lower()
            assert "simulated orchestration" in text
            assert "merge policy" in text
