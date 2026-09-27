from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from app.agents.planner import KNOWN_CONTROLS, extract_entity_id
from app.config import get_settings
from app.identity import current_user
from app.services.factory import get_services
from app.services.temporal_engine import classify_evidence_role, compare_graphs, reconstruct_from_graph
from app.temporal import parse_iso

router = APIRouter()


class ToolCall(BaseModel):
    tenant_id: str
    valid_as_of: str | None = None
    system_as_of: str | None = None
    query: str | None = None
    control_id: str | None = None
    first_valid_date: str | None = None
    second_valid_date: str | None = None


def _auth(x_verichron_tool_token: str | None) -> None:
    expected = get_settings().openclaw_tool_token
    if expected and x_verichron_tool_token != expected:
        raise HTTPException(401, "invalid tool token")


def _tenant(req_tenant: str) -> str:
    user = current_user()
    if user.role != "ADMIN" and req_tenant and req_tenant != user.tenant_id:
        raise HTTPException(403, "tenant isolation: request tenant_id does not match caller")
    return user.tenant_id


def _dates(valid_s: str | None, system_s: str | None) -> tuple[date, date]:
    vd = parse_iso(valid_s)
    sd = parse_iso(system_s)
    if valid_s and vd is None:
        raise HTTPException(400, "I couldn't determine the requested date. Please specify a date such as April 15, 2025.")
    if system_s and sd is None:
        raise HTTPException(400, "I couldn't determine the requested system date. Please specify a date such as May 1, 2025.")
    if vd is None or sd is None:
        raise HTTPException(400, "valid_as_of and system_as_of are required and must be ISO dates (YYYY-MM-DD). No silent default.")
    return vd, sd


def _unknown_control(control_id: str | None) -> dict[str, Any] | None:
    if not control_id:
        return None
    if control_id in KNOWN_CONTROLS or control_id.startswith("CC") or "-" in control_id:
        node = get_services().neo4j.get_entity(control_id)
        if node is None:
            return {"error": f"No matching control was found for '{control_id}'.", "nodes": [], "path": [], "records": []}
    return None


@router.post("/search_compliance_graph")
def search_compliance_graph(req: ToolCall, x_verichron_tool_token: str | None = Header(default=None)):
    _auth(x_verichron_tool_token)
    tenant = _tenant(req.tenant_id)
    vd, sd = _dates(req.valid_as_of, req.system_as_of)
    entity = extract_entity_id(req.query or "")
    unknown = _unknown_control(entity)
    if unknown:
        return {**unknown, "tenant_id": tenant}
    payload = get_services().neo4j.graph(entity, vd, sd, None)
    return {
        "tool": "search_compliance_graph",
        "tenant_id": tenant,
        "valid_as_of": vd.isoformat(),
        "system_as_of": sd.isoformat(),
        "source": getattr(get_services().neo4j, "source", "unknown"),
        "cypher": getattr(get_services().neo4j, "last_cypher", "")[:500],
        "nodes": [n.id for n in payload.nodes][:40],
        "relationships": len(payload.edges),
        "count": len(payload.nodes),
    }


@router.post("/traverse_control")
def traverse_control(req: ToolCall, x_verichron_tool_token: str | None = Header(default=None)):
    _auth(x_verichron_tool_token)
    tenant = _tenant(req.tenant_id)
    vd, sd = _dates(req.valid_as_of, req.system_as_of)
    cid = req.control_id or extract_entity_id(req.query or "") or ""
    unknown = _unknown_control(cid)
    if unknown:
        return {**unknown, "tenant_id": tenant}
    payload = get_services().neo4j.graph(cid, vd, sd, None)
    path = [n.id for n in payload.nodes][:16]
    return {
        "tool": "traverse_control",
        "tenant_id": tenant,
        "control_id": cid,
        "path": path,
        "nodes": len(payload.nodes),
        "source": getattr(get_services().neo4j, "source", "unknown"),
        "cypher": getattr(get_services().neo4j, "last_cypher", "")[:500],
    }


@router.post("/reconstruct_state")
def reconstruct_state(req: ToolCall, x_verichron_tool_token: str | None = Header(default=None)):
    _auth(x_verichron_tool_token)
    tenant = _tenant(req.tenant_id)
    vd, sd = _dates(req.valid_as_of, req.system_as_of)
    cid = req.control_id
    unknown = _unknown_control(cid)
    if unknown:
        return {**unknown, "tenant_id": tenant}
    payload = get_services().neo4j.graph(cid, vd, sd, None)
    out = reconstruct_from_graph(payload.nodes, vd, sd)
    out["tenant_id"] = tenant
    return out


@router.post("/compare_states")
def compare_states(req: ToolCall, x_verichron_tool_token: str | None = Header(default=None)):
    _auth(x_verichron_tool_token)
    tenant = _tenant(req.tenant_id)
    a = parse_iso(req.first_valid_date)
    b = parse_iso(req.second_valid_date)
    sysd = parse_iso(req.system_as_of)
    if not a or not b or not sysd:
        raise HTTPException(400, "first_valid_date, second_valid_date, and system_as_of are required ISO dates.")
    cid = req.control_id
    unknown = _unknown_control(cid)
    if unknown:
        return {**unknown, "tenant_id": tenant}
    g1 = get_services().neo4j.graph(cid, a, a, None)
    g2 = get_services().neo4j.graph(cid, b, sysd, None)
    return {"tool": "compare_states", "tenant_id": tenant, "diff": compare_graphs(g1.nodes, g2.nodes), "from": a.isoformat(), "to": b.isoformat(), "system_as_of": sysd.isoformat()}


@router.post("/get_evidence")
def get_evidence(req: ToolCall, x_verichron_tool_token: str | None = Header(default=None)):
    _auth(x_verichron_tool_token)
    tenant = _tenant(req.tenant_id)
    vd, sd = _dates(req.valid_as_of, req.system_as_of)
    cid = req.control_id
    unknown = _unknown_control(cid)
    if unknown:
        return {**unknown, "tenant_id": tenant}
    payload = get_services().neo4j.graph(cid, vd, sd, None)
    records = []
    for n in payload.nodes:
        if n.type != "Evidence":
            continue
        records.append({**n.model_dump(mode="json"), "role": classify_evidence_role(n, set())})
    return {"tool": "get_evidence", "tenant_id": tenant, "count": len(records), "records": records[:16], "source": "neo4j"}


@router.post("/analyze_evidence")
def analyze_evidence(req: ToolCall, x_verichron_tool_token: str | None = Header(default=None)):
    _auth(x_verichron_tool_token)
    body = get_evidence(req, x_verichron_tool_token)
    roles: dict[str, list[str]] = {}
    conflicts = []
    for r in body.get("records") or []:
        roles.setdefault(r.get("role") or "CONTEXTUAL", []).append(r.get("id"))
    if "CONTRADICTING" in roles and "SUPPORTING" in roles:
        conflicts.append(
            {
                "message": "Supporting and contradicting evidence are both visible at the requested as-of clocks. Do not arbitrarily pick one.",
                "supporting": roles["SUPPORTING"],
                "contradicting": roles["CONTRADICTING"],
            }
        )
    return {"tool": "analyze_evidence", "tenant_id": body.get("tenant_id"), "roles": roles, "conflicts": conflicts, "records": body.get("records")}
