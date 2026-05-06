from pathlib import Path


def test_levels_no_reintroduced_hardcoded_teacher_generic_strings():
    text = Path("src/levels.py").read_text(encoding="utf-8")
    assert "The teacher begins the lesson" not in text
    assert "Design a 2-hour Year 10 revision workshop" not in text
