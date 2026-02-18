from __future__ import annotations

import argparse

from . import analyze_log_file, render_human_readable_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="openshift-log-analyzer",
        description="Analyze OpenShift logs and produce a human-readable summary.",
    )
    parser.add_argument("log_file", help="Path to an OpenShift log file")
    parser.add_argument("--top", type=int, default=5, help="Top N pods/namespaces and error lines")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = analyze_log_file(args.log_file, top_n=args.top)
    print(render_human_readable_report(summary))


if __name__ == "__main__":
    main()
