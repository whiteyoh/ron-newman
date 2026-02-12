from __future__ import annotations

from pathlib import Path

from .evolver import EvolutionEngine
from .models import EvolutionState
from .planner import ToolPlanner
from .pr_manager import PRManager
from .scanner import FolderScanner


class AgenticBuilder:
    def __init__(self) -> None:
        self.scanner = FolderScanner()
        self.planner = ToolPlanner()
        self.pr_manager = PRManager()
        self.evolver = EvolutionEngine()

    def run(self, target_folder: str) -> dict[str, str]:
        insight = self.scanner.scan(Path(target_folder))
        blueprint = self.planner.build_blueprint(insight)
        pr_draft = self.pr_manager.create_draft(blueprint)

        return {
            "title": blueprint.title,
            "summary": blueprint.summary,
            "pr_title": pr_draft.title,
            "pr_body": pr_draft.body,
        }

    def evolve(self, feedback: str, state: EvolutionState) -> str:
        return self.evolver.record_feedback(state, feedback)
