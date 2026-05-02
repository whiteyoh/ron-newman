from __future__ import annotations

import ast

Number = int | float
MAX_AST_DEPTH = 25
MAX_EXPONENT = 8
MAX_ABS_VALUE = 1_000_000_000


class _SafeMathEvaluator(ast.NodeVisitor):
    def __init__(self) -> None:
        self.depth = 0

    def _check_number(self, value: Number) -> Number:
        if abs(value) > MAX_ABS_VALUE:
            raise ValueError("numeric value too large")
        return value

    def visit(self, node: ast.AST) -> Number:  # type: ignore[override]
        self.depth += 1
        if self.depth > MAX_AST_DEPTH:
            raise ValueError("expression too deep")
        try:
            return super().visit(node)
        finally:
            self.depth -= 1

    def visit_Expression(self, node: ast.Expression) -> Number:
        return self.visit(node.body)

    def visit_BinOp(self, node: ast.BinOp) -> Number:
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(node.op, ast.Add):
            return self._check_number(left + right)
        if isinstance(node.op, ast.Sub):
            return self._check_number(left - right)
        if isinstance(node.op, ast.Mult):
            return self._check_number(left * right)
        if isinstance(node.op, ast.Div):
            return self._check_number(left / right)
        if isinstance(node.op, ast.Pow):
            if abs(right) > MAX_EXPONENT:
                raise ValueError("exponent too large")
            return self._check_number(left**right)
        raise ValueError("unsupported operator")

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Number:
        operand = self.visit(node.operand)
        if isinstance(node.op, ast.UAdd):
            return self._check_number(+operand)
        if isinstance(node.op, ast.USub):
            return self._check_number(-operand)
        raise ValueError("unsupported unary operator")

    def visit_Constant(self, node: ast.Constant) -> Number:
        if isinstance(node.value, (int, float)):
            return self._check_number(node.value)
        raise ValueError("unsupported constant")

    def generic_visit(self, node: ast.AST) -> Number:
        raise ValueError(f"unsupported syntax: {type(node).__name__}")


def calculator_tool(expression: str) -> str:
    if len(expression) > 200:
        raise ValueError("expression too long")
    try:
        parsed = ast.parse(expression, mode="eval")
        result = _SafeMathEvaluator().visit(parsed)
    except ZeroDivisionError as err:
        raise ValueError("division by zero") from err
    except SyntaxError as err:
        raise ValueError("malformed expression") from err
    return str(result)


def retrieve_local_facts(question: str) -> str:
    kb = {
        "postgres": "PostgreSQL default port is 5432.",
        "redis": "Redis default port is 6379.",
        "nginx": "Nginx commonly serves HTTP on port 80.",
        "smart learning objective": "A SMART learning objective is Specific, Measurable, Achievable, Relevant, and Time-bound.",
        "smart objective": "A SMART learning objective is Specific, Measurable, Achievable, Relevant, and Time-bound.",
    }
    lower_question = question.lower()
    for key, value in kb.items():
        if key in lower_question:
            return value
    return "No matching fact found in local knowledge base."
