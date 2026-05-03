from src.constants import AGENTICNESS, LEVELS
from src.levels import run_level


class DummyClient:
    def available(self):
        return True

    def chat(self, prompt, _context):
        p = prompt.lower()
        if "score this draft" in p:
            return "80"
        if "verifier" in p:
            return "supported: good"
        return "ok"


def test_all_levels_have_yegge_simulation_and_score():
    for level in LEVELS:
        payload = run_level(level, DummyClient())
        assert payload["yegge_simulation"]
        assert AGENTICNESS[level]["yegge_alignment_score"] >= 8
        assert payload["why_not_production"]


def test_level_specific_mechanics():
    p2 = run_level(2, DummyClient())
    assert p2["permission_flow"] is not None
    assert p2["diff_preview"]

    p3 = run_level(3, DummyClient())
    assert "yolo" in str(p3["permission_flow"]).lower()
    assert "post-run" in str(p3["review_gate"]).lower()

    p5 = run_level(5, DummyClient())
    assert p5["command_preview"]["run_id"]

    p6 = run_level(6, DummyClient())
    assert 3 <= len(p6["parallel_agents"]) <= 5

    p7 = run_level(7, DummyClient())
    assert len(p7["parallel_agents"]) >= 10


def test_level8_taskboard_is_real_orchestrator_data():
    p8 = run_level(8, DummyClient())
    assert p8["taskboard"]
    assert any("worker_name" in w for w in p8["taskboard"])
