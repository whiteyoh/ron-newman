from __future__ import annotations

from .models import FolderInsight, ToolBlueprint


class ToolPlanner:
    """Rule-based planner that proposes an agentic builder from folder insights."""

    def build_blueprint(self, insight: FolderInsight) -> ToolBlueprint:
        ext_text = ", ".join(f"{k}: {v}" for k, v in insight.extensions.items()) or "unknown"
        capabilities = [
            "Analyze uploaded folder structure and file types.",
            "Generate implementation plans and tasks as pull-request sized units.",
            "Stream every decision and generated artifact into a human-visible chat window.",
            "Capture feedback and turn it into iterative improvement proposals.",
        ]

        architecture = [
            "Ingestion Agent: scans files, classifies technologies, and builds context.",
            "Planning Agent: proposes tool architecture, milestones, and backlog.",
            "PR Agent: drafts branch names, commit plans, and pull-request descriptions.",
            "Evolution Agent: incorporates human feedback into the next planning cycle.",
        ]

        tests = [
            "Unit tests for folder analysis and blueprint generation.",
            "Contract tests ensuring PR drafts include objective, scope, and validation sections.",
            "Regression tests for evolution logic to ensure feedback is preserved.",
        ]

        summary = (
            f"Scanned `{insight.root.name}` with {insight.file_count} files. "
            f"Detected extension profile: {ext_text}. "
            "The generated system should optimize for transparent chat-first collaboration and PR-first delivery."
        )

        return ToolBlueprint(
            title=f"Agentic Builder for {insight.root.name}",
            summary=summary,
            capabilities=capabilities,
            architecture=architecture,
            tests=tests,
        )
