import shutil
import subprocess
from pathlib import Path


def test_frontend_js_files_parse():
    node = shutil.which("node")
    assert node, "node is required for JS syntax checks"

    for path in Path("web/js").glob("*.js"):
        subprocess.run(
            [node, "--check", str(path)],
            check=True,
            capture_output=True,
            text=True,
        )


def test_main_menu_button_bindings_exist():
    text = Path("web/js/main.js").read_text(encoding="utf-8")
    assert "on(el('start-btn'), 'click'" in text
    assert "on(refs.confirmBtn, 'click'" in text
    assert "on(refs.setupModeExampleBtn, 'click'" in text
    assert "on(refs.setupModeCustomBtn, 'click'" in text
    assert "on(refs.setupModeSurpriseBtn, 'click'" in text
