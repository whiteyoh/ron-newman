from pathlib import Path


def test_onboarding_static_content():
    html = Path("web/index.html").read_text(encoding="utf-8")
    js = Path("web/js/onboarding.js").read_text(encoding="utf-8")

    assert "Try your first Glytch run" in html
    assert "Show guide again" in html
    assert "Skip guide" in html
    assert "Finish guide" in html
    assert "js/main.js" in html
    assert "glytch.firstRunGuide.completed" in js
    assert "lowest useful level" in js
    assert "Level 1" in js
    assert "Level 3" in js
    assert "confirm-btn" in js
    assert "guideFinishBtn" in js
    assert "You’ve now compared Level 1 and Level 3" in js
    assert "footer-disclaimer" in html


def test_onboarding_module_referenced():
    main_js = Path("web/js/main.js").read_text(encoding="utf-8")
    assert "from './onboarding.js'" in main_js
