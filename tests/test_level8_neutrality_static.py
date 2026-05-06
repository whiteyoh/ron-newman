from pathlib import Path


def test_orchestrator_generic_worker_labels_are_neutral():
    text = Path("src/orchestrator.py").read_text(encoding="utf-8")
    assert "teacher_resource_writer" not in text
    assert "Draft classroom-ready resource text." not in text
    assert "content_writer" in text
    assert "Draft user-ready content for the confirmed use case." in text


def test_frontend_strings_for_taskboard_and_labels():
    taskboard = Path("web/js/render-taskboard.js").read_text(encoding="utf-8")
    main = Path("web/js/main.js").read_text(encoding="utf-8")
    state = Path("web/js/state.js").read_text(encoding="utf-8")
    dom = Path("web/js/dom.js").read_text(encoding="utf-8")
    html = Path("web/index.html").read_text(encoding="utf-8")

    assert "No workers in this state." not in taskboard
    assert "Review and merge simulation" in taskboard
    assert "Simulated review outcome" in taskboard
    assert "Simulated merge decision" in taskboard
    assert "Approved for merge" not in taskboard
    assert "Merged after verifier and approval gate" not in taskboard

    assert "confirmedUseCaseLabel" in main
    assert "Backend key:" in main
    assert "selectedUseCaseLabel" in state
    assert "confirmedUseCaseLabel" in state

    assert "final-output-panel" in html
    assert "raw-trace-details" in html
    assert "finalOutputPanel" in dom
    assert "finalOutputBody" in dom


def test_custom_business_context_no_education_leakage():
    text = Path("src/orchestrator.py").read_text(encoding="utf-8").lower()
    assert "classroom-ready" not in text
    assert "teacher resource" not in text
    assert "lesson resource" not in text
