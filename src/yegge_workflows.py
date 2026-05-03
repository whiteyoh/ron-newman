from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class PermissionRequest:
    mode: str
    actions: list[str]
    approval_required: bool


@dataclass
class DiffPreview:
    target: str
    before: str
    after: str
    summary: str


@dataclass
class CommandPreview:
    run_id: str
    commands: list[str]
    simulated_only: bool = True


@dataclass
class ToolRunPreview:
    tool: str
    input: str
    output: str


@dataclass
class AgentInstance:
    name: str
    objective: str
    status: str
    output_summary: str
    confidence_note: str


@dataclass
class ParallelRunGroup:
    mode: str
    agents: list[AgentInstance] = field(default_factory=list)


@dataclass
class SwarmSummary:
    total_agents: int
    stress_meter: str
    pressure_points: list[str]
    board: dict[str, list[str]]


@dataclass
class HumanReviewGate:
    checkpoint: str
    required: bool
    review_style: str


@dataclass
class WorkflowRisk:
    risk: str
    control: str


@dataclass
class WorkflowOutcome:
    status: str
    note: str


@dataclass
class YeggeWorkflowSimulation:
    level: int
    closest_yegge_stage: int
    workflow_name: str
    capability_being_taught: str
    yegge_pattern: str
    human_role: str
    agent_role: str
    trust_level: str
    autonomy_level: str
    simulated_environment: str
    permissions: PermissionRequest | None
    previewed_changes: list[DiffPreview]
    command_preview: CommandPreview | None
    agent_instances: list[AgentInstance]
    review_gate: HumanReviewGate
    risk_controls: list[WorkflowRisk]
    audit_events: list[str]
    outcome: WorkflowOutcome
    why_this_maps_to_yegge: str
    why_not_production: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_yegge_simulation(level: int, objective: str, use_case: str) -> YeggeWorkflowSimulation:
    base_risks = [
        WorkflowRisk("Over-trust in generated output", "Human approval gate before use"),
        WorkflowRisk(
            "External side effects", "Workshop-safe simulation with no real external action"
        ),
    ]
    if level == 1:
        return YeggeWorkflowSimulation(
            level,
            1,
            "Prompt-only baseline",
            "Autocomplete / Ask",
            "Near-zero AI",
            "Human owns context and execution",
            "Tiny continuation helper",
            "low",
            "none",
            "chat-only simulation",
            None,
            [],
            None,
            [],
            HumanReviewGate("final sentence check", True, "human reads the whole output"),
            base_risks,
            ["no tools", "no repo access", "no autonomy"],
            WorkflowOutcome("complete", "Human did almost all work"),
            "Faithfully simulates Stage 1 by keeping AI tiny and human-owned.",
            "No tools, no file writes, no command execution.",
        )
    if level == 2:
        return YeggeWorkflowSimulation(
            level,
            2,
            "Permissioned IDE agent",
            "Instruction following",
            "IDE agent with permissions on",
            "Approves each action",
            "Proposes edits and checks",
            "cautious",
            "low",
            "simulated IDE sidebar",
            PermissionRequest("permission on", ["read file", "propose change", "run check"], True),
            [DiffPreview("lesson_plan.md", "old line", "new line", "small edit proposal")],
            None,
            [],
            HumanReviewGate("per-action approval", True, "pre-action approval"),
            base_risks,
            ["permission prompt shown", "diff preview shown"],
            WorkflowOutcome("complete", "Only approved actions proceed"),
            "Maps to Stage 2 with explicit permission + diff preview loop.",
            "No real files are modified.",
        )
    if level == 3:
        return YeggeWorkflowSimulation(
            level,
            3,
            "Sandbox YOLO mode",
            "Tool use",
            "IDE YOLO simulation",
            "Sets pre-approved budget and reviews after run",
            "Runs safe simulated tools",
            "moderate",
            "medium",
            "sandbox-only tool run",
            PermissionRequest("YOLO simulation within sandbox", ["safe tool run"], False),
            [],
            None,
            [],
            HumanReviewGate("post-run review", True, "review after autonomous burst"),
            base_risks
            + [WorkflowRisk("Unchecked tool action", "No external writes / no persistent changes")],
            ["budget granted", "tool trace reviewed"],
            WorkflowOutcome("complete", "Autonomous burst completed inside sandbox"),
            "Matches Stage 3: fewer interrupts, post-run review.",
            "No real command execution or persistence.",
        )
    if level == 4:
        return YeggeWorkflowSimulation(
            level,
            4,
            "Wide IDE agent",
            "Retrieval + grounding",
            "Conversation over diffs",
            "Steers direction, reviews summary",
            "Synthesizes broad context and proposal",
            "moderate-high",
            "medium",
            "wide-context simulation",
            PermissionRequest("guided", ["read sources", "draft proposal"], True),
            [
                DiffPreview(
                    "resource proposal",
                    "current structure",
                    "evidence-backed structure",
                    "directional diff summary",
                )
            ],
            None,
            [],
            HumanReviewGate("direction check", True, "conversation-level review"),
            base_risks,
            ["context bundle reviewed", "evidence cited"],
            WorkflowOutcome("complete", "Direction accepted with evidence"),
            "Matches Stage 4: conversation + wider context dominate.",
            "Still simulated context, no repository change.",
        )
    if level == 5:
        return YeggeWorkflowSimulation(
            level,
            5,
            "CLI-first run",
            "Multi-step reasoning",
            "CLI-first single agent",
            "Defines objective and validates run output",
            "Executes bounded plan",
            "high",
            "medium-high",
            "CLI-style run simulation",
            PermissionRequest("bounded run", ["preview command", "simulate check"], True),
            [],
            CommandPreview(
                "sim-run-5", ["plan --objective", "check --safety", "finalize --artifact"], True
            ),
            [],
            HumanReviewGate("final artifact", True, "operator reviews run summary"),
            base_risks,
            ["run id assigned", "command preview shown"],
            WorkflowOutcome("complete", "Run completed with checks"),
            "Matches Stage 5 by centering a run log over IDE edits.",
            "Commands are previews only.",
        )
    if level == 6:
        agents = [
            AgentInstance("planner", "split work", "complete", "plan drafted", "medium"),
            AgentInstance("writer", "draft content", "complete", "draft ready", "medium"),
            AgentInstance("critic", "find weaknesses", "complete", "issues listed", "high"),
            AgentInstance("verifier", "check support", "complete", "verification note", "high"),
        ]
        return YeggeWorkflowSimulation(
            level,
            6,
            "Parallel agents",
            "Critique + revision",
            "Several parallel agents",
            "Reviews merged output",
            "Runs scoped agents in parallel",
            "task-dependent",
            "high",
            "parallel workshop simulation",
            PermissionRequest("parallel scoped", ["parallel draft", "merge with gate"], True),
            [],
            None,
            agents,
            HumanReviewGate("verifier + human merge gate", True, "merge only after verifier"),
            base_risks,
            ["parallel group launched", "merge gate enforced"],
            WorkflowOutcome("complete", "Parallel outputs merged after review"),
            "Matches Stage 6 parallel coordination pattern.",
            "No background jobs or persistent workers.",
        )
    if level == 7:
        cards = [
            AgentInstance(
                f"agent-{i}",
                "micro-task",
                "running" if i < 5 else "ready",
                "partial output",
                "mixed",
            )
            for i in range(1, 12)
        ]
        return YeggeWorkflowSimulation(
            level,
            7,
            "Hand-managed swarm",
            "Constrained agent loop",
            "10+ hand-managed agents",
            "Acts as coordinator under pressure",
            "Produces many lightweight outputs",
            "selective",
            "very high",
            "swarm card simulation",
            PermissionRequest("manual dispatch", ["assign card", "move board state"], True),
            [],
            None,
            cards,
            HumanReviewGate("coordination checkpoint", True, "human resolves conflicts"),
            base_risks,
            ["coordination pressure observed", "duplicate work detected"],
            WorkflowOutcome("strained", "Shows orchestration need"),
            "Matches Stage 7 by surfacing manual coordination stress with 10+ agents.",
            "Simulated cards only; not real concurrent production agents.",
        )
    return YeggeWorkflowSimulation(
        level,
        8,
        "Custom orchestrator",
        "Mini-orchestrator",
        "Custom orchestrator policy",
        "Defines orchestration policy and final approval",
        "Routes workers, retries, verifies, proposes merge",
        "governed",
        "programmable high",
        "taskboard orchestrator simulation",
        PermissionRequest(
            "policy-governed", ["route task", "retry worker", "apply merge policy"], True
        ),
        [],
        CommandPreview("orch-run", ["dispatch workers", "run verifier", "approval gate"], True),
        [],
        HumanReviewGate("approval before merge", True, "policy + human gate"),
        base_risks
        + [WorkflowRisk("Bad merge decision", "Verifier supported + approval gate required")],
        ["task lifecycle logged", "worker lifecycle logged"],
        WorkflowOutcome("complete", "Merged only when verifier and approval pass"),
        "Matches Stage 8 with explicit orchestration policy and lifecycle.",
        "High-fidelity workshop simulation, not production orchestration.",
    )
