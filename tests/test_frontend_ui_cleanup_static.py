from pathlib import Path


def test_index_html_copy_and_panel_order_updates():
    html = Path("web/index.html").read_text(encoding="utf-8")

    assert "I need to plan a revision lesson for Year 10 food technology" not in html
    assert (
        "I need to plan a product launch, revision session, workshop, report, or workflow" in html
    )

    assert "Human approval gates" not in html
    assert "Human review checkpoints" in html

    assert "visible checks and approval gates" not in html
    assert "visible checks and review checkpoints" in html

    final_output_idx = html.index('<section id="final-output-panel"')
    score_panel_idx = html.index('<div id="score-panel" class="dashboard-grid"></div>')
    assert final_output_idx < score_panel_idx


def test_styles_taskboard_grid_uses_responsive_autofit_in_desktop_and_override():
    css = Path("web/styles.css").read_text(encoding="utf-8")

    assert "repeat(auto-fit, minmax(220px, 1fr));" in css
    assert "body.force-desktop .taskboard-grid" in css
    assert "repeat(auto-fit, minmax(220px, 1fr)) !important;" in css


def test_surprise_card_selection_clears_optional_context_input():
    text = Path("web/js/render-static.js").read_text(encoding="utf-8")

    assert 'if (refs.contextInput) refs.contextInput.value = "";' in text


def test_main_js_confirmation_copy_and_context_merge_behaviour_are_preserved():
    text = Path("web/js/main.js").read_text(encoding="utf-8")

    assert "Context included:" in text
    assert "mergeOptionalContext" in text
    assert "User refinement:" in text

    assert "Small business launch" in text
    assert "new product or service" in text
    assert "do not assume a specific industry" in text
    assert "sustainable coffee brand" not in text
    assert "coffee brand" not in text
    expected_call = (
        "runLevelRequest({ level, use_case: state.confirmedUseCase, "
        "use_case_context: state.selectedUseCaseContext })"
    )
    assert expected_call in text
