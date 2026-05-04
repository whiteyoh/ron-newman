"""Generate conceptual architecture diagrams for Glytch levels 1-8."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

CANVAS_WIDTH = 1400
CANVAS_HEIGHT = 760
BOX_W = 180
BOX_H = 88

COLORS = {
    "background": "#071426",
    "white": "#EAF2FF",
    "cyan": "#22D3EE",
    "magenta": "#F472B6",
    "muted": "#8AA3C7",
    "panel": "#0E223B",
}

LEVEL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "level": 1,
        "title": "Autocomplete",
        "subtitle": "Linear suggestion flow",
        "note": "Simple, linear, human-led.",
        "nodes": ["User", "Prompt", "Model", "Output", "Human decides next"],
        "edges": [(0, 1), (1, 2), (2, 3), (3, 4)],
    },
    {
        "level": 2,
        "title": "Instruction following",
        "subtitle": "Clearer instruction contract",
        "note": "The model follows a clearer contract, but the human still approves.",
        "nodes": ["User", "Structured instruction", "Model", "Output", "Human approval"],
        "edges": [(0, 1), (1, 2), (2, 3), (3, 4)],
    },
    {
        "level": 3,
        "title": "Tool use",
        "subtitle": "Bounded tool path",
        "note": "The model can use a bounded tool path.",
        "nodes": [
            "User",
            "Model",
            "Tool selection",
            "Tool",
            "Result",
            "Final output",
            "Human review",
        ],
        "edges": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6)],
    },
    {
        "level": 4,
        "title": "Retrieval + grounding",
        "subtitle": "Evidence-backed responses",
        "note": "The answer is tied to supplied evidence.",
        "nodes": [
            "User",
            "Model",
            "Evidence source",
            "Grounded answer",
            "Support check",
            "Human review",
        ],
        "edges": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)],
    },
    {
        "level": 5,
        "title": "Planning",
        "subtitle": "Plan then execute",
        "note": "Work is broken into visible steps before completion.",
        "nodes": [
            "User objective",
            "Planner",
            "Step plan",
            "Execute steps",
            "Verification",
            "Final answer",
        ],
        "edges": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)],
    },
    {
        "level": 6,
        "title": "Review loop",
        "subtitle": "Bounded critique cycle",
        "note": "The model improves work through a bounded review loop.",
        "nodes": [
            "Draft",
            "Critique",
            "Revise",
            "Threshold / stop",
            "Final answer",
            "Human approval",
        ],
        "edges": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)],
        "loops": [(2, 1)],
    },
    {
        "level": 7,
        "title": "Swarm / multi-agent coordination",
        "subtitle": "Coordinator with multiple workers",
        "note": "Multiple agents create coordination pressure.",
        "nodes": [
            "User objective",
            "Coordinator",
            "Worker A",
            "Worker B",
            "Worker C",
            "Manual review bottleneck",
            "Verification",
            "Final result",
        ],
        "edges": [(0, 1), (1, 2), (1, 3), (1, 4), (2, 5), (3, 5), (4, 5), (5, 6), (6, 7)],
    },
    {
        "level": 8,
        "title": "Custom orchestrator",
        "subtitle": "Request-scoped orchestration",
        "note": "A request-scoped orchestrator coordinates workers, checks and merge policy.",
        "nodes": [
            "User request",
            "Orchestrator",
            "Taskboard",
            "Specialist workers",
            "Verifier",
            "Human approval gate",
            "Merge decision",
            "Final result",
        ],
        "edges": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7)],
    },
]


def svg_header(title: str) -> str:
    marker = (
        f'<defs><marker id="arrow" markerWidth="10" markerHeight="8" refX="9" refY="4" '
        f'orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="{COLORS["cyan"]}" />'
        "</marker></defs>\n"
    )
    bg = (
        f'<rect x="0" y="0" width="{CANVAS_WIDTH}" height="{CANVAS_HEIGHT}" '
        f'fill="{COLORS["background"]}" />\n'
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_WIDTH}" '
        f'height="{CANVAS_HEIGHT}" viewBox="0 0 {CANVAS_WIDTH} {CANVAS_HEIGHT}">\n'
        f"<title>{escape(title)}</title>\n{marker}{bg}"
    )


def svg_footer() -> str:
    return "</svg>\n"


def box(
    x: int, y: int, w: int, h: int, title: str, subtitle: str | None = None, accent: str = "cyan"
) -> str:
    body = (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{COLORS["panel"]}" '
        f'stroke="{COLORS[accent]}" stroke-width="2" />\n'
        f'<text x="{x + w / 2}" y="{y + 42}" text-anchor="middle" fill="{COLORS["white"]}" '
        'font-family="Inter, Arial, sans-serif" font-size="20" font-weight="600">'
        f"{escape(title)}</text>\n"
    )
    if not subtitle:
        return body
    return (
        body + f'<text x="{x + w / 2}" y="{y + 64}" text-anchor="middle" fill="{COLORS["muted"]}" '
        'font-family="Inter, Arial, sans-serif" font-size="15">'
        f"{escape(subtitle)}</text>\n"
    )


def arrow(x1: int, y1: int, x2: int, y2: int, color: str = "cyan") -> str:
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{COLORS[color]}" '
        'stroke-width="3" marker-end="url(#arrow)" />\n'
    )


def loop_arrow(x: int, y: int, up: int = 56, right: int = 76) -> str:
    return (
        f'<path d="M{x} {y} C {x + right} {y - up}, {x + right} {y - up}, {x} {y - 8}" '
        f'fill="none" stroke="{COLORS["magenta"]}" stroke-width="3" marker-end="url(#arrow)" />\n'
    )


def _horizontal_positions(count: int, y: int = 280) -> list[tuple[int, int]]:
    start_x = 80
    row_gap = 140
    max_per_row = max(1, (CANVAS_WIDTH - (start_x * 2)) // (BOX_W + 24))
    if count <= max_per_row:
        gap = (CANVAS_WIDTH - start_x * 2 - BOX_W) // max(count - 1, 1)
        return [(start_x + idx * gap, y) for idx in range(count)]
    positions: list[tuple[int, int]] = []
    for idx in range(count):
        row = idx // max_per_row
        col = idx % max_per_row
        x = start_x + col * (BOX_W + 24)
        positions.append((x, y + (row * row_gap)))
    return positions


def get_node_positions(level_definition: dict[str, Any]) -> list[tuple[int, int]]:
    level = level_definition["level"]
    if level == 7:
        return [
            (80, 120),
            (320, 120),
            (580, 40),
            (580, 180),
            (580, 320),
            (800, 180),
            (1010, 180),
            (1220, 180),
        ]
    if level == 8:
        return [
            (80, 90),
            (320, 90),
            (560, 90),
            (560, 280),
            (800, 280),
            (1020, 280),
            (1020, 470),
            (1220, 470),
        ]
    return _horizontal_positions(len(level_definition["nodes"]))


def render_level(level_definition: dict[str, Any]) -> str:
    level = level_definition["level"]
    title = level_definition["title"]
    subtitle = level_definition["subtitle"]
    nodes = level_definition["nodes"]
    edges = level_definition["edges"]
    loops = level_definition.get("loops", [])

    pieces = [svg_header(f"Glytch Level {level}: {title}")]
    pieces.append(
        f'<text x="80" y="84" fill="{COLORS["white"]}" '
        'font-family="Inter, Arial, sans-serif" font-size="36" font-weight="700">'
        f"Level {level}: {escape(title)}</text>\n"
    )
    pieces.append(
        f'<text x="80" y="120" fill="{COLORS["muted"]}" '
        'font-family="Inter, Arial, sans-serif" font-size="20">'
        f"{escape(subtitle)}</text>\n"
    )

    positions = get_node_positions(level_definition)
    for idx, node in enumerate(nodes):
        x, y = positions[idx]
        pieces.append(box(x, y, BOX_W, BOX_H, node, accent="magenta" if idx % 2 else "cyan"))

    for src, dst in edges:
        x1, y1 = positions[src]
        x2, y2 = positions[dst]
        pieces.append(arrow(x1 + BOX_W, y1 + BOX_H // 2, x2, y2 + BOX_H // 2))

    for src, _dst in loops:
        x, y = positions[src]
        pieces.append(loop_arrow(x + BOX_W // 2, y + 4))

    note = level_definition.get("note")
    if note:
        pieces.append(box(80, 620, 1240, 90, "Note", note, accent="magenta"))

    pieces.append(svg_footer())
    return "".join(pieces)


def write_svg(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    out = Path("architecture/generated")
    for definition in LEVEL_DEFINITIONS:
        svg = render_level(definition)
        write_svg(out / f"level-{definition['level']}.svg", svg)
    print(f"Generated {len(LEVEL_DEFINITIONS)} diagrams in {out}/")


if __name__ == "__main__":
    main()
