import ast
from typing import Union


Number = Union[int, float]


class _SafeMathEvaluator(ast.NodeVisitor):
    def visit_Expression(self, node: ast.Expression) -> Number:
        return self.visit(node.body)

    def visit_BinOp(self, node: ast.BinOp) -> Number:
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.Pow):
            return left ** right
        raise ValueError("unsupported operator")

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Number:
        operand = self.visit(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.USub):
            return -operand
        raise ValueError("unsupported unary operator")

    def visit_Constant(self, node: ast.Constant) -> Number:
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("unsupported constant")

    def generic_visit(self, node: ast.AST) -> Number:
        raise ValueError(f"unsupported syntax: {type(node).__name__}")


def calculator_tool(expression: str) -> str:
    if len(expression) > 200:
        raise ValueError("expression too long")

    try:
        parsed = ast.parse(expression, mode="eval")
        result = _SafeMathEvaluator().visit(parsed)
    except ZeroDivisionError:
        raise ValueError("division by zero")
    except SyntaxError:
        raise ValueError("malformed expression")

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
