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
    api_failure_signals: list[str]
    watch_storm_signals: list[str]
    problematic_namespaces: list[tuple[str, int]]
    master_node_risk_signals: list[str]
    unhealthy_operator_signals: list[str]


@dataclass(frozen=True)
class SignalRule:
    pattern: re.Pattern[str]
    label: str


API_FAILURE_RULES = [
    SignalRule(re.compile(r"\b(4\d\d|5\d\d)\b"), "HTTP 4xx/5xx status responses"),
    SignalRule(re.compile(r"\b(api server|apiserver).*(error|failed|timeout|unavailable)", re.IGNORECASE), "API server error/failure"),
    SignalRule(re.compile(r"\b(connection reset|broken pipe|i/o timeout|timed out)\b", re.IGNORECASE), "API connectivity disruption"),
]

WATCH_STORM_RULES = [
    SignalRule(re.compile(r"\btoo many (watches|watch events)\b", re.IGNORECASE), "Too many watch events"),
    SignalRule(re.compile(r"\bwatch(ing)?\b.*\b(restarted|relist|resync)\b", re.IGNORECASE), "Watch restart/relist churn"),
    SignalRule(re.compile(r"\betcd\b.*\b(watch|compaction)\b", re.IGNORECASE), "etcd watch/compaction pressure"),
]

MASTER_NODE_RISK_RULES = [
    SignalRule(re.compile(r"\betcd\b.*\b(quorum|leader changed|unhealthy|timeout|defrag)\b", re.IGNORECASE), "etcd stability risk"),
    SignalRule(re.compile(r"\b(kube-apiserver|kube-scheduler|kube-controller-manager)\b.*\b(crashloop|panic|fatal|unavailable|failed)\b", re.IGNORECASE), "Control-plane component instability"),
    SignalRule(re.compile(r"\b(node not ready|master.*notready|kubelet.*not ready|out of memory|oomkilled)\b", re.IGNORECASE), "Master/node readiness or resource pressure"),
]

UNHEALTHY_OPERATOR_RULES = [
    SignalRule(re.compile(r"\bclusteroperator\b.*\b(degraded|unavailable|not available|failing)\b", re.IGNORECASE), "ClusterOperator degraded/unavailable"),
    SignalRule(re.compile(r"\boperator\b.*\b(degraded|failing|unhealthy|not progressing)\b", re.IGNORECASE), "Operator health issue"),
    SignalRule(re.compile(r"\b(status=.*degraded|condition=.*degraded)\b", re.IGNORECASE), "Operator reports degraded condition"),
]


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
    api_failure_signals: list[str] = []
    watch_storm_signals: list[str] = []
    master_node_risk_signals: list[str] = []
    unhealthy_operator_signals: list[str] = []
    problematic_namespace_counts: Counter[str] = Counter()

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

        lower_line = line.lower()
        namespace_name = namespace_match.group(1) if namespace_match else None

        if _line_matches_rules(line, API_FAILURE_RULES):
            _record_signal(api_failure_signals, line, top_n)
            if namespace_name:
                problematic_namespace_counts[namespace_name] += 1

        if _line_matches_rules(line, WATCH_STORM_RULES):
            _record_signal(watch_storm_signals, line, top_n)
            if namespace_name:
                problematic_namespace_counts[namespace_name] += 1

        if _line_matches_rules(line, MASTER_NODE_RISK_RULES):
            _record_signal(master_node_risk_signals, line, top_n)
            if namespace_name:
                problematic_namespace_counts[namespace_name] += 1

        if _line_matches_rules(line, UNHEALTHY_OPERATOR_RULES):
            _record_signal(unhealthy_operator_signals, line, top_n)
            if namespace_name:
                problematic_namespace_counts[namespace_name] += 1

        if namespace_name and any(token in lower_line for token in ("error", "failed", "timeout", "degraded", "unavailable")):
            problematic_namespace_counts[namespace_name] += 1

    return LogSummary(
        file_path=path,
        total_lines=len(lines),
        levels=dict(sorted(level_counts.items())),
        top_pods=pod_counts.most_common(top_n),
        top_namespaces=namespace_counts.most_common(top_n),
        notable_errors=notable_errors,
        api_failure_signals=api_failure_signals,
        watch_storm_signals=watch_storm_signals,
        problematic_namespaces=problematic_namespace_counts.most_common(top_n),
        master_node_risk_signals=master_node_risk_signals,
        unhealthy_operator_signals=unhealthy_operator_signals,
    )


def _line_matches_rules(line: str, rules: list[SignalRule]) -> bool:
    return any(rule.pattern.search(line) for rule in rules)


def _record_signal(bucket: list[str], line: str, top_n: int) -> None:
    if len(bucket) < top_n:
        bucket.append(line.strip())
