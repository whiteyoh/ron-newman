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
