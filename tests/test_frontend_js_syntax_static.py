import re
import shutil
import subprocess
from pathlib import Path


def test_frontend_js_files_parse():
    node = shutil.which("node")
    assert node, "node is required for JS syntax checks"

    for path in sorted(Path("web/js").glob("*.js")):
        subprocess.run(
            [node, "--check", str(path)],
            check=True,
            capture_output=True,
            text=True,
        )


def test_frontend_js_files_do_not_contain_broken_literal_newline_join_pattern():
    broken_join_with_literal_newline = re.compile(r"\.join\('\s*" + "\n" + r"\s*'\)")

    for path in sorted(Path("web/js").glob("*.js")):
        text = path.read_text(encoding="utf-8")
        assert broken_join_with_literal_newline.search(text) is None


def test_main_js_context_flow_regressions():
    text = Path("web/js/main.js").read_text(encoding="utf-8")
    assert "mergeOptionalContext" in text
    assert "User refinement:" in text
    assert "use_case_context: state.selectedUseCaseContext" in text
    assert "Small business launch" in text
    assert "new product or service" in text
    assert "do not assume a specific industry" in text
    assert "sustainable coffee brand" not in text
    assert "coffee brand" not in text


def test_render_static_surprise_me_clears_optional_context():
    text = Path("web/js/render-static.js").read_text(encoding="utf-8")
    assert "refs.contextInput" in text
    assert "refs.contextInput.value = ''" in text or 'refs.contextInput.value = ""' in text


def test_index_html_review_copy_and_panel_order_regressions():
    text = Path("web/index.html").read_text(encoding="utf-8")
    assert "visible checks and review checkpoints" in text
    assert "visible checks and approval gates" not in text
    assert "Human review checkpoints" in text

    assert text.index("final-output-panel") < text.index("score-panel")


def test_main_menu_button_bindings_exist():
    text = Path("web/js/main.js").read_text(encoding="utf-8")
    assert "on(el('start-btn'), 'click'" in text
    assert "on(refs.confirmBtn, 'click'" in text
    assert "on(refs.setupModeExampleBtn, 'click'" in text
    assert "on(refs.setupModeCustomBtn, 'click'" in text
    assert "on(refs.setupModeSurpriseBtn, 'click'" in text


def test_ui_ux_lift_static_regressions():
    html = Path("web/index.html").read_text(encoding="utf-8")
    assert "See AI evolve from simple prompts into controlled workflows." in html
    assert "Not sure? Start with Level 1" in html
    assert "Candidate output" in html
    assert "final-output-panel" in html
    assert 'id="copy-output"' in html

    dom = Path("web/js/dom.js").read_text(encoding="utf-8")
    assert "copyOutputBtn" in dom
    assert "copyOutputBtn: el('copy-output')" in dom

    main = Path("web/js/main.js").read_text(encoding="utf-8")
    assert "navigator.clipboard.writeText" in main
    assert "'Copied'" in main
    assert "'Copy output'" in main
    assert "if (refs.copyOutputBtn) refs.copyOutputBtn.disabled = false;" in main
    assert "if (refs.copyOutputBtn) refs.copyOutputBtn.disabled = true;" in main

    run_ui = Path("web/js/run-ui.js").read_text(encoding="utf-8")
    assert "copyOutputBtn" in run_ui
    assert "refs.copyOutputBtn.disabled = true;" in run_ui
    assert "refs.copyOutputBtn.textContent = 'Copy output';" in run_ui

    static_js = Path("web/js/render-static.js").read_text(encoding="utf-8")
    assert "Prompting" in static_js
    assert "Tool use" in static_js
    assert "Workflow control" in static_js
    assert "Orchestration" in static_js
    assert "level-card" in static_js

    score_js = Path("web/js/render-score.js").read_text(encoding="utf-8")
    assert "Workflow control" in score_js
    assert "Maturity match" in score_js
    assert "Closest maturity stage" in score_js
    assert "Why this maps to the maturity model" in score_js
    assert "Closest Yegge stage" not in score_js
    assert "Why this maps to Yegge" not in score_js

    css = Path("web/styles.css").read_text(encoding="utf-8")
    assert ".level-group" in css
    assert ".level-group-grid" in css
    assert ".final-output-panel" in css
    assert "width: min(240px, 100%);" in css
