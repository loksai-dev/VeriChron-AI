from app.agents.planner import extract_entity_id, is_remember_intent, plan_tools


def test_remember_intent():
    assert is_remember_intent("Remember that the MFA exception was approved.")
    tools = plan_tools("Remember that the MFA exception was approved.", "general", None)
    assert tools == [("retain_memory", {"content": "Remember that the MFA exception was approved.", "context": "operator"})]


def test_unknown_token_extracted():
    assert extract_entity_id("What happened to PAM-01?") == "PAM-01"


def test_does_not_always_include_cc61_traverse():
    names = [n for n, _ in plan_tools("What happened to PAM?", "general", "PAM")]
    assert "traverse_compliance_graph" in names
    args = dict(plan_tools("What happened to PAM?", "general", "PAM"))
    assert args["traverse_compliance_graph"]["start_id"] == "PAM"


def test_evidence_question_selects_neo4j():
    names = [n for n, _ in plan_tools("What evidence proves CC6.1 failed?", "evidence", "CC6.1")]
    assert "search_neo4j" in names
    assert "get_evidence" in names
