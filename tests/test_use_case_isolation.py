from src.levels import run_level


class DummyClient:
    def available(self):
        return True

    def chat(self, *_args, **_kwargs):
        return "ok"


def _joined_lines(level: int, use_case_key: str, use_case_context: str = "") -> str:
    payload = run_level(
        level=level,
        client=DummyClient(),
        use_case_key=use_case_key,
        use_case_context=use_case_context,
    )
    return "\n".join(payload["lines"])


def test_custom_use_case_does_not_inherit_default_teacher_prompt():
    text = _joined_lines(
        1,
        "custom",
        "Goal: create a product launch plan. Audience: small business owner.",
    ).lower()
    assert "uk year 10 teacher" not in text
    assert "classroom-ready" not in text
    assert "lesson plan" not in text
    assert "teacher create" not in text


def test_custom_student_revision_context_does_not_inherit_teacher_prompt():
    text = _joined_lines(
        2,
        "custom",
        (
            "Goal: build a revision plan for a GCSE student preparing for exams. "
            "Audience: student and parent."
        ),
    ).lower()
    assert "teacher create" not in text
    assert "classroom-ready lesson" not in text
    assert "lesson plan" not in text


def test_year10_exam_student_does_not_use_teacher_preset_prompt():
    text = _joined_lines(2, "year10_exam_student").lower()
    assert "uk year 10 teacher create engaging" not in text
    assert "classroom-ready lesson" not in text
    assert "year 10" in text
    assert "student" in text


def test_uk_year10_teacher_still_contains_teacher_prompting():
    text = _joined_lines(2, "uk_year10_teacher").lower()
    assert "teacher" in text or "classroom" in text
