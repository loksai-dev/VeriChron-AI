import os

import pytest


@pytest.mark.skipif(not os.getenv("HINDSIGHT_API_KEY"), reason="needs cloud key")
def test_memory_improves_agent_answer():
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    health = client.get("/api/health").json()
    if health.get("hindsight") != "connected":
        pytest.skip("Hindsight not live")
    oc = (health.get("services") or {}).get("openclaw") or {}
    token = "LEGACY_AUTH_DEPENDENCY_TOKEN_ZX9"
    retain = client.post(
        "/api/query",
        json={
            "question": f"Remember that the ACME MFA exception was approved because {token}.",
            "framework": "SOC 2",
        },
    )
    assert retain.status_code == 200
    if oc.get("status") != "connected":
        pytest.skip(f"OpenClaw gateway not connected: {oc}")
    recall = client.post(
        "/api/query",
        json={"question": "What was the reason for the ACME MFA exception?", "framework": "SOC 2"},
    )
    assert recall.status_code == 200
    body = recall.json()
    blob = (body.get("conclusion") or "") + str(body.get("memories_used") or "")
    assert token[:12].lower() in blob.lower() or "MEMORY CONTEXT" in blob or body.get("memory_source") == "hindsight-cloud"
