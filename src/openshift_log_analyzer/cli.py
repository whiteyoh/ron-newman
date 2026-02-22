from __future__ import annotations

import argparse
import textwrap

from . import analyze_log_file, render_human_readable_report
from .ollama_agent import AgentPolicy, ExecutionMode, WorkflowTrace, request_ollama_agent_analysis


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
    parser.add_argument(
        "--interactive-agent",
        action="store_true",
        help="Stream workflow step outputs and request human approval before automated fixes.",
    )
    return parser


def _render_streamed_step(trace: WorkflowTrace) -> None:
    status = "ok" if trace.success else "failed"
    print(f"\n[{trace.step.value}] {status} ({trace.latency_ms}ms)")
    print(textwrap.shorten(trace.detail.replace("\n", " "), width=180, placeholder="..."))


def _request_human_approval(recommendation: str) -> bool:
    print("\n--- Human Approval Required ---")
    print("Agent recommendation preview:")
    print(textwrap.shorten(recommendation.replace("\n", " "), width=200, placeholder="..."))
    while True:
        response = input("Apply automated fix plan? [y/N]: ").strip().lower()
        if response in {"y", "yes"}:
            return True
        if response in {"", "n", "no"}:
            return False
        print("Please answer 'y' or 'n'.")


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
            step_event_handler=_render_streamed_step if args.interactive_agent else None,
            approval_callback=_request_human_approval if args.interactive_agent else None,
        )
        print(agent_analysis)


if __name__ == "__main__":
    main()
