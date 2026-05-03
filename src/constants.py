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
    "uk_year10_teacher": (
        "Use case for all levels: help a UK Year 10 teacher create engaging, "
        "classroom-ready lesson and revision plans with clear sequence, timings, "
        "activities, assessment, and differentiation. Every response must include "
        "real, curriculum-relevant subject content (key concepts, worked examples, "
        "misconceptions, retrieval questions, and success criteria), not just "
        "templates or layout placeholders. If the user asks for revision or lesson "
        "planning, produce a complete, teachable plan with topic-specific details "
        "and model answers. Use provided context and reasonable defaults when "
        "details are missing; do not ask follow-up questions. End every response "
        "with a clear, easy-to-scan section titled 'What you should do next' "
        "that translates the output into practical human steps (for example: "
        "classroom session breakdown, revision plan, and immediate actions)."
    ),
    "year10_exam_student": (
        "Use case for all levels: support a Year 10 student with exam-prep "
        "requests only (revision plans, concept explanations, and practice "
        "support). Every response must include concrete subject knowledge for the "
        "requested topic (facts, formulas, vocabulary, examples, and short "
        "self-test questions with answers), not just study structure."
    ),
    "curriculum_designer": (
        "Use case for all levels: help a school curriculum designer "
        "produce downloadable schemes of work, lesson sequences, and revision "
        "resources aligned to Year 10 outcomes."
    ),
}

DEFAULT_USE_CASE_KEY = "uk_year10_teacher"

AGENTICNESS = {
    1: {
        "score": 1,
        "explanation": "Autocomplete predicts likely text but does not choose goals or actions.",
        "chooses_actions": False,
        "uses_tools": False,
        "loops": False,
        "runs_independently": False,
        "self_verifies": False,
        "multi_agent": False,
        "closest_yegge_stage": 1,
        "yegge_alignment_score": 1,
        "yegge_alignment_explanation": "No autonomous workflow behavior.",
    },
    2: {
        "score": 1,
        "explanation": "Instruction following obeys prompts, but autonomy remains minimal.",
        "chooses_actions": False,
        "uses_tools": False,
        "loops": False,
        "runs_independently": False,
        "self_verifies": False,
        "multi_agent": False,
        "closest_yegge_stage": 2,
        "yegge_alignment_score": 1,
        "yegge_alignment_explanation": "Prompt following but not autonomous execution.",
    },
    3: {
        "score": 4,
        "explanation": "Model selects between direct answer and calculator, then returns a visible tool trace.",
        "chooses_actions": True,
        "system_selected_tool": False,
        "uses_tools": True,
        "loops": False,
        "runs_independently": False,
        "self_verifies": False,
        "multi_agent": False,
        "closest_yegge_stage": 3,
        "yegge_alignment_score": 4,
        "yegge_alignment_explanation": "Model chooses tool action but stays workshop bounded.",
    },
    4: {
        "score": 4,
        "explanation": "Retrieval now includes evidence trace, source, sufficiency check, and support verification.",
        "chooses_actions": True,
        "system_selected_tool": False,
        "uses_tools": True,
        "loops": False,
        "runs_independently": False,
        "self_verifies": True,
        "multi_agent": False,
        "closest_yegge_stage": 4,
        "yegge_alignment_score": 4,
        "yegge_alignment_explanation": "Evidence-grounded response with support checks resembles wider supervised workflows.",
    },
    5: {
        "score": 5,
        "explanation": "Plan-execute-verify with one conditional revision pass improves outcome quality.",
        "chooses_actions": True,
        "uses_tools": False,
        "loops": False,
        "runs_independently": False,
        "self_verifies": False,
        "multi_agent": False,
        "closest_yegge_stage": 5,
        "yegge_alignment_score": 5,
        "yegge_alignment_explanation": "Single-agent plan/execute/verify loop with revision decision.",
    },
    6: {
        "score": 5,
        "explanation": "Bounded critique loop scores attempts and revises up to two times.",
        "chooses_actions": True,
        "uses_tools": False,
        "loops": True,
        "runs_independently": False,
        "self_verifies": True,
        "multi_agent": False,
        "closest_yegge_stage": 5,
        "yegge_alignment_score": 5,
        "yegge_alignment_explanation": "Bounded evaluator loop improves drafts iteratively.",
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
        "yegge_alignment_score": 8,
        "yegge_alignment_explanation": "Parallel worker orchestration with verifier+merger, still workshop-safe and limited.",
    },
}
