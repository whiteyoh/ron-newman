import re
from pathlib import Path


def test_onboarding_static_content():
    html = Path("web/index.html").read_text(encoding="utf-8")
    js = Path("web/js/onboarding.js").read_text(encoding="utf-8")
    dom_js = Path("web/js/dom.js").read_text(encoding="utf-8")

    assert "Try your first Glytch run" in html
    assert "Show guide again" in html
    assert "guide-inline-btn" in html
    assert "Show guide" in html
    assert "Skip guide" in html
    assert "Finish guide" in html
    assert "js/main.js" in html
    assert "footer-disclaimer" in html
    assert (
        "https://justin.abrah.ms/blog/2026-01-08-yegge-s-developer-agent-evolution-model.html"
        in html
    )

    assert "glytch.firstRunGuide.completed" in js
    assert "lowest useful level" in js
    assert "Level 1" in js
    assert "Level 3" in js
    assert "confirm-btn" in js
    assert "guideFinishBtn" in js
    assert "Try Level 3 next" in html
    assert "Finish guide" in html
    assert "Use an example" in html
    assert "Create my own" in html
    assert "Surprise me" in html
    assert "custom-goal-input" in html
    assert "custom-audience-input" in html
    assert "custom-constraints-input" in html
    assert "surprise-use-case-options" in html
    assert "You’ve now compared Level 1 and Level 3" in js
    assert "level3StartedFromGuide" in js
    assert "waitingForLevel3Comparison" in js
    assert "setGuideReplayControlsVisible" in js
    assert "focusGuideCard" in js
    assert "addEventListener" in js
    assert "guideInlineBtn" in js
    assert "setGuideReplayControlsVisible" in js
    assert "readGuideCompleted" in js
    assert "writeGuideCompleted" in js
    assert "try {" in js
    assert "localStorage.setItem(GUIDE_KEY, 'completed')" in js
    match = re.search(
        r"function writeGuideCompleted\(\)\s*\{(?P<body>.*?)\n\}",
        js,
        re.DOTALL,
    )
    assert match is not None
    assert "writeGuideCompleted();" not in match.group("body")
    assert "refs.guideInlineBtn.onclick" not in js

    assert "guideInlineBtn" in dom_js


def test_onboarding_module_referenced():
    main_js = Path("web/js/main.js").read_text(encoding="utf-8")
    assert "addEventListener" in main_js
    assert "setupModeExampleBtn" in main_js
    assert "setupModeCustomBtn" in main_js
    assert "setupModeSurpriseBtn" in main_js
    assert "refs.setupModeExampleBtn.onclick" not in main_js
    assert "refs.setupModeCustomBtn.onclick" not in main_js
    assert "refs.setupModeSurpriseBtn.onclick" not in main_js
    assert "refs.customGoalInput.addEventListener" not in main_js
    assert "from './onboarding.js'" in main_js
    assert "selectedUseCaseContext" in main_js
    assert "custom use case" in main_js.lower()
    assert "uk_year10_teacher" in Path("web/js/state.js").read_text(encoding="utf-8")
