from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import re


LEVEL_PATTERN = re.compile(r"\b(INFO|WARN|WARNING|ERROR|FATAL|DEBUG)\b", re.IGNORECASE)
POD_PATTERN = re.compile(r"pod[=/]([a-z0-9][a-z0-9-]*)", re.IGNORECASE)
NAMESPACE_PATTERN = re.compile(r"namespace[=/]([a-z0-9][a-z0-9-]*)", re.IGNORECASE)


@dataclass
class LogSummary:
    file_path: Path
    total_lines: int
    levels: dict[str, int]
    top_pods: list[tuple[str, int]]
    top_namespaces: list[tuple[str, int]]
    notable_errors: list[str]


def _normalize_level(level: str) -> str:
    level = level.upper()
    if level == "WARNING":
        return "WARN"
    return level


def analyze_log_file(file_path: str | Path, *, top_n: int = 5) -> LogSummary:
    path = Path(file_path).expanduser().resolve()
    if not path.exists() or not path.is_file():
        raise ValueError(f"Invalid log file path: {path}")

    level_counts: Counter[str] = Counter()
    pod_counts: Counter[str] = Counter()
    namespace_counts: Counter[str] = Counter()
    notable_errors: list[str] = []

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for line in lines:
        level_match = LEVEL_PATTERN.search(line)
        if level_match:
            level_counts[_normalize_level(level_match.group(1))] += 1

        pod_match = POD_PATTERN.search(line)
        if pod_match:
            pod_counts[pod_match.group(1)] += 1

        namespace_match = NAMESPACE_PATTERN.search(line)
        if namespace_match:
            namespace_counts[namespace_match.group(1)] += 1

        if "error" in line.lower() or "failed" in line.lower():
            if len(notable_errors) < top_n:
                notable_errors.append(line.strip())

    return LogSummary(
        file_path=path,
        total_lines=len(lines),
        levels=dict(sorted(level_counts.items())),
        top_pods=pod_counts.most_common(top_n),
        top_namespaces=namespace_counts.most_common(top_n),
        notable_errors=notable_errors,
    )
