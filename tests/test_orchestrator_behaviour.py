from src.agent_models import AgentTask
from src.orchestrator import run_mini_orchestrator


class SupportedClient:
    def available(self):
        return True

    def chat(self, prompt, _context):
        p = prompt.lower()
        if "verifier" in p:
            return "supported: objective covered"
        if "merger" in p:
            return "merged answer"
        return "worker output"


class UnsupportedVerifierClient(SupportedClient):
    def chat(self, prompt, context):
        if "verifier" in prompt.lower():
            return "unsupported: missing constraints"
        return super().chat(prompt, context)


class FailOnceClient(SupportedClient):
    def __init__(self):
        self.failed = False

    def chat(self, prompt, context):
        if "researcher" in prompt.lower() and not self.failed:
            self.failed = True
            raise RuntimeError("transient failure")
        return super().chat(prompt, context)


def test_supported_verifier_allows_merge_and_statuses_merged():
    result = run_mini_orchestrator(SupportedClient(), AgentTask(objective="x"), parallel=False)
    assert result["approved_for_merge"] is True
    assert result["status"] == "merged"
    assert all(t["status"] == "merged" for t in result["taskboard"])


def test_unsupported_verifier_blocks_merge_and_needs_review_statuses():
    result = run_mini_orchestrator(
        UnsupportedVerifierClient(), AgentTask(objective="x"), parallel=False
    )
    assert result["approved_for_merge"] is False
    assert result["status"] == "needs_human_review"
    assert all(t["status"] == "needs_human_review" for t in result["taskboard"])


def test_failed_worker_retries_once_and_audit_log_contains_lifecycle_events():
    result = run_mini_orchestrator(FailOnceClient(), AgentTask(objective="x"), parallel=False)
    rec = next(t for t in result["taskboard"] if t["worker_name"] == "researcher")
    assert rec["attempt"] == 2
    log = "\n".join(result["audit_log"]).lower()
    for needle in [
        "created task",
        "started worker",
        "completed worker",
        "verifier completed",
        "approval decision",
        "merge decision",
    ]:
        assert needle in log
