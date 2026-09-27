from datetime import date

from app.agents.planner import KNOWN_CONTROLS, extract_entity_id
from app.identity import bank_id_for_tenant, current_user


def test_unknown_control_not_in_known():
    eid = extract_entity_id("What happened to ZZ-UNKNOWN-99?")
    assert eid == "ZZ-UNKNOWN-99"
    assert eid not in KNOWN_CONTROLS


def test_tenant_bank_naming():
    assert bank_id_for_tenant("northstar", "verichron") == "verichron-northstar"
    assert current_user().tenant_id == "acme"


def test_reconstruct_uses_graph_ids():
    from app.models.schemas import GraphNode
    from app.services.temporal_engine import reconstruct_from_graph

    nodes = [
        GraphNode(id="EV-TEST-FAIL", type="Evidence", name="fail", valid_start=date(2025, 5, 5), system_start=date(2025, 5, 5)),
        GraphNode(id="CC6.1", type="Control", name="MFA", status="degraded", valid_start=date(2025, 1, 1), system_start=date(2025, 1, 1)),
    ]
    out = reconstruct_from_graph(nodes, date(2025, 5, 15), date(2025, 5, 15))
    assert out["source"] == "neo4j-graph"
    assert out["label"] == "PARTIALLY COMPLIANT"
