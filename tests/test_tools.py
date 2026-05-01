import pytest

from src.levels import use_case_prompt
from src.tools import calculator_tool, retrieve_local_facts


def test_calculator_tool_multiplies():
    assert calculator_tool("17*43") == "731"


def test_calculator_tool_power_operator():
    assert calculator_tool("2**8") == "256"


def test_calculator_tool_division_by_zero():
    with pytest.raises(ValueError, match="division by zero"):
        calculator_tool("1/0")


def test_calculator_tool_malformed_expression():
    with pytest.raises(ValueError, match="malformed expression"):
        calculator_tool("1+(")


def test_calculator_tool_very_large_input_rejected():
    with pytest.raises(ValueError, match="expression too long"):
        calculator_tool("1" * 201)


def test_calculator_tool_rejects_unsafe_input():
    with pytest.raises(ValueError):
        calculator_tool("__import__('os').system('echo bad')")


def test_retrieve_local_facts_known_key():
    assert retrieve_local_facts("Which port does Redis use?") == "Redis default port is 6379."


def test_retrieve_local_facts_unknown_key():
    assert retrieve_local_facts("What is Kafka default port?") == "No matching fact found in local knowledge base."


def test_use_case_prompt_includes_human_revision_and_clarification_requirements():
    result = use_case_prompt("Draft a response")
    assert "what to revise and how to revise it" in result
    assert "if key details are missing, ask follow-up questions" in result


def test_use_case_prompt_prefixes_text():
    result = use_case_prompt("Draft a response")
    assert "Use case for all levels" in result
    assert result.endswith("Draft a response")
