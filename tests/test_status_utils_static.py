from pathlib import Path


def test_status_utils_module_and_import_regressions() -> None:
    status_utils = Path("web/js/status-utils.js")
    assert status_utils.exists()
    status_utils_text = status_utils.read_text(encoding="utf-8")
    assert "export function normalizeStatus" in status_utils_text
    assert "export function humanizeStatus" in status_utils_text

    theatre_text = Path("web/js/render-theatre.js").read_text(encoding="utf-8")
    assert "from './status-utils.js'" in theatre_text

    taskboard_text = Path("web/js/render-taskboard.js").read_text(encoding="utf-8")
    assert "from './status-utils.js'" in taskboard_text
    assert "from './render-theatre.js'" not in taskboard_text
