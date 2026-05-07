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
