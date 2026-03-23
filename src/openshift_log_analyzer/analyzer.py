from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from html import escape
from pathlib import Path
import re
import tarfile
from tempfile import TemporaryDirectory
import gzip
import shutil
from typing import Iterable

DATE_TOKEN_PATTERN = re.compile(r"(20\d{2}[-/]\d{2}[-/]\d{2})")
SEVERITY_PATTERN = re.compile(r"\b(INFO|WARN|WARNING|ERROR|FATAL|CRITICAL)\b", re.IGNORECASE)
NAMESPACE_PATTERN = re.compile(r'\b(?:namespace|ns)[=/:\"]+([a-z0-9][a-z0-9-]*)', re.IGNORECASE)
NODE_PATTERN = re.compile(r'\b(?:node|host|machine)[=/:\"]+([a-z0-9][a-z0-9.-]*)', re.IGNORECASE)
POD_PATTERN = re.compile(r'\bpod[=/:\"]+([a-z0-9][a-z0-9-]*)', re.IGNORECASE)

ROOT_CAUSE_RULES: dict[str, tuple[re.Pattern[str], str]] = {
    "api_availability": (
        re.compile(r"\b(apiserver|api server|oauth|authentication)\b.*\b(timeout|unavailable|503|connection reset|refused)\b", re.IGNORECASE),
        "API availability degradation affecting authentication or cluster control-plane access.",
    ),
    "etcd_health": (
        re.compile(r"\betcd\b.*\b(leader changed|timeout|unhealthy|quorum|election|mvcc|compaction)\b", re.IGNORECASE),
        "etcd instability likely destabilized the control plane and amplified cascading API failures.",
    ),
    "node_resource_pressure": (
        re.compile(r"\b(node not ready|disk pressure|memory pressure|oomkilled|evicted|filesystem full)\b", re.IGNORECASE),
        "Node resource pressure disrupted workloads or supporting daemons.",
    ),
    "operator_degradation": (
        re.compile(r"\b(clusteroperator|operator)\b.*\b(degraded|unavailable|failing|not progressing)\b", re.IGNORECASE),
        "Cluster operators reported degraded or unavailable conditions, indicating platform instability.",
    ),
    "network_instability": (
        re.compile(r"\b(i/o timeout|tls handshake timeout|connection reset|no route to host|context deadline exceeded)\b", re.IGNORECASE),
        "Network instability or transport failures contributed to the incident timeline.",
    ),
}


@dataclass(frozen=True)
class Evidence:
    source: str
    line_number: int
    severity: str
    line: str


@dataclass(frozen=True)
class RootCauseCandidate:
    key: str
    title: str
    hit_count: int
    rationale: str
    evidence: list[Evidence]


@dataclass(frozen=True)
class LogSummary:
    source_path: Path
    incident_date: str
    extracted_dir: Path | None
    total_files_scanned: int
    matched_lines: int
    levels: dict[str, int]
    top_namespaces: list[tuple[str, int]]
    top_nodes: list[tuple[str, int]]
    top_pods: list[tuple[str, int]]
    root_cause_candidates: list[RootCauseCandidate]
    timeline: list[Evidence]
    recommendations: list[str]
    notable_errors: list[str] = field(default_factory=list)
    api_failure_signals: list[str] = field(default_factory=list)
    watch_storm_signals: list[str] = field(default_factory=list)
    problematic_namespaces: list[tuple[str, int]] = field(default_factory=list)
    master_node_risk_signals: list[str] = field(default_factory=list)
    unhealthy_operator_signals: list[str] = field(default_factory=list)
    problematic_nodes: list[tuple[str, int]] = field(default_factory=list)
    infrastructure_hotspots: list[tuple[str, int]] = field(default_factory=list)


def _normalize_incident_date(value: str) -> str:
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    raise ValueError(f"Invalid incident date: {value}. Use YYYY-MM-DD.")


def _normalize_level(level: str) -> str:
    level = level.upper()
    return "WARN" if level == "WARNING" else level


BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".bin", ".xz", ".bz2"}
COMPRESSED_TEXT_SUFFIXES = {".gz"}


def _iter_text_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() not in BINARY_SUFFIXES | COMPRESSED_TEXT_SUFFIXES:
            yield path


def _decompress_gzip_file(source: Path, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    target = destination.with_suffix("") if destination.suffix.lower() == ".gz" else destination
    with gzip.open(source, "rb") as compressed, target.open("wb") as unpacked:
        shutil.copyfileobj(compressed, unpacked)
    return target


def _prepare_input(source: Path) -> tuple[Path, TemporaryDirectory | None, Path | None]:
    if source.is_dir():
        return source, None, None
    if source.is_file() and tarfile.is_tarfile(source):
        temp_dir = TemporaryDirectory(prefix="must-gather-")
        with tarfile.open(source) as archive:
            archive.extractall(temp_dir.name)
        return Path(temp_dir.name), temp_dir, None
    if source.is_file() and source.suffix.lower() == ".gz":
        temp_dir = TemporaryDirectory(prefix="must-gather-")
        unpacked_file = _decompress_gzip_file(source, Path(temp_dir.name) / source.name)
        return Path(temp_dir.name), temp_dir, unpacked_file
    if source.is_file():
        return source.parent, None, source
    raise ValueError(f"Invalid must-gather input: {source}. Provide a directory, single text file, or a .tar, .tgz, or .tar.gz archive.")


def analyze_log_file(file_path: str | Path, *, incident_date: str, top_n: int = 5) -> LogSummary:
    source = Path(file_path).expanduser().resolve()
    if not source.exists():
        raise ValueError(f"Invalid must-gather input: {source}")

    normalized_date = _normalize_incident_date(incident_date)
    root, temp_dir, prepared_file = _prepare_input(source)

    level_counts: Counter[str] = Counter()
    namespace_counts: Counter[str] = Counter()
    node_counts: Counter[str] = Counter()
    pod_counts: Counter[str] = Counter()
    rule_hits: Counter[str] = Counter()
    rule_evidence: dict[str, list[Evidence]] = defaultdict(list)
    timeline: list[Evidence] = []

    files_scanned = 0
    candidate_files = [prepared_file] if prepared_file is not None else list(_iter_text_files(root))
    for text_file in candidate_files:
        files_scanned += 1
        try:
            lines = text_file.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue

        for line_number, line in enumerate(lines, start=1):
            date_match = DATE_TOKEN_PATTERN.search(line)
            if not date_match:
                continue
            if date_match.group(1).replace("/", "-") != normalized_date:
                continue

            severity_match = SEVERITY_PATTERN.search(line)
            severity = _normalize_level(severity_match.group(1)) if severity_match else "INFO"
            evidence = Evidence(
                source=str(text_file.relative_to(root)),
                line_number=line_number,
                severity=severity,
                line=line.strip(),
            )
            timeline.append(evidence)
            level_counts[severity] += 1

            if namespace_match := NAMESPACE_PATTERN.search(line):
                namespace_counts[namespace_match.group(1)] += 1
            if node_match := NODE_PATTERN.search(line):
                node_counts[node_match.group(1)] += 1
            if pod_match := POD_PATTERN.search(line):
                pod_counts[pod_match.group(1)] += 1

            for key, (pattern, _rationale) in ROOT_CAUSE_RULES.items():
                if pattern.search(line):
                    rule_hits[key] += 1
                    if len(rule_evidence[key]) < top_n:
                        rule_evidence[key].append(evidence)

    ranked_causes = [
        RootCauseCandidate(
            key=key,
            title=key.replace("_", " ").title(),
            hit_count=count,
            rationale=ROOT_CAUSE_RULES[key][1],
            evidence=rule_evidence[key],
        )
        for key, count in rule_hits.most_common(top_n)
    ]

    recommendations = _build_recommendations(ranked_causes)

    temp_path = Path(temp_dir.name) if temp_dir else None
    return LogSummary(
        source_path=source,
        incident_date=normalized_date,
        extracted_dir=temp_path,
        total_files_scanned=files_scanned,
        matched_lines=len(timeline),
        levels=dict(sorted(level_counts.items())),
        top_namespaces=namespace_counts.most_common(top_n),
        top_nodes=node_counts.most_common(top_n),
        top_pods=pod_counts.most_common(top_n),
        root_cause_candidates=ranked_causes,
        timeline=timeline[: max(top_n * 3, 10)],
        recommendations=recommendations,
        notable_errors=[e.line for e in timeline if e.severity in {"ERROR", "FATAL", "CRITICAL"}][:top_n],
        api_failure_signals=[e.line for e in rule_evidence.get("api_availability", [])],
        watch_storm_signals=[e.line for e in rule_evidence.get("etcd_health", [])],
        problematic_namespaces=namespace_counts.most_common(top_n),
        master_node_risk_signals=[e.line for e in rule_evidence.get("node_resource_pressure", [])],
        unhealthy_operator_signals=[e.line for e in rule_evidence.get("operator_degradation", [])],
        problematic_nodes=node_counts.most_common(top_n),
        infrastructure_hotspots=[(cause.title, cause.hit_count) for cause in ranked_causes],
    )


def _build_recommendations(causes: list[RootCauseCandidate]) -> list[str]:
    if not causes:
        return [
            "No strong root-cause signature was detected for the requested date. Expand the date filter or inspect additional must-gather content.",
        ]

    recommendations: list[str] = []
    for cause in causes[:3]:
        if cause.key == "etcd_health":
            recommendations.append("Prioritize etcd health verification, quorum checks, and control-plane node resource review before restarting dependent operators.")
        elif cause.key == "api_availability":
            recommendations.append("Validate kube-apiserver and oauth availability, then correlate with ingress and authentication operator events.")
        elif cause.key == "node_resource_pressure":
            recommendations.append("Inspect node pressure signals, disk utilization, eviction activity, and kubelet readiness transitions for affected nodes.")
        elif cause.key == "operator_degradation":
            recommendations.append("Review degraded cluster operators in event order to separate primary failures from downstream symptoms.")
        elif cause.key == "network_instability":
            recommendations.append("Correlate connection resets and timeouts with SDN/OVN, DNS, and infrastructure network changes around the incident window.")
    return recommendations


def render_human_readable_report(summary: LogSummary) -> str:
    def bullet_ranked(items: list[tuple[str, int]], empty: str) -> str:
        return "\n".join(f"- {name}: {count}" for name, count in items) if items else f"- {empty}"

    lines = [
        "# OpenShift Must-Gather Incident Report",
        "",
        f"- Source bundle: `{summary.source_path}`",
        f"- Incident date: `{summary.incident_date}`",
        f"- Files scanned: **{summary.total_files_scanned}**",
        f"- Matching dated lines: **{summary.matched_lines}**",
        "",
        "## Most Likely Root Causes",
    ]
    if summary.root_cause_candidates:
        for idx, cause in enumerate(summary.root_cause_candidates, start=1):
            lines.append(f"{idx}. **{cause.title}** ({cause.hit_count} matching signals) — {cause.rationale}")
    else:
        lines.append("1. No strong root-cause candidate detected for the requested date.")

    lines.extend(
        [
            "",
            "## Severity Breakdown",
            bullet_ranked(list(summary.levels.items()), "No dated severity markers found."),
            "",
            "## Highest-Volume Namespaces",
            bullet_ranked(summary.top_namespaces, "No namespaces matched the requested date."),
            "",
            "## Highest-Volume Nodes",
            bullet_ranked(summary.top_nodes, "No nodes matched the requested date."),
            "",
            "## Timeline Highlights",
        ]
    )
    if summary.timeline:
        lines.extend(
            f"- [{event.severity}] {event.source}:{event.line_number} — {event.line}" for event in summary.timeline[:10]
        )
    else:
        lines.append("- No dated evidence lines found in the must-gather content.")

    lines.extend(["", "## Recommended Next Steps"])
    lines.extend(f"- {item}" for item in summary.recommendations)
    return "\n".join(lines)


def render_html_report(summary: LogSummary) -> str:
    def ranked_list(items: list[tuple[str, int]], empty: str) -> str:
        if not items:
            return f"<li>{escape(empty)}</li>"
        return "".join(f"<li><strong>{escape(name)}</strong>: {count}</li>" for name, count in items)

    causes_html = "".join(
        "<article class='card'><h3>{title}</h3><p><strong>{hits} matching signals.</strong> {rationale}</p>{evidence}</article>".format(
            title=escape(cause.title),
            hits=cause.hit_count,
            rationale=escape(cause.rationale),
            evidence=(
                "<ul>" + "".join(
                    f"<li><code>{escape(ev.source)}:{ev.line_number}</code> — {escape(ev.line)}</li>" for ev in cause.evidence
                ) + "</ul>"
            ) if cause.evidence else "<p>No example evidence captured.</p>",
        )
        for cause in summary.root_cause_candidates
    ) or "<article class='card'><h3>No clear root cause found</h3><p>Try broadening the date filter or supplying a fuller must-gather archive.</p></article>"

    timeline_html = "".join(
        f"<tr><td>{escape(ev.severity)}</td><td>{escape(ev.source)}</td><td>{ev.line_number}</td><td>{escape(ev.line)}</td></tr>"
        for ev in summary.timeline[:20]
    ) or "<tr><td colspan='4'>No dated evidence lines were found.</td></tr>"

    recommendations_html = "".join(f"<li>{escape(item)}</li>" for item in summary.recommendations)

    return f"""<!DOCTYPE html>
<html lang='en'>
<head>
  <meta charset='utf-8'>
  <title>OpenShift Must-Gather Incident Analysis</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem auto; max-width: 1100px; color: #1f2937; line-height: 1.5; }}
    h1, h2, h3 {{ color: #111827; }}
    .hero {{ background: #f3f4f6; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1rem; }}
    .card {{ background: white; border: 1px solid #d1d5db; border-radius: 10px; padding: 1rem; box-shadow: 0 1px 2px rgba(0,0,0,.04); }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border: 1px solid #e5e7eb; padding: .65rem; vertical-align: top; text-align: left; }}
    th {{ background: #f9fafb; }}
    code {{ background: #f3f4f6; padding: .1rem .3rem; border-radius: 4px; }}
  </style>
</head>
<body>
  <section class='hero'>
    <h1>OpenShift 4.16 Must-Gather Incident Analysis</h1>
    <p>This report analyzes must-gather content for <strong>{escape(summary.incident_date)}</strong> and highlights the most probable root causes with supporting evidence.</p>
    <ul>
      <li><strong>Source bundle:</strong> <code>{escape(str(summary.source_path))}</code></li>
      <li><strong>Files scanned:</strong> {summary.total_files_scanned}</li>
      <li><strong>Dated evidence lines:</strong> {summary.matched_lines}</li>
    </ul>
  </section>

  <h2>Executive Summary</h2>
  <div class='grid'>{causes_html}</div>

  <h2>Hotspots</h2>
  <div class='grid'>
    <article class='card'><h3>Namespaces</h3><ul>{ranked_list(summary.top_namespaces, 'No namespaces matched the requested date.')}</ul></article>
    <article class='card'><h3>Nodes</h3><ul>{ranked_list(summary.top_nodes, 'No nodes matched the requested date.')}</ul></article>
    <article class='card'><h3>Pods</h3><ul>{ranked_list(summary.top_pods, 'No pods matched the requested date.')}</ul></article>
  </div>

  <h2>Recommended Next Steps</h2>
  <div class='card'><ol>{recommendations_html}</ol></div>

  <h2>Timeline Evidence</h2>
  <table>
    <thead><tr><th>Severity</th><th>Source</th><th>Line</th><th>Evidence</th></tr></thead>
    <tbody>{timeline_html}</tbody>
  </table>
</body>
</html>
"""
