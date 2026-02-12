from __future__ import annotations

from pathlib import Path
from typing import Callable

from .evolver import EvolutionEngine
from .models import EvolutionState, FolderInsight
from .planner import ToolPlanner
from .pr_manager import PRManager
from .scanner import FolderScanner


class AgenticBuilder:
    def __init__(self) -> None:
        self._agents: dict[str, object] = {}

    def _get_or_create_agent(
        self,
        name: str,
        factory: Callable[[], object],
        chat_log: list[str],
    ) -> object:
        if name not in self._agents:
            self._agents[name] = factory()
            chat_log.append(f"🛠️ `{name}` agent not found. Creating it now.")
        else:
            chat_log.append(f"♻️ Reusing existing `{name}` agent.")
        return self._agents[name]

    def _decide_focus(self, insight: FolderInsight, chat_log: list[str]) -> str:
        extensions = insight.extensions
        if not extensions:
            decision = "No files found, so start with project scaffolding and discovery questions."
            chat_log.append(f"🧭 Decision: {decision}")
            return decision

        dominant_extension, dominant_count = max(extensions.items(), key=lambda item: item[1])
        language_focus = {
            ".py": "prioritize Python packaging, linting, and tests",
            ".ts": "prioritize TypeScript build pipelines and API contracts",
            ".js": "prioritize JavaScript runtime checks and module boundaries",
            ".md": "prioritize documentation quality and contributor workflows",
            "<no_ext>": "prioritize repository hygiene and baseline automation",
        }
        guidance = language_focus.get(
            dominant_extension,
            "prioritize modular architecture and incremental delivery",
        )
        decision = (
            f"Detected `{dominant_extension}` as the dominant file type "
            f"({dominant_count} file(s)); {guidance}."
        )
        chat_log.append(f"🧭 Decision: {decision}")
        return decision

    def run(self, target_folder: str) -> dict[str, str]:
        chat_log: list[str] = [f"📁 Starting analysis for `{target_folder}`."]
        scanner = self._get_or_create_agent("scanner", FolderScanner, chat_log)
        planner = self._get_or_create_agent("planner", ToolPlanner, chat_log)
        pr_manager = self._get_or_create_agent("pr_manager", PRManager, chat_log)

        insight = scanner.scan(Path(target_folder))
        chat_log.append(
            f"🔎 Scanner analyzed `{insight.root}` and found {insight.file_count} file(s)."
        )
        decision = self._decide_focus(insight, chat_log)

        blueprint = planner.build_blueprint(insight)
        chat_log.append("🧠 Planner generated a tool blueprint from the folder insight.")
        pr_draft = pr_manager.create_draft(blueprint)
        chat_log.append("📝 PR manager drafted a pull request plan and validation checklist.")

        return {
            "title": blueprint.title,
            "summary": blueprint.summary,
            "pr_title": pr_draft.title,
            "pr_body": pr_draft.body,
            "decision": decision,
            "chat_log": "\n".join(f"- {line}" for line in chat_log),
        }

    def evolve(self, feedback: str, state: EvolutionState) -> str:
        evolver = self._agents.get("evolver")
        if evolver is None:
            evolver = EvolutionEngine()
            self._agents["evolver"] = evolver
        return evolver.record_feedback(state, feedback)
