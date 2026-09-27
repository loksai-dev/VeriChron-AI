from __future__ import annotations

import json
from datetime import date
from time import perf_counter
from typing import Any, Callable

from app.data import demo
from app.logging_util import agent_log


def _ms(t0: float) -> int:
    return int((perf_counter() - t0) * 1000)


def _parse_date(value: str | None, default: date) -> date:
    if not value:
        return default
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return default


class AgentToolbox:
    def __init__(self, services):
        self.s = services

    def search_neo4j(self, query: str = "", valid_as_of: str | None = None, system_as_of: str | None = None) -> dict[str, Any]:
        t0 = perf_counter()
        agent_log("NEO4J", "Query started")
        vd = _parse_date(valid_as_of, date(2025, 7, 15))
        sd = _parse_date(system_as_of, vd)
        entity = None
        q = (query or "").upper()
        if "CC6.1" in q or "MFA" in q:
            entity = "CC6.1"
        payload = self.s.neo4j.graph(entity, vd, sd, None)
        agent_log("NEO4J", f"{len(payload.nodes)} nodes returned")
        return {
            "tool": "search_neo4j",
            "cypher": getattr(self.s.neo4j, "last_cypher", ""),
            "nodes": len(payload.nodes),
            "relationships": len(payload.edges),
            "node_ids": [n.id for n in payload.nodes][:40],
            "source": getattr(self.s.neo4j, "source", "unknown"),
            "ms": _ms(t0),
        }

    def get_entity(self, entity_id: str) -> dict[str, Any]:
        t0 = perf_counter()
        node = self.s.neo4j.get_entity(entity_id)
        return {
            "tool": "get_entity",
            "entity": node.model_dump(mode="json") if node else None,
            "found": node is not None,
            "ms": _ms(t0),
        }

    def traverse_compliance_graph(self, start_id: str = "CC6.1") -> dict[str, Any]:
        t0 = perf_counter()
        payload = self.s.neo4j.graph(start_id, date(2025, 7, 15), date(2025, 7, 15), None)
        path = [n.id for n in payload.nodes]
        ordered = [i for i in demo.CAUSAL_PATH if i in {n.id for n in payload.nodes}] or path[:8]
        return {
            "tool": "traverse_compliance_graph",
            "start": start_id,
            "path": ordered,
            "nodes": len(payload.nodes),
            "relationships": len(payload.edges),
            "cypher": getattr(self.s.neo4j, "last_cypher", ""),
            "ms": _ms(t0),
        }

    def search_hindsight(self, query: str, valid_as_of: str | None = None, system_as_of: str | None = None) -> dict[str, Any]:
        t0 = perf_counter()
        agent_log("HINDSIGHT", "Recall started")
        vd = _parse_date(valid_as_of, date(2025, 7, 15)) if valid_as_of else None
        sd = _parse_date(system_as_of, vd or date(2025, 7, 15)) if system_as_of else vd
        recalled = self.s.hindsight.recall(query, valid_as_of=vd, system_as_of=sd)
        facts = recalled.get("facts") or []
        agent_log("HINDSIGHT", f"{len(facts)} memories returned")
        return {"tool": "search_hindsight", "memories": facts[:12], "count": len(facts), "ms": _ms(t0)}

    def reconstruct_historical_state(self, as_of: str) -> dict[str, Any]:
        t0 = perf_counter()
        day = _parse_date(as_of, date(2025, 5, 15))
        events = [e for e in demo.TIMELINE if demo.occurred_by(e, day, day)]
        evidence_known = [e for e in demo.EVIDENCE if demo.visible_at(e, day, day)]
        evidence_future = [e for e in demo.EVIDENCE if e.system_start and e.system_start > day]
        findings = [f for f in demo.FINDINGS if demo.visible_at(f, day, day)]
        mfa_gap = any(e.id == "t-iam" for e in events) and not any(e.id == "t-fix" for e in events)
        remediated = any(e.id == "t-test-pass" for e in events)
        if remediated:
            status, label = "compliant", "COMPLIANT"
        elif mfa_gap:
            status, label = "at_risk", "PARTIALLY COMPLIANT"
        else:
            status, label = "compliant", "COMPLIANT"
        controls = []
        for c in demo.CONTROLS:
            known = demo.visible_at(c, day, day)
            st = c.status
            if c.id == "CC6.1" and mfa_gap:
                st = "non_compliant"
            if c.id == "CC6.1" and remediated:
                st = "compliant"
            controls.append({"id": c.id, "name": c.name, "status": st, "known": known})
        return {
            "tool": "reconstruct_historical_state",
            "as_of": day.isoformat(),
            "compliance_status": status,
            "label": label,
            "controls": controls,
            "open_findings": [f.model_dump(mode="json") for f in findings if f.status != "remediated" or (f.valid_end and f.valid_end >= day)],
            "known_evidence": [e.id for e in evidence_known],
            "unknown_future_evidence": [e.id for e in evidence_future],
            "events": [e.model_dump(mode="json") for e in events],
            "ms": _ms(t0),
        }

    def get_evidence(self, entity_id: str | None = None, system_as_of: str | None = None) -> dict[str, Any]:
        t0 = perf_counter()
        day = _parse_date(system_as_of, date(2025, 7, 15))
        items = [e for e in demo.EVIDENCE if e.system_start <= day]
        if entity_id:
            items = [e for e in items if e.entity_id == entity_id or entity_id in e.id]
        return {
            "tool": "get_evidence",
            "count": len(items),
            "records": [e.model_dump(mode="json") for e in items[:12]],
            "ms": _ms(t0),
        }

    def get_control_status(self, control_id: str = "CC6.1", as_of: str | None = None) -> dict[str, Any]:
        t0 = perf_counter()
        state = self.reconstruct_historical_state(as_of or "2025-07-15")
        row = next((c for c in state["controls"] if c["id"] == control_id or control_id in c["name"]), None)
        return {"tool": "get_control_status", "control": row, "as_of": as_of, "ms": _ms(t0)}

    def analyze_compliance(self, question: str, as_of: str | None = None) -> dict[str, Any]:
        t0 = perf_counter()
        agent_log("AGENT", "Evidence synthesis started")
        day = as_of or "2025-07-15"
        state = self.reconstruct_historical_state(day)
        q = question.lower()
        if "between" in q and "may 15" in q and "june 25" in q:
            a = self.reconstruct_historical_state("2025-05-15")
            b = self.reconstruct_historical_state("2025-06-25")
            return {
                "tool": "analyze_compliance",
                "kind": "diff",
                "may_15": {"status": a["label"], "mfa": "disabled", "test": "failed", "finding": "open"},
                "june_25": {"status": b["label"], "mfa": "enabled", "test": "passed", "finding": "remediated"},
                "ms": _ms(t0),
            }
        if "unresolved" in q or "open" in q:
            open_f = [f for f in demo.FINDINGS if f.status == "open"]
            return {"tool": "analyze_compliance", "kind": "gaps", "findings": [f.model_dump(mode="json") for f in open_f], "ms": _ms(t0)}
        return {
            "tool": "analyze_compliance",
            "kind": "posture",
            "label": state["label"],
            "status": state["compliance_status"],
            "reason": "MFA was disabled for one production IAM group." if state["label"] == "PARTIALLY COMPLIANT" else state["label"],
            "future_excluded": state["unknown_future_evidence"],
            "ms": _ms(t0),
        }

    def dispatch(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        import inspect

        fn = getattr(self, name, None)
        if not callable(fn) or name.startswith("_"):
            return {"error": f"unknown tool {name}"}
        allowed = set(inspect.signature(fn).parameters)
        kwargs = {k: v for k, v in (arguments or {}).items() if k in allowed}
        return fn(**kwargs)


GROQ_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": name,
            "description": desc,
            "parameters": {
                "type": "object",
                "properties": props,
            },
        },
    }
    for name, desc, props in [
        ("search_neo4j", "Search the compliance knowledge graph", {"query": {"type": "string"}, "valid_as_of": {"type": "string"}, "system_as_of": {"type": "string"}}),
        ("get_entity", "Fetch one graph entity by id", {"entity_id": {"type": "string"}}),
        ("traverse_compliance_graph", "Walk relationships from a control or requirement", {"start_id": {"type": "string"}}),
        ("search_hindsight", "Recall long-term memories", {"query": {"type": "string"}, "valid_as_of": {"type": "string"}, "system_as_of": {"type": "string"}}),
        ("reconstruct_historical_state", "Bitemporal reconstruction for a date YYYY-MM-DD", {"as_of": {"type": "string"}}),
        ("get_evidence", "List evidence known at system time", {"entity_id": {"type": "string"}, "system_as_of": {"type": "string"}}),
        ("analyze_compliance", "Synthesize posture/gaps/diff from retrieved evidence", {"question": {"type": "string"}, "as_of": {"type": "string"}}),
        ("get_control_status", "Status of a control at a date", {"control_id": {"type": "string"}, "as_of": {"type": "string"}}),
    ]
]
