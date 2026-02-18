from pathlib import Path

import pytest

from openshift_log_analyzer import analyze_log_file, render_human_readable_report


def test_analyze_log_file_summarizes_levels_and_entities(tmp_path: Path) -> None:
    log_file = tmp_path / "openshift.log"
    log_file.write_text(
        """
INFO pod=api-7 namespace=payments Request started
WARNING pod=api-7 namespace=payments Slow response
ERROR pod=worker-2 namespace=batch Failed to process job
DEBUG pod=api-7 namespace=payments Trace detail
""".strip()
        + "\n",
        encoding="utf-8",
    )

    summary = analyze_log_file(log_file, top_n=2)

    assert summary.total_lines == 4
    assert summary.levels["INFO"] == 1
    assert summary.levels["WARN"] == 1
    assert summary.levels["ERROR"] == 1
    assert summary.top_pods[0][0] == "api-7"
    assert summary.top_namespaces[0][0] == "payments"
    assert len(summary.notable_errors) == 1


def test_render_human_readable_report_contains_expected_sections(tmp_path: Path) -> None:
    log_file = tmp_path / "openshift.log"
    log_file.write_text("ERROR pod=foo namespace=bar failed to connect\n", encoding="utf-8")

    summary = analyze_log_file(log_file)
    report = render_human_readable_report(summary)

    assert "# OpenShift Log Analysis Report" in report
    assert "## Log Level Breakdown" in report
    assert "## Most Frequent Pods" in report
    assert "## Most Frequent Namespaces" in report
    assert "## Notable Error/Failure Lines" in report


def test_analyze_log_file_rejects_invalid_path() -> None:
    with pytest.raises(ValueError, match="Invalid log file path"):
        analyze_log_file("/tmp/does-not-exist.log")
