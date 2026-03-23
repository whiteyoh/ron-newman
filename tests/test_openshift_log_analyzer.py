from pathlib import Path

import pytest

from openshift_log_analyzer import analyze_log_file, render_human_readable_report


def test_analyze_log_file_scans_master_infra_worker_and_control_plane_logs(tmp_path: Path) -> None:
    log_file = tmp_path / "cluster.log"
    log_file.write_text(
        """
INFO pod=router-77 namespace=openshift-ingress node=infra-0 Route admitted
ERROR pod=kube-apiserver-master-0 namespace=openshift-kube-apiserver node=master-0 kube-apiserver unavailable with status=503 and i/o timeout
WARN pod=etcd-master-1 namespace=openshift-etcd node=master-1 etcd leader changed, watch relist storm, mvcc compaction required
ERROR pod=machine-config-daemon-9 namespace=openshift-machine-config-operator node=worker-2 kubelet node not ready due to disk pressure
WARN namespace=openshift-monitoring clusteroperator monitoring degraded and unavailable
WARN pod=oauth-openshift namespace=openshift-authentication node=master-0 apiserver connection reset while processing token review
""".strip()
        + "\n",
        encoding="utf-8",
    )

    summary = analyze_log_file(log_file, top_n=5)

    assert summary.total_lines == 6
    assert summary.levels["INFO"] == 1
    assert summary.levels["WARN"] == 3
    assert summary.levels["ERROR"] == 2

    assert len(summary.api_failure_signals) >= 2
    assert len(summary.watch_storm_signals) >= 1
    assert len(summary.master_node_risk_signals) >= 2
    assert len(summary.unhealthy_operator_signals) >= 1

    assert summary.problematic_namespaces[0][0] == "openshift-kube-apiserver"
    problematic_nodes = dict(summary.problematic_nodes)
    assert "master-0" in problematic_nodes
    assert "worker-2" in problematic_nodes

    infrastructure_hotspots = dict(summary.infrastructure_hotspots)
    assert infrastructure_hotspots["kube-apiserver"] >= 1
    assert infrastructure_hotspots["etcd"] >= 1


def test_render_human_readable_report_contains_comprehensive_scan_sections(tmp_path: Path) -> None:
    log_file = tmp_path / "openshift.log"
    log_file.write_text("ERROR node=master-0 namespace=bar kube-apiserver failed to connect\n", encoding="utf-8")

    summary = analyze_log_file(log_file)
    report = render_human_readable_report(summary)

    assert "# OpenShift Log Analysis Report" in report
    assert "## Log Level Breakdown" in report
    assert "## API Failures & Failure Patterns" in report
    assert "## Watch Storm / Watch Collapse Signals" in report
    assert "## Problematic Namespaces" in report
    assert "## Problematic Nodes (master/infra/worker)" in report
    assert "## Control Plane / Infrastructure Hotspots" in report
    assert "## Master Node Risk Indicators" in report
    assert "## Unhealthy Operator Signals" in report


def test_analyze_log_file_rejects_invalid_path() -> None:
    with pytest.raises(ValueError, match="Invalid log file path"):
        analyze_log_file("/tmp/does-not-exist.log")
