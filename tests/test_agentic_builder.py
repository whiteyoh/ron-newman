from pathlib import Path

from agentic_builder import AgenticBuilder, EvolutionState
from agentic_builder.planner import ToolPlanner
from agentic_builder.pr_manager import PRManager
from agentic_builder.scanner import FolderScanner


def test_folder_scanner_collects_extensions(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text("print('ok')\n", encoding="utf-8")
    (tmp_path / "README").write_text("notes\n", encoding="utf-8")

    insight = FolderScanner().scan(tmp_path)

    assert insight.file_count == 2
    assert insight.extensions[".py"] == 1
    assert insight.extensions["<no_ext>"] == 1


def test_end_to_end_orchestration(tmp_path: Path) -> None:
    (tmp_path / "api.ts").write_text("export const x = 1;\n", encoding="utf-8")

    builder = AgenticBuilder()
    result = builder.run(str(tmp_path))

    assert "Agentic Builder" in result["title"]
    assert "PR Title" not in result["pr_body"]
    assert "## Objective" in result["pr_body"]
    assert "dominant file type" in result["decision"]
    assert "Creating it now" in result["chat_log"]


def test_builder_reuses_agents_on_second_run(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text("print('ok')\n", encoding="utf-8")

    builder = AgenticBuilder()
    first = builder.run(str(tmp_path))
    second = builder.run(str(tmp_path))

    assert "Creating it now" in first["chat_log"]
    assert "Reusing existing `scanner` agent" in second["chat_log"]
    assert "Reusing existing `planner` agent" in second["chat_log"]
    assert "Reusing existing `pr_manager` agent" in second["chat_log"]


def test_pr_manager_sections() -> None:
    state = EvolutionState()
    builder = AgenticBuilder()
    suggestion = builder.evolve("Need explicit security checks", state)

    assert "Need explicit security checks" in suggestion
    assert len(state.history) == 1
    assert len(state.feedback_log) == 1

    pr_body = PRManager().create_draft(
        ToolPlanner().build_blueprint(FolderScanner().scan(Path(".")))
    ).body
    assert "## Scope" in pr_body
    assert "## Prioritized Backlog (Important Features)" in pr_body
    assert "TKT-001" in pr_body
    assert "## Amendment Ticket Slice (Max 2 per PR)" in pr_body
    assert "## Validation" in pr_body


def test_evolution_classifies_priority_and_theme() -> None:
    state = EvolutionState()
    builder = AgenticBuilder()

    suggestion = builder.evolve("Critical security policy checks are missing", state)

    assert "TKT-001" in suggestion
    assert "[P0/security]" in suggestion
    assert "Backlog now contains 1 unique item(s)" in suggestion
    assert len(state.backlog) == 1


def test_evolution_deduplicates_repeated_feedback() -> None:
    state = EvolutionState()
    builder = AgenticBuilder()

    first = builder.evolve("Improve chat UX response formatting", state)
    second = builder.evolve("Improve chat UX response formatting", state)

    assert "Backlog now contains 1 unique item(s)" in first
    assert "already tracked" in second
    assert len(state.backlog) == 1
    assert len(state.history) == 2
    assert len(state.feedback_log) == 2


def test_pr_manager_limits_amendment_slice_to_two_tickets(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text("print('ok')\n", encoding="utf-8")
    blueprint = ToolPlanner().build_blueprint(FolderScanner().scan(tmp_path))
    pr_body = PRManager().create_draft(blueprint).body

    lines = pr_body.splitlines()
    start = lines.index("## Amendment Ticket Slice (Max 2 per PR)") + 1
    end = lines.index("", start)
    slice_lines = [line for line in lines[start:end] if line.startswith("-")]

    assert len(slice_lines) == 2
