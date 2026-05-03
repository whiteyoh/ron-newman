from src.constants import AGENTICNESS
from src.levels import run_level


class DummyClient:
    def available(self):
        return True

    def chat(self, prompt, _context):
        p = prompt.lower()
        if "return strict json only" in p:
            return '{"action":"use_calculator","tool_input":"17*43","final_answer":""}'
        if "sufficient" in p:
            return "sufficient: evidence directly defines SMART"
        if "fully supported" in p:
            return "supported: answer quotes provided evidence"
        if "verify against objective" in p:
            return "weak: missing differentiation"
        if "revise to fix" in p:
            return "revised agenda with differentiation"
        if "score this draft" in p:
            return "75"
        if "verify final answer" in p:
            return "safe: aligns to objective"
        return "ok"


def text(level):
    return "\n".join(run_level(level, DummyClient())["lines"])


def test_level3_model_selected_action_trace():
    t = text(3)
    assert "Model selected action:" in t and "Tool result:" in t


def test_level4_evidence_sufficiency_support_trace():
    t = text(4)
    assert "Evidence source:" in t and "Sufficiency check:" in t and "Support verifier:" in t


def test_level5_verify_and_revision_decision():
    t = text(5)
    assert "Verification result:" in t and "Revision decision:" in t


def test_level6_bounded_scoring_loop():
    t = text(6)
    assert "Attempt number:" in t and "Score:" in t and "Selected final answer:" in t


def test_level7_policy_budget_verdict():
    t = text(7)
    for needle in [
        "Agent policy:",
        "Action budget remaining:",
        "Final verifier step:",
        "Structured run summary:",
        "final_verdict:",
    ]:
        assert needle in t


def test_level8_orchestrator_roles_trace():
    t = text(8)
    for role in ["planner", "researcher", "teacher_resource_writer", "critic"]:
        assert role in t
    assert "verifier result:" in t and "merge policy:" in t


def test_agenticness_yegge_fields_and_raised_scores():
    for lvl in range(1, 9):
        assert "yegge_alignment_score" in AGENTICNESS[lvl]
        assert "closest_yegge_stage" in AGENTICNESS[lvl]
    assert AGENTICNESS[3]["score"] >= 4
    assert AGENTICNESS[4]["score"] >= 4
    assert AGENTICNESS[5]["score"] >= 4
    assert AGENTICNESS[6]["score"] >= 5
    assert AGENTICNESS[7]["score"] >= 7
    assert AGENTICNESS[8]["score"] >= 7
