import pytest
from datetime import date


def test_neo4j_status():
    from app.services.factory import get_services

    s = get_services()
    ok, detail = s.neo4j.status()
    live = getattr(s.neo4j, "is_live", lambda: False)()
    if not live:
        pytest.skip(f"Neo4j not live: {detail}")
    g = s.neo4j.graph(None, date(2025, 7, 15), date(2025, 7, 15), None)
    assert len(g.nodes) > 0
    assert ok
