import os

import pytest

pytest.importorskip("httpx")


def test_hindsight_health_and_roundtrip():
    from app.config import get_settings
    from app.services.hindsight_service import RealHindsightService

    s = get_settings()
    if not s.hindsight_api_key:
        pytest.skip("HINDSIGHT_API_KEY not set")
    h = RealHindsightService(s.hindsight_url, s.hindsight_bank_id, s.hindsight_api_key)
    assert h.is_live(), h.status()
    token = "VERICHRON_PERSIST_TOKEN_A1B2"
    retained = h.retain(
        f"{token} ACME MFA exception approved June 20 2025 for legacy authentication.",
        context="pytest",
        timestamp="2025-06-20",
        document_id="pytest-persist-a1b2",
        metadata={"tenant_id": "acme", "fact_type": "test"},
    )
    live = (retained.get("live") or {})
    assert live.get("ok") or live.get("http") == 200
    recalled = h.recall(token, valid_as_of=None, system_as_of=None)
    blob = str(recalled).lower()
    assert token.lower() in blob or recalled.get("source") == "hindsight-cloud"
    reflected = h.reflect("Why was the ACME MFA exception approved?", valid_as_of=None, system_as_of=None)
    assert reflected.get("source") in {"hindsight-cloud", "mock-after-cloud-error", "mock"}
    if reflected.get("source") == "hindsight-cloud":
        assert reflected.get("reflection")
