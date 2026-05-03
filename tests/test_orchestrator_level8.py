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
        "verifier result:",
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
