import pytest

from src.tools import calculator_tool


def test_calculator_basic() -> None:
    assert calculator_tool("17*43") == "731"


def test_calculator_blocks_huge_power() -> None:
    with pytest.raises(ValueError, match="exponent too large"):
        calculator_tool("2**100")


def test_calculator_blocks_deep_expression() -> None:
    expr = "+" * 30 + "1"
    with pytest.raises(ValueError, match="too deep"):
        calculator_tool(expr)
