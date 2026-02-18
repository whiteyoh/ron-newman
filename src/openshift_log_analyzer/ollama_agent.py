from __future__ import annotations

import json
from urllib import error, request

from .analyzer import LogSummary
from .renderer import render_human_readable_report


def request_ollama_agent_analysis(
    *,
    summary: LogSummary,
    model: str,
    base_url: str,
    timeout_seconds: int = 60,
) -> str:
    prompt = _build_operator_prompt(summary)
    payload = {
        "model": model,
        "stream": False,
        "prompt": prompt,
    }

    base_url = base_url.rstrip("/")
    url = f"{base_url}/api/generate"

    req = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=timeout_seconds) as response:
            body = response.read().decode("utf-8")
    except error.URLError as exc:
        return (
            "Unable to reach Ollama. Ensure Ollama is running locally and that the model is pulled. "
            f"Connection error: {exc}"
        )

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        return f"Ollama returned non-JSON output:\n{body}"

    if "response" not in parsed:
        return f"Unexpected Ollama response payload:\n{body}"

    return str(parsed["response"]).strip()


def _build_operator_prompt(summary: LogSummary) -> str:
    top_issue_lines = [
        *summary.notable_errors,
        *summary.api_failure_signals,
        *summary.watch_storm_signals,
        *summary.master_node_risk_signals,
        *summary.unhealthy_operator_signals,
    ]
    unique_lines = list(dict.fromkeys(line for line in top_issue_lines if line.strip()))
    condensed_lines = unique_lines[:20]
    condensed_issue_text = "\n".join(f"- {line}" for line in condensed_lines) or "- No issue lines captured"

    return "\n".join(
        [
            "You are an OpenShift SRE agent.",
            "Analyze the provided log report and issue lines.",
            "Respond with:",
            "1) probable root causes,",
            "2) immediate mitigation steps,",
            "3) a 24-hour stabilization plan,",
            "4) suggested kubectl/oc commands to verify assumptions.",
            "Keep the answer concise and action-oriented.",
            "",
            "=== Analyzer Report ===",
            render_human_readable_report(summary),
            "",
            "=== Condensed Raw Issue Lines ===",
            condensed_issue_text,
        ]
    )
