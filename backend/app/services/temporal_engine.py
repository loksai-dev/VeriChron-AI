from __future__ import annotations

from datetime import date
from typing import Any

from app.models.schemas import GraphNode


def _ids(nodes: list[GraphNode]) -> set[str]:
    return {n.id for n in nodes}


def reconstruct_from_graph(nodes: list[GraphNode], valid_as_of: date, system_as_of: date) -> dict[str, Any]:
    ids = _ids(nodes)
    controls = [n for n in nodes if n.type == "Control"]
    findings = [n for n in nodes if n.type == "AuditFinding"]
    evidence = [n for n in nodes if n.type == "Evidence"]
    has_fail = "EV-TEST-FAIL" in ids
    has_pass = "EV-TEST-PASS" in ids
    has_iam = "EV-CT-MFA" in ids
    has_fix = "REM-MFA" in ids and any(n.id == "REM-MFA" and (n.status or "") in {"complete", "done"} for n in nodes)
    if has_pass or has_fix:
        status, label = "compliant", "COMPLIANT"
    elif has_fail or has_iam:
        status, label = "at_risk", "PARTIALLY COMPLIANT"
    else:
        status, label = "compliant", "COMPLIANT"
    control_rows = []
    for c in controls:
        st = c.status
        if c.id == "CC6.1" and (has_fail or has_iam) and not has_pass:
            st = "non_compliant"
        if c.id == "CC6.1" and has_pass:
            st = "compliant"
        control_rows.append({"id": c.id, "name": c.name, "status": st, "known": True})
    open_f = [n for n in findings if (n.status or "") not in {"remediated", "complete", "done"}]
    return {
        "tool": "reconstruct_historical_state",
        "valid_as_of": valid_as_of.isoformat(),
        "system_as_of": system_as_of.isoformat(),
        "as_of": valid_as_of.isoformat(),
        "compliance_status": status,
        "label": label,
        "controls": control_rows,
        "open_findings": [{"id": n.id, "name": n.name, "status": n.status} for n in open_f],
        "known_evidence": [n.id for n in evidence],
        "unknown_future_evidence": [],
        "events": [{"id": n.id, "title": n.name, "type": n.type} for n in nodes if n.type in {"Evidence", "AuditFinding", "Remediation"}],
        "source": "neo4j-graph",
        "node_count": len(nodes),
    }


def compare_graphs(before: list[GraphNode], after: list[GraphNode]) -> dict[str, Any]:
    a, b = _ids(before), _ids(after)
    added = sorted(b - a)
    removed = sorted(a - b)
    before_map = {n.id: n for n in before}
    after_map = {n.id: n for n in after}
    changed = []
    for i in sorted(a & b):
        bn, an = before_map[i], after_map[i]
        if (bn.status or "") != (an.status or "") or (bn.description or "") != (an.description or ""):
            changed.append(i)
    return {
        "ADDED": added,
        "REMOVED": removed,
        "CHANGED": changed,
        "SUPERSEDED": removed,
        "NEWLY_KNOWN": added,
        "UNCHANGED": sorted(a & b)[:40],
        "before_count": len(a),
        "after_count": len(b),
    }


def classify_evidence_role(node: GraphNode, related_types: set[str]) -> str:
    name = (node.name or "").lower() + (node.description or "").lower()
    if "contradict" in name or node.id == "EV-CONFLICT":
        return "CONTRADICTING"
    if "pack" in name or (node.system_start and str(node.system_start) >= "2025-07-15"):
        return "STALE" if "pack" in name else "CONTEXTUAL"
    if "pass" in name:
        return "SUPERSEDED" if "fail" in related_types else "SUPPORTING"
    if "fail" in name or "cloudtrail" in name:
        return "SUPPORTING"
    return "CONTEXTUAL"
