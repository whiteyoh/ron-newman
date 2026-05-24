from pathlib import Path
import re


DOC_FILES = [
    "README.md",
    "STEP_BY_STEP.md",
    "docs/first_lesson_walkthrough.md",
    "docs/teacher_guide.md",
    "docs/student_worksheet.md",
    "docs/architecture.md",
    "docs/how_llms_work.md",
]

NAV_LABELS = [
    "Home",
    "First Lesson Walkthrough",
    "Teacher Guide",
    "Student Worksheet",
    "Architecture",
    "How AI Workflows Work",
]

REQUIRED_SECTIONS = {
    "README.md": [
        "# Glytch",
        "## Why Glytch?",
        "## Core principle",
        "## Documentation map",
        "## Book",
    ],
    "STEP_BY_STEP.md": [
        "# Glytch Step-by-Step Guide",
        "## 2. Start the workshop-safe demo",
        "## 6. Run Level 8 (orchestration)",
        "## 9. Use the classroom pack and printables",
    ],
    "docs/first_lesson_walkthrough.md": [
        "# First Lesson Walkthrough",
        "## Session setup",
        "## What success looks like",
        "## Step 4 - Run Level 8",
        "## Exit ticket",
    ],
    "docs/teacher_guide.md": [
        "# Teacher Guide",
        "## Quick-reference classroom flow",
        "## Suggested classroom pacing",
        "## Facilitation tips",
        "## Common misconceptions and Q&A guidance",
        "## Printable materials",
    ],
    "docs/student_worksheet.md": [
        "# Student Worksheet",
        "## Activity 1 - Level 1 baseline",
        "## Activity 3 - Level 4 or Level 6",
        "## Activity 4 - Level 8 orchestration",
        "## Final reflection",
    ],
    "docs/architecture.md": [
        "# Architecture",
        "## System diagram",
        "## Request flow",
        "## Level progression model",
        "## Human review gate",
    ],
    "docs/how_llms_work.md": [
        "# How AI Workflows Work (Simple)",
        "## The key idea",
        "## What changes when structure is added",
        "## Lowest safe level principle",
        "## FAQ",
    ],
}


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_required_sections_exist_in_docs() -> None:
    for path, sections in REQUIRED_SECTIONS.items():
        content = _read(path)
        for section in sections:
            assert section in content, f"Missing section '{section}' in {path}"


def test_assets_and_docs_exist_and_are_referenced() -> None:
    required_paths = [
        "docs/assets/glytch-logo.svg",
        "docs/assets/simple-architecture-flowchart.svg",
        "docs/assets/level-comparison-map.svg",
        "docs/assets/human-review-gate.svg",
        "docs/first_lesson_walkthrough.md",
        "docs/teacher_guide.md",
        "docs/student_worksheet.md",
        "docs/architecture.md",
        "docs/how_llms_work.md",
        "docs/tech_i_can_glytch_book.md",
        "docs/printable/teacher_guide.pdf",
        "docs/printable/student_worksheet.pdf",
        "docs/printable/first_lesson_walkthrough.pdf",
        "docs/printable/Glytch_Teacher_Guide.pdf",
        "docs/printable/Glytch_Student_Worksheet.pdf",
        "docs/printable/Glytch_First_Lesson_Walkthrough.pdf",
        "docs/printable/Tech_I_Can_Glytch_Book.pdf",
    ]
    for path in required_paths:
        assert Path(path).exists(), f"Missing required path: {path}"

    readme = _read("README.md")
    for asset in [
        "docs/assets/simple-architecture-flowchart.svg",
        "docs/assets/level-comparison-map.svg",
        "docs/assets/human-review-gate.svg",
        "docs/printable/Tech_I_Can_Glytch_Book.pdf",
    ]:
        assert asset in readme, f"README missing reference: {asset}"


def test_top_and_footer_navigation_present() -> None:
    for path in DOC_FILES:
        if path in {"README.md", "STEP_BY_STEP.md"}:
            continue
        content = _read(path)
        for label in NAV_LABELS:
            assert label in content, f"Missing nav label '{label}' in {path}"

        assert content.count('<p align="center">') >= 2, (
            f"Expected top and footer navigation blocks in {path}"
        )


def test_markdown_links_and_image_src_are_valid() -> None:
    markdown_link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    image_src_pattern = re.compile(r'<img[^>]+src="([^"]+)"')

    for path in DOC_FILES + ["docs/tech_i_can_glytch_book.md"]:
        content = _read(path)
        base_dir = Path(path).parent

        for target in markdown_link_pattern.findall(content):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            link_path = target.split("#", maxsplit=1)[0]
            if not link_path:
                continue
            resolved = (base_dir / link_path).resolve()
            assert resolved.exists(), f"Broken markdown link in {path}: {target}"

        for img_src in image_src_pattern.findall(content):
            resolved = (base_dir / img_src).resolve()
            assert resolved.exists(), f"Broken image source in {path}: {img_src}"


def test_printable_pdfs_are_committed_and_readable() -> None:
    pdfs = [
        "docs/printable/teacher_guide.pdf",
        "docs/printable/student_worksheet.pdf",
        "docs/printable/first_lesson_walkthrough.pdf",
        "docs/printable/Glytch_Teacher_Guide.pdf",
        "docs/printable/Glytch_Student_Worksheet.pdf",
        "docs/printable/Glytch_First_Lesson_Walkthrough.pdf",
        "docs/printable/Tech_I_Can_Glytch_Book.pdf",
    ]

    for path in pdfs:
        data = Path(path).read_bytes()
        assert data.startswith(b"%PDF-"), f"Printable is not a PDF: {path}"
        assert len(data) > 1_000, f"Printable looks unexpectedly small: {path}"


def test_printable_pdf_aliases_match_primary_files() -> None:
    aliases = {
        "docs/printable/teacher_guide.pdf": "docs/printable/Glytch_Teacher_Guide.pdf",
        "docs/printable/student_worksheet.pdf": "docs/printable/Glytch_Student_Worksheet.pdf",
        "docs/printable/first_lesson_walkthrough.pdf": (
            "docs/printable/Glytch_First_Lesson_Walkthrough.pdf"
        ),
    }

    for primary, alias in aliases.items():
        assert Path(primary).read_bytes() == Path(alias).read_bytes(), (
            f"Printable alias differs from primary file: {alias}"
        )
