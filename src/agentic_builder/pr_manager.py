from __future__ import annotations

from .models import PullRequestDraft, ToolBlueprint


class PRManager:
    def create_draft(self, blueprint: ToolBlueprint) -> PullRequestDraft:
        title = f"feat: bootstrap {blueprint.title.lower()}"
        body_sections = [
            "## Objective",
            blueprint.summary,
            "",
            "## Scope",
            *[f"- {item}" for item in blueprint.capabilities],
            "",
            "## Architecture",
            *[f"- {item}" for item in blueprint.architecture],
            "",
            "## Validation",
            *[f"- {item}" for item in blueprint.tests],
        ]
        return PullRequestDraft(title=title, body="\n".join(body_sections))
