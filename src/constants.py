# ruff: noqa: E501
LEVELS = {
    1: {
        "name": "Autocomplete",
        "desc": "Predicts likely next text from a short prompt.",
        "nourishment": (
            "Gives a fast first draft you can react to instead of starting from a blank page."
        ),
    },
    2: {
        "name": "Instruction Following",
        "desc": "Follows explicit constraints in a prompt.",
        "nourishment": (
            "Improves reliability by honoring exact format, length, and scope requirements."
        ),
    },
    3: {
        "name": "Tool Use",
        "desc": "Selects and uses a calculator tool for exact arithmetic.",
        "nourishment": (
            "Raises accuracy for concrete tasks by combining language with dependable tool outputs."
        ),
    },
    4: {
        "name": "Retrieval + Grounding",
        "desc": "Reads local facts, then answers using retrieved context.",
        "nourishment": "Builds trust by tying responses to evidence instead of free-form guessing.",
    },
    5: {
        "name": "Multi-step Reasoning",
        "desc": "Builds and executes a structured plan for a concrete goal.",
        "nourishment": "Turns broad goals into actionable sequences that are easier to execute.",
    },
    6: {
        "name": "Critique + Revision",
        "desc": "Uses model critique to revise an initial draft once.",
        "nourishment": "Improves quality through a quick feedback loop before you use the result.",
    },
    7: {
        "name": "Constrained Agent Loop",
        "desc": (
            "Runs a bounded observe, act, observe, replan cycle using allowed "
            "tools and explicit stop conditions."
        ),
        "nourishment": (
            "Adds controlled autonomy so complex tasks progress safely with "
            "visible reasoning steps."
        ),
    },
    8: {
        "name": "Mini Orchestrator / Self-improving Workflow",
        "desc": (
            "Workshop-safe simulation that coordinates planner, critic, "
            "teacher-resource-writer, and verifier roles."
        ),
        "nourishment": (
            "Delivers stronger final answers by iterating and selecting the "
            "best-performing version."
        ),
    },
}

USE_CASE_OPTIONS = {
    "uk_year10_teacher": "Use case for all levels: help a UK Year 10 teacher create engaging, classroom-ready lesson and revision plans with clear sequence, timings, activities, assessment, and differentiation. Every response must include real, curriculum-relevant subject content (key concepts, worked examples, misconceptions, retrieval questions, and success criteria), not just templates or layout placeholders. If the user asks for revision or lesson planning, produce a complete, teachable plan with topic-specific details and model answers. Use provided context and reasonable defaults when details are missing; do not ask follow-up questions. End every response with a clear, easy-to-scan section titled 'What you should do next' that translates the output into practical human steps (for example: classroom session breakdown, revision plan, and immediate actions).",
    "year10_exam_student": "Use case for all levels: support a Year 10 student with exam-prep requests only (revision plans, concept explanations, and practice support). Every response must include concrete subject knowledge for the requested topic (facts, formulas, vocabulary, examples, and short self-test questions with answers), not just study structure.",
    "curriculum_designer": "Use case for all levels: help a school curriculum designer produce downloadable schemes of work, lesson sequences, and revision resources aligned to Year 10 outcomes.",
}
DEFAULT_USE_CASE_KEY = "uk_year10_teacher"

AGENTICNESS = {
    1: {
        "score": 7,
        "explanation": "Supervised completion agent now runs objective-policy-action-verify flow with approval gate and audit trail.",
        "chooses_actions": True,
        "uses_tools": False,
        "loops": True,
        "runs_independently": True,
        "self_verifies": True,
        "multi_agent": False,
        "closest_yegge_stage": 2,
        "yegge_alignment_score": 7,
        "yegge_alignment_explanation": "Autocomplete is uplifted into a bounded supervised completion agent with verification and human approval.",
    },
    2: {
        "score": 7,
        "explanation": "Permissioned instruction-following agent uses instruction contract, constraint verification, revision path, and approval gate.",
        "chooses_actions": True,
        "uses_tools": False,
        "loops": True,
        "runs_independently": True,
        "self_verifies": True,
        "multi_agent": False,
        "closest_yegge_stage": 3,
        "yegge_alignment_score": 7,
        "yegge_alignment_explanation": "Mirrors supervised IDE/YOLO transition with explicit permission and verifier gates.",
    },
    3: {
        "score": 7,
        "explanation": "Tool-action loop now includes model-selected action trace, independent calculator verification, approval gate, and audit trail.",
        "chooses_actions": True,
        "system_selected_tool": False,
        "uses_tools": True,
        "loops": True,
        "runs_independently": True,
        "self_verifies": True,
        "multi_agent": False,
        "closest_yegge_stage": 4,
        "yegge_alignment_score": 7,
        "yegge_alignment_explanation": "Demonstrates bounded autonomous tool-use and verification resembling wider IDE-to-CLI behavior.",
    },
    4: {
        "score": 7,
        "explanation": "Grounded research agent now plans evidence lookup, checks sufficiency/support, routes through approval gate, and logs decisions.",
        "chooses_actions": True,
        "system_selected_tool": False,
        "uses_tools": True,
        "loops": True,
        "runs_independently": True,
        "self_verifies": True,
        "multi_agent": False,
        "closest_yegge_stage": 5,
        "yegge_alignment_score": 7,
        "yegge_alignment_explanation": "Adds CLI-style bounded evidence workflow with explicit verifier and human control gates.",
    },
    5: {
        "score": 7,
        "explanation": "Planning capability now executes as CLI-style bounded run with action budget, verifier, stop condition, approval gate, and audit trail.",
        "chooses_actions": True,
        "uses_tools": False,
        "loops": True,
        "runs_independently": True,
        "self_verifies": True,
        "multi_agent": False,
        "closest_yegge_stage": 5,
        "yegge_alignment_score": 7,
        "yegge_alignment_explanation": "Represents single-agent terminal workflow mechanics without production autonomy claims.",
    },
    6: {
        "score": 7,
        "explanation": "Critique/revision is now a bounded evaluator agent loop with scoring, revision decisions, best-candidate selection, approval gate, and audit trail.",
        "chooses_actions": True,
        "uses_tools": False,
        "loops": True,
        "runs_independently": True,
        "self_verifies": True,
        "multi_agent": False,
        "closest_yegge_stage": 6,
        "yegge_alignment_score": 7,
        "yegge_alignment_explanation": "Shows bounded autonomous evaluator behavior approaching parallel-agent maturity concepts while staying single-agent.",
    },
    7: {
        "score": 7,
        "explanation": "Bounded agent run enforces policy, budgets, tool-error limits, and final verification gate.",
        "chooses_actions": True,
        "uses_tools": True,
        "loops": True,
        "runs_independently": True,
        "self_verifies": True,
        "multi_agent": False,
        "closest_yegge_stage": 5,
        "yegge_alignment_score": 7,
        "yegge_alignment_explanation": "Closest to CLI-first single-agent with policy gates, budgets, and verification.",
    },
    8: {
        "score": 8,
        "explanation": "Mini orchestrator adds isolated worker roles, verifier gate, merge policy, and parallel-safe execution.",
        "chooses_actions": True,
        "uses_tools": False,
        "loops": True,
        "runs_independently": True,
        "self_verifies": True,
        "multi_agent": True,
        "closest_yegge_stage": 6,
        "yegge_alignment_score": 9,
        "yegge_alignment_explanation": "Now includes taskboard state, worker lifecycle, retry policy, verifier gate, approval gate, and merge policy. Still workshop-safe and not a production orchestrator.",
    },
}
