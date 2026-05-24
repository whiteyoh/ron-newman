from __future__ import annotations

from pathlib import Path
import re


BOOK_MD = Path("docs/tech_i_can_glytch_book.md")


def _lines() -> list[str]:
    return BOOK_MD.read_text(encoding="utf-8").splitlines()


def test_book_has_required_chapter_learning_structure() -> None:
    lines = _lines()
    chapter_blocks = "\n".join(lines).split("\n# ")
    for block in chapter_blocks:
        if not block.strip():
            continue
        text = "# " + block if not block.startswith("# ") else block
        if "# Chapter " not in text:
            continue
        for required in (
            "## About this chapter",
            "## What you are going to use",
            "## What you will learn in this chapter",
            "## The work, clearly laid out",
            "## Examples of what you might see",
            "## Why This Matters",
            "## Action 1: What You Learned",
            "## Action 2: Reflect",
            "## Action 3: Do This Next",
        ):
            assert required in text


def test_book_has_expected_minimum_number_of_chapters() -> None:
    text = BOOK_MD.read_text(encoding="utf-8")
    chapters = re.findall(r"^# Chapter \d+:", text, flags=re.M)
    assert len(chapters) >= 8


def test_book_intro_sections_have_minimum_depth() -> None:
    lines = _lines()
    chapter = ""
    in_intro = False
    intro_words = 0
    intro_counts: dict[str, int] = {}

    for raw in lines:
        stripped = raw.strip()
        if stripped.startswith("# "):
            if chapter.startswith("Chapter "):
                intro_counts[chapter] = intro_words
            chapter = stripped[2:].strip()
            in_intro = False
            intro_words = 0
            continue
        if stripped.startswith("## "):
            in_intro = stripped[3:].strip().lower() == "about this chapter"
            continue
        if not in_intro or not stripped:
            continue
        intro_words += len(stripped.split())

    if chapter.startswith("Chapter "):
        intro_counts[chapter] = intro_words

    assert intro_counts
    assert all(count >= 20 for count in intro_counts.values())


def test_book_includes_references_section() -> None:
    text = BOOK_MD.read_text(encoding="utf-8")
    assert "## References (APA 7th Edition)" in text


def test_each_chapter_has_three_reflection_questions() -> None:
    text = BOOK_MD.read_text(encoding="utf-8")
    chapter_blocks = re.split(r"\n# Chapter \d+: ", text)[1:]

    for block in chapter_blocks:
        chapter_title = block.splitlines()[0].strip()
        reflect_match = re.search(
            r"## Action 2: Reflect\n(.*?)(\n## Action 3: Do This Next|\n---|\Z)",
            block,
            flags=re.S,
        )
        assert reflect_match is not None, f"Missing reflection section in chapter: {chapter_title}"
        bullets = [
            line.strip()[2:].strip()
            for line in reflect_match.group(1).splitlines()
            if line.strip().startswith("- ")
        ]
        assert len(bullets) == 3, f"Expected 3 reflection questions in chapter: {chapter_title}"


def test_action_three_contains_collaborative_next_step() -> None:
    text = BOOK_MD.read_text(encoding="utf-8")
    chapter_blocks = re.split(r"\n# Chapter \d+: ", text)[1:]
    collaboration_tokens = (
        "peer",
        "colleague",
        "partner",
        "group",
        "classmate",
        "teacher",
        "swap",
        "pair",
        "together",
        "team",
    )

    for block in chapter_blocks:
        chapter_title = block.splitlines()[0].strip()
        action_match = re.search(r"## Action 3: Do This Next\n(.*?)(\n---|\Z)", block, flags=re.S)
        assert action_match is not None, f"Missing Action 3 in chapter: {chapter_title}"
        bullets = [
            line.strip()[2:].strip().lower()
            for line in action_match.group(1).splitlines()
            if line.strip().startswith("- ")
        ]
        assert len(bullets) >= 2, f"Action 3 needs at least two bullets in chapter: {chapter_title}"
        assert any(any(token in bullet for token in collaboration_tokens) for bullet in bullets), (
            f"Action 3 missing collaborative language in chapter: {chapter_title}"
        )
