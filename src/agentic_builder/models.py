from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class FileInsight:
    path: str
    extension: str
    size_bytes: int


@dataclass(frozen=True)
class FolderInsight:
    root: Path
    file_count: int
    extensions: dict[str, int]
    files: list[FileInsight]


@dataclass(frozen=True)
class ToolBlueprint:
    title: str
    summary: str
    capabilities: list[str]
    architecture: list[str]
    tests: list[str]


@dataclass(frozen=True)
class PullRequestDraft:
    title: str
    body: str


@dataclass
class EvolutionState:
    history: list[str] = field(default_factory=list)
    feedback_log: list[str] = field(default_factory=list)
    backlog: dict[str, str] = field(default_factory=dict)

    def append_feedback(self, feedback: str) -> None:
        timestamp = datetime.now(tz=timezone.utc).isoformat()
        self.feedback_log.append(f"[{timestamp}] {feedback}")

    def append_improvement(self, suggestion: str) -> None:
        timestamp = datetime.now(tz=timezone.utc).isoformat()
        self.history.append(f"[{timestamp}] {suggestion}")

    def upsert_backlog_item(self, key: str, value: str) -> tuple[str, str]:
        if key in self.backlog:
            existing_value = self.backlog[key]
            ticket_id = existing_value.split(" ", maxsplit=1)[0]
            return "existing", ticket_id

        ticket_id = f"TKT-{len(self.backlog) + 1:03d}"
        self.backlog[key] = f"{ticket_id} {value}"
        return "new", ticket_id
