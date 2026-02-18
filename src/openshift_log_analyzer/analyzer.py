from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import re


LEVEL_PATTERN = re.compile(r"\b(INFO|WARN|WARNING|ERROR|FATAL|DEBUG)\b", re.IGNORECASE)
POD_PATTERN = re.compile(r"pod[=/]([a-z0-9][a-z0-9-]*)", re.IGNORECASE)
NAMESPACE_PATTERN = re.compile(r"namespace[=/]([a-z0-9][a-z0-9-]*)", re.IGNORECASE)
NODE_PATTERN = re.compile(r"(?:node|host|machine)[=/]([a-z0-9][a-z0-9.-]*)", re.IGNORECASE)


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
    problematic_nodes: list[tuple[str, int]]
    infrastructure_hotspots: list[tuple[str, int]]


@dataclass(frozen=True)
class SignalRule:
    pattern: re.Pattern[str]


API_FAILURE_RULES = [
    SignalRule(re.compile(r"\b(4\d\d|5\d\d)\b")),
    SignalRule(re.compile(r"\b(api server|apiserver).*(error|failed|timeout|unavailable)", re.IGNORECASE)),
    SignalRule(re.compile(r"\b(connection reset|broken pipe|i/o timeout|timed out|tls handshake timeout)\b", re.IGNORECASE)),
]

WATCH_STORM_RULES = [
    SignalRule(re.compile(r"\btoo many (watches|watch events)\b", re.IGNORECASE)),
    SignalRule(re.compile(r"\bwatch(ing)?\b.*\b(restarted|relist|resync|bookmark)\b", re.IGNORECASE)),
    SignalRule(re.compile(r"\betcd\b.*\b(watch|compaction|mvcc)\b", re.IGNORECASE)),
]

MASTER_NODE_RISK_RULES = [
    SignalRule(re.compile(r"\betcd\b.*\b(quorum|leader changed|unhealthy|timeout|defrag|election)\b", re.IGNORECASE)),
    SignalRule(re.compile(r"\b(kube-apiserver|kube-scheduler|kube-controller-manager)\b.*\b(crashloop|panic|fatal|unavailable|failed)\b", re.IGNORECASE)),
    SignalRule(re.compile(r"\b(node not ready|master.*notready|kubelet.*not ready|out of memory|oomkilled|disk pressure)\b", re.IGNORECASE)),
]

UNHEALTHY_OPERATOR_RULES = [
    SignalRule(re.compile(r"\bclusteroperator\b.*\b(degraded|unavailable|not available|failing)\b", re.IGNORECASE)),
    SignalRule(re.compile(r"\boperator\b.*\b(degraded|failing|unhealthy|not progressing)\b", re.IGNORECASE)),
    SignalRule(re.compile(r"\b(status=.*degraded|condition=.*degraded)\b", re.IGNORECASE)),
]

INFRASTRUCTURE_COMPONENT_RULES: dict[str, re.Pattern[str]] = {
    "kube-apiserver": re.compile(r"\bkube-apiserver\b", re.IGNORECASE),
    "etcd": re.compile(r"\betcd\b", re.IGNORECASE),
    "kube-controller-manager": re.compile(r"\bkube-controller-manager\b", re.IGNORECASE),
    "kube-scheduler": re.compile(r"\bkube-scheduler\b", re.IGNORECASE),
}


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
    problematic_namespace_counts: Counter[str] = Counter()
    problematic_node_counts: Counter[str] = Counter()
    infrastructure_hotspot_counts: Counter[str] = Counter()

    notable_errors: list[str] = []
    api_failure_signals: list[str] = []
    watch_storm_signals: list[str] = []
    master_node_risk_signals: list[str] = []
    unhealthy_operator_signals: list[str] = []

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for line in lines:
        lower_line = line.lower()

        level_match = LEVEL_PATTERN.search(line)
        if level_match:
            level_counts[_normalize_level(level_match.group(1))] += 1

        pod_match = POD_PATTERN.search(line)
        if pod_match:
            pod_counts[pod_match.group(1)] += 1

        namespace_match = NAMESPACE_PATTERN.search(line)
        namespace_name = namespace_match.group(1) if namespace_match else None
        if namespace_name:
            namespace_counts[namespace_name] += 1

        node_match = NODE_PATTERN.search(line)
        node_name = node_match.group(1) if node_match else None

        if "error" in lower_line or "failed" in lower_line:
            _record_signal(notable_errors, line, top_n)

        api_hit = _line_matches_rules(line, API_FAILURE_RULES)
        watch_hit = _line_matches_rules(line, WATCH_STORM_RULES)
        master_hit = _line_matches_rules(line, MASTER_NODE_RISK_RULES)
        operator_hit = _line_matches_rules(line, UNHEALTHY_OPERATOR_RULES)
        generic_issue_hit = any(token in lower_line for token in ("error", "failed", "timeout", "degraded", "unavailable"))

        if api_hit:
            _record_signal(api_failure_signals, line, top_n)

        if watch_hit:
            _record_signal(watch_storm_signals, line, top_n)

        if master_hit:
            _record_signal(master_node_risk_signals, line, top_n)

        if operator_hit:
            _record_signal(unhealthy_operator_signals, line, top_n)

        if namespace_name and (api_hit or watch_hit or master_hit or operator_hit or generic_issue_hit):
            problematic_namespace_counts[namespace_name] += 1

        if node_name and (master_hit or watch_hit or generic_issue_hit):
            problematic_node_counts[node_name] += 1

        for component, pattern in INFRASTRUCTURE_COMPONENT_RULES.items():
            if pattern.search(line) and (api_hit or watch_hit or master_hit or generic_issue_hit):
                infrastructure_hotspot_counts[component] += 1

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
        problematic_nodes=problematic_node_counts.most_common(top_n),
        infrastructure_hotspots=infrastructure_hotspot_counts.most_common(top_n),
    )


def _line_matches_rules(line: str, rules: list[SignalRule]) -> bool:
    return any(rule.pattern.search(line) for rule in rules)


def _record_signal(bucket: list[str], line: str, top_n: int) -> None:
    if len(bucket) < top_n:
        bucket.append(line.strip())
