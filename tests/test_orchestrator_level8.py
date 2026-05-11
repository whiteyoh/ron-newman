from src.agent_models import AgentTask
from src.constants import AGENTICNESS
from src.levels import run_level
from src.orchestrator import run_mini_orchestrator


class StableClient:
    def available(self):
        return True

    def chat(self, prompt, _context):
        p = prompt.lower()
        if "verifier" in p:
            return "supported: objective is covered"
        if "merger" in p:
            return "merged final answer"
        return "worker output"


class FlakyClient(StableClient):
    def __init__(self):
        self.fail_once = True

    def chat(self, prompt, context):
        p = prompt.lower()
        if "researcher" in p and self.fail_once:
            self.fail_once = False
            raise RuntimeError("temporary worker failure")
        return super().chat(prompt, context)


class UnsupportedClient(StableClient):
    def chat(self, prompt, context):
        p = prompt.lower()
        if "verifier" in p:
            return "unsupported: key gaps remain"
        return super().chat(prompt, context)


def test_level8_output_includes_taskboard_audit_and_approval_gate():
    lines = "\n".join(run_level(8, StableClient())["lines"])
    for needle in [
        "Taskboard:",
        "Audit trail:",
        "Approval gate:",
        "approval required: yes",
        "approved for merge: yes",
        "merge policy:",
    ]:
        assert needle in lines


def test_orchestrator_successful_parallel_run():
    result = run_mini_orchestrator(StableClient(), AgentTask(objective="x"), parallel=True)
    assert result["mode"] == "parallel"
    assert result["approved_for_merge"] is True
    assert result["status"] == "merged"
    assert any("completed worker:" in e for e in result["audit_log"])


def test_orchestrator_worker_failure_then_retry():
    result = run_mini_orchestrator(FlakyClient(), AgentTask(objective="x"), parallel=False)
    researcher = next(t for t in result["taskboard"] if t["worker_name"] == "researcher")
    assert researcher["attempt"] == 2
    assert any("retried worker: researcher" in e for e in result["audit_log"])


def test_orchestrator_unsupported_verifier_needs_human_review_and_blocks_merger():
    result = run_mini_orchestrator(UnsupportedClient(), AgentTask(objective="x"), parallel=True)
    assert result["approved_for_merge"] is False
    assert result["status"] == "needs_human_review"
    assert result["final_answer"] == "needs human review"
    assert any("merge decision: blocked" in e for e in result["audit_log"])


def test_level8_yegge_alignment_score_increased_by_one():
    assert AGENTICNESS[8]["score"] == 8
    assert AGENTICNESS[8]["yegge_alignment_score"] == 9


def test_level8_custom_outage_input_produces_customer_update_sections():
    class OutageClient(StableClient):
        def chat(self, prompt, context):
            p = prompt.lower()
            if "merger" in p:
                return (
                    "Draft customer update\n\n"
                    "We experienced a service outage lasting 42 minutes.\n\n"
                    "Confirmed facts:\n- Service unavailable for 42 minutes\n"
                    "Current assumption / still being verified:\n- Likely failed database connection pool\n"
                    "Check before sending:\n- Confirm recovery and timeline\n"
                    "Internal approval checklist:\n- Incident lead, support lead, communications owner"
                )
            return super().chat(prompt, context)

    custom_context = (
        "Goal: customer update for outage; Audience: non-technical customers and senior managers; "
        "Constraints: calm, honest, plain English, separate facts from assumptions."
    )
    payload = run_level(8, OutageClient(), use_case_key="custom", use_case_context=custom_context)
    text = "\n".join(payload["lines"]).lower()
    assert "draft customer update" in text
    assert "confirmed facts" in text
    assert "current assumption" in text or "still being verified" in text
    assert "check before sending" in text
    assert "internal approval checklist" in text
