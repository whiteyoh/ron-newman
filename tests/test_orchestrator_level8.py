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


def test_level8_custom_input_produces_requested_artifact_sections():
    class ArtifactClient(StableClient):
        def chat(self, prompt, context):
            p = prompt.lower()
            if "merger" in p:
                return (
                    "Draft output\n\n"
                    "Summary based on confirmed information.\n\n"
                    "Assumptions:\n- Pending verification item\n"
                    "Checks before use:\n- Confirm latest inputs\n"
                    "Next steps:\n- Route for human approval"
                )
            return super().chat(prompt, context)

    custom_context = (
        "Goal: Create a customer-facing update based on confirmed facts and assumptions. "
        "Audience: Non-technical readers. Constraints: Plain English, "
        "do not invent facts, include checks before use."
    )
    payload = run_level(8, ArtifactClient(), use_case_key="custom", use_case_context=custom_context)
    text = "\n".join(payload["lines"]).lower()
    assert "draft output" in text
    assert "assumptions" in text
    assert "checks before use" in text
    assert "final answer:" in text


def test_level8_merger_prompt_requires_artifact_first_and_not_generic_guidance():
    class PromptCaptureClient(StableClient):
        def __init__(self):
            self.merger_prompt = ""

        def chat(self, prompt, context):
            if "you are merger" in prompt.lower():
                self.merger_prompt = prompt
                return "Draft update\n\nCheck before use:\n- Confirm dates"
            return super().chat(prompt, context)

    client = PromptCaptureClient()
    run_level(
        8,
        client,
        use_case_key="custom",
        use_case_context=(
            "Goal: Create a customer-facing update from provided facts and assumptions. "
            "Audience: Non-technical readers. Constraints: Plain English. Do not invent facts."
        ),
    )
    prompt = client.merger_prompt.lower()
    assert "produce the user-requested output first" in prompt
    assert "do not default to generic guidance" in prompt
    assert "guidance for preparing" in prompt
    assert "check before use" in prompt


def test_level8_output_order_and_single_verifier_result():
    lines = run_level(
        8,
        StableClient(),
        use_case_key="custom",
        use_case_context="Goal: Draft a short status update.",
    )["lines"]
    text = "\n".join(lines)
    assert text.count("Verifier result:") == 1
    assert "verifier result:" not in text
    assert "teacher-resource-writer" not in text.lower()
    assert "nourishment:" not in text
    assert "what this level shows: what this level shows:" not in text.lower()
    assert "topic tip: optimization tip" not in text.lower()
    assert "practical guidance for preparing" not in text.lower()
    expected = [
        "Running Level 8",
        "What this level shows:",
        "Run focus:",
        "Confirmed user context:",
        "Orchestrator summary:",
        "Taskboard:",
        "Verifier result:",
        "Approval gate:",
        "Final answer:",
        "honest limitation note:",
    ]
    positions = [text.index(marker) for marker in expected]
    assert positions == sorted(positions)


def test_level8_workshop_safe_limitations_remain_visible():
    text = "\n".join(run_level(8, StableClient())["lines"]).lower()
    assert "workshop-safe orchestrator simulation" in text
    assert "no real external action was taken" in text
    assert "human review is required before use" in text
