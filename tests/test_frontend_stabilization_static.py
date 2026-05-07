import re
from pathlib import Path


def test_main_js_runtime_warning_order_and_start_reset_and_catch_guards():
    text = Path("web/js/main.js").read_text(encoding="utf-8")

    assert "runtime_error" in text
    clear_idx = text.index("setText(refs.log, '');")
    intro_idx = text.index(
        "appendMessage('trace', "
        "'Read-only simulation trace. Nothing here requires you to answer.');"
    )
    warning_idx = text.index("if (data?.runtime_error) {")
    assert intro_idx > clear_idx
    assert warning_idx > intro_idx

    start_handler = re.search(
        r"on\(el\('start-btn'\), 'click', \(\) => \{(?P<body>.*?)\}\);",
        text,
        re.DOTALL,
    )
    assert start_handler is not None
    body = start_handler.group("body")
    assert "onboarding.openApp();" in body
    assert "state.selectedUseCaseContext = '';" in body
    assert "if (refs.contextInput) refs.contextInput.value = '';" in body

    assert "if (refs.buttons) {" in text
    assert "if (refs.maturityCards && !refs.maturityCards.children.length)" in text
    assert "if (refs.beforeAfter && !refs.beforeAfter.children.length)" in text

    assert "].join('\\n')" in text
    assert "].join('\n'));" not in text


def test_onboarding_js_open_app_and_start_guide_null_safety():
    text = Path("web/js/onboarding.js").read_text(encoding="utf-8")

    assert "const entry = el('entry');" in text
    assert "const app = el('app');" in text
    assert "if (entry) entry.classList.add('hidden');" in text
    assert "if (app) app.classList.remove('hidden');" in text

    assert "state.selectedUseCaseContext = GUIDED_CONTEXT;" in text
    assert "if (refs.contextInput) refs.contextInput.value = GUIDED_CONTEXT;" in text
    assert "if (refs.confirmBtn) refs.confirmBtn.disabled = false;" in text
    assert "const options = refs.useCaseOptions ? [" in text
    assert "refs.useCaseOptions.querySelectorAll('.option')" in text
    assert "if (refs.selectionLabel) refs.selectionLabel.textContent =" in text


def test_context_input_has_no_default_value_or_guided_placeholder():
    html = Path("web/index.html").read_text(encoding="utf-8")

    match = re.search(
        (
            r'<textarea id="context-input"[^>]*placeholder="(?P<placeholder>[^"]*)"[^>]*>'
            r"\s*</textarea>"
        ),
        html,
    )
    assert match is not None
    assert "Year 10 revision lesson on nutrition and healthy eating" not in match.group(
        "placeholder"
    )
    assert "Example: audience, constraints, or workshop focus" in match.group("placeholder")


def test_main_js_final_answer_priority_and_trace_intro_once():
    text = Path("web/js/main.js").read_text(encoding="utf-8")

    assert "data?.final_answer || data?.approval_summary?.final_answer" in text

    run_idx = text.index("const data = await runLevelRequest")
    trace_intro = (
        "appendMessage('trace', "
        "'Read-only simulation trace. Nothing here requires you to answer.');"
    )
    first_intro_idx = text.find(trace_intro)
    assert first_intro_idx > run_idx

    clear_after_idx = text.index("setText(refs.log, '');", run_idx)
    intro_after_idx = text.index(trace_intro, clear_after_idx)
    assert intro_after_idx > clear_after_idx

    assert "if (refs.finalOutputPanel && isUsefulFinalAnswer) {" in text
    assert "else if (refs.finalOutputPanel) refs.finalOutputPanel.classList.add('hidden');" in text


def test_raw_trace_details_has_no_static_intro_and_keeps_log_container():
    html = Path("web/index.html").read_text(encoding="utf-8")

    assert '<details id="raw-trace-details" class="raw-trace-details">' in html
    assert '<div id="log"' in html

    details_section = re.search(
        r'<details id="raw-trace-details" class="raw-trace-details">(?P<body>.*?)</details>',
        html,
        re.DOTALL,
    )
    assert details_section is not None
    assert (
        "Read-only simulation trace. Nothing here requires you to answer."
        not in details_section.group("body")
    )


def test_main_js_has_single_post_response_trace_intro_and_no_pre_request_intro():
    text = Path("web/js/main.js").read_text(encoding="utf-8")

    trace_intro = (
        "appendMessage('trace', "
        "'Read-only simulation trace. Nothing here requires you to answer.');"
    )

    assert text.count(trace_intro) == 1

    run_idx = text.index("const data = await runLevelRequest")
    intro_idx = text.index(trace_intro)
    assert intro_idx > run_idx
