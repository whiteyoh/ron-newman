from __future__ import annotations

from .analyzer import LogSummary


def render_human_readable_report(summary: LogSummary) -> str:
    def format_ranked(items: list[tuple[str, int]], label: str) -> str:
        if not items:
            return f"- No {label} found in this file."
        return "\n".join(f"- {name}: {count} entries" for name, count in items)

    levels = "\n".join(f"- {level}: {count}" for level, count in summary.levels.items())
    if not levels:
        levels = "- No standard log levels detected."

    notable = "\n".join(f"- {entry}" for entry in summary.notable_errors)
    if not notable:
        notable = "- No explicit error/failure lines detected."

    return "\n".join(
        [
            "# OpenShift Log Analysis Report",
            "",
            f"Analyzed file: `{summary.file_path}`",
            f"Total lines processed: **{summary.total_lines}**",
            "",
            "## Log Level Breakdown",
            levels,
            "",
            "## Most Frequent Pods",
            format_ranked(summary.top_pods, "pods"),
            "",
            "## Most Frequent Namespaces",
            format_ranked(summary.top_namespaces, "namespaces"),
            "",
            "## Notable Error/Failure Lines",
            notable,
        ]
    )
