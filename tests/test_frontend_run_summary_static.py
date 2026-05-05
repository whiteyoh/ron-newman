from pathlib import Path


def test_run_summary_markup_and_live_regions():
    html = Path("web/index.html").read_text(encoding="utf-8")
    assert "run-summary-panel" in html
    assert "run-summary-title" in html
    assert "run-summary-status" in html
    assert "run-summary-copy" in html
    assert "run-summary-list" in html
    assert 'aria-labelledby="run-summary-title"' in html
    assert 'aria-live="polite"' in html


def test_run_summary_dom_refs_and_main_runtime_warning_copy():
    dom_js = Path("web/js/dom.js").read_text(encoding="utf-8")
    main_js = Path("web/js/main.js").read_text(encoding="utf-8")
    run_ui_js = Path("web/js/run-ui.js").read_text(encoding="utf-8")

    for key in ["runSummaryPanel", "runSummaryStatus", "runSummaryCopy", "runSummaryList"]:
        assert key in dom_js

    assert "runtime_error" in main_js
    assert "Rendered with warning" in main_js
    assert "Run summary" in Path("web/index.html").read_text(encoding="utf-8")
    assert "No external action was taken." in main_js
    assert "clearRunPanels()" in main_js
    assert "runSummaryPanel" in run_ui_js


def test_theatre_label_softening_and_summary_styles():
    theatre_js = Path("web/js/render-theatre.js").read_text(encoding="utf-8")
    css = Path("web/styles.css").read_text(encoding="utf-8")

    assert "Human approval gate" in theatre_js
    assert "Human review checkpoint" in theatre_js
    assert "Simulated approval" in theatre_js
    assert "Candidate output" in theatre_js
    assert "Merge would be allowed" in theatre_js

    assert ".run-summary-panel" in css
    assert ".run-summary-panel.warning" in css
    assert "overflow-wrap" in css or "word-break" in css
