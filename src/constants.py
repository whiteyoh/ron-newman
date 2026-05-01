LEVELS = {
    1: {"name": "Autocomplete", "desc": "Predicts likely next text from a short prompt."},
    2: {"name": "Instruction Following", "desc": "Follows explicit constraints in a prompt."},
    3: {"name": "Tool Use", "desc": "Selects and uses a calculator tool for exact arithmetic."},
    4: {"name": "Retrieval + Grounding", "desc": "Reads local facts, then answers using retrieved context."},
    5: {"name": "Multi-step Reasoning", "desc": "Builds and executes a structured plan for a concrete goal."},
    6: {"name": "Agentic Loop", "desc": "Iterates with critique + revision until quality target is met."},
    7: {"name": "Multi-agent Collaboration", "desc": "Uses role-specialized agents to produce one final result."},
    8: {"name": "Self-improving Workflow", "desc": "Scores outputs and keeps the best improved candidate."},
}

USE_CASE_OPTIONS = {
    "uk_year10_teacher": "Use case for all levels: help a UK Year 10 teacher create engaging, classroom-ready lesson and revision plans with clear sequence, timings, activities, assessment, and differentiation. Every response must include real, curriculum-relevant subject content (key concepts, worked examples, misconceptions, retrieval questions, and success criteria), not just templates or layout placeholders. If the user asks for revision or lesson planning, produce a complete, teachable plan with topic-specific details and model answers. Use provided context and reasonable defaults when details are missing; do not ask follow-up questions. End every response with a clear, easy-to-scan section titled 'What you should do next' that translates the output into practical human steps (for example: classroom session breakdown, revision plan, and immediate actions).",
    "year10_exam_student": "Use case for all levels: support a Year 10 student with exam-prep requests only (revision plans, concept explanations, and practice support). Every response must include concrete subject knowledge for the requested topic (facts, formulas, vocabulary, examples, and short self-test questions with answers), not just study structure.",
    "curriculum_designer": "Use case for all levels: help a school curriculum designer produce downloadable schemes of work, lesson sequences, and revision resources aligned to Year 10 outcomes.",
}

DEFAULT_USE_CASE_KEY = "uk_year10_teacher"
