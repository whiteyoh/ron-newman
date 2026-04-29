def calculator_tool(expression: str) -> str:
    allowed = set("0123456789+-*/(). ")
    if any(c not in allowed for c in expression):
        raise ValueError("unsupported characters in expression")
    return str(eval(expression, {"__builtins__": {}}, {}))


def retrieve_local_facts(question: str) -> str:
    kb = {
        "postgres": "PostgreSQL default port is 5432.",
        "redis": "Redis default port is 6379.",
        "nginx": "Nginx commonly serves HTTP on port 80.",
    }
    lower_question = question.lower()
    for key, value in kb.items():
        if key in lower_question:
            return value
    return "No matching fact found in local knowledge base."
