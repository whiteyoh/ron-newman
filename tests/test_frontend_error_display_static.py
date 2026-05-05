from pathlib import Path


def test_frontend_run_error_display_static() -> None:
    api_js = Path("web/js/api.js").read_text(encoding="utf-8")
    main_js = Path("web/js/main.js").read_text(encoding="utf-8")

    assert "error.code" in api_js
    assert "error.status" in api_js
    assert "error.field" in api_js

    assert "Simulation could not complete" in main_js
    assert "Reason:" in main_js
    assert "HTTP status:" in main_js
    assert "Code:" in main_js
    assert "OPENAI_MODEL" in main_js
    assert "gpt-4.1-mini" in main_js

    assert "Authorization" not in main_js
    assert "api_key" not in main_js
