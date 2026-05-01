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
    "saas_product": "Use case for all levels: improve customer support response quality for a SaaS product.",
    "uk_year10_teacher": "Use case for all levels: help a UK Year 10 school teacher design lessons, explanations, and assessment support.",
    "year10_exam_student": "Use case for all levels: help a Year 10 student prepare effectively for upcoming exams.",
}

DEFAULT_USE_CASE_KEY = "saas_product"
