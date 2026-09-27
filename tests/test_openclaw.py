from app.config import Settings
from app.openclaw.client import OpenClawGatewayClient


def test_health_disconnected_is_honest():
    s = Settings()
    s.openclaw_gateway_url = "http://127.0.0.1:1"
    s.openclaw_gateway_token = ""
    h = OpenClawGatewayClient(s).health()
    assert h["status"] == "disconnected"
    assert h["status"] != "connected"


def test_unknown_control_tool_empty():
    from fastapi.testclient import TestClient
    from app.main import app

    c = TestClient(app)
    r = c.post(
        "/api/internal/openclaw/tools/traverse_control",
        json={"tenant_id": "acme", "control_id": "PAM-01", "valid_as_of": "2025-05-15", "system_as_of": "2025-05-15"},
    )
    assert r.status_code == 200
    body = r.json()
    assert "No matching control" in (body.get("error") or "")
    assert body.get("path") == []


def test_missing_dates_rejected():
    from fastapi.testclient import TestClient
    from app.main import app

    c = TestClient(app)
    r = c.post(
        "/api/internal/openclaw/tools/search_compliance_graph",
        json={"tenant_id": "acme", "query": "CC6.1"},
    )
    assert r.status_code == 400
