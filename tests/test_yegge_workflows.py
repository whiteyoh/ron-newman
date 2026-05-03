from src.yegge_workflows import build_yegge_simulation


def test_all_levels_have_required_fields_and_safety_claims():
    required = {
        "level",
        "closest_yegge_stage",
        "workflow_name",
        "capability_being_taught",
        "yegge_pattern",
        "human_role",
        "agent_role",
        "simulated_environment",
        "review_gate",
        "risk_controls",
        "outcome",
        "why_this_maps_to_yegge",
        "why_not_production",
    }
    for level in range(1, 9):
        sim = build_yegge_simulation(level, "objective", "use case").to_dict()
        assert required.issubset(sim.keys())
        assert sim["why_not_production"]
        lower = str(sim).lower()
        assert "real shell execution" not in lower
        assert "real file writes" not in lower
        assert "github writes" not in lower


def test_level_specific_semantics():
    l1 = build_yegge_simulation(1, "o", "u").to_dict()
    assert l1["closest_yegge_stage"] == 1
    l2 = build_yegge_simulation(2, "o", "u").to_dict()
    assert "permission" in str(l2).lower() and "diff preview" in str(l2).lower()
    l3 = build_yegge_simulation(3, "o", "u").to_dict()
    assert "yolo" in str(l3).lower() and "post-run review" in str(l3).lower()
    l4 = build_yegge_simulation(4, "o", "u").to_dict()
    assert "wide" in str(l4).lower() and "diff" in str(l4).lower()
    l5 = build_yegge_simulation(5, "o", "u").to_dict()
    assert "command preview" in str(l5).lower() and "simulated" in str(l5).lower()
    l6 = build_yegge_simulation(6, "o", "u").to_dict()
    assert 3 <= len(l6["agent_instances"]) <= 5
    l7 = build_yegge_simulation(7, "o", "u").to_dict()
    assert len(l7["agent_instances"]) >= 10
    l8 = build_yegge_simulation(8, "o", "u").to_dict()
    assert "orchestrator" in str(l8).lower() and "approval" in str(l8).lower()
