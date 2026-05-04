from src.constants import AGENTICNESS
from src.levels import run_level


class DummyClient:
    def available(self):
        return True

    def chat(self, prompt, _context):
        p = prompt.lower()
        if "score this draft" in p:
            return "75"
        if "exact 7-word" in p:
            return "pass: exactly seven words"
        if "verify" in p:
            return "safe: verified"
        return "ok"


def text(level):
    return "\n".join(run_level(level, DummyClient())["lines"])


def test_level1_is_prompt_only_baseline():
    t = text(1).lower()
    for phrase in [
        "prompt-only baseline",
        "one model continuation",
        "no tools used",
        "no verification performed",
        "human decides next",
        "final suggestion",
    ]:
        assert phrase in t


def test_levels_2_to_6_agentic_mechanics_visible():
    for lvl in range(2, 7):
        t = text(lvl)
        assert ("Policy" in t) or ("policy" in t.lower())
        assert ("Verification" in t) or ("verification" in t.lower())
        assert ("Approval gate" in t) or ("approval" in t.lower())
        assert "Final verdict" in t
        assert "Audit trail" in t


def test_level1_score_is_perfect_baseline_alignment():
    assert AGENTICNESS[1]["score"] == 10
    assert AGENTICNESS[1]["agenticness_score"] <= 2
    assert AGENTICNESS[1]["yegge_alignment_score"] == 10


def test_levels_2_to_6_scores_and_yegge_alignment():
    for lvl in range(2, 7):
        assert AGENTICNESS[lvl]["score"] == 7
        assert AGENTICNESS[lvl]["yegge_alignment_score"] >= 7


def test_level7_and_level8_unchanged_scores():
    assert AGENTICNESS[7]["score"] == 7
    assert AGENTICNESS[8]["score"] == 8
