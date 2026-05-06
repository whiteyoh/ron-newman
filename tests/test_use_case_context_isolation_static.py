from pathlib import Path


def test_render_static_clears_guided_context_and_custom_state_on_preset_select():
    text = Path("web/js/render-static.js").read_text(encoding="utf-8")
    assert (
        "const GUIDED_CONTEXT = 'Year 10 revision lesson on nutrition and healthy eating';" in text
    )
    assert "clearPresetSelectionState();" in text
    assert (
        "if (state.selectedUseCaseContext === GUIDED_CONTEXT) state.selectedUseCaseContext = '';"
        in text
    )
    assert (
        "if (refs.contextInput?.value.trim() === GUIDED_CONTEXT) refs.contextInput.value = '';"
        in text
    )
    assert "state.selectedCustomScenario = null;" in text
    assert "state.customUseCaseGoal = '';" in text
    assert "state.customUseCaseAudience = '';" in text
    assert "state.customUseCaseConstraints = '';" in text
    assert "state.selectedUseCaseContext = GUIDED_CONTEXT;" not in text


def test_start_demo_clears_selected_context():
    text = Path("web/js/main.js").read_text(encoding="utf-8")
    assert "on(el('start-btn'), 'click', () => {" in text
    assert "state.selectedUseCaseContext = '';" in text


def test_guided_context_lives_only_in_onboarding_and_not_in_index_value():
    onboarding = Path("web/js/onboarding.js").read_text(encoding="utf-8")
    html = Path("web/index.html").read_text(encoding="utf-8")
    assert "Year 10 revision lesson on nutrition and healthy eating" in onboarding
    assert "Year 10 revision lesson on nutrition and healthy eating" not in html
    assert 'id="context-input"' in html
    assert ">Year 10 revision lesson on nutrition and healthy eating</textarea>" not in html


def test_confirm_handler_merges_optional_context_for_surprise_and_custom_without_duplication():
    text = Path("web/js/main.js").read_text(encoding="utf-8")
    assert "function mergeOptionalContext(baseContext, optionalContext) {" in text
    assert "User refinement:" in text
    assert "if (state.setupMode === 'example') {" in text
    assert "state.selectedUseCaseContext = optionalContext;" in text
    assert "if (state.setupMode === 'surprise') {" in text
    assert "const baseContext = state.selectedCustomScenario" in text
    assert (
        "state.selectedUseCaseContext = mergeOptionalContext(baseContext, optionalContext);" in text
    )
    assert "if (state.setupMode === 'custom') {" in text
    assert (
        "state.selectedUseCaseContext = mergeOptionalContext("
        "buildCustomContext(), optionalContext);" in text
    )
