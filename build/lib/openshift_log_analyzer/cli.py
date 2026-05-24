from __future__ import annotations

import argparse
from pathlib import Path

from . import analyze_log_file, render_html_report, render_human_readable_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="openshift-must-gather-analyzer",
        description="Analyze an OpenShift 4.16 must-gather archive for a specific incident date and produce human-readable output.",
    )
    parser.add_argument("bundle", help="Path to a must-gather directory or tar/tgz archive")
    parser.add_argument("--incident-date", required=True, help="Incident date to analyze (YYYY-MM-DD)")
    parser.add_argument("--top", type=int, default=5, help="Top N namespaces, nodes, pods, and root-cause candidates to show")
    parser.add_argument(
        "--html-output",
        type=Path,
        help="Optional destination for a standalone HTML report. If omitted, only the text report is printed.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = analyze_log_file(args.bundle, incident_date=args.incident_date, top_n=args.top)
    print(render_human_readable_report(summary))

    if args.html_output:
        args.html_output.write_text(render_html_report(summary), encoding="utf-8")
        print(f"\nHTML report written to: {args.html_output}")


if __name__ == "__main__":
    main()
