import tarfile
from pathlib import Path

import pytest

from openshift_log_analyzer import analyze_log_file, render_html_report, render_human_readable_report


def test_analyze_must_gather_archive_for_specific_incident_date(tmp_path: Path) -> None:
    bundle_root = tmp_path / "must-gather-src"
    events_dir = bundle_root / "namespaces" / "openshift-etcd"
    events_dir.mkdir(parents=True)
    log_file = events_dir / "events.log"
    log_file.write_text(
        "\n".join(
            [
                "2026-03-15T10:01:00Z ERROR namespace=openshift-kube-apiserver node=master-0 pod=kube-apiserver-master-0 kube-apiserver unavailable with status=503",
                "2026-03-15T10:02:00Z WARN namespace=openshift-etcd node=master-1 pod=etcd-master-1 etcd leader changed after timeout and quorum instability",
                "2026-03-15T10:03:00Z WARN namespace=openshift-cluster-version node=master-0 clusteroperator authentication degraded and unavailable",
                "2026-03-14T23:59:00Z ERROR namespace=old node=worker-0 unrelated previous day line",
            ]
        ),
        encoding="utf-8",
    )

    archive = tmp_path / "must-gather.tgz"
    with tarfile.open(archive, "w:gz") as tar:
        tar.add(bundle_root, arcname="must-gather")

    summary = analyze_log_file(archive, incident_date="2026-03-15", top_n=5)

    assert summary.incident_date == "2026-03-15"
    assert summary.total_files_scanned >= 1
    assert summary.matched_lines == 3
    assert summary.root_cause_candidates
    assert summary.root_cause_candidates[0].key in {"api_availability", "etcd_health", "operator_degradation"}
    assert dict(summary.top_nodes)["master-0"] >= 1
    assert dict(summary.top_namespaces)["openshift-etcd"] >= 1


def test_reports_are_human_readable_and_include_html_sections(tmp_path: Path) -> None:
    log_file = tmp_path / "events.log"
    log_file.write_text(
        "2026-03-15T10:01:00Z ERROR namespace=openshift-kube-apiserver node=master-0 pod=kube-apiserver-master-0 kube-apiserver unavailable with status=503\n",
        encoding="utf-8",
    )

    summary = analyze_log_file(log_file, incident_date="2026-03-15")
    text_report = render_human_readable_report(summary)
    html_report = render_html_report(summary)

    assert "# OpenShift Must-Gather Incident Report" in text_report
    assert "## Most Likely Root Causes" in text_report
    assert "## Timeline Highlights" in text_report
    assert "<html" in html_report
    assert "OpenShift 4.16 Must-Gather Incident Analysis" in html_report
    assert "Executive Summary" in html_report
    assert "Timeline Evidence" in html_report


def test_analyze_log_file_rejects_invalid_path() -> None:
    with pytest.raises(ValueError, match="Invalid must-gather input"):
        analyze_log_file("/tmp/does-not-exist.log", incident_date="2026-03-15")
