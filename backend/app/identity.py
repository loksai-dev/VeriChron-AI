from __future__ import annotations

from dataclasses import dataclass

from app.config import get_settings


@dataclass
class CurrentUser:
    tenant_id: str
    role: str  # ADMIN | AUDITOR | ANALYST
    username: str


def current_user() -> CurrentUser:
    s = get_settings()
    return CurrentUser(
        tenant_id=getattr(s, "tenant_id", None) or "acme",
        role=getattr(s, "dev_role", None) or "AUDITOR",
        username=getattr(s, "dev_user", None) or "demo-auditor",
    )


def bank_id_for_tenant(tenant_id: str, configured: str) -> str:
    """Cloud bank is a UUID; logical isolation uses configured bank + tenant tag in metadata."""
    if configured and len(configured) > 20:
        return configured
    return f"verichron-{tenant_id}"


def memories_for_tenant(facts: list, tenant_id: str) -> list:
    """Drop memories tagged for another tenant. Untagged demo memories stay on ACME."""
    out = []
    for f in facts or []:
        if not isinstance(f, dict):
            continue
        meta = f.get("metadata") if isinstance(f.get("metadata"), dict) else {}
        tid = f.get("tenant_id") or meta.get("tenant_id")
        blob = f"{f.get('content') or ''} {f.get('text') or ''}".lower()
        if "tenant:northstar" in blob and tenant_id != "northstar":
            continue
        if tid and tid != tenant_id:
            continue
        if tenant_id == "northstar" and tid != "northstar" and "tenant:northstar" not in blob:
            continue
        out.append(f)
    return out
