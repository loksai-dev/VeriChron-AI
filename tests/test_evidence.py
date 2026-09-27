from datetime import date

from app.models.schemas import GraphNode
from app.services.temporal_engine import classify_evidence_role, compare_graphs


def test_contradicting_role():
    n = GraphNode(
        id="EV-CONFLICT",
        type="Evidence",
        name="Contradicting snapshot",
        description="contradicts MFA disable",
        valid_start=date(2025, 5, 1),
        system_start=date(2025, 5, 1),
    )
    assert classify_evidence_role(n, set()) == "CONTRADICTING"


def test_compare_added_removed():
    a = [
        GraphNode(id="A", type="Evidence", name="a", valid_start=date(2025, 4, 1), system_start=date(2025, 4, 1)),
    ]
    b = [
        GraphNode(id="A", type="Evidence", name="a", status="stale", valid_start=date(2025, 4, 1), system_start=date(2025, 4, 1)),
        GraphNode(id="B", type="Evidence", name="b", valid_start=date(2025, 5, 1), system_start=date(2025, 5, 1)),
    ]
    d = compare_graphs(a, b)
    assert "B" in d["ADDED"]
    assert "B" in d["NEWLY_KNOWN"]
    assert "A" in d["CHANGED"]
