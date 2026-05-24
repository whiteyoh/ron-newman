from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
from html import escape
from pathlib import Path
import re
import shutil
import subprocess
import textwrap

try:
    from PIL import Image as PILImage
    from PIL import ImageDraw, ImageFont
    from PIL import ImageFilter
    from reportlab import rl_config
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfdoc
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.platypus import (
        BaseDocTemplate,
        Frame,
        Image,
        KeepTogether,
        NextPageTemplate,
        PageBreak,
        PageBreakIfNotEmpty,
        PageTemplate,
        Paragraph,
        Preformatted,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.platypus.tableofcontents import TableOfContents
    from pypdf import PdfReader
    from pypdf import PdfWriter
    from pypdf.generic import BooleanObject, DictionaryObject, NameObject, TextStringObject
except Exception as exc:  # pragma: no cover
    raise SystemExit("Missing PDF tooling. Install with: pip install -e \".[pdf]\"") from exc


ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
ASSETS = DOCS / "assets"
PRINTABLE = DOCS / "printable"
BOOK_MD = DOCS / "tech_i_can_glytch_book.md"
BOOK_PDF = PRINTABLE / "Tech_I_Can_Glytch_Book.pdf"
COVER_IMAGE = ASSETS / "tech-i-can-cover.jpg"
FIGURE_LEARNING_LOOP = ASSETS / "figure-learning-loop.jpg"
FIGURE_LEARN_MODE = ASSETS / "figure-learn-mode.jpg"
FIGURE_TRAINING_CURVE = ASSETS / "figure-training-curve.jpg"
FIGURE_QA_GROUNDING = ASSETS / "figure-qa-grounding.jpg"
FIGURE_LESSON_DELIVERY_MAP = ASSETS / "figure-lesson-delivery-map.jpg"
FIGURE_WEEKLY_IMPLEMENTATION_MAP = ASSETS / "figure-weekly-implementation-map.jpg"
FIGURE_IMPROVEMENT_CYCLE = ASSETS / "figure-improvement-cycle.jpg"
FIGURE_GLOSSARY_LOOKUP_MAP = ASSETS / "figure-glossary-lookup-map.jpg"
FIGURE_INDEX_LOOKUP_FLOW = ASSETS / "figure-index-lookup-flow.jpg"
ICON_LIGHTBULB = ASSETS / "icon-lightbulb.png"
ICON_DEFINITION = ASSETS / "icon-definition.png"
ICON_NOTE = ASSETS / "icon-note.png"
ICON_SNIPPET_PURPOSE = ASSETS / "icon-snippet-purpose.png"
ICON_SNIPPET_CHANGE = ASSETS / "icon-snippet-change.png"

BOOK_TITLE = "Tech I Can"
BOOK_TAGLINE = "Curious today, Confident tomorrow"
BOOK_SUBTITLE = "Glytch: A Beginner-Friendly Guide to AI Workflow Judgement"
BOOK_AUTHOR = "Paul McMurray"
BOOK_EDITION = "Classroom Edition (2026)"
BOOK_SERIES = "Tech I Can Series"
BOOK_PUBLISHER = "Tech I Can"
BOOK_PUBLICATION_DATE = "May 2026"
BOOK_ISBN = "ISBN: Not assigned (Edition 1 school release, not for retail sale)"
BOOK_KEYWORDS = "education, ai literacy, glytch, workflow literacy, classroom, beginner ai"
BRAND_ACCENTS = ["#2563eb", "#0d9488", "#ea580c", "#7c3aed", "#0891b2", "#be123c"]
BOOK_META_TITLE = "Tech I Can | Glytch"
BOOK_META_AUTHOR = "Paul McMurray"
BOOK_META_SUBJECT = "Beginner guide to Glytch"
BOOK_META_CREATOR = "Tech I Can Production Pipeline"
BOOK_META_CREATION_DATE = "2026-05-01T00:00:00+00:00"
TARGET_PDF_SIZE_BYTES = 650 * 1024
MIN_INTRO_WORDS = 20
DISPLAY_FONT_CANDIDATES: list[tuple[str, str]] = []
REQUIRED_INDEX_TERMS: list[str] = [
    "Approval gate",
    "Capability",
    "Checklist",
    "Confidence",
    "Context",
    "Controlled loop",
    "Critique",
    "Evidence",
    "Grounding",
    "Human review",
    "Level 1",
    "Level 8",
    "Lowest safe level",
    "Merge decision",
    "Orchestration",
    "Prompt",
    "Reliability",
    "Revision",
    "Risk",
    "Simulation trace",
    "Taskboard",
    "Verifier",
    "Workflow detail",
    "Workflow literacy",
]
TERM_SEARCH_ALIASES: dict[str, list[str]] = {
    "Approval gate": ["approval gate", "approved for merge"],
    "Capability": ["capability"],
    "Controlled loop": ["controlled loop", "observe-act-check-stop", "observe act check stop"],
    "Critique": ["critique", "review and improve"],
    "Evidence": ["evidence", "grounded"],
    "Human review": ["human review", "human judgement"],
    "Level 1": ["level 1"],
    "Level 8": ["level 8"],
    "Lowest safe level": ["lowest safe level"],
    "Merge decision": ["merge decision", "merged"],
    "Orchestration": ["orchestration", "orchestrated"],
    "Prompt": ["prompt"],
    "Reliability": ["reliability", "trustworthy"],
    "Revision": ["revision", "revised"],
    "Risk": ["risk", "risky"],
    "Simulation trace": ["simulation trace", "trace"],
    "Taskboard": ["taskboard"],
    "Verifier": ["verifier"],
    "Workflow detail": ["workflow detail"],
    "Workflow literacy": ["workflow literacy", "ai literacy"],
}
KEYWORD_PRIMARY_PAGE_OVERRIDES: dict[str, int] = {}
KEYWORD_FULL_RANGE_START_OVERRIDES: dict[str, int] = {}
KEY_WORDS_INDEX_HEADING_RE = re.compile(r"^#\s+Chapter\s+\d+:\s+Key Words Index\s*$", re.IGNORECASE)


def _build_mod_date() -> str:
    return datetime.now(tz=UTC).strftime("D:%Y%m%d%H%M%SZ")


def apply_accessibility_catalog_tags(pdf_path: Path) -> None:
    reader = PdfReader(str(pdf_path))
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    for page in writer.pages:
        page_obj = getattr(page, "get_object", lambda: page)()
        page_obj.update({NameObject("/Tabs"): NameObject("/S")})
    writer._root_object.update(  # type: ignore[attr-defined]
        {
            NameObject("/MarkInfo"): DictionaryObject({NameObject("/Marked"): BooleanObject(True)}),
            NameObject("/Lang"): TextStringObject("en-GB"),
            NameObject("/PageMode"): NameObject("/UseOutlines"),
            NameObject("/ViewerPreferences"): DictionaryObject(
                {NameObject("/DisplayDocTitle"): BooleanObject(True)}
            ),
        }
    )
    tagged_path = pdf_path.with_name(f"{pdf_path.stem}.tagged{pdf_path.suffix}")
    with tagged_path.open("wb") as handle:
        writer.write(handle)
    tagged_path.replace(pdf_path)


def _optimise_pdf_with_pypdf(pdf_path: Path) -> bool:
    optimised_path = pdf_path.with_name(f"{pdf_path.stem}.optimised{pdf_path.suffix}")
    reader = PdfReader(str(pdf_path))
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    for page in writer.pages:
        compress_fn = getattr(page, "compress_content_streams", None)
        if callable(compress_fn):
            compress_fn()

    with optimised_path.open("wb") as handle:
        writer.write(handle)
    optimised_path.replace(pdf_path)
    return True


def optimise_pdf_with_ghostscript(pdf_path: Path) -> bool:
    gs_path = shutil.which("gs")
    if not gs_path:
        print("Ghostscript not found; using pypdf fallback optimisation.")
        return _optimise_pdf_with_pypdf(pdf_path)

    optimised_path = pdf_path.with_name(f"{pdf_path.stem}.optimised{pdf_path.suffix}")
    cmd = [
        gs_path,
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/ebook",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={optimised_path}",
        str(pdf_path),
    ]
    try:
        subprocess.run(cmd, check=True)
        optimised_path.replace(pdf_path)
    except subprocess.CalledProcessError:
        print("Ghostscript optimisation failed; using pypdf fallback optimisation.")
        return _optimise_pdf_with_pypdf(pdf_path)

    if pdf_path.stat().st_size > TARGET_PDF_SIZE_BYTES:
        print("Ghostscript output still above size target; applying pypdf fallback optimisation.")
        return _optimise_pdf_with_pypdf(pdf_path)

    return True


def ensure_support_figure_images() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)

    def _font(size: int) -> ImageFont.ImageFont:
        candidates = [
            "/System/Library/Fonts/Supplemental/Helvetica.ttc",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        ]
        for candidate in candidates:
            try:
                return ImageFont.truetype(candidate, size=size)
            except OSError:
                continue
        return ImageFont.load_default()

    def _save_figure(path: Path, painter) -> None:
        w, h = 1280, 720
        img = PILImage.new("RGB", (w, h), "#f8fafc")
        draw = ImageDraw.Draw(img)
        # subtle header band
        draw.rectangle((0, 0, w, 92), fill="#e2e8f0")
        painter(draw, w, h)
        resampling = getattr(PILImage, "Resampling", PILImage)
        img = img.resize((960, 540), resample=resampling.LANCZOS)
        img.save(path, format="JPEG", quality=36, optimize=True, progressive=True, subsampling=2)

    def _paint_learning_loop(draw: ImageDraw.ImageDraw, w: int, h: int) -> None:
        title = _font(44)
        body = _font(22)
        draw.text((52, 20), "Learning Evidence Loop", fill="#0f172a", font=title)
        labels = ["Run", "Observe", "Compare", "Explain", "Improve"]
        points = [(175, 306), (440, 176), (780, 200), (960, 420), (510, 520)]
        for i, (x, y) in enumerate(points):
            nx, ny = points[(i + 1) % len(points)]
            draw.line((x + 52, y, nx - 52, ny), fill="#334155", width=5)
        for i, (x, y) in enumerate(points):
            draw.ellipse((x - 58, y - 58, x + 58, y + 58), fill="#dbeafe", outline="#2563eb", width=4)
            label = labels[i]
            left, top, right, bottom = draw.textbbox((0, 0), label, font=body)
            text_w = right - left
            text_h = bottom - top
            draw.text((x - text_w / 2, y - text_h / 2 - 1), label, fill="#1e3a8a", font=body)
        draw.text((52, 654), "Use this cycle for every chapter activity and reflection.", fill="#334155", font=body)

    def _paint_training_curve(draw: ImageDraw.ImageDraw, w: int, h: int) -> None:
        title = _font(44)
        body = _font(22)
        draw.text((52, 20), "Training vs Validation Curve Read", fill="#0f172a", font=title)
        # axes
        draw.line((110, 600, 1150, 600), fill="#1f2937", width=4)
        draw.line((110, 600, 110, 140), fill="#1f2937", width=4)
        # train curve
        train_pts = [(144, 546), (338, 453), (552, 373), (766, 313), (974, 286)]
        val_pts = [(144, 520), (338, 413), (552, 360), (766, 373), (974, 406)]
        draw.line(train_pts, fill="#0ea5e9", width=5)
        draw.line(val_pts, fill="#f97316", width=5)
        for x, y in train_pts:
            draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill="#0ea5e9")
        for x, y in val_pts:
            draw.rectangle((x - 6, y - 6, x + 6, y + 6), fill="#f97316")
        draw.text((1020, 246), "Train", fill="#0c4a6e", font=body)
        draw.text((1020, 426), "Validation", fill="#9a3412", font=body)
        draw.text((148, 628), "Epoch", fill="#334155", font=body)
        draw.text((22, 136), "Loss", fill="#334155", font=body)
        draw.text((52, 670), "Watch for the gap: train down, validation up.", fill="#334155", font=body)

    def _paint_learn_mode(draw: ImageDraw.ImageDraw, w: int, h: int) -> None:
        title = _font(44)
        body = _font(22)
        draw.text((52, 20), "Learn Mode Evidence Surfaces", fill="#0f172a", font=title)
        panels = [
            (78, 152, 406, 506, "#e0f2fe", "Token Preview", "How text is split"),
            (476, 152, 804, 506, "#ede9fe", "Probabilities", "What the model prefers"),
            (874, 152, 1202, 506, "#dcfce7", "Attention Map", "What tokens influence focus"),
        ]
        for x1, y1, x2, y2, fill, title_txt, sub_txt in panels:
            draw.rounded_rectangle((x1, y1, x2, y2), radius=20, fill=fill, outline="#334155", width=3)
            draw.text((x1 + 18, y1 + 16), title_txt, fill="#0f172a", font=body)
            draw.text((x1 + 18, y1 + 62), sub_txt, fill="#334155", font=_font(18))
            for i in range(6):
                y = y1 + 112 + i * 38
                draw.rectangle((x1 + 18, y, x2 - 18, y + 18), fill="#ffffff", outline="#cbd5e1", width=1)
        draw.text((52, 654), "Use each panel to support a specific claim in your reflection notes.", fill="#334155", font=body)

    def _paint_qa_grounding(draw: ImageDraw.ImageDraw, w: int, h: int) -> None:
        title = _font(44)
        body = _font(22)
        draw.text((52, 20), "Grounded QA Flow", fill="#0f172a", font=title)
        # boxes
        boxes = [
            (78, 172, 412, 346, "#dbeafe", "Question"),
            (472, 172, 840, 346, "#dcfce7", "Context"),
            (908, 172, 1202, 346, "#fef3c7", "Answer"),
        ]
        for x1, y1, x2, y2, color, label in boxes:
            draw.rounded_rectangle((x1, y1, x2, y2), radius=18, fill=color, outline="#334155", width=3)
            draw.text((x1 + 16, y1 + 16), label, fill="#0f172a", font=body)
        draw.text((98, 236), "Who pilots\nthe Aurora?", fill="#1e3a8a", font=body)
        draw.text((494, 236), "Captain Rowan is\nthe pilot.", fill="#14532d", font=body)
        draw.text((928, 236), "Captain Rowan\npilots the Aurora.", fill="#92400e", font=body)
        draw.line((412, 258, 472, 258), fill="#334155", width=5)
        draw.line((840, 258, 908, 258), fill="#334155", width=5)
        draw.text((52, 654), "Better context gives clearer, safer answers.", fill="#334155", font=body)

    def _paint_lesson_delivery_map(draw: ImageDraw.ImageDraw, w: int, h: int) -> None:
        title = _font(44)
        body = _font(22)
        draw.text((52, 20), "45-Minute Lesson Arc", fill="#0f172a", font=title)
        stages = [
            ("Warm-up", "#dbeafe"),
            ("Baseline", "#dcfce7"),
            ("Retrain", "#fef3c7"),
            ("Compare", "#ede9fe"),
            ("Debrief", "#fee2e2"),
        ]
        x = 70
        for label, fill in stages:
            draw.rounded_rectangle((x, 214, x + 220, 414), radius=20, fill=fill, outline="#334155", width=3)
            draw.text((x + 36, 290), label, fill="#0f172a", font=body)
            if x < 1030:
                draw.line((x + 220, 314, x + 256, 314), fill="#334155", width=5)
            x += 236
        draw.text((52, 654), "Plan time intentionally so evidence discussion is never rushed.", fill="#334155", font=body)

    def _paint_weekly_implementation_map(draw: ImageDraw.ImageDraw, w: int, h: int) -> None:
        title = _font(44)
        body = _font(22)
        draw.text((52, 20), "Week-by-Week Delivery Map", fill="#0f172a", font=title)
        draw.rounded_rectangle((76, 166, 1210, 558), radius=18, outline="#334155", width=3, fill="#ffffff")
        week_labels = [
            ("Week 1", "Setup + Baseline"),
            ("Week 2", "Retrain + Compare"),
            ("Week 3", "QA + Grounding"),
            ("Week 4", "Capstone Share"),
        ]
        x = 116
        colors_map = ["#dbeafe", "#dcfce7", "#fef3c7", "#ede9fe"]
        for idx, (week, detail) in enumerate(week_labels):
            draw.rounded_rectangle((x, 222, x + 252, 510), radius=16, fill=colors_map[idx], outline="#475569", width=2)
            draw.text((x + 24, 270), week, fill="#0f172a", font=body)
            draw.text((x + 24, 334), detail, fill="#334155", font=_font(18))
            if idx < len(week_labels) - 1:
                draw.line((x + 252, 366, x + 286, 366), fill="#334155", width=4)
            x += 286
        draw.text((52, 654), "Each week should end with one clear artifact and one clear explanation.", fill="#334155", font=body)

    def _paint_improvement_cycle(draw: ImageDraw.ImageDraw, w: int, h: int) -> None:
        title = _font(44)
        body = _font(22)
        draw.text((52, 20), "Continuous Improvement Cycle", fill="#0f172a", font=title)
        nodes = [
            ("Collect", 210, 270),
            ("Prioritize", 520, 174),
            ("Test", 870, 250),
            ("Measure", 930, 470),
            ("Adjust", 470, 520),
        ]
        for i, (_label, x, y) in enumerate(nodes):
            nx, ny = nodes[(i + 1) % len(nodes)][1:]
            draw.line((x + 60, y + 40, nx + 60, ny + 40), fill="#334155", width=4)
        for label, x, y in nodes:
            draw.rounded_rectangle((x, y, x + 180, y + 86), radius=18, fill="#e2e8f0", outline="#334155", width=3)
            draw.text((x + 22, y + 30), label, fill="#0f172a", font=body)
        draw.text((52, 654), "Improve one thing at a time, then prove whether it helped.", fill="#334155", font=body)

    def _paint_glossary_lookup_map(draw: ImageDraw.ImageDraw, w: int, h: int) -> None:
        title = _font(44)
        body = _font(22)
        draw.text((52, 20), "Glossary to Classroom Use", fill="#0f172a", font=title)
        steps = [
            ("Term", "Grounding"),
            ("Meaning", "Answer tied to context"),
            ("Command", "--context / --context_file"),
            ("Use", "Explain output limits"),
        ]
        y = 168
        for label, detail in steps:
            draw.rounded_rectangle((126, y, 1150, y + 120), radius=16, fill="#f8fafc", outline="#334155", width=2)
            draw.text((156, y + 22), label, fill="#1e3a8a", font=body)
            draw.text((390, y + 22), detail, fill="#0f172a", font=body)
            if y < 520:
                draw.line((638, y + 120, 638, y + 150), fill="#64748b", width=4)
            y += 150
        draw.text((52, 654), "Map each term to action so definitions become teaching tools.", fill="#334155", font=body)

    def _paint_index_lookup_flow(draw: ImageDraw.ImageDraw, w: int, h: int) -> None:
        title = _font(44)
        body = _font(22)
        draw.text((52, 20), "Index Lookup Workflow", fill="#0f172a", font=title)
        draw.rounded_rectangle((96, 188, 1180, 548), radius=18, fill="#ffffff", outline="#334155", width=3)
        columns = [
            ("Pick term", "Temperature"),
            ("Find page", "Primary: 84"),
            ("Open chapter", "Read command + example"),
            ("Apply", "Use in your lesson plan"),
        ]
        x = 140
        for idx, (label, detail) in enumerate(columns):
            draw.rounded_rectangle((x, 252, x + 220, 478), radius=14, fill="#e2e8f0", outline="#64748b", width=2)
            draw.text((x + 18, 302), label, fill="#0f172a", font=body)
            draw.text((x + 18, 360), detail, fill="#334155", font=_font(18))
            if idx < len(columns) - 1:
                draw.line((x + 220, 364, x + 252, 364), fill="#334155", width=4)
            x += 252
        draw.text((52, 654), "Use the index first, then jump to the chapter where the term is taught in context.", fill="#334155", font=body)

    _save_figure(FIGURE_LEARNING_LOOP, _paint_learning_loop)
    _save_figure(FIGURE_LEARN_MODE, _paint_learn_mode)
    _save_figure(FIGURE_TRAINING_CURVE, _paint_training_curve)
    _save_figure(FIGURE_QA_GROUNDING, _paint_qa_grounding)
    _save_figure(FIGURE_LESSON_DELIVERY_MAP, _paint_lesson_delivery_map)
    _save_figure(FIGURE_WEEKLY_IMPLEMENTATION_MAP, _paint_weekly_implementation_map)
    _save_figure(FIGURE_IMPROVEMENT_CYCLE, _paint_improvement_cycle)
    _save_figure(FIGURE_GLOSSARY_LOOKUP_MAP, _paint_glossary_lookup_map)
    _save_figure(FIGURE_INDEX_LOOKUP_FLOW, _paint_index_lookup_flow)


def ensure_callout_icons() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)

    def _save(path: Path, painter) -> None:
        size = 80
        img = PILImage.new("RGBA", (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse((2, 2, size - 2, size - 2), fill=(249, 250, 251, 255), outline=(15, 23, 42, 255), width=3)
        painter(draw, size)
        img.save(path, format="PNG", optimize=True)

    def _lightbulb(draw: ImageDraw.ImageDraw, size: int) -> None:
        draw.ellipse((22, 16, 58, 48), outline=(2, 6, 23, 255), width=4, fill=(254, 240, 138, 255))
        draw.rectangle((34, 47, 46, 59), fill=(71, 85, 105, 255))
        draw.rectangle((31, 59, 49, 66), fill=(100, 116, 139, 255))
        draw.line((40, 8, 40, 2), fill=(217, 119, 6, 255), width=3)
        draw.line((18, 20, 12, 15), fill=(217, 119, 6, 255), width=3)
        draw.line((62, 20, 68, 15), fill=(217, 119, 6, 255), width=3)

    def _definition(draw: ImageDraw.ImageDraw, size: int) -> None:
        draw.rounded_rectangle((16, 18, 64, 62), radius=5, outline=(30, 64, 175, 255), width=3, fill=(219, 234, 254, 255))
        draw.line((40, 18, 40, 62), fill=(30, 64, 175, 255), width=2)
        draw.line((24, 30, 34, 30), fill=(30, 64, 175, 255), width=2)
        draw.line((24, 38, 34, 38), fill=(30, 64, 175, 255), width=2)
        draw.line((46, 30, 58, 30), fill=(30, 64, 175, 255), width=2)
        draw.line((46, 38, 58, 38), fill=(30, 64, 175, 255), width=2)

    def _note(draw: ImageDraw.ImageDraw, size: int) -> None:
        draw.rounded_rectangle((18, 16, 62, 62), radius=6, outline=(22, 101, 52, 255), width=3, fill=(220, 252, 231, 255))
        draw.polygon([(46, 16), (62, 16), (62, 32)], fill=(134, 239, 172, 255), outline=(22, 101, 52, 255))
        draw.line((26, 34, 54, 34), fill=(22, 101, 52, 255), width=2)
        draw.line((26, 42, 54, 42), fill=(22, 101, 52, 255), width=2)
        draw.line((26, 50, 47, 50), fill=(22, 101, 52, 255), width=2)

    def _snippet_purpose(draw: ImageDraw.ImageDraw, size: int) -> None:
        draw.rounded_rectangle((15, 24, 65, 56), radius=5, outline=(30, 64, 175, 255), width=3, fill=(219, 234, 254, 255))
        draw.text((23, 30), "</>", fill=(30, 64, 175, 255))

    def _snippet_change(draw: ImageDraw.ImageDraw, size: int) -> None:
        draw.arc((18, 18, 62, 62), start=35, end=215, fill=(124, 58, 237, 255), width=4)
        draw.arc((18, 18, 62, 62), start=215, end=395, fill=(14, 116, 144, 255), width=4)
        draw.polygon([(56, 18), (64, 17), (61, 25)], fill=(124, 58, 237, 255))
        draw.polygon([(24, 62), (16, 63), (19, 55)], fill=(14, 116, 144, 255))

    _save(ICON_LIGHTBULB, _lightbulb)
    _save(ICON_DEFINITION, _definition)
    _save(ICON_NOTE, _note)
    _save(ICON_SNIPPET_PURPOSE, _snippet_purpose)
    _save(ICON_SNIPPET_CHANGE, _snippet_change)


rl_config.invariant = 1
PAGE_TOTAL_HINT = 0


class BookPDFInfo(pdfdoc.PDFInfo):
    def format(self, document):  # type: ignore[override]
        data = {
            "Title": pdfdoc.PDFString(self.title),
            "Author": pdfdoc.PDFString(self.author),
            "Subject": pdfdoc.PDFString(self.subject),
            "Creator": pdfdoc.PDFString(self.creator),
            "Producer": pdfdoc.PDFString(self.producer),
            "Keywords": pdfdoc.PDFString(self.keywords),
            "CreationDate": pdfdoc.PDFString(BOOK_META_CREATION_DATE),
            "ModDate": pdfdoc.PDFString(_build_mod_date()),
            "Trapped": pdfdoc.PDFName(self.trapped),
        }
        return pdfdoc.PDFDictionary(data).format(document)


class DeterministicCanvas(Canvas):
    last_page_count = 0

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("invariant", 1)
        super().__init__(*args, **kwargs)
        self._doc.info = BookPDFInfo()
        self.setTitle(BOOK_META_TITLE)
        self.setAuthor(BOOK_META_AUTHOR)
        self.setSubject(BOOK_META_SUBJECT)
        self.setCreator(BOOK_META_CREATOR)
        self.setKeywords(BOOK_KEYWORDS)

    def save(self):  # type: ignore[override]
        # ReportLab's final page index can be one step ahead at save-time.
        DeterministicCanvas.last_page_count = max(0, self.getPageNumber() - 1)
        super().save()


class BookDocTemplate(BaseDocTemplate):
    def afterFlowable(self, flowable):  # type: ignore[no-untyped-def]
        level = getattr(flowable, "_toc_level", None)
        text = getattr(flowable, "_toc_text", None)
        if level is not None and text:
            self.notify("TOCEntry", (int(level), text, self.page))
        chapter_marker = getattr(flowable, "_running_chapter", None)
        section_marker = getattr(flowable, "_running_section", None)
        if chapter_marker:
            self.current_running_chapter = chapter_marker
        chapter_number = getattr(flowable, "_chapter_number", None)
        if chapter_number is not None:
            self.current_chapter_number = chapter_number
        chapter_accent = getattr(flowable, "_chapter_accent", None)
        if chapter_accent:
            self.current_chapter_accent = chapter_accent
        if section_marker:
            self.current_running_section = section_marker


def ensure_cover_image(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    width, height = 1600, 2262
    image = PILImage.new("RGB", (width, height), "#f8f7f1")
    draw = ImageDraw.Draw(image)

    # Base warm-to-cool vertical gradient.
    for y in range(height):
        ratio = y / max(1, height - 1)
        r = int(248 + (232 - 248) * ratio)
        g = int(247 + (241 - 247) * ratio)
        b = int(241 + (246 - 241) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Abstract geometric field to distinguish Glytch from Kairo cover style.
    accents = PILImage.new("RGBA", (width, height), (0, 0, 0, 0))
    accents_draw = ImageDraw.Draw(accents, "RGBA")
    accents_draw.rectangle((0, 0, width, 320), fill=(17, 94, 89, 255))
    accents_draw.rectangle((0, 320, width, 390), fill=(244, 114, 70, 220))
    accents_draw.polygon([(0, 390), (680, 390), (250, 920), (0, 920)], fill=(14, 116, 144, 165))
    accents_draw.polygon([(1600, 560), (940, 560), (1600, 1320)], fill=(251, 146, 60, 150))
    accents_draw.ellipse((980, 1180, 1780, 1980), fill=(20, 184, 166, 85))
    accents_draw.ellipse((-220, 1540, 520, 2280), fill=(251, 146, 60, 78))

    # Subtle dot matrix layer.
    for y in range(460, height, 60):
        for x in range(70, width, 60):
            accents_draw.ellipse((x, y, x + 6, y + 6), fill=(15, 23, 42, 24))

    accents = accents.filter(ImageFilter.GaussianBlur(0.5))
    image = PILImage.alpha_composite(image.convert("RGBA"), accents).convert("RGB")

    # Clean content slab for typography.
    slab = PILImage.new("RGBA", (width, height), (0, 0, 0, 0))
    slab_draw = ImageDraw.Draw(slab, "RGBA")
    slab_draw.rounded_rectangle((126, 868, 1478, 1988), radius=34, fill=(250, 250, 248, 232), outline=(15, 23, 42, 56), width=2)
    slab_draw.rectangle((170, 924, 1434, 952), fill=(17, 94, 89, 220))
    slab_draw.rectangle((170, 1904, 1434, 1932), fill=(30, 41, 59, 165))
    image = PILImage.alpha_composite(image.convert("RGBA"), slab).convert("RGB")

    def load_font(size: int) -> ImageFont.ImageFont:
        candidates = [
            "/System/Library/Fonts/Supplemental/Helvetica.ttc",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        ]
        for candidate in candidates:
            try:
                return ImageFont.truetype(candidate, size=size)
            except OSError:
                continue
        return ImageFont.load_default()

    draw = ImageDraw.Draw(image)
    title_font = load_font(128)
    chapter_font = load_font(96)
    tag_font = load_font(40)
    subtitle_font = load_font(30)
    meta_font = load_font(28)
    strip_font = load_font(30)
    author_font = load_font(42)

    def draw_centered_text(text: str, font: ImageFont.ImageFont, y: int, fill: tuple[int, int, int]) -> None:
        left, right = 280, 2140
        bbox = draw.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        x = int(left + ((right - left - width) / 2))
        draw.text((x, y), text, fill=fill, font=font)

    draw.text((176, 1032), "TECH I CAN", fill=(15, 23, 42), font=title_font)
    draw.text((176, 1178), "Glytch", fill=(13, 148, 136), font=chapter_font)
    draw.text((176, 1330), BOOK_TAGLINE, fill=(51, 65, 85), font=tag_font)
    draw.text((176, 1428), BOOK_SUBTITLE, fill=(30, 41, 59), font=subtitle_font)
    draw.text((176, 1580), BOOK_EDITION, fill=(71, 85, 105), font=meta_font)
    draw.text((176, 1632), BOOK_SERIES, fill=(71, 85, 105), font=meta_font)
    draw.text((176, 1700), f"By {BOOK_AUTHOR}", fill=(15, 23, 42), font=author_font)
    draw_centered_text("Understand. Check. Review. Decide.", strip_font, 1776, (15, 23, 42))

    image.save(
        path,
        format="JPEG",
        quality=56,
        optimize=True,
        progressive=True,
        subsampling=2,
    )


def clean_lines(text: str) -> list[str]:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "---":
            continue
        lines.append(line.rstrip())
    return lines


def validate_book_structure(lines: list[str]) -> None:
    text = "\n".join(lines)
    if "## References (APA 7th Edition)" not in text:
        raise SystemExit("Book markdown is missing the APA references section.")

    code_blocks: list[tuple[int, int, str]] = []
    in_code = False
    start = 0
    lang = ""
    for idx, line in enumerate(lines, start=1):
        if line.startswith("```"):
            if not in_code:
                in_code = True
                start = idx
                lang = line[3:].strip().lower()
            else:
                code_blocks.append((start, idx, lang))
                in_code = False
    if in_code:
        raise SystemExit("Book markdown has an unclosed fenced code block.")

    allowed_languages = {"bash", "sh", "text", "python", "yaml", "json", "sql", "toml"}
    unlabeled_blocks = [start for start, _end, lang in code_blocks if not lang]
    if unlabeled_blocks:
        raise SystemExit(f"Code block(s) must include a language label at lines: {unlabeled_blocks}")
    unsupported_blocks = [(start, lang) for start, _end, lang in code_blocks if lang not in allowed_languages]
    if unsupported_blocks:
        detail = ", ".join(f"line {line}: '{lang}'" for line, lang in unsupported_blocks[:12])
        raise SystemExit(f"Unsupported code block language label(s): {detail}")

    missing_snippet: list[int] = []
    shell_output_markers: list[int] = []
    shell_prompt_lines: list[int] = []
    smart_quote_lines: list[int] = []
    for start_line, _end, block_lang in code_blocks:
        block_lines = lines[start_line:_end - 1]
        for idx, content_line in enumerate(block_lines, start=start_line + 1):
            stripped_content = content_line.strip()
            if any(ch in content_line for ch in "“”‘’"):
                smart_quote_lines.append(idx)
            if block_lang in {"bash", "sh"} and stripped_content.startswith("$"):
                shell_prompt_lines.append(idx)
            if block_lang in {"bash", "sh"} and re.match(
                r"^(Generated|Output|Traceback|ERROR|Warning:|Ghostscript|Book PDF is)\b",
                stripped_content,
            ):
                shell_output_markers.append(idx)
        if block_lang not in {"bash", "sh"}:
            continue
        context = [lines[i - 1].strip() for i in range(max(1, start_line - 6), start_line)]
        if not any(item.startswith("Snippet Purpose:") for item in context):
            missing_snippet.append(start_line)
    if missing_snippet:
        raise SystemExit(f"Missing 'Snippet Purpose:' before bash block lines: {missing_snippet}")
    if shell_prompt_lines:
        raise SystemExit(f"Shell snippets must be copy/paste safe: remove '$' prompt at lines: {shell_prompt_lines}")
    if smart_quote_lines:
        raise SystemExit(f"Code snippets must not include smart quotes at lines: {smart_quote_lines}")
    if shell_output_markers:
        raise SystemExit(
            "Shell snippets should contain commands only; move expected output into a separate text block. "
            f"Output-like lines detected at: {shell_output_markers}"
        )

    glossary_index = next((i for i, line in enumerate(lines) if line.startswith("# Chapter 41: Glossary")), -1)
    keyword_index_start = next(
        (i for i, line in enumerate(lines) if KEY_WORDS_INDEX_HEADING_RE.match(line.strip())),
        -1,
    )
    all_params = set(re.findall(r"--[a-zA-Z0-9_]+", text))
    if glossary_index >= 0 and all_params:
        glossary_slice_end = keyword_index_start if keyword_index_start > glossary_index else len(lines)
        glossary_text = "\n".join(lines[glossary_index:glossary_slice_end])
        glossary_params = set(re.findall(r"\*\*`(--[a-zA-Z0-9_]+)`\*\*", glossary_text))
        missing_glossary_params = sorted(param for param in all_params if param not in glossary_params)
        if missing_glossary_params:
            raise SystemExit(
                f"Parameter(s) used in manuscript but missing from glossary: {missing_glossary_params}"
            )

    # Image accessibility and caption discipline.
    image_line_re = re.compile(r"^!\[(.*?)\]\((.*?)\)$")
    for idx, line in enumerate(lines):
        stripped = line.strip()
        image_match = image_line_re.match(stripped)
        if not image_match:
            continue
        alt_text = image_match.group(1).strip()
        if len(alt_text) < 8:
            raise SystemExit(f"Image at line {idx + 1} must include meaningful alt text.")

        caption_found = False
        for probe in range(idx + 1, min(len(lines), idx + 5)):
            candidate = lines[probe].strip()
            if not candidate:
                continue
            caption_found = candidate.lower().startswith("caption:")
            break
        if not caption_found:
            raise SystemExit(f"Image at line {idx + 1} must be followed by a 'Caption:' line.")

    # Guard against repeated boilerplate in learning/assessment bullets.
    section = ""
    chapter = ""
    learned_seen: dict[str, str] = {}
    reflection_seen: dict[str, str] = {}
    for raw_line in lines:
        stripped = raw_line.strip()
        if stripped.startswith("# Chapter "):
            chapter = stripped[2:].strip()
            section = ""
            continue
        if stripped.startswith("## "):
            section = stripped[3:].strip().lower()
            continue
        if not stripped.startswith("- "):
            continue
        bullet = stripped[2:].strip().lower()
        if section.startswith("action 1: what you learned"):
            prior = learned_seen.get(bullet)
            if prior and prior != chapter:
                raise SystemExit(f"Repeated 'What you learned' bullet in {prior} and {chapter}: {bullet}")
            learned_seen[bullet] = chapter
        if section.startswith("action 2: reflect"):
            prior = reflection_seen.get(bullet)
            if prior and prior != chapter:
                raise SystemExit(f"Repeated reflection question in {prior} and {chapter}: {bullet}")
            reflection_seen[bullet] = chapter

    # Treat markdown as publishable master: chapter intros must stand on their own.
    chapter = ""
    in_intro = False
    intro_words = 0
    chapter_intro_counts: dict[str, int] = {}
    for raw_line in lines:
        stripped = raw_line.strip()
        if stripped.startswith("# "):
            if chapter.startswith("Chapter "):
                chapter_intro_counts[chapter] = intro_words
            chapter = stripped[2:].strip()
            in_intro = False
            intro_words = 0
            continue
        if stripped.startswith("## "):
            in_intro = stripped[3:].strip().lower() == "about this chapter"
            continue
        if not in_intro or not stripped or stripped.startswith("![") or stripped.startswith("Caption:"):
            continue
        intro_words += len(stripped.split())
    if chapter.startswith("Chapter "):
        chapter_intro_counts[chapter] = intro_words

    short_intros = [(name, count) for name, count in chapter_intro_counts.items() if count < MIN_INTRO_WORDS]
    if short_intros:
        sample = ", ".join(f"{name} ({count} words)" for name, count in short_intros[:8])
        raise SystemExit(f"Chapter intro sections are too short (<{MIN_INTRO_WORDS} words): {sample}")


def extract_keyword_terms(lines: list[str]) -> list[str]:
    terms: list[str] = []
    in_glossary = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# Chapter 41: Glossary"):
            in_glossary = True
            continue
        if in_glossary and KEY_WORDS_INDEX_HEADING_RE.match(stripped):
            break
        if not in_glossary or not stripped.startswith("- **"):
            continue
        match = re.match(r"^- \*\*`?([^*`]+?)`?\*\*:", stripped)
        if not match:
            continue
        term = match.group(1).strip()
        if term.startswith("--"):
            continue
        if term and term not in terms:
            terms.append(term)
    for required in REQUIRED_INDEX_TERMS:
        if required not in terms:
            terms.append(required)
    return terms


def find_heading_page(reader: PdfReader, heading: str) -> int | None:
    needle = heading.lower()
    for idx, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").lower()
        if needle in text:
            return idx
    return None


def find_heading_page_last(reader: PdfReader, heading: str) -> int | None:
    needle = heading.lower()
    found = None
    for idx, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").lower()
        if needle in text:
            found = idx
    return found


def build_keyword_page_map(pdf_path: Path, terms: list[str]) -> dict[str, list[int]]:
    reader = PdfReader(str(pdf_path))
    index_page = find_heading_page_last(reader, "Key Words Index")
    max_page = (index_page - 1) if index_page else len(reader.pages)

    def _first_body_page() -> int:
        for idx in range(1, max_page + 1):
            text = (reader.pages[idx - 1].extract_text() or "")
            low = text.lower()
            if "chapter 1: welcome to tech i can" in low and "you are about to learn ai by doing" in low:
                return idx
        return 1

    def _is_substantive_body_page(raw_text: str) -> bool:
        low = raw_text.lower()
        if not low.strip():
            return False
        if "in this chapter . . ." in low and "what you will walk away with" in low:
            return False
        return True

    first_body_page = _first_body_page()
    page_text: list[tuple[int, str]] = []
    for page_no in range(first_body_page, max_page + 1):
        raw = reader.pages[page_no - 1].extract_text() or ""
        if not _is_substantive_body_page(raw):
            continue
        page_text.append((page_no, raw.lower()))

    def _patterns_for_term(term: str) -> list[str]:
        alias_terms = TERM_SEARCH_ALIASES.get(term, [term])
        patterns: list[str] = []
        for alias in alias_terms:
            if alias.startswith("--"):
                patterns.append(rf"(?<!\w){re.escape(alias)}(?!\w)")
            else:
                token = re.escape(alias.lower()).replace(r"\ ", r"\s+")
                patterns.append(rf"(?<!\w){token}(?!\w)")
        return patterns

    page_map: dict[str, list[int]] = defaultdict(list)
    for term in terms:
        patterns = _patterns_for_term(term)
        for page_no, text in page_text:
            if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns):
                page_map[term].append(page_no)
    return dict(page_map)


def inline_markup(text: str) -> str:
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = escape(text)
    text = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    return text


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_table_separator(line: str) -> bool:
    cells = split_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in cells)


def chapter_accent_for_heading(heading: str) -> str:
    match = re.match(r"^Chapter\s+(\d+):", heading, flags=re.IGNORECASE)
    if not match:
        return BRAND_ACCENTS[0]
    chapter_no = int(match.group(1))
    return BRAND_ACCENTS[(chapter_no - 1) % len(BRAND_ACCENTS)]


def tint(color_hex: str, amount: float = 0.85) -> colors.Color:
    base = colors.HexColor(color_hex)
    amt = min(1.0, max(0.0, amount))
    return colors.Color(
        base.red + (1 - base.red) * amt,
        base.green + (1 - base.green) * amt,
        base.blue + (1 - base.blue) * amt,
    )


def wrap_code_lines(lines: list[str], width: int = 74) -> str:
    wrapped: list[str] = []
    for line in lines:
        if not line:
            wrapped.append("")
            continue
        indent_len = len(line) - len(line.lstrip(" "))
        indent = line[:indent_len]
        body = line[indent_len:]
        available = max(24, width - indent_len)
        parts = textwrap.wrap(body, width=available, break_long_words=False, break_on_hyphens=False)
        if not parts:
            wrapped.append(line)
            continue
        wrapped.append(indent + parts[0])
        continuation_indent = indent + "  "
        wrapped.extend(continuation_indent + part for part in parts[1:])
    return "\n".join(wrapped)


def merge_callout_continuations(lines: list[str]) -> list[str]:
    merged: list[str] = []
    i = 0
    callout_pattern = re.compile(
        r"^(Lightbulb Takeaway|Definition|Note|Snippet Purpose|Snippet Change):\s*(.*)$",
        flags=re.IGNORECASE,
    )
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        match = callout_pattern.match(stripped)
        if not match:
            merged.append(line)
            i += 1
            continue

        label = match.group(1).strip()
        message_parts = [match.group(2).strip()] if match.group(2).strip() else []
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if not nxt:
                break
            if (
                nxt.startswith(("```", "- ", "# ", "## ", "### ", "|"))
                or re.match(r"^\d+\.\s+", nxt)
                or callout_pattern.match(nxt)
            ):
                break
            message_parts.append(nxt)
            i += 1
        message = " ".join(message_parts).strip()
        merged.append(f"{label}: {message}" if message else f"{label}:")
    return merged


def chapter_focus_bridge(chapter_title: str, objectives: list[str]) -> str:
    cleaned = [item.strip().rstrip(".") for item in objectives if item.strip()]
    if not cleaned:
        return ""

    primary = cleaned[0]
    secondary = cleaned[1] if len(cleaned) > 1 else cleaned[0]
    tertiary = cleaned[2] if len(cleaned) > 2 else cleaned[-1]
    variants = [
        f"In practical terms, this chapter helps you {primary}, then {secondary}, and finally {tertiary}. Keep your notes focused on what changed and why.",
        f"Think of this chapter as a guided rehearsal for {primary}. You then deepen that work through {secondary} and {tertiary}, so you can explain your results with confidence.",
        f"Your main target here is to {primary}. The chapter then extends into {secondary} and {tertiary}, giving you a complete evidence trail to discuss.",
        f"This chapter moves step by step: first {primary}, then {secondary}, then {tertiary}. By the end, you should be able to teach the same sequence clearly to someone else.",
    ]
    index = sum(ord(ch) for ch in chapter_title) % len(variants)
    return variants[index]


def parse_markdown_image(line: str) -> tuple[str, str] | None:
    match = re.match(r"^!\[(.*?)\]\((.*?)\)$", line.strip())
    if not match:
        return None
    alt_text = match.group(1).strip()
    rel_path = match.group(2).strip()
    if not rel_path:
        return None
    return (alt_text, rel_path)


def pick_primary_pages(pages: list[int], max_items: int = 5) -> list[int]:
    if not pages:
        return []
    if len(pages) <= max_items:
        return pages
    anchors = [0, len(pages) // 4, len(pages) // 2, (3 * len(pages)) // 4, len(pages) - 1]
    chosen: list[int] = []
    for idx in anchors:
        page = pages[idx]
        if page not in chosen:
            chosen.append(page)
        if len(chosen) >= max_items:
            break
    return chosen


def _page_ranges(pages: list[int]) -> list[tuple[int, int]]:
    if not pages:
        return []
    ranges: list[tuple[int, int]] = []
    start = prev = pages[0]
    for page in pages[1:]:
        if page == prev + 1:
            prev = page
            continue
        ranges.append((start, prev))
        start = prev = page
    ranges.append((start, prev))
    return ranges


def format_page_ranges(pages: list[int], max_ranges: int | None = None) -> str:
    if not pages:
        return "not found"
    ranges = _page_ranges(pages)
    truncated = False
    if max_ranges is not None and len(ranges) > max_ranges:
        ranges = ranges[:max_ranges]
        truncated = True

    rendered: list[str] = []
    for start, end in ranges:
        rendered.append(str(start) if start == end else f"{start}-{end}")
    joined = ", ".join(rendered)
    return f"{joined}, ..." if truncated else joined


def code_language_label(lang: str) -> str:
    label_map = {
        "bash": "Bash",
        "sh": "Shell",
        "python": "Python",
        "yaml": "YAML",
        "json": "JSON",
        "sql": "SQL",
        "toml": "TOML",
        "text": "Text Output",
    }
    return label_map.get(lang.lower(), lang.upper() if lang else "Code")


def callout_icon(label: str) -> str:
    lookup = {
        "lightbulb takeaway": "✦",
        "definition": "◆",
        "note": "▣",
        "snippet purpose": "⌘",
        "snippet change": "↺",
    }
    return lookup.get(label.lower(), "•")


def callout_icon_path(label: str) -> Path | None:
    lookup = {
        "lightbulb takeaway": ICON_LIGHTBULB,
        "definition": ICON_DEFINITION,
        "note": ICON_NOTE,
        "snippet purpose": ICON_SNIPPET_PURPOSE,
        "snippet change": ICON_SNIPPET_CHANGE,
    }
    return lookup.get(label.lower())


def callout_icon_markup(label: str) -> str:
    path = callout_icon_path(label)
    if path and path.exists():
        return f'<img src="{escape(str(path))}" width="10" height="10" valign="middle"/>'
    return escape(callout_icon(label))


def build_styles(fonts: dict[str, str]) -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    flow_control = {
        "allowOrphans": 0,
        "allowWidows": 0,
        "splitLongWords": 0,
    }
    return {
        "book_title": ParagraphStyle(
            "BookTitle",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=30,
            leading=34,
            alignment=1,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=10,
            **flow_control,
        ),
        "book_subtitle": ParagraphStyle(
            "BookSubtitle",
            parent=base["BodyText"],
            fontName=fonts["body"],
            fontSize=13,
            leading=18,
            alignment=1,
            textColor=colors.HexColor("#334155"),
            spaceAfter=6,
            **flow_control,
        ),
        "book_tag": ParagraphStyle(
            "BookTag",
            parent=base["BodyText"],
            fontName=fonts["body"],
            fontSize=12,
            leading=16,
            alignment=1,
            textColor=colors.HexColor("#0f766e"),
            spaceAfter=14,
            **flow_control,
        ),
        "book_meta": ParagraphStyle(
            "BookMeta",
            parent=base["BodyText"],
            fontName=fonts["body"],
            fontSize=10.5,
            leading=14,
            alignment=1,
            textColor=colors.HexColor("#475569"),
            spaceAfter=8,
            **flow_control,
        ),
        "running_header": ParagraphStyle(
            "RunningHeader",
            parent=base["BodyText"],
            fontName=fonts["body"],
            fontSize=10.0,
            leading=12.5,
            alignment=0,
            textColor=colors.HexColor("#334155"),
            spaceAfter=0,
            **flow_control,
        ),
        "dedication": ParagraphStyle(
            "Dedication",
            parent=base["BodyText"],
            fontName=fonts["body"],
            fontSize=12.0,
            leading=18.0,
            alignment=1,
            textColor=colors.HexColor("#1e293b"),
            spaceAfter=10,
            **flow_control,
        ),
        "toc_title": ParagraphStyle(
            "TocTitle",
            parent=base["Heading1"],
            fontName=fonts["display"],
            fontSize=31,
            leading=34,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=16,
            **flow_control,
        ),
        "toc_item": ParagraphStyle(
            "TocItem",
            parent=base["BodyText"],
            fontName=fonts["body"],
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#1f2937"),
            leftIndent=8,
            spaceAfter=2,
            **flow_control,
        ),
        "copyright": ParagraphStyle(
            "Copyright",
            parent=base["BodyText"],
            fontName=fonts["body"],
            fontSize=10.5,
            leading=16,
            alignment=4,
            textColor=colors.HexColor("#334155"),
            spaceAfter=8,
            **flow_control,
        ),
        "imprint": ParagraphStyle(
            "Imprint",
            parent=base["BodyText"],
            fontName=fonts["body"],
            fontSize=10,
            leading=14,
            alignment=0,
            textColor=colors.HexColor("#1f2937"),
            spaceAfter=4,
            **flow_control,
        ),
        "chapter": ParagraphStyle(
            "ChapterTitle",
            parent=base["Heading1"],
            fontName=fonts["chapter"],
            fontSize=23,
            leading=29,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=12,
            spaceAfter=10,
            **flow_control,
        ),
        "section": ParagraphStyle(
            "SectionTitle",
            parent=base["Heading2"],
            fontName=fonts["section"],
            fontSize=14.4,
            leading=18.2,
            textColor=colors.HexColor("#1f2937"),
            spaceBefore=10,
            spaceAfter=6,
            **flow_control,
        ),
        "intro_bridge": ParagraphStyle(
            "IntroBridge",
            parent=base["BodyText"],
            fontName=fonts["body"],
            fontSize=11.0,
            leading=16.2,
            alignment=4,
            textColor=colors.HexColor("#1f2937"),
            backColor=colors.HexColor("#f8fafc"),
            borderColor=colors.HexColor("#cbd5e1"),
            borderWidth=0.6,
            borderPadding=6,
            borderRadius=2,
            spaceBefore=5,
            spaceAfter=8,
            **flow_control,
        ),
        "takeaway_box": ParagraphStyle(
            "TakeawayBox",
            parent=base["BodyText"],
            fontName=fonts["section"],
            fontSize=11,
            leading=16,
            textColor=colors.HexColor("#7c2d12"),
            backColor=colors.HexColor("#fef3c7"),
            borderColor=colors.HexColor("#f59e0b"),
            borderWidth=0.8,
            borderPadding=6,
            borderRadius=4,
            leftIndent=0,
            rightIndent=0,
            spaceBefore=10,
            spaceAfter=6,
            keepWithNext=1,
            **flow_control,
        ),
        "definition_box": ParagraphStyle(
            "DefinitionBox",
            parent=base["BodyText"],
            fontName=fonts["section"],
            fontSize=11,
            leading=16,
            textColor=colors.HexColor("#111827"),
            backColor=colors.HexColor("#e2e8f0"),
            borderColor=colors.HexColor("#64748b"),
            borderWidth=0.8,
            borderPadding=6,
            borderRadius=2,
            leftIndent=0,
            rightIndent=0,
            spaceBefore=8,
            spaceAfter=6,
            keepWithNext=1,
            **flow_control,
        ),
        "note_box": ParagraphStyle(
            "NoteBox",
            parent=base["BodyText"],
            fontName=fonts["section"],
            fontSize=11,
            leading=16,
            textColor=colors.HexColor("#0f172a"),
            backColor=colors.HexColor("#f8fafc"),
            borderColor=colors.HexColor("#94a3b8"),
            borderWidth=0.8,
            borderPadding=6,
            borderRadius=2,
            leftIndent=0,
            rightIndent=0,
            spaceBefore=8,
            spaceAfter=6,
            keepWithNext=1,
            **flow_control,
        ),
        "snippet_box": ParagraphStyle(
            "SnippetBox",
            parent=base["BodyText"],
            fontName=fonts["section"],
            fontSize=11,
            leading=16,
            textColor=colors.HexColor("#1e3a8a"),
            backColor=colors.HexColor("#dbeafe"),
            borderColor=colors.HexColor("#3b82f6"),
            borderWidth=0.8,
            borderPadding=6,
            borderRadius=2,
            leftIndent=0,
            rightIndent=0,
            spaceBefore=8,
            spaceAfter=5,
            keepWithNext=1,
            **flow_control,
        ),
        "success_box": ParagraphStyle(
            "SuccessBox",
            parent=base["BodyText"],
            fontName=fonts["section"],
            fontSize=11,
            leading=16,
            textColor=colors.HexColor("#14532d"),
            backColor=colors.HexColor("#dcfce7"),
            borderColor=colors.HexColor("#22c55e"),
            borderWidth=0.8,
            borderPadding=6,
            borderRadius=2,
            leftIndent=0,
            rightIndent=0,
            spaceBefore=8,
            spaceAfter=6,
            keepWithNext=1,
            **flow_control,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName=fonts["body"],
            fontSize=11.0,
            leading=16.4,
            alignment=0,
            textColor=colors.HexColor("#111827"),
            leftIndent=2,
            rightIndent=2,
            spaceAfter=8,
            **flow_control,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["BodyText"],
            fontName=fonts["body"],
            fontSize=11.0,
            leading=16.2,
            leftIndent=24,
            bulletIndent=11,
            textColor=colors.HexColor("#111827"),
            spaceAfter=4,
            **flow_control,
        ),
        "learned_detail": ParagraphStyle(
            "LearnedDetail",
            parent=base["BodyText"],
            fontName=fonts["body"],
            fontSize=11.0,
            leading=16.2,
            leftIndent=24,
            bulletIndent=11,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=4,
            **flow_control,
        ),
        "code": ParagraphStyle(
            "Code",
            fontName="Courier",
            fontSize=10.0,
            leading=14.0,
            textColor=colors.HexColor("#020617"),
            backColor=colors.HexColor("#f1f5f9"),
            borderColor=colors.HexColor("#94a3b8"),
            borderWidth=0.6,
            borderPadding=7,
            leftIndent=1,
            rightIndent=1,
            spaceBefore=4,
            spaceAfter=9,
            **flow_control,
        ),
        "code_label": ParagraphStyle(
            "CodeLabel",
            parent=base["BodyText"],
            fontName=fonts["section"],
            fontSize=10.0,
            leading=12.2,
            textColor=colors.HexColor("#1e3a8a"),
            backColor=colors.HexColor("#dbeafe"),
            borderColor=colors.HexColor("#93c5fd"),
            borderWidth=0.5,
            borderPadding=4,
            spaceBefore=6,
            spaceAfter=2,
            **flow_control,
        ),
        "figure_caption": ParagraphStyle(
            "FigureCaption",
            parent=base["BodyText"],
            fontName=fonts["section"],
            fontSize=10.0,
            leading=13.2,
            textColor=colors.HexColor("#334155"),
            alignment=1,
            spaceBefore=2,
            spaceAfter=2,
            **flow_control,
        ),
        "figure_alt": ParagraphStyle(
            "FigureAlt",
            parent=base["BodyText"],
            fontName=fonts["body"],
            fontSize=10.0,
            leading=13.2,
            textColor=colors.HexColor("#475569"),
            alignment=1,
            spaceBefore=0,
            spaceAfter=8,
            **flow_control,
        ),
        "index_entry": ParagraphStyle(
            "IndexEntry",
            parent=base["BodyText"],
            fontName=fonts["body"],
            fontSize=10.2,
            leading=13.8,
            leftIndent=16,
            bulletIndent=4,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=1,
            **flow_control,
        ),
        "cell": ParagraphStyle(
            "Cell",
            parent=base["BodyText"],
            fontName=fonts["body"],
            fontSize=10.0,
            leading=13.2,
            **flow_control,
        ),
        "toc_level_0": ParagraphStyle(
            "TocLevel0",
            parent=base["BodyText"],
            fontName=fonts["body"],
            fontSize=12.4,
            leading=15.8,
            textColor=colors.HexColor("#111827"),
            leftIndent=10,
            firstLineIndent=0,
            spaceBefore=4,
            spaceAfter=3,
            **flow_control,
        ),
        "toc_level_1": ParagraphStyle(
            "TocLevel1",
            parent=base["BodyText"],
            fontName=fonts["body"],
            fontSize=11.3,
            leading=14.8,
            textColor=colors.HexColor("#1e293b"),
            leftIndent=30,
            firstLineIndent=0,
            spaceBefore=2,
            spaceAfter=2,
            **flow_control,
        ),
        "chapter_prelude_kicker": ParagraphStyle(
            "ChapterPreludeKicker",
            parent=base["BodyText"],
            fontName=fonts["display"],
            fontSize=34,
            leading=37,
            alignment=1,
            textColor=colors.HexColor("#111827"),
            spaceAfter=10,
            **flow_control,
        ),
        "chapter_prelude_story": ParagraphStyle(
            "ChapterPreludeStory",
            parent=base["BodyText"],
            fontName=fonts["body"],
            fontSize=11.0,
            leading=16.2,
            alignment=0,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=10,
            **flow_control,
        ),
        "chapter_prelude_section": ParagraphStyle(
            "ChapterPreludeSection",
            parent=base["BodyText"],
            fontName=fonts["section"],
            fontSize=13.2,
            leading=16.8,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=3,
            spaceAfter=4,
            **flow_control,
        ),
        "chapter_prelude_bullet": ParagraphStyle(
            "ChapterPreludeBullet",
            parent=base["BodyText"],
            fontName=fonts["body"],
            fontSize=11.0,
            leading=16.2,
            leftIndent=18,
            bulletIndent=7,
            textColor=colors.HexColor("#111827"),
            spaceAfter=2,
            **flow_control,
        ),
        "chapter_prelude_focus": ParagraphStyle(
            "ChapterPreludeFocus",
            parent=base["BodyText"],
            fontName=fonts["section"],
            fontSize=10.6,
            leading=14,
            textColor=colors.HexColor("#1e3a8a"),
            spaceBefore=6,
            **flow_control,
        ),
        "icon_legend_label": ParagraphStyle(
            "IconLegendLabel",
            parent=base["BodyText"],
            fontName=fonts["section"],
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=2,
            **flow_control,
        ),
        "icon_legend_body": ParagraphStyle(
            "IconLegendBody",
            parent=base["BodyText"],
            fontName=fonts["body"],
            fontSize=11.0,
            leading=16.2,
            textColor=colors.HexColor("#111827"),
            spaceAfter=2,
            **flow_control,
        ),
        "subsection": ParagraphStyle(
            "SubsectionTitle",
            parent=base["Heading3"],
            fontName=fonts["section"],
            fontSize=12.0,
            leading=15.2,
            textColor=colors.HexColor("#1f2937"),
            spaceBefore=8,
            spaceAfter=4,
            **flow_control,
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

    cols = max(len(r) for r in table_rows)
    for row in table_rows:
        while len(row) < cols:
            row.append(Paragraph("", styles["cell"]))

    table = Table(table_rows, colWidths=[width / cols] * cols, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
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
    story.extend([table, Spacer(1, 8)])


def append_chapter_band(story: list[object], width: float, accent_hex: str) -> None:
    band_w = min(width * 0.36, 64 * mm)
    band = Table([[""]], colWidths=[band_w], rowHeights=[2.6 * mm], hAlign="LEFT")
    band.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(accent_hex)),
                ("LINEBELOW", (0, 0), (-1, -1), 0, colors.white),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    story.append(band)
    story.append(Spacer(1, 3))


def chapter_toc_title(chapter_heading: str) -> str:
    return chapter_heading.strip()


def register_display_fonts() -> dict[str, str]:
    fonts = {
        "display": "Helvetica-Bold",
        "chapter": "Helvetica-Bold",
        "section": "Helvetica-Bold",
        "body": "Helvetica",
    }
    for font_name, font_path in DISPLAY_FONT_CANDIDATES:
        if not Path(font_path).exists():
            continue
        try:
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            fonts["display"] = font_name
            break
        except Exception:
            continue
    return fonts


def extract_chapter_preludes(lines: list[str]) -> dict[str, dict[str, object]]:
    chapter_data: dict[str, dict[str, object]] = {}
    chapter_heading = ""
    section = ""
    intro_lines: list[str] = []
    learn_items: list[str] = []

    def commit() -> None:
        nonlocal intro_lines, learn_items
        if not chapter_heading:
            return
        intro_text = " ".join(line.strip() for line in intro_lines if line.strip())
        clean_items = [item.strip() for item in learn_items if item.strip()]
        chapter_data[chapter_heading] = {"intro": intro_text, "learn": clean_items}
        intro_lines = []
        learn_items = []

    for raw in lines:
        stripped = raw.strip()
        if stripped.startswith("# "):
            commit()
            chapter_heading = stripped[2:].strip() if stripped.startswith("# Chapter ") else ""
            section = ""
            continue
        if not chapter_heading:
            continue
        if stripped.startswith("## "):
            section = stripped[3:].strip().lower()
            continue
        if section == "about this chapter":
            if stripped and not stripped.startswith("![") and not stripped.startswith("Caption:"):
                intro_lines.append(stripped)
            continue
        if section == "what you will learn in this chapter" and stripped.startswith("- "):
            learn_items.append(stripped[2:].strip())
            continue
    commit()
    return chapter_data


def extract_front_matter_paragraphs(lines: list[str], heading: str) -> list[str]:
    target = heading.strip().lower()
    in_section = False
    current_lines: list[str] = []
    paragraphs: list[str] = []

    def flush() -> None:
        if current_lines:
            paragraphs.append(" ".join(current_lines).strip())
            current_lines.clear()

    for raw in lines:
        stripped = raw.strip()
        if stripped.startswith("#"):
            if in_section:
                flush()
                break
            heading_text = stripped.lstrip("#").strip().lower()
            in_section = heading_text == target
            continue
        if not in_section:
            continue
        if stripped == "---":
            continue
        if not stripped:
            flush()
            continue
        current_lines.append(stripped)

    flush()
    return [item for item in paragraphs if item]


def build_chapter_prelude_summary(heading_text: str, intro_text: str, learn_items: list[str]) -> str:
    title = re.sub(r"^Chapter\s+\d+:\s*", "", heading_text, flags=re.IGNORECASE).strip()
    topic = title if title else "this chapter"
    points = [item.strip().rstrip(".") for item in learn_items if item.strip()]
    topic_clause = f"'{topic}'" if topic and topic.lower() != "this chapter" else "this chapter"
    if len(points) >= 3:
        return (
            f"This chapter focuses on {topic_clause}. "
            f"You will examine {points[0]}, {points[1]}, and {points[2]}."
        )
    if len(points) == 2:
        return f"This chapter focuses on {topic_clause}. You will examine {points[0]} and {points[1]}."
    if len(points) == 1:
        return f"This chapter focuses on {topic_clause}. You will examine {points[0]}."

    sentences = [chunk.strip() for chunk in re.split(r"(?<=[.!?])\s+", intro_text) if chunk.strip()]
    if sentences:
        return f"This chapter focuses on {topic_clause}. {sentences[0]}"
    return f"This chapter focuses on {topic_clause}. You will work through the topic in clear, practical steps."


def chapter_prelude_visual_meta(heading_text: str) -> tuple[Path | None, str, str]:
    match = re.match(r"^Chapter\s+(\d+):", heading_text, flags=re.IGNORECASE)
    chapter_no = int(match.group(1)) if match else 0
    if 1 <= chapter_no <= 8:
        return (ICON_LIGHTBULB, "Foundations", "Build confidence with the core workflow.")
    if 9 <= chapter_no <= 16:
        return (ICON_NOTE, "Classroom Core", "Move from setup to repeatable delivery.")
    if 17 <= chapter_no <= 25:
        return (ICON_DEFINITION, "Technical Depth", "Understand why model behavior changes.")
    if 26 <= chapter_no <= 34:
        return (ICON_SNIPPET_PURPOSE, "Applied Practice", "Run guided labs and evidence-rich tasks.")
    if 35 <= chapter_no <= 40:
        return (ICON_SNIPPET_CHANGE, "Operations", "Keep lessons reliable, measurable, and calm.")
    return (ICON_NOTE, "Reference", "Use this section as a quick teaching lookup.")


def append_chapter_prelude_page(
    story: list[object],
    styles: dict[str, ParagraphStyle],
    heading_text: str,
    chapter_preludes: dict[str, dict[str, object]],
    width: float,
) -> None:
    prelude = chapter_preludes.get(heading_text, {})
    intro_text = str(prelude.get("intro", "")).strip()
    learn_items = [str(item) for item in prelude.get("learn", [])]
    display_title = chapter_toc_title(heading_text)
    if not intro_text:
        intro_text = (
            "This chapter gives you a guided path through the next skill in your Glytch journey. "
            "You will work in small steps, collect evidence, and explain what your outputs show."
        )
    story_seed = build_chapter_prelude_summary(heading_text, intro_text, learn_items)
    icon_path, track_label, track_hint = chapter_prelude_visual_meta(heading_text)

    track_icon: object
    if icon_path and icon_path.exists():
        track_icon = Image(str(icon_path), width=9 * mm, height=9 * mm, hAlign="LEFT")
    else:
        track_icon = Paragraph("•", styles["chapter_prelude_section"])

    track_text = Paragraph(
        f"<b>{inline_markup(track_label)}</b><br/>{inline_markup(track_hint)}",
        styles["chapter_prelude_story"],
    )
    track_table = Table([[track_icon, track_text]], colWidths=[12 * mm, width - (12 * mm)], hAlign="LEFT")
    track_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#e2e8f0")),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#94a3b8")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    card_rows: list[list[object]] = []
    card_rows.append([track_table])
    card_rows.append([Paragraph("Chapter Overview", styles["chapter_prelude_kicker"])])
    card_rows.append([Paragraph(inline_markup(story_seed), styles["chapter_prelude_story"])])
    if learn_items:
        card_rows.append([Paragraph("What you will walk away with", styles["chapter_prelude_section"])])
        for item in learn_items[:4]:
            card_rows.append([Paragraph(inline_markup(item), styles["chapter_prelude_bullet"], bulletText="•")])
    card_rows.append([Paragraph(f"Chapter Focus: {inline_markup(display_title)}", styles["chapter_prelude_focus"])])

    card = Table(card_rows, colWidths=[width], hAlign="LEFT")
    card.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("BOX", (0, 0), (-1, -1), 1.0, colors.HexColor("#0f172a")),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.append(Spacer(1, 18 * mm))
    story.append(card)
    story.append(PageBreak())


def build_body_story(
    lines: list[str],
    styles: dict[str, ParagraphStyle],
    width: float,
    keyword_page_map: dict[str, list[int]] | None = None,
    keyword_terms: list[str] | None = None,
    chapter_preludes: dict[str, dict[str, object]] | None = None,
) -> list[object]:
    lines = merge_callout_continuations(lines)
    story: list[object] = []
    paragraph: list[str] = []
    code: list[str] = []
    code_lang = ""
    table: list[str] = []
    in_code = False
    # Skip manuscript title preamble; start rendering from the first front-matter section.
    in_body = False
    first_heading = True
    in_after_learning = False
    current_chapter_title = ""
    learned_points = 0
    has_custom_reflection = False
    has_custom_try_next = False
    in_intro_section = False
    intro_char_count = 0
    chapter_objectives: list[str] = []
    in_learning_objectives = False
    figure_counter = 0
    pending_figure_number: int | None = None

    def flush_paragraph() -> None:
        nonlocal intro_char_count
        if paragraph:
            joined = " ".join(paragraph).strip()
            story.append(Paragraph(inline_markup(joined), styles["body"]))
            if in_intro_section:
                intro_char_count += len(joined)
            paragraph.clear()

    def flush_code() -> None:
        nonlocal code_lang
        if code:
            story.append(Paragraph(f"Snippet Type: {code_language_label(code_lang)}", styles["code_label"]))
            story.append(Preformatted(wrap_code_lines(code), styles["code"]))
            code.clear()
            code_lang = ""

    def flush_table() -> None:
        if table:
            append_table(story, table, styles, width)
            table.clear()

    def append_recap_extensions() -> None:
        nonlocal in_after_learning, learned_points, has_custom_reflection, has_custom_try_next
        if not in_after_learning or learned_points == 0:
            in_after_learning = False
            learned_points = 0
            has_custom_reflection = False
            has_custom_try_next = False
            return

        chapter_ref = current_chapter_title or "this chapter"
        if not has_custom_reflection:
            story.append(Paragraph("Action 2: Reflect", styles["section"]))
            story.append(
                Paragraph(
                    inline_markup(f"What changed in {chapter_ref}, and which exact output lines prove your claim?"),
                    styles["bullet"],
                    bulletText="•",
                )
            )
            story.append(
                Paragraph(
                    inline_markup("What part was most difficult, and what evidence helped you understand it?"),
                    styles["bullet"],
                    bulletText="•",
                )
            )
            story.append(
                Paragraph(
                    inline_markup("How would you explain this chapter to someone with no coding background?"),
                    styles["bullet"],
                    bulletText="•",
                )
            )
        if not has_custom_try_next:
            story.append(Paragraph("Action 3: Do This Next", styles["section"]))
            story.append(
                Paragraph(
                    inline_markup("Re-run one command with a small controlled setting change and compare outcomes."),
                    styles["bullet"],
                    bulletText="•",
                )
            )
            story.append(
                Paragraph(
                    inline_markup("Try one additional prompt and check whether your conclusion still holds."),
                    styles["bullet"],
                    bulletText="•",
                )
            )
        story.append(Spacer(1, 4))
        in_after_learning = False
        learned_points = 0
        has_custom_reflection = False
        has_custom_try_next = False

    def append_intro_bridge_if_needed() -> None:
        # Markdown is now treated as publishable source-of-truth.
        # Keep renderer output faithful and avoid hidden prose injection.
        return

    def append_keyword_index() -> None:
        entries = keyword_page_map or {}
        ordered_terms = sorted(set(keyword_terms or entries.keys()), key=lambda item: item.lower())
        if not entries:
            story.append(
                Paragraph(
                    inline_markup("Keyword pages will appear after the first render pass."),
                    styles["note_box"],
                )
            )
            return
        story.append(
            Paragraph(
                inline_markup("Use this index to jump quickly to where each term is taught."),
                styles["note_box"],
            )
        )
        story.append(
            Paragraph(
                inline_markup(
                    "Format: primary pages show the best starting points; full references show complete page ranges."
                ),
                styles["imprint"],
            )
        )
        for term in ordered_terms:
            pages = entries.get(term, [])
            if pages:
                primary_page = KEYWORD_PRIMARY_PAGE_OVERRIDES.get(term, pages[0])
                primary = str(primary_page)
                full_start = KEYWORD_FULL_RANGE_START_OVERRIDES.get(term, pages[0])
                full_end = pages[-1]
                full = str(full_start) if full_start == full_end else f"{full_start}-{full_end}"
                page_list = f"Primary: {primary} | Full: {full}"
            else:
                page_list = "not found"
            story.append(Paragraph(inline_markup(f"{term}: {page_list}"), styles["index_entry"], bulletText="•"))

    for line in lines:
        stripped = line.strip()

        if not in_body:
            if (
                stripped.startswith("# Preface")
                or stripped.startswith("# How to Use This Book")
                or stripped.startswith("# Chapter ")
            ):
                in_body = True
            else:
                continue

        if not stripped:
            flush_paragraph()
            story.append(Spacer(1, 5))
            continue

        callout_match = re.match(
            r"^(Lightbulb Takeaway|Definition|Note|Snippet Purpose|Snippet Change):\s*(.*)$",
            stripped,
            flags=re.IGNORECASE,
        )
        if callout_match:
            flush_paragraph()
            flush_table()
            label = callout_match.group(1).strip()
            message = callout_match.group(2).strip()
            style_map = {
                "lightbulb takeaway": "takeaway_box",
                "definition": "definition_box",
                "note": "note_box",
                "snippet purpose": "snippet_box",
                "snippet change": "note_box",
            }
            style_key = style_map[label.lower()]
            icon_html = callout_icon_markup(label)
            message_html = inline_markup(message) if message else ""
            label_html = escape(label)
            text = f"{icon_html}  <b>{label_html}:</b> {message_html}" if message else f"{icon_html}  <b>{label_html}</b>"
            story.append(KeepTogether([Paragraph(text, styles[style_key])]))
            continue

        image_info = parse_markdown_image(stripped)
        if image_info:
            flush_paragraph()
            flush_table()
            alt_text, rel_path = image_info
            figure_counter += 1
            pending_figure_number = figure_counter
            image_path = (ROOT / rel_path).resolve() if not Path(rel_path).is_absolute() else Path(rel_path)
            if image_path.exists():
                with PILImage.open(image_path) as img_meta:
                    src_w, src_h = img_meta.size
                target_w = width * 0.86
                ratio = src_h / max(1, src_w)
                target_h = target_w * ratio
                max_h = 92 * mm
                if target_h > max_h:
                    scale = max_h / target_h
                    target_h = max_h
                    target_w *= scale
                fig = Image(str(image_path), width=target_w, height=target_h, hAlign="CENTER")
                story.append(fig)
                alt_label = alt_text
                if pending_figure_number is not None:
                    alt_label = re.sub(
                        r"^Figure\s+\d+",
                        f"Figure {pending_figure_number}",
                        alt_label,
                        flags=re.IGNORECASE,
                    )
                story.append(Paragraph(inline_markup(f"Alt text: {alt_label}"), styles["figure_alt"]))
            else:
                story.append(Paragraph(inline_markup(f"Note: missing figure file: {rel_path}"), styles["note_box"]))
            continue

        if stripped.lower().startswith("caption:"):
            flush_paragraph()
            caption_text = stripped.split(":", 1)[1].strip()
            if pending_figure_number is not None:
                if re.match(r"^Figure\s+\d+\.", caption_text, flags=re.IGNORECASE):
                    caption_text = re.sub(
                        r"^Figure\s+\d+\.",
                        f"Figure {pending_figure_number}.",
                        caption_text,
                        flags=re.IGNORECASE,
                    )
                else:
                    caption_text = f"Figure {pending_figure_number}. {caption_text}"
            pending_figure_number = None
            story.append(Paragraph(inline_markup(caption_text), styles["figure_caption"]))
            continue

        if stripped.startswith("```"):
            flush_paragraph()
            flush_table()
            if in_code:
                flush_code()
                in_code = False
            else:
                in_code = True
                code_lang = stripped[3:].strip().lower()
            continue

        if stripped == "[[AUTO_KEYWORD_INDEX]]":
            flush_paragraph()
            flush_table()
            append_keyword_index()
            continue

        if in_code:
            code.append(line)
            continue

        if "|" in stripped and stripped.startswith("|"):
            flush_paragraph()
            table.append(stripped)
            continue
        flush_table()

        if stripped.startswith("# "):
            flush_paragraph()
            append_intro_bridge_if_needed()
            append_recap_extensions()
            heading_text = stripped[2:]
            if not first_heading:
                story.append(PageBreakIfNotEmpty())
            if heading_text.startswith("Chapter ") and chapter_preludes is not None:
                append_chapter_prelude_page(story, styles, heading_text, chapter_preludes, width)
            first_heading = False
            current_chapter_title = chapter_toc_title(heading_text)
            chapter_accent = chapter_accent_for_heading(heading_text)
            has_custom_reflection = False
            has_custom_try_next = False
            in_intro_section = False
            intro_char_count = 0
            chapter_objectives = []
            in_learning_objectives = False
            para = Paragraph(inline_markup(heading_text), styles["chapter"])
            para._toc_level = 0  # type: ignore[attr-defined]
            para._toc_text = chapter_toc_title(heading_text)  # type: ignore[attr-defined]
            para._running_chapter = chapter_toc_title(heading_text)  # type: ignore[attr-defined]
            chapter_no_match = re.match(r"^Chapter\s+(\d+):", heading_text, flags=re.IGNORECASE)
            if chapter_no_match:
                para._chapter_number = chapter_no_match.group(1)  # type: ignore[attr-defined]
            else:
                para._chapter_number = ""  # type: ignore[attr-defined]
            para._chapter_accent = chapter_accent  # type: ignore[attr-defined]
            story.append(para)
            append_chapter_band(story, width, chapter_accent)
            continue
        if stripped.startswith("## "):
            flush_paragraph()
            append_intro_bridge_if_needed()
            section_text = stripped[3:]
            section_lower = section_text.lower()
            in_intro_section = section_lower.startswith("about this chapter")
            if not in_intro_section:
                intro_char_count = 0
            in_learning_objectives = section_lower.startswith("what you will learn in this chapter")
            if in_after_learning and section_lower.startswith("action 2: reflect"):
                has_custom_reflection = True
                in_after_learning = False
            elif in_after_learning and section_lower.startswith("action 3: do this next"):
                has_custom_try_next = True
                in_after_learning = False
            else:
                append_recap_extensions()
            if section_text.lower().startswith("action 1: what you learned"):
                in_after_learning = True
                learned_points = 0
                has_custom_reflection = False
                has_custom_try_next = False
            para = Paragraph(inline_markup(section_text), styles["section"])
            if section_text.lower().startswith(
                ("lightbulb takeaway:", "definition:", "note:", "snippet purpose:", "snippet change:")
            ):
                story.append(para)
                continue
            para._running_section = section_text  # type: ignore[attr-defined]
            story.append(para)
            continue
        if stripped.startswith("### "):
            flush_paragraph()
            append_intro_bridge_if_needed()
            story.append(Paragraph(inline_markup(stripped[4:]), styles["subsection"]))
            continue
        if stripped.startswith("- "):
            flush_paragraph()
            if in_learning_objectives:
                chapter_objectives.append(stripped[2:].strip())
            if in_after_learning:
                learned_points += 1
                story.append(Paragraph(inline_markup(stripped[2:]), styles["learned_detail"], bulletText="•"))
            else:
                story.append(Paragraph(inline_markup(stripped[2:]), styles["bullet"], bulletText="•"))
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

        paragraph.append(stripped)

    flush_paragraph()
    append_intro_bridge_if_needed()
    append_recap_extensions()
    flush_code()
    flush_table()
    return story


def draw_body_page_background(canvas, doc) -> None:  # type: ignore[no-untyped-def]
    canvas.saveState()
    page_w, page_h = doc.pagesize
    canvas.setFillColor(colors.HexColor("#e7ebf1"))
    canvas.rect(0, 0, page_w, page_h, stroke=0, fill=1)
    canvas.setFillColor(colors.HexColor("#ffffff"))
    canvas.rect(doc.leftMargin - 6 * mm, doc.bottomMargin - 4 * mm, doc.width + 12 * mm, doc.height + 8 * mm, stroke=0, fill=1)
    accent_hex = getattr(doc, "current_chapter_accent", BRAND_ACCENTS[0])
    canvas.setFillColor(tint(accent_hex, 0.84))
    canvas.rect(doc.leftMargin - 6 * mm, doc.bottomMargin - 4 * mm, 1.6 * mm, doc.height + 8 * mm, stroke=0, fill=1)
    canvas.setFillColor(tint(accent_hex, 0.92))
    canvas.circle(page_w - doc.rightMargin + 1.5 * mm, page_h - doc.topMargin + 2 * mm, 4.2 * mm, stroke=0, fill=1)
    canvas.restoreState()


def draw_body_page_overlay(canvas, doc) -> None:  # type: ignore[no-untyped-def]
    canvas.saveState()
    page_w, page_h = doc.pagesize
    accent_hex = getattr(doc, "current_chapter_accent", BRAND_ACCENTS[0])
    accent = colors.HexColor(accent_hex)
    canvas.setStrokeColor(tint(accent_hex, 0.72))
    canvas.setLineWidth(0.5)
    canvas.line(doc.leftMargin, page_h - 15 * mm, page_w - doc.rightMargin, page_h - 15 * mm)
    chapter = getattr(doc, "current_running_chapter", "Main")
    chapter_number = str(getattr(doc, "current_chapter_number", ""))

    canvas.setFillColor(colors.HexColor("#0f172a"))
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(doc.leftMargin, page_h - 11.3 * mm, f"{BOOK_TITLE} | {chapter}")
    if chapter_number:
        canvas.setFillColor(tint(accent_hex, 0.78))
        canvas.setFont("Helvetica-Bold", 34)
        canvas.drawRightString(page_w - doc.rightMargin + 4.2 * mm, page_h - 10.2 * mm, chapter_number)

    # Footer with progress line and page index.
    progress_left = doc.leftMargin
    progress_width = page_w - doc.leftMargin - doc.rightMargin
    progress_bottom = 8.8 * mm
    canvas.setFillColor(colors.HexColor("#cbd5e1"))
    canvas.rect(progress_left, progress_bottom, progress_width, 1.2 * mm, stroke=0, fill=1)
    if PAGE_TOTAL_HINT > 0:
        ratio = min(1.0, max(0.0, canvas.getPageNumber() / PAGE_TOTAL_HINT))
        canvas.setFillColor(accent)
        canvas.rect(progress_left, progress_bottom, progress_width * ratio, 1.2 * mm, stroke=0, fill=1)
    canvas.setFillColor(colors.HexColor("#334155"))
    canvas.setFont("Helvetica", 10)
    canvas.drawCentredString(page_w / 2, 6.2 * mm, f"Page {canvas.getPageNumber()}")
    canvas.restoreState()


def draw_front_matter_page(canvas, doc) -> None:  # type: ignore[no-untyped-def]
    canvas.saveState()
    page_w, _ = doc.pagesize
    canvas.setFillColor(colors.HexColor("#475569"))
    canvas.setFont("Helvetica", 10)
    canvas.drawCentredString(page_w / 2, 9 * mm, f"{canvas.getPageNumber()}")
    canvas.restoreState()


def append_about_author_front_page(
    story: list[object],
    styles: dict[str, ParagraphStyle],
    about_author_paragraphs: list[str],
) -> None:
    story.append(Paragraph("About the Author", styles["toc_title"]))
    story.append(Spacer(1, 10 * mm))
    paragraphs = about_author_paragraphs or [
        "Lightbulb Takeaway: The teaching intent is simple: clear steps, honest evidence, and confidence through practice.",
        "Paul McMurray is the founder of Tech I Can, based in North Shields. He focuses on practical AI literacy for schools using clear, beginner-friendly steps that help learners run, observe, compare, and explain model behaviour with confidence.",
    ]
    for paragraph in paragraphs:
        if paragraph.lower().startswith("lightbulb takeaway:"):
            takeaway = paragraph.split(":", 1)[1].strip()
            story.append(Paragraph(inline_markup(f"Teaching intent: {takeaway}"), styles["body"]))
            story.append(Spacer(1, 4 * mm))
            continue
        story.append(Paragraph(inline_markup(paragraph), styles["body"]))
        story.append(Spacer(1, 2.2 * mm))
    story.append(PageBreak())


def append_disclaimer_front_page(
    story: list[object],
    styles: dict[str, ParagraphStyle],
    disclaimer_paragraphs: list[str],
) -> None:
    story.append(Paragraph("Disclaimer", styles["toc_title"]))
    story.append(Spacer(1, 8 * mm))
    paragraphs = disclaimer_paragraphs or [
        "This book is an educational guide for classroom and self-study use. It is not legal, safeguarding, or professional policy advice.",
        "Glytch is a workshop-safe simulation model. Outputs can be incomplete, biased, or unexpected. Always review outputs critically and use teacher supervision for classroom activity.",
        "Before delivery, confirm your school or organisation IT rules, data policy, and age-appropriate usage standards. Do not use personal or sensitive student data in prompts, datasets, or saved logs.",
        "All examples are provided as learning demonstrations. You remain responsible for local compliance and safe use.",
    ]
    for paragraph in paragraphs:
        story.append(Paragraph(inline_markup(paragraph), styles["body"]))
        story.append(Spacer(1, 2.2 * mm))
    story.append(PageBreak())


def append_icon_legend_page(story: list[object], styles: dict[str, ParagraphStyle], width: float) -> None:
    story.append(Paragraph("Icons Used in This Book", styles["toc_title"]))
    story.append(
        Paragraph(
            "You will see these symbols throughout the chapters. They signal what kind of guidance is being offered.",
            styles["body"],
        )
    )
    icon_rows: list[list[object]] = []
    legend_items = [
        (ICON_LIGHTBULB, "Lightbulb Takeaway", "A practical classroom takeaway you should remember."),
        (ICON_DEFINITION, "Definition", "A clear meaning for a technical term used in the chapter."),
        (ICON_NOTE, "Note", "Useful context, guardrails, or teaching detail for this step."),
        (ICON_SNIPPET_PURPOSE, "Snippet Purpose", "Why this command is being run before you use it."),
        (ICON_SNIPPET_CHANGE, "Snippet Change", "What changed from a previous command and why it matters."),
    ]
    for icon_path, label, meaning in legend_items:
        icon_cell: object
        if icon_path.exists():
            icon_cell = Image(str(icon_path), width=8.3 * mm, height=8.3 * mm, hAlign="LEFT")
        else:
            icon_cell = Paragraph("•", styles["section"])
        icon_rows.append(
            [
                icon_cell,
                Paragraph(label, styles["icon_legend_label"]),
                Paragraph(meaning, styles["icon_legend_body"]),
            ]
        )
    legend = Table(icon_rows, colWidths=[12 * mm, 48 * mm, width - (60 * mm)], hAlign="LEFT")
    legend.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("LINEBELOW", (0, 0), (-1, -1), 0.2, colors.HexColor("#cbd5e1")),
            ]
        )
    )
    story.append(legend)
    story.append(PageBreak())


def render_book(out_pdf: Path) -> None:
    global PAGE_TOTAL_HINT
    ensure_cover_image(COVER_IMAGE)
    ensure_support_figure_images()
    ensure_callout_icons()
    lines = clean_lines(BOOK_MD.read_text(encoding="utf-8"))
    validate_book_structure(lines)
    keyword_terms = extract_keyword_terms(lines)
    fonts = register_display_fonts()
    styles = build_styles(fonts)
    chapter_preludes = extract_chapter_preludes(lines)
    about_author_paragraphs = extract_front_matter_paragraphs(lines, "About the Author")
    disclaimer_paragraphs = extract_front_matter_paragraphs(lines, "Disclaimer")
    page_w, page_h = A4

    def make_doc() -> BookDocTemplate:
        doc = BookDocTemplate(
            str(out_pdf),
            pagesize=A4,
            leftMargin=23 * mm,
            rightMargin=23 * mm,
            topMargin=22 * mm,
            bottomMargin=20 * mm,
            title=f"{BOOK_TITLE} | Glytch",
            author=BOOK_AUTHOR,
            subject="Beginner guide to Glytch",
            keywords=BOOK_KEYWORDS,
            creator=f"{BOOK_PUBLISHER} Production Pipeline",
        )
        cover_frame = Frame(
            0,
            0,
            page_w,
            page_h,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
            id="cover",
        )
        front_frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="front")
        body_frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="body")
        doc.addPageTemplates(
            [
                PageTemplate(id="cover", frames=[cover_frame]),
                PageTemplate(id="front", frames=[front_frame], onPage=draw_front_matter_page),
                PageTemplate(
                    id="body",
                    frames=[body_frame],
                    onPage=draw_body_page_background,
                    onPageEnd=draw_body_page_overlay,
                ),
            ]
        )
        doc.current_running_chapter = "Preface"
        doc.current_running_section = ""
        doc.current_chapter_accent = BRAND_ACCENTS[0]
        doc.current_chapter_number = ""
        return doc

    body_width = make_doc().width

    def build_story(keyword_map: dict[str, list[int]] | None = None) -> list[object]:
        story: list[object] = []
        story.append(Image(str(COVER_IMAGE), width=page_w, height=page_h))
        story.append(NextPageTemplate("front"))
        story.append(PageBreak())

        story.append(Spacer(1, 18 * mm))
        story.append(Paragraph(BOOK_TITLE, styles["book_title"]))
        story.append(Paragraph("Glytch", styles["book_title"]))
        story.append(Paragraph(BOOK_TAGLINE, styles["book_tag"]))
        story.append(Paragraph(BOOK_SUBTITLE, styles["book_subtitle"]))
        story.append(Spacer(1, 12 * mm))
        story.append(Paragraph(BOOK_AUTHOR, styles["book_meta"]))
        story.append(Paragraph(BOOK_EDITION, styles["book_meta"]))
        story.append(PageBreak())

        story.append(Spacer(1, 90 * mm))
        story.append(
            Paragraph(
                "Dedicated to all of the budding techies of the future.<br/>"
                "The world is ready for your brilliance.",
                styles["dedication"],
            )
        )
        story.append(PageBreak())

        story.append(Paragraph("Copyright", styles["toc_title"]))
        story.append(
            Paragraph(
                "Copyright © 2026 Paul McMurray. "
                "This project is distributed under the MIT License. "
                "Permission is granted to use, copy, modify, merge, publish, distribute, sublicense, and sell copies, "
                "subject to inclusion of the copyright and license notice.",
                styles["copyright"],
            )
        )
        story.append(
            Paragraph(
                "Published by Tech I Can, for practical AI literacy in schools and workshops. "
                "See the repository LICENSE file for full terms and warranty disclaimer.",
                styles["copyright"],
            )
        )
        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph("Publication Data", styles["section"]))
        story.append(Paragraph(f"Publisher: {BOOK_PUBLISHER}", styles["imprint"]))
        story.append(Paragraph(f"Publication date: {BOOK_PUBLICATION_DATE}", styles["imprint"]))
        story.append(Paragraph(BOOK_ISBN, styles["imprint"]))
        story.append(Paragraph(f"Edition: {BOOK_EDITION}", styles["imprint"]))
        story.append(Paragraph("Trim size: A4 digital classroom edition", styles["imprint"]))
        story.append(Spacer(1, 10 * mm))
        story.append(Paragraph(BOOK_TITLE, styles["book_subtitle"]))
        story.append(Paragraph("Curious today, Confident tomorrow.", styles["book_subtitle"]))
        story.append(Spacer(1, 18 * mm))
        story.append(Paragraph("Printed in digital format for classroom distribution.", styles["copyright"]))
        story.append(
            Paragraph(
                "For classroom and school use, the Disclaimer on the following page applies alongside the licence terms above.",
                styles["copyright"],
            )
        )
        story.append(PageBreak())

        append_disclaimer_front_page(story, styles, disclaimer_paragraphs)
        append_about_author_front_page(story, styles, about_author_paragraphs)
        append_icon_legend_page(story, styles, body_width)

        story.append(Paragraph("Contents", styles["toc_title"]))
        toc = TableOfContents()
        toc.levelStyles = [styles["toc_level_0"], styles["toc_level_1"]]
        toc.dotsMinLevel = 0
        story.append(toc)
        story.append(NextPageTemplate("body"))
        story.append(PageBreak())

        story.extend(
                build_body_story(
                    lines,
                    styles,
                    body_width,
                    keyword_page_map=keyword_map,
                    keyword_terms=keyword_terms,
                    chapter_preludes=chapter_preludes,
                )
            )
        return story

    # Pass 1: render manuscript and gather keyword page map.
    make_doc().multiBuild(build_story(), canvasmaker=DeterministicCanvas)
    PAGE_TOTAL_HINT = len(PdfReader(str(out_pdf)).pages)
    keyword_page_map = build_keyword_page_map(out_pdf, keyword_terms)

    # Pass 2: render final book with populated keyword index.
    make_doc().multiBuild(build_story(keyword_map=keyword_page_map), canvasmaker=DeterministicCanvas)
    PAGE_TOTAL_HINT = len(PdfReader(str(out_pdf)).pages)
    apply_accessibility_catalog_tags(out_pdf)
    optimise_pdf_with_ghostscript(out_pdf)
    if out_pdf.stat().st_size > TARGET_PDF_SIZE_BYTES:
        raise SystemExit(
            f"Book PDF is {out_pdf.stat().st_size} bytes, above target {TARGET_PDF_SIZE_BYTES} bytes. "
            "Install Ghostscript (`gs`) for stronger optimisation."
        )


def main() -> int:
    PRINTABLE.mkdir(parents=True, exist_ok=True)
    render_book(BOOK_PDF)
    print(f"Generated {BOOK_PDF.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
