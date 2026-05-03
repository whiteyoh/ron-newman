from src.constants import AGENTICNESS, LEVELS
from src.levels import run_level


class DummyClient:
    def available(self):
        return True

    def chat(self, prompt, _context):
        p = prompt.lower()
        if "verifier" in p:
            return "supported: objective covered"
        if "merger" in p:
            return "merged final answer"
        if "score this draft" in p:
            return "89"
        return "ok"


def test_structured_payload_fields_all_levels():
    keys = {
        "lines",
        "agenticness",
        "score_summary",
        "yegge_simulation",
        "yegge_score_summary",
        "theatre_steps",
        "replay_steps",
        "why_not_production",
    }
    for level in LEVELS:
        payload = run_level(level, DummyClient())
        assert keys.issubset(payload)
        assert AGENTICNESS[level]["yegge_alignment_score"] >= 8
        assert payload["theatre_steps"]
        assert len(set(step["label"] for step in payload["theatre_steps"])) > 1


def test_level8_taskboard_and_approval_summary():
    p8 = run_level(8, DummyClient())
    assert isinstance(p8["taskboard"], list)
    assert p8["taskboard"] and "worker_name" in p8["taskboard"][0]
    for k in ["approval_required", "approved", "merge_decision", "verifier_result", "merge_policy"]:
        assert k in p8["approval_summary"]


def test_no_levels_1_to_7_claim_production_autonomy():
    for level in range(1, 8):
        payload = run_level(level, DummyClient())
        text = str(payload).lower()
        assert "real shell execution" not in text
        assert "real shell execution" not in text
