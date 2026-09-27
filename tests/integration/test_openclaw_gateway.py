import os

import pytest


def test_openclaw_gateway_models():
    from app.config import get_settings
    from app.openclaw.client import OpenClawGatewayClient

    h = OpenClawGatewayClient(get_settings()).health()
    if h.get("status") != "connected":
        pytest.skip(f"gateway not connected: {h}")
    assert "openclaw" in str(h.get("models"))
