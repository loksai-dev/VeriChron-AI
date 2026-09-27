import pytest

pytest.importorskip("fastapi")


def test_api_health_structure():
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert "services" in body
    assert "neo4j" in body["services"]
    assert "hindsight" in body["services"]
    assert "openclaw" in body["services"]
    groq = body["services"]["groq"]
    assert "reasoning" in groq
    assert "classification" in groq
    h = body["services"]["hindsight"]
    if h.get("status") == "healthy":
        assert h.get("mode") == "live"
    else:
        assert h.get("mode") in {"MOCK MODE", "disconnected", "down"} or h.get("status") == "down"


def test_unknown_control_query():
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    r = client.post("/api/query", json={"question": "What happened to PAM-01?", "framework": "SOC 2"})
    assert r.status_code == 200
    body = r.json()
    assert "PAM-01" in body.get("conclusion", "")
    assert body.get("affected_controls") == []
    assert "CC6.1" not in (body.get("affected_controls") or [])


def test_unknown_date_query():
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    r = client.post(
        "/api/query",
        json={"question": "What was the control state as of last quarter?", "framework": "SOC 2"},
    )
    assert r.status_code == 200
    assert "April 15" in r.json().get("conclusion", "")
