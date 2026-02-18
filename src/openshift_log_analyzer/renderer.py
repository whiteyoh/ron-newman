from __future__ import annotations

from .analyzer import LogSummary


def render_human_readable_report(summary: LogSummary) -> str:
    def format_ranked(items: list[tuple[str, int]], label: str) -> str:
        if not items:
            return f"- No {label} found in this file."
        return "\n".join(f"- {name}: {count} entries" for name, count in items)

    def format_signals(signals: list[str], label: str) -> str:
        if not signals:
            return f"- No {label} detected."
        return "\n".join(f"- {entry}" for entry in signals)

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
            "",
            "## API Failures & Failure Patterns",
            format_signals(summary.api_failure_signals, "API failures or repeating failure patterns"),
            "",
            "## Watch Storm / Watch Collapse Signals",
            format_signals(summary.watch_storm_signals, "watch storm/collapse indicators"),
            "",
            "## Problematic Namespaces",
            format_ranked(summary.problematic_namespaces, "problematic namespaces"),
            "",
            "## Master Node Risk Indicators",
            format_signals(summary.master_node_risk_signals, "master-node risk indicators"),
            "",
            "## Unhealthy Operator Signals",
            format_signals(summary.unhealthy_operator_signals, "unhealthy operator indicators"),
        ]
    )
