from app.identity import memories_for_tenant


def test_northstar_does_not_see_acme_tagged():
    facts = [
        {"id": "1", "text": "acme finding", "tenant_id": "acme"},
        {"id": "2", "text": "tenant:northstar secret", "tenant_id": "northstar"},
    ]
    acme = memories_for_tenant(facts, "acme")
    ns = memories_for_tenant(facts, "northstar")
    assert {f["id"] for f in acme} == {"1"}
    assert {f["id"] for f in ns} == {"2"}
