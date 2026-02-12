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
        self._agent_descriptions = {
            "scanner": "Scans folders, counts files, and profiles file extensions.",
            "planner": "Builds the implementation blueprint from folder insights.",
            "pr_manager": "Drafts a PR title/body with scope, backlog, and validation.",
            "evolver": "Turns feedback into prioritized backlog suggestions.",
        }

    def _get_or_create_agent(
        self,
        name: str,
        factory: Callable[[], object],
        chat_log: list[str],
    ) -> object:
        if name not in self._agents:
            self._agents[name] = factory()
            chat_log.append(
                f"🛠️ `{name}` agent not found. Auto-creating it now (no user confirmation required)."
            )
        else:
            chat_log.append(f"♻️ Reusing existing `{name}` agent.")
        return self._agents[name]

    def describe_agent_registry(self) -> list[dict[str, str | bool]]:
        return [
            {
                "name": agent_name,
                "active": agent_name in self._agents,
                "description": description,
            }
            for agent_name, description in self._agent_descriptions.items()
        ]

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

    def _describe_inspection_scope(self, insight: FolderInsight) -> str:
        top_level_counts: dict[str, int] = {}
        for file in insight.files:
            top_level = file.path.split("/", maxsplit=1)[0]
            top_level_counts[top_level] = top_level_counts.get(top_level, 0) + 1

        top_sections = sorted(top_level_counts.items(), key=lambda item: (-item[1], item[0]))[:5]
        section_text = ", ".join(f"`{name}` ({count})" for name, count in top_sections) or "none"

        largest_files = sorted(insight.files, key=lambda file: file.size_bytes, reverse=True)[:3]
        largest_text = (
            ", ".join(f"`{file.path}` ({file.size_bytes} bytes)" for file in largest_files)
            if largest_files
            else "none"
        )

        return (
            "I inspected the following areas first: "
            f"{section_text}. Largest files reviewed for context: {largest_text}."
        )

    def run_with_updates(self, target_folder: str):
        chat_log: list[str] = [f"📁 Starting analysis for `{target_folder}`."]
        existing_agents = set(self._agents)

        yield "I am checking which agents are available and creating any missing ones."
        scanner = self._get_or_create_agent("scanner", FolderScanner, chat_log)
        planner = self._get_or_create_agent("planner", ToolPlanner, chat_log)
        pr_manager = self._get_or_create_agent("pr_manager", PRManager, chat_log)

        yield "I am scanning your folder now so I can explain exactly what I am looking at."
        insight = scanner.scan(Path(target_folder))
        chat_log.append(
            f"🔎 Scanner analyzed `{insight.root}` and found {insight.file_count} file(s)."
        )
        inspection_note = self._describe_inspection_scope(insight)
        chat_log.append(f"🗂️ Scope: {inspection_note}")

        yield "I finished the scan and I am now deciding the best implementation focus."
        decision = self._decide_focus(insight, chat_log)

        yield "I am drafting the blueprint with capabilities, architecture, and tests."
        blueprint = planner.build_blueprint(insight)
        chat_log.append("🧠 Planner generated a tool blueprint from the folder insight.")

        yield "I am turning the blueprint into a PR-style execution plan."
        pr_draft = pr_manager.create_draft(blueprint)
        chat_log.append("📝 PR manager drafted a pull request plan and validation checklist.")
        created_agents = sorted(set(self._agents) - existing_agents)

        final_result = {
            "title": blueprint.title,
            "summary": blueprint.summary,
            "pr_title": pr_draft.title,
            "pr_body": pr_draft.body,
            "decision": decision,
            "created_agents": ", ".join(created_agents) or "none",
            "chat_log": "\n".join(f"- {line}" for line in chat_log),
            "inspection_note": inspection_note,
        }

        yield "done", final_result

    def run(self, target_folder: str) -> dict[str, str]:
        final_result: dict[str, str] = {}
        for update in self.run_with_updates(target_folder):
            if isinstance(update, tuple) and update[0] == "done":
                final_result = update[1]
        return final_result

    def evolve(self, feedback: str, state: EvolutionState) -> str:
        evolver = self._agents.get("evolver")
        if evolver is None:
            evolver = EvolutionEngine()
            self._agents["evolver"] = evolver
        return evolver.record_feedback(state, feedback)
