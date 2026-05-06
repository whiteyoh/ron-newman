from src.constants import AGENTICNESS, LEVELS
from src.levels import run_level


class DummyClient:
    def __init__(self):
        self.chat_calls = 0

    def available(self):
        return True

    def chat(self, prompt, _context):
        self.chat_calls += 1
        p = prompt.lower()
        if "verifier" in p:
            return "supported: objective covered"
        if "merger" in p:
            return "merged final answer"
        if "score this draft" in p:
            return "89"
        return "ok"


class UnavailableClient(DummyClient):
    def available(self):
        return False


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
        "final_answer",
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


def test_level1_score_and_baseline_metadata():
    l1 = AGENTICNESS[1]
    assert l1["score"] == 10
    assert l1["capability_score"] == 1
    assert l1["agenticness_score"] <= 2
    assert l1["yegge_alignment_score"] == 10
    assert l1["uses_tools"] is False
    assert l1["loops"] is False
    assert l1["runs_independently"] is False
    assert l1["self_verifies"] is False
    assert l1["multi_agent"] is False


def test_level1_runtime_is_single_completion_baseline():
    client = DummyClient()
    payload = run_level(1, client)
    assert client.chat_calls == 1
    assert payload["approval_summary"]["final_status"] == "needs_human_review"
    assert payload["approval_summary"]["verifier_result"] == "not run"
    labels = [s["label"] for s in payload["theatre_steps"]]
    assert "Human prompt provided" in labels
    assert "Model continuation generated" in labels
    assert "Human decides next" in labels
    assert payload["replay_steps"] == [
        f"{s['label']}: {s['summary']}" for s in payload["theatre_steps"]
    ]
    text = " ".join(payload["lines"]).lower()
    assert "no tools used" in text
    assert "no tool use" in text
    assert "tool-action" not in text
    assert "tool result" not in text
    assert "selected action" not in text
    assert "orchestration" not in text
    assert "production autonomy" not in text
    assert payload["approval_summary"]["merge_decision"] == "human_decides"


def test_level1_no_key_fallback_is_structured_and_no_chat():
    client = UnavailableClient()
    payload = run_level(1, client)
    assert client.chat_calls == 0
    assert payload["approval_summary"]["final_status"] == "needs_human_review"
    assert payload["approval_summary"]["merge_decision"] == "human_decides"
    assert any("AI backend not configured" in line for line in payload["lines"])
    continuation_step = next(
        s for s in payload["theatre_steps"] if s["label"] == "Model continuation not generated"
    )
    assert "not generated" in continuation_step["detail"].lower()


def test_no_key_fallback_levels_2_to_8_are_level_aware_and_no_chat():
    client = UnavailableClient()
    for level in range(2, 9):
        payload = run_level(level, client)
        assert payload["score_summary"]
        assert payload["theatre_steps"]
        assert payload["replay_steps"]
        assert payload["approval_summary"]
        assert payload["stage_summary"]
        assert payload["lines"]
        assert any("AI backend not configured" in line for line in payload["lines"])
        assert payload["approval_summary"]["final_status"] == "needs_human_review"
        assert payload["approval_summary"]["merge_decision"] == "not_run"
        theatre_labels = [s["label"] for s in payload["theatre_steps"]]
        assert "Level could not run" in theatre_labels
        assert "No model call attempted" in theatre_labels
        assert "Model continuation generated" not in theatre_labels
        assert "Human prompt provided" not in theatre_labels
        text = str(payload).lower()
        assert "level could not run" in text
        assert "was not executed" in text
        assert "merged final answer" not in text
        assert "production-ready" not in text
    assert client.chat_calls == 0


def test_level8_top_level_final_answer_is_present_and_useful():
    payload = run_level(8, DummyClient())
    final_answer = str(payload.get("final_answer", "")).strip()

    assert final_answer
    assert final_answer == str(payload.get("final_answer")).strip()
    assert not final_answer.lower().startswith("honest limitation note")
    assert not final_answer.lower().startswith("workshop-safe")
