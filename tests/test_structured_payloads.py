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


ACCEPTED_STATUSES = {
    "pending",
    "running",
    "completed",
    "approved",
    "blocked",
    "needs_human_review",
    "merged",
    "failed",
}


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
        "approval_summary",
    }
    for level in LEVELS:
        payload = run_level(level, DummyClient())
        assert keys.issubset(payload)
        assert AGENTICNESS[level]["yegge_alignment_score"] >= 8
        assert payload["theatre_steps"]
        for step in payload["theatre_steps"]:
            assert {"label", "actor", "status", "summary", "detail"}.issubset(step)
            assert step["status"] in ACCEPTED_STATUSES
        assert payload["replay_steps"] == [
            f"{s['label']}: {s['summary']}" for s in payload["theatre_steps"]
        ]
        approval = payload["approval_summary"]
        for k in [
            "approval_required",
            "approved",
            "merge_decision",
            "verifier_result",
            "merge_policy",
            "final_status",
        ]:
            assert k in approval


def test_level7_action_and_swarm_summary():
    p7 = run_level(7, DummyClient())
    action_steps = [s for s in p7["theatre_steps"] if s["label"] == "Action selected"]
    assert action_steps
    assert any("Iteration" in s["summary"] and ":" in s["summary"] for s in action_steps)
    assert p7["swarm_summary"]["total_agents"] >= 10


def test_level8_taskboard_and_approval_summary_shapes():
    p8 = run_level(8, DummyClient())
    assert isinstance(p8["taskboard"], list)
    assert p8["taskboard"]
    for rec in p8["taskboard"]:
        assert {"worker_name", "worker_role", "task", "status", "attempt"}.issubset(rec)
    assert p8["approval_summary"]["final_status"] in {
        "merged",
        "needs_human_review",
        "failed",
        "blocked",
        "completed",
    }
    assert p8["approval_summary"]["final_status"] != p8["stage_summary"]["name"]


def test_no_levels_1_to_7_claim_production_autonomy():
    banned = [
        "real shell execution",
        "real file writes",
        "github writes",
        "production orchestrator",
        "fully autonomous",
    ]
    for level in range(1, 8):
        payload = run_level(level, DummyClient())
        text = str(payload).lower()
        for phrase in banned:
            assert phrase not in text


def test_level8_theatre_lifecycle_and_worker_mapping():
    p8 = run_level(8, DummyClient())
    labels = [s["label"] for s in p8["theatre_steps"]]
    assert "Orchestrator run created" in labels
    assert "Policy loaded" in labels
    assert "Verification performed" in labels
    assert "Human approval gate" in labels
    assert "Final verdict" in labels

    worker_steps = [s for s in p8["theatre_steps"] if s["label"].startswith("Worker ")]
    assert worker_steps
    assert len(worker_steps) >= len(p8["taskboard"])
    worker_names = {rec["worker_name"] for rec in p8["taskboard"]}
    joined = " ".join(f"{s['summary']} {s['detail']}" for s in worker_steps)
    for worker in worker_names:
        assert worker in joined

    assert p8["replay_steps"] == [f"{s['label']}: {s['summary']}" for s in p8["theatre_steps"]]
    for step in p8["theatre_steps"]:
        assert step["status"] in ACCEPTED_STATUSES
