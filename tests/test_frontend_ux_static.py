from pathlib import Path


def test_main_js_ux_regressions():
    text = Path("web/js/main.js").read_text(encoding="utf-8")

    assert "Context changed. Confirm this direction again before running." in text
    assert "on(refs.contextInput, 'input'" in text
    assert "state.confirmedUseCase = null" in text
    assert "updateLevelButtonsVisibility()" in text
    assert "scrollIntoView" in text
    assert "dashboard-title" in text
    assert "Workshop-safe simulation mode" in text
    assert "OpenAI API Not Connected" not in text
    assert "Rendered with warning" in text
    assert "Completed with warning" not in text


def test_new_ux_cards_and_confirmed_context_static():
    html = Path("web/index.html").read_text(encoding="utf-8")
    for snippet in [
        "What just happened?",
        "Learning takeaway",
        "Recommended next step",
        "quick-compare-actions",
        "confirmed-context-details",
        "confirmed-context-body",
    ]:
        assert snippet in html

    dom_js = Path("web/js/dom.js").read_text(encoding="utf-8")
    for snippet in [
        "runInsightPanel",
        "runInsightCopy",
        "learningTakeawayPanel",
        "learningTakeawayCopy",
        "nextStepPanel",
        "nextStepCopy",
        "quickCompareActions",
        "confirmedContextDetails",
        "confirmedContextBody",
    ]:
        assert snippet in dom_js

    main_js = Path("web/js/main.js").read_text(encoding="utf-8")
    for snippet in [
        "getRunInsight",
        "getLearningTakeaway",
        "getRecommendedNextStep",
        "getRuntimeWarningLines",
        "renderQuickCompareActions",
        "This is basic prompting",
        "This is orchestration",
        "Next, try Level 3",
        "Compare Level 1",
        "Compare Level 3",
        "Compare Level 8",
        "upstream_timeout",
        "The AI provider took too long to respond",
    ]:
        assert snippet in main_js
    assert "Action: Check OPENAI_MODEL, model access, quota or billing" not in main_js

    for snippet in [
        "state.customUseCaseGoal.length < 8",
        "state.confirmedUseCase = null",
        "state.confirmedUseCaseLabel = null",
        "hideConfirmedContext();",
        "Custom use case changed. Add a clear goal, then confirm direction again.",
        "updateLevelButtonsVisibility();",
        "const previousMode = state.setupMode",
        "const modeChanged = previousMode && previousMode !== mode",
        "if (modeChanged)",
    ]:
        assert snippet in main_js

    run_ui_js = Path("web/js/run-ui.js").read_text(encoding="utf-8")
    for snippet in [
        "runInsightPanel",
        "learningTakeawayPanel",
        "nextStepPanel",
        "quickCompareActions",
    ]:
        assert snippet in run_ui_js

    confirmed_context_js = Path("web/js/confirmed-context.js").read_text(encoding="utf-8")
    for snippet in [
        "export function showConfirmedContext",
        "export function hideConfirmedContext",
        "import { refs }",
        "import { state }",
    ]:
        assert snippet in confirmed_context_js

    render_static_js = Path("web/js/render-static.js").read_text(encoding="utf-8")
    assert "import { hideConfirmedContext } from './confirmed-context.js';" in render_static_js
    assert render_static_js.count("hideConfirmedContext();") >= 2

    css = Path("web/styles.css").read_text(encoding="utf-8")
    for snippet in [
        ".run-insight-panel",
        ".learning-takeaway-panel",
        ".next-step-panel",
        ".quick-compare-actions",
        ".confirmed-context-details",
    ]:
        assert snippet in css


def test_render_theatre_humanizes_visible_status():
    text = Path("web/js/render-theatre.js").read_text(encoding="utf-8")

    assert "humanizeStatus" in text
    assert "normalizeStatus" in text
    assert "createEl('span', `pill ${status}`, humanizeStatus(status))" in text


def test_render_taskboard_humanizes_user_visible_statuses():
    text = Path("web/js/render-taskboard.js").read_text(encoding="utf-8")

    assert "humanizeStatus" in text
    assert "createEl('h4', '', humanizeStatus(status))" in text
    expected = (
        "appendKV(wc, 'Status', `${humanizeStatus(w.status)} · Worker: "
        "${humanizeStatus(w.worker_status)}`);"
    )
    assert expected in text


def test_onboarding_handles_unexpected_level_choices_in_guide():
    text = Path("web/js/onboarding.js").read_text(encoding="utf-8")

    assert "You ran Level" in text
    assert "continue exploring freely" in text
    assert "if (refs.guideLevel3Btn) refs.guideLevel3Btn.classList.add('hidden');" in text
    assert "if (refs.guideFinishBtn) refs.guideFinishBtn.classList.remove('hidden');" in text


def test_ui_polish_regressions_static():
    css = Path("web/styles.css").read_text(encoding="utf-8")
    assert ".level-recommendation" in css
    assert "flex-basis: 100%" in css
    assert ".level-group-grid" in css
    assert "grid-template-columns: 1fr" in css
    assert ".level-group-grid { grid-template-columns: repeat(2" not in css
    assert "#buttons" in css
    assert "repeat(auto-fit, minmax(240px, 1fr))" in css
    assert ".level-group-description" in css
    assert ".final-output-panel h3" in css
    assert ".final-output-body" in css
    assert "font-size: 1.03rem" in css
    assert "font-size: clamp(2.7rem, 8vw, 5.8rem)" in css
    for snippet in [
        "h1,",
        "h2,",
        "h3 {",
        "letter-spacing: -0.06em",
        "letter-spacing: -0.035em",
        "letter-spacing: -0.02em",
    ]:
        assert snippet in css
    assert ".hero::after" in css
    assert "button:hover:not(:disabled)" in css
    assert "transform: translateY(-1px)" in css
    assert ".ghost:hover:not(:disabled)" in css
    assert ".final-output-panel" in css

    static_js = Path("web/js/render-static.js").read_text(encoding="utf-8")
    assert "Ask and answer." in static_js
    assert "Use bounded tools." in static_js
    assert "Add checks and structure." in static_js
    assert "Coordinate multiple workers." in static_js
    assert "Prompting" in static_js
    assert "Tool use" in static_js
    assert "Workflow control" in static_js
    assert "Orchestration" in static_js
    assert "level-card" in static_js

    score_js = Path("web/js/render-score.js").read_text(encoding="utf-8")
    assert "Capability = what the AI is being asked to do" in score_js
    assert (
        "Workflow control = how much structure, checking, and process surrounds the AI" in score_js
    )
    assert "Maturity match = how clearly this run demonstrates the intended level" in score_js
    assert "workflow control/autonomy surrounds it" not in score_js


def test_first_run_advanced_details_static():
    html = Path("web/index.html").read_text(encoding="utf-8")
    for snippet in [
        "advanced-results-details",
        "advanced-results-body",
        "Show workflow detail",
        "Behind the scenes",
        "Score, steps, taskboard and raw trace",
    ]:
        assert snippet in html

    dom_js = Path("web/js/dom.js").read_text(encoding="utf-8")
    assert "advancedResultsDetails" in dom_js

    run_ui_js = Path("web/js/run-ui.js").read_text(encoding="utf-8")
    for snippet in [
        "advancedResultsDetails",
        "classList.add('hidden')",
        "open = false",
    ]:
        assert snippet in run_ui_js

    main_js = Path("web/js/main.js").read_text(encoding="utf-8")
    for snippet in [
        "advancedResultsDetails",
        "classList.remove('hidden')",
        "open = false",
    ]:
        assert snippet in main_js

    css = Path("web/styles.css").read_text(encoding="utf-8")
    for snippet in [
        ".advanced-results-details",
        ".advanced-results-body",
        ".advanced-results-details > summary",
        ".advanced-results-details[open] > summary::after",
    ]:
        assert snippet in css
