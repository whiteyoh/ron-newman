from pathlib import Path

from scripts.generate_architecture_diagrams import LEVEL_DEFINITIONS, render_level, write_svg


def test_level_definitions_cover_eight_levels() -> None:
    assert len(LEVEL_DEFINITIONS) == 8
    assert [item["level"] for item in LEVEL_DEFINITIONS] == [1, 2, 3, 4, 5, 6, 7, 8]


def test_level_definitions_have_required_fields() -> None:
    for level in LEVEL_DEFINITIONS:
        assert level["title"]
        assert len(level["nodes"]) >= 4
        assert len(level["edges"]) >= 1


def test_render_level_returns_svg_with_title() -> None:
    rendered = render_level(LEVEL_DEFINITIONS[0])
    assert "<svg" in rendered
    assert "Level 1: Autocomplete" in rendered


def test_write_svg_writes_only_when_called(tmp_path: Path) -> None:
    output = tmp_path / "out.svg"
    write_svg(output, "<svg></svg>")
    assert output.exists()
    assert output.read_text(encoding="utf-8") == "<svg></svg>"
