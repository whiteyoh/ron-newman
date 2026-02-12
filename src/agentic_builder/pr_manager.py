from __future__ import annotations

from .models import PullRequestDraft, ToolBlueprint


class PRManager:
    def create_draft(self, blueprint: ToolBlueprint) -> PullRequestDraft:
        title = f"feat: bootstrap {blueprint.title.lower()}"
        prioritized_backlog = [
            f"TKT-{index:03d} (High) {item}"
            for index, item in enumerate(blueprint.capabilities, start=1)
        ]
        amendment_slice = prioritized_backlog[:2]

        body_sections = [
            "## Objective",
            blueprint.summary,
            "",
            "## Scope",
            *[f"- {item}" for item in blueprint.capabilities],
            "",
            "## Prioritized Backlog (Important Features)",
            *[f"- {item}" for item in prioritized_backlog],
            "",
            "## Amendment Ticket Slice (Max 2 per PR)",
            *[f"- {item}" for item in amendment_slice],
            "",
            "## Amendment Rules",
            "- Every pull request amendment must include no more than 2 ticket numbers.",
            "- Unselected tickets stay in backlog for later amendments.",
            "",
            "## Architecture",
            *[f"- {item}" for item in blueprint.architecture],
            "",
            "## Validation",
            *[f"- {item}" for item in blueprint.tests],
        ]
        return PullRequestDraft(title=title, body="\n".join(body_sections))
