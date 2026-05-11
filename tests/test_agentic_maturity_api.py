from src.agentic_maturity import AGENTIC_MATURITY_STAGES, ASSESSMENT_QUESTIONS
from src.constants import AGENTICNESS
from src.levels import run_level


class DummyClient:
    def available(self):
        return True

    def chat(self, *_args, **_kwargs):
        return "ok"


def test_maturity_has_eight_stages_and_required_fields():
    assert len(AGENTIC_MATURITY_STAGES) == 8
    required = {
        "id",
        "name",
        "plain_english_summary",
        "how_it_feels",
        "what_the_human_does",
        "what_the_agent_does",
        "trust_level",
        "autonomy_level",
        "risk",
        "example_workflow",
        "evidence_of_this_level",
        "next_step_to_level_up",
    }
    for stage in AGENTIC_MATURITY_STAGES:
        assert required.issubset(stage.keys())


def test_assessment_questions_exist():
    assert len(ASSESSMENT_QUESTIONS) >= 6


def test_agenticness_scores_exist_for_all_levels():
    for level in range(1, 9):
        assert level in AGENTICNESS
        assert "score" in AGENTICNESS[level]


def test_run_level_has_agenticness_for_every_level():
    for level in range(1, 9):
        payload = run_level(level, DummyClient())
        assert "agenticness" in payload
        for field in (
            "score",
            "explanation",
            "chooses_actions",
            "uses_tools",
            "loops",
            "runs_independently",
            "self_verifies",
            "multi_agent",
        ):
            assert field in payload["agenticness"]


def test_level7_trace_has_action_observation_stop_condition():
    payload = run_level(7, DummyClient())
    text = "\n".join(payload["lines"])
    assert "Agent loop timeline:" in text
    assert "Chosen action:" in text
    assert "Observation:" in text
    assert "Stop condition:" in text


def test_level8_orchestrator_roles_present():
    payload = run_level(8, DummyClient())
    text = "\n".join(payload["lines"])
    assert "Orchestrator summary:" in text
    assert "planner" in text
    assert "critic" in text
    assert "content writer" in text
    assert "verifier" in text
