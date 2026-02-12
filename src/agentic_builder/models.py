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

    def append_feedback(self, feedback: str) -> None:
        timestamp = datetime.now(tz=timezone.utc).isoformat()
        self.feedback_log.append(f"[{timestamp}] {feedback}")

    def append_improvement(self, suggestion: str) -> None:
        timestamp = datetime.now(tz=timezone.utc).isoformat()
        self.history.append(f"[{timestamp}] {suggestion}")
