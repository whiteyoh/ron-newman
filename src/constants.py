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
    "uk_year10_teacher": "Use case for all levels: help a UK Year 10 teacher create engaging lesson plans. Keep a human in the loop by asking them to choose one of five subjects (English, Maths, Science, History, Geography), learning objectives, and class constraints before generating the plan.",
    "year10_exam_student": "Use case for all levels: support a Year 10 student with exam-prep requests only (revision plans, concept explanations, and practice support).",
    "curriculum_designer": "Use case for all levels: help a school curriculum designer produce downloadable schemes of work, lesson sequences, and revision resources aligned to Year 10 outcomes.",
}

DEFAULT_USE_CASE_KEY = "uk_year10_teacher"
