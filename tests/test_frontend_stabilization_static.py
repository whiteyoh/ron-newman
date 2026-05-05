import re
from pathlib import Path


def test_main_js_runtime_warning_order_and_start_reset_and_catch_guards():
    text = Path("web/js/main.js").read_text(encoding="utf-8")

    assert "runtime_error" in text
    clear_idx = text.index("refs.log.textContent = '';")
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
