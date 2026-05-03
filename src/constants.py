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
        "name": "Self-improving Workflow",
        "desc": "Scores outputs and keeps the best improved candidate.",
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
    },
    3: {
        "score": 3,
        "explanation": "Tool use is a small step into action-taking, but still user-directed.",
        "chooses_actions": True,
        "uses_tools": True,
        "loops": False,
        "runs_independently": False,
        "self_verifies": False,
        "multi_agent": False,
    },
    4: {
        "score": 3,
        "explanation": "Retrieval grounds answers in evidence, improving reliability more than autonomy.",
        "chooses_actions": True,
        "uses_tools": True,
        "loops": False,
        "runs_independently": False,
        "self_verifies": True,
        "multi_agent": False,
    },
    5: {
        "score": 3,
        "explanation": "Planning shows structured reasoning, but is still single-pass and supervised.",
        "chooses_actions": True,
        "uses_tools": False,
        "loops": False,
        "runs_independently": False,
        "self_verifies": False,
        "multi_agent": False,
    },
    6: {
        "score": 4,
        "explanation": "Critique and revision adds one self-improvement loop.",
        "chooses_actions": True,
        "uses_tools": False,
        "loops": True,
        "runs_independently": False,
        "self_verifies": True,
        "multi_agent": False,
    },
    7: {
        "score": 6,
        "explanation": "Bounded agent loop runs observe-act-decide cycles with stop rules.",
        "chooses_actions": True,
        "uses_tools": True,
        "loops": True,
        "runs_independently": True,
        "self_verifies": True,
        "multi_agent": False,
    },
    8: {
        "score": 5,
        "explanation": "Mini orchestrator coordinates specialist roles and verification, but remains workshop-scale simulation.",
        "chooses_actions": True,
        "uses_tools": False,
        "loops": True,
        "runs_independently": True,
        "self_verifies": True,
        "multi_agent": True,
    },
}
