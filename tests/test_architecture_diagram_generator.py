from pathlib import Path
from xml.etree import ElementTree as ET

from scripts.generate_architecture_diagrams import (
    BOX_H,
    BOX_W,
    LEVEL_DEFINITIONS,
    get_node_positions,
    render_level,
    write_svg,
)


def _overlap(a, b):
    ax, ay = a
    bx, by = b
    return not (ax + BOX_W <= bx or bx + BOX_W <= ax or ay + BOX_H <= by or by + BOX_H <= ay)


def test_level_definitions_cover_eight_levels() -> None:
    assert len(LEVEL_DEFINITIONS) == 8
    assert [item["level"] for item in LEVEL_DEFINITIONS] == list(range(1, 9))


def test_level_definitions_have_required_fields() -> None:
    for level in LEVEL_DEFINITIONS:
        assert level["title"]
        assert level["subtitle"]
        assert level["nodes"]
        assert level["edges"]


def test_all_levels_render_and_parse() -> None:
    for definition in LEVEL_DEFINITIONS:
        rendered = render_level(definition)
        assert "<svg" in rendered
        assert f"Level {definition['level']}: {definition['title']}" in rendered
        ET.fromstring(rendered)


def test_write_all_svgs_to_tmp_path(tmp_path: Path) -> None:
    for definition in LEVEL_DEFINITIONS:
        rendered = render_level(definition)
        out = tmp_path / f"level-{definition['level']}.svg"
        write_svg(out, rendered)
        assert out.exists()
        assert out.read_text(encoding="utf-8").strip()


def test_level7_and_level8_nodes_present() -> None:
    level7 = next(item for item in LEVEL_DEFINITIONS if item["level"] == 7)
    level8 = next(item for item in LEVEL_DEFINITIONS if item["level"] == 8)
    for node in [
        "User objective",
        "Coordinator",
        "Worker A",
        "Worker B",
        "Worker C",
        "Manual review bottleneck",
        "Verification",
        "Final result",
    ]:
        assert node in level7["nodes"]
    for node in [
        "User request",
        "Orchestrator",
        "Taskboard",
        "Specialist workers",
        "Verifier",
        "Human approval gate",
        "Merge decision",
        "Final result",
    ]:
        assert node in level8["nodes"]


def test_no_node_overlap_per_level() -> None:
    for definition in LEVEL_DEFINITIONS:
        positions = get_node_positions(definition)
        assert len(positions) == len(definition["nodes"])
        for i, pos_a in enumerate(positions):
            for pos_b in positions[i + 1 :]:
                assert not _overlap(pos_a, pos_b)
