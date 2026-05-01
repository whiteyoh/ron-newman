from src.agent_runtime import choose_next_action, run_constrained_agent_loop
from src.tools import calculator_tool, retrieve_local_facts


class SequenceClient:
    def __init__(self, responses):
        self.responses = list(responses)

    def chat(self, *_args, **_kwargs):
        if not self.responses:
            return '{"action":"finish","input":"","reason":"done","final":"fallback"}'
        return self.responses.pop(0)


def test_valid_json_action_selection():
    client = SequenceClient(['{"action":"research","input":"smart objective","reason":"need facts","final":""}'])
    decision = choose_next_action(client, "obj", [], "")
    assert decision.action == "research"
    assert decision.input == "smart objective"


def test_invalid_json_fallback_after_retry():
    client = SequenceClient(["not json", "still not json"])
    decision = choose_next_action(client, "obj", [], "")
    assert decision.action == "draft"
    assert "Fallback" in decision.reason


def test_calculate_tool_success():
    client = SequenceClient(
        [
            '{"action":"calculate","input":"2*60","reason":"compute minutes","final":""}',
            '{"action":"finish","input":"","reason":"done","final":"120 minutes"}',
        ]
    )
    result = run_constrained_agent_loop(client, "obj", retrieve_local_facts, calculator_tool)
    assert any(step.action == "calculate" and step.observation == "120" for step in result["trace"])


def test_calculate_tool_error_recovery():
    client = SequenceClient(
        [
            '{"action":"calculate","input":"1/0","reason":"try calc","final":""}',
            '{"action":"finish","input":"","reason":"done","final":"handled"}',
        ]
    )
    result = run_constrained_agent_loop(client, "obj", retrieve_local_facts, calculator_tool)
    assert "tool error" in result["trace"][0].observation
    assert result["final_answer"] == "handled"


def test_finish_stops_loop():
    client = SequenceClient(['{"action":"finish","input":"","reason":"done","final":"answer"}'])
    result = run_constrained_agent_loop(client, "obj", retrieve_local_facts, calculator_tool)
    assert len(result["trace"]) == 1
    assert result["stopped_on_finish"] is True


def test_max_iteration_fallback():
    loop_response = '{"action":"research","input":"postgres","reason":"collect","final":""}'
    client = SequenceClient([loop_response, loop_response, loop_response, loop_response, loop_response, "best effort"])
    result = run_constrained_agent_loop(client, "obj", retrieve_local_facts, calculator_tool, max_iterations=5)
    assert result["stopped_on_finish"] is False
    assert result["final_answer"] == "best effort"
