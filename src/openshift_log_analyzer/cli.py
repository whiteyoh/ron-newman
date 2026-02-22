from __future__ import annotations

import argparse

from . import analyze_log_file, render_human_readable_report
from .ollama_agent import AgentPolicy, ExecutionMode, request_ollama_agent_analysis


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="openshift-log-analyzer",
        description="Analyze OpenShift logs and produce a human-readable summary.",
    )
    parser.add_argument("log_file", help="Path to an OpenShift log file")
    parser.add_argument("--top", type=int, default=5, help="Top N pods/namespaces and error lines")
    parser.add_argument(
        "--ollama-agent",
        action="store_true",
        help="Ask a local Ollama model to produce an operator-style analysis from the report and log context.",
    )
    parser.add_argument(
        "--ollama-model",
        default="llama3.2",
        help="Local Ollama model to use when --ollama-agent is enabled (default: llama3.2).",
    )
    parser.add_argument(
        "--ollama-url",
        default="http://127.0.0.1:11434",
        help="Base URL for a local Ollama server (default: http://127.0.0.1:11434).",
    )
    parser.add_argument(
        "--agent-mode",
        choices=[mode.value for mode in ExecutionMode],
        default=ExecutionMode.PROPOSE_CHANGES.value,
        help="Human gate mode: propose_changes (default) or apply_changes.",
    )
    parser.add_argument("--tenant", default="default", help="Tenant identifier for policy checks.")
    parser.add_argument("--namespace", default="default", help="Namespace identifier for policy checks.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = analyze_log_file(args.log_file, top_n=args.top)
    rendered_summary = render_human_readable_report(summary)
    print(rendered_summary)

    if args.ollama_agent:
        print("\n## Ollama Agent Analysis\n")
        agent_analysis = request_ollama_agent_analysis(
            summary=summary,
            model=args.ollama_model,
            base_url=args.ollama_url,
            mode=ExecutionMode(args.agent_mode),
            policy=AgentPolicy(
                tenant=args.tenant,
                namespace=args.namespace,
                allowed_tools={"ollama.generate": ["*"]},
            ),
        )
        print(agent_analysis)


if __name__ == "__main__":
    main()
