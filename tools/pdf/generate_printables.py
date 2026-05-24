from __future__ import annotations

from html import escape
from pathlib import Path
import re
import shutil
import sys
import textwrap

try:
    from reportlab import rl_config
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.platypus import (
        Paragraph,
        Preformatted,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
except Exception as exc:  # pragma: no cover
    raise SystemExit("Missing PDF tooling. Install with: pip install reportlab") from exc


ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
PRINTABLE = DOCS / "printable"

DOC_MAP = {
    "teacher_guide": DOCS / "teacher_guide.md",
    "student_worksheet": DOCS / "student_worksheet.md",
    "first_lesson_walkthrough": DOCS / "first_lesson_walkthrough.md",
}

PDF_TITLES = {
    "teacher_guide": "Teacher Guide",
    "student_worksheet": "Student Worksheet",
    "first_lesson_walkthrough": "First Lesson Walkthrough",
}

ALIASES = {
    "teacher_guide": ["teacher_guide.pdf", "Glytch_Teacher_Guide.pdf"],
    "student_worksheet": ["student_worksheet.pdf", "Glytch_Student_Worksheet.pdf"],
    "first_lesson_walkthrough": [
        "first_lesson_walkthrough.pdf",
        "Glytch_First_Lesson_Walkthrough.pdf",
    ],
}

# Keep generated PDFs byte-stable across repeated runs when content is unchanged.
rl_config.invariant = 1


class DeterministicCanvas(Canvas):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("invariant", 1)
        super().__init__(*args, **kwargs)


def page_size_from_arg(value: str) -> tuple[float, float]:
    return letter if value.lower() == "letter" else A4


def printable_lines(src: str) -> list[str]:
    """Remove repository navigation HTML blocks that are useful online but noisy on paper."""
    lines: list[str] = []
    skip_html_block = False
    for line in src.splitlines():
        stripped = line.strip()
        if stripped.startswith('<p align="center">'):
            skip_html_block = True
            continue
        if skip_html_block:
            if stripped == "</p>":
                skip_html_block = False
            continue
        if stripped == "---":
            continue
        lines.append(line.rstrip())
    return lines


def inline_markup(text: str) -> str:
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = escape(text)
    text = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", text)
    return text


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_table_separator(line: str) -> bool:
    cells = split_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in cells)


def wrap_code_lines(lines: list[str], width: int = 82) -> str:
    wrapped: list[str] = []
    for line in lines:
        if not line:
            wrapped.append("")
            continue

        indent_len = len(line) - len(line.lstrip(" "))
        indent = line[:indent_len]
        body = line[indent_len:]
        available = max(24, width - indent_len)
        parts = textwrap.wrap(
            body,
            width=available,
            break_long_words=False,
            break_on_hyphens=False,
        )
        if not parts:
            wrapped.append(line)
            continue

        wrapped.append(indent + parts[0])
        continuation_indent = indent + "  "
        wrapped.extend(continuation_indent + part for part in parts[1:])
    return "\n".join(wrapped)


def build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "h1": ParagraphStyle(
            "GlytchH1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=27,
            spaceAfter=10,
            textColor=colors.HexColor("#0f172a"),
        ),
        "h2": ParagraphStyle(
            "GlytchH2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=19,
            spaceBefore=8,
            spaceAfter=6,
            textColor=colors.HexColor("#1f2937"),
        ),
        "h3": ParagraphStyle(
            "GlytchH3",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            spaceBefore=6,
            spaceAfter=4,
            textColor=colors.HexColor("#374151"),
        ),
        "body": ParagraphStyle(
            "GlytchBody",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            spaceAfter=5,
            textColor=colors.HexColor("#111827"),
        ),
        "bullet": ParagraphStyle(
            "GlytchBullet",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            leftIndent=14,
            bulletIndent=0,
            spaceAfter=3,
        ),
        "quote": ParagraphStyle(
            "GlytchQuote",
            parent=base["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=10,
            leading=14,
            leftIndent=12,
            textColor=colors.HexColor("#4b5563"),
            borderColor=colors.HexColor("#cbd5e1"),
            borderWidth=0,
            spaceAfter=5,
        ),
        "code": ParagraphStyle(
            "GlytchCode",
            fontName="Courier",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#f9fafb"),
            backColor=colors.HexColor("#111827"),
            borderPadding=6,
            spaceBefore=4,
            spaceAfter=8,
        ),
        "cell": ParagraphStyle(
            "GlytchCell",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
        ),
    }


def append_table(story: list[object], rows: list[str], styles: dict[str, ParagraphStyle], width: float) -> None:
    table_rows: list[list[Paragraph]] = []
    for row in rows:
        if is_table_separator(row):
            continue
        table_rows.append([Paragraph(inline_markup(cell), styles["cell"]) for cell in split_table_row(row)])
    if not table_rows:
        return

    columns = max(len(row) for row in table_rows)
    for row in table_rows:
        while len(row) < columns:
            row.append(Paragraph("", styles["cell"]))

    table = Table(table_rows, colWidths=[width / columns] * columns, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.extend([table, Spacer(1, 6)])


def markdown_to_story(lines: list[str], styles: dict[str, ParagraphStyle], width: float) -> list[object]:
    story: list[object] = []
    paragraph: list[str] = []
    code: list[str] = []
    table: list[str] = []
    in_code = False

    def flush_paragraph() -> None:
        if paragraph:
            story.append(Paragraph(inline_markup(" ".join(paragraph).strip()), styles["body"]))
            paragraph.clear()

    def flush_code() -> None:
        if code:
            story.append(Preformatted(wrap_code_lines(code), styles["code"]))
            code.clear()

    def flush_table() -> None:
        if table:
            append_table(story, table, styles, width)
            table.clear()

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            flush_paragraph()
            flush_table()
            if in_code:
                flush_code()
                in_code = False
            else:
                in_code = True
            continue

        if in_code:
            code.append(line)
            continue

        if "|" in stripped and stripped.startswith("|"):
            flush_paragraph()
            table.append(stripped)
            continue
        flush_table()

        if not stripped:
            flush_paragraph()
            story.append(Spacer(1, 4))
            continue

        if stripped.startswith("# "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[2:]), styles["h1"]))
            continue
        if stripped.startswith("## "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[3:]), styles["h2"]))
            continue
        if stripped.startswith("### "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[4:]), styles["h3"]))
            continue

        if stripped.startswith("- "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[2:]), styles["bullet"], bulletText="-"))
            continue

        numbered = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if numbered:
            flush_paragraph()
            story.append(
                Paragraph(
                    inline_markup(numbered.group(2)),
                    styles["bullet"],
                    bulletText=f"{numbered.group(1)}.",
                )
            )
            continue

        if stripped.startswith("> "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[2:]), styles["quote"]))
            continue

        paragraph.append(stripped)

    flush_paragraph()
    flush_code()
    flush_table()
    return story


def draw_page(canvas, doc) -> None:  # type: ignore[no-untyped-def]
    canvas.saveState()
    title = getattr(doc, "printable_title", "Classroom Printable")
    canvas.setTitle(f"Glytch {title}")
    canvas.setAuthor("Glytch")
    canvas.setSubject("Glytch classroom printable")
    canvas.setCreator("Glytch printable generator")
    page_width, page_height = doc.pagesize
    canvas.setStrokeColor(colors.HexColor("#d1d5db"))
    canvas.setLineWidth(0.5)
    canvas.line(doc.leftMargin, page_height - 14 * mm, page_width - doc.rightMargin, page_height - 14 * mm)
    canvas.setFillColor(colors.HexColor("#111827"))
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(doc.leftMargin, page_height - 11 * mm, f"Glytch | {title}")
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#4b5563"))
    canvas.drawCentredString(page_width / 2, 9 * mm, f"Page {canvas.getPageNumber()}")
    canvas.restoreState()


def render(md_path: Path, out_pdf: Path, page_size: tuple[float, float]) -> None:
    styles = build_styles()
    title = PDF_TITLES.get(md_path.stem, md_path.stem.replace("_", " ").title())
    doc = SimpleDocTemplate(
        str(out_pdf),
        pagesize=page_size,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=22 * mm,
        bottomMargin=18 * mm,
        title=f"Glytch {title}",
    )
    doc.printable_title = title
    story = markdown_to_story(printable_lines(md_path.read_text(encoding="utf-8")), styles, doc.width)
    doc.build(story, onFirstPage=draw_page, onLaterPages=draw_page, canvasmaker=DeterministicCanvas)


def main() -> int:
    page_size = page_size_from_arg(sys.argv[1] if len(sys.argv) > 1 else "A4")
    PRINTABLE.mkdir(parents=True, exist_ok=True)

    for stem, md in DOC_MAP.items():
        primary = PRINTABLE / ALIASES[stem][0]
        render(md, primary, page_size)
        for alias in ALIASES[stem][1:]:
            shutil.copyfile(primary, PRINTABLE / alias)
        print(f"Generated {', '.join(ALIASES[stem])}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
