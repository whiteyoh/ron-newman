from pathlib import Path


def test_onboarding_static_content():
    html = Path("web/index.html").read_text(encoding="utf-8")
    js = Path("web/js/onboarding.js").read_text(encoding="utf-8")

    assert "Try your first Glytch run" in html
    assert ("Show guide again" in html) or ("Skip guide" in html)
    assert "js/main.js" in html
    assert "lowest useful level" in js
    assert "Level 1" in js
    assert "Level 3" in js
    assert "footer-disclaimer" in html


def test_onboarding_module_referenced():
    main_js = Path("web/js/main.js").read_text(encoding="utf-8")
    assert "from './onboarding.js'" in main_js
