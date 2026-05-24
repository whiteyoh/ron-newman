from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


def _load_pdf_module():
    module_path = Path("tools/pdf/generate_printables.py")
    spec = importlib.util.spec_from_file_location("glytch_pdf_tools", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load PDF module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_pdf_render_is_deterministic_for_same_input(tmp_path: Path) -> None:
    try:
        module = _load_pdf_module()
    except SystemExit:
        pytest.skip("reportlab not installed")

    md_path = tmp_path / "guide.md"
    md_path.write_text(
        "\n".join(
            [
                "# Workshop Guide",
                "",
                "## Checklist",
                "- First item",
                "- Second item",
                "",
                "```bash",
                "python app.py",
                "```",
            ]
        ),
        encoding="utf-8",
    )

    first_pdf = tmp_path / "first.pdf"
    second_pdf = tmp_path / "second.pdf"
    page_size = module.page_size_from_arg("A4")

    module.render(md_path, first_pdf, page_size)
    module.render(md_path, second_pdf, page_size)

    assert first_pdf.read_bytes() == second_pdf.read_bytes()
