from __future__ import annotations

import json
from datetime import date
from time import perf_counter
from typing import Any, Callable

from app.data import demo
from app.identity import current_user, memories_for_tenant
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
        from app.agents.planner import extract_entity_id

        t0 = perf_counter()
        agent_log("NEO4J", "Query started")
        vd = _parse_date(valid_as_of, date(2025, 7, 15))
        sd = _parse_date(system_as_of, vd)
        entity = extract_entity_id(query or "")
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

    def traverse_compliance_graph(
        self,
        start_id: str,
        valid_as_of: str | None = None,
        system_as_of: str | None = None,
    ) -> dict[str, Any]:
        t0 = perf_counter()
        vd = _parse_date(valid_as_of, date(2025, 7, 15))
        sd = _parse_date(system_as_of, vd)
        payload = self.s.neo4j.graph(start_id, vd, sd, None)
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
        if not facts and recalled.get("results"):
            from app.services.hindsight_service import normalize_recall

            recalled = normalize_recall(recalled)
            facts = recalled.get("facts") or []
        facts = memories_for_tenant(facts, current_user().tenant_id)
        agent_log("HINDSIGHT", f"{len(facts)} memories returned source={recalled.get('source')}")
        return {
            "tool": "search_hindsight",
            "memories": facts[:12],
            "count": len(facts),
            "source": recalled.get("source"),
            "ms": _ms(t0),
        }

    def reconstruct_historical_state(
        self,
        as_of: str | None = None,
        valid_as_of: str | None = None,
        system_as_of: str | None = None,
    ) -> dict[str, Any]:
        from app.services.temporal_engine import reconstruct_from_graph

        t0 = perf_counter()
        vd = _parse_date(valid_as_of or as_of, date(2025, 7, 15))
        sd = _parse_date(system_as_of, vd)
        payload = self.s.neo4j.graph(None, vd, sd, None)
        out = reconstruct_from_graph(payload.nodes, vd, sd)
        later = self.s.neo4j.graph(None, date(2025, 12, 31), date(2025, 12, 31), None)
        known = {n.id for n in payload.nodes}
        out["unknown_future_evidence"] = [
            n.id for n in later.nodes if n.type == "Evidence" and n.id not in known
        ]
        out["cypher"] = getattr(self.s.neo4j, "last_cypher", "")
        out["ms"] = _ms(t0)
        return out

    def get_evidence(
        self,
        entity_id: str | None = None,
        system_as_of: str | None = None,
        valid_as_of: str | None = None,
    ) -> dict[str, Any]:
        from app.services.temporal_engine import classify_evidence_role

        t0 = perf_counter()
        vd = _parse_date(valid_as_of or system_as_of, date(2025, 7, 15))
        sd = _parse_date(system_as_of, vd)
        payload = self.s.neo4j.graph(entity_id, vd, sd, None) if entity_id else self.s.neo4j.graph(None, vd, sd, None)
        items = [n for n in payload.nodes if n.type == "Evidence"]
        records = []
        for n in items[:16]:
            records.append(
                {
                    **n.model_dump(mode="json"),
                    "role": classify_evidence_role(n, set()),
                }
            )
        return {"tool": "get_evidence", "count": len(records), "records": records, "ms": _ms(t0), "source": "neo4j"}

    def retain_memory(self, content: str, context: str = "operator") -> dict[str, Any]:
        t0 = perf_counter()
        text = content
        lower = content.lower()
        if lower.startswith("remember that"):
            text = content[len("Remember that") :].strip() if content[:1].isupper() else content.split(" ", 1)[-1]
            if lower.startswith("remember that"):
                idx = lower.find("remember that")
                text = content[idx + len("remember that") :].strip()
        out = self.s.hindsight.retain(
            content=text,
            context=context,
            timestamp=date.today().isoformat(),
            document_id=None,
            metadata={"tenant_id": current_user().tenant_id, "fact_type": "operator_retain"},
        )
        live = bool((out.get("live") or {}).get("ok")) if isinstance(out.get("live"), dict) else self.s.hindsight.is_live()
        return {"tool": "retain_memory", "retained": out, "live": live, "text": text, "ms": _ms(t0)}

    def reflect_memory(self, query: str, valid_as_of: str | None = None, system_as_of: str | None = None) -> dict[str, Any]:
        t0 = perf_counter()
        vd = date.fromisoformat(valid_as_of) if valid_as_of else None
        sd = date.fromisoformat(system_as_of) if system_as_of else None
        out = self.s.hindsight.reflect(query, valid_as_of=vd, system_as_of=sd)
        return {"tool": "reflect_memory", **out, "ms": _ms(t0)}

    def compare_temporal_states(
        self,
        question: str = "",
        valid_from: str | None = None,
        valid_to: str | None = None,
        system_as_of: str | None = None,
    ) -> dict[str, Any]:
        from app.services.temporal_engine import compare_graphs, reconstruct_from_graph
        from app.temporal import extract_dates_from_text

        t0 = perf_counter()
        dates = extract_dates_from_text(question)
        a = _parse_date(valid_from or (dates[0].isoformat() if dates else None), date(2025, 5, 15))
        b = _parse_date(valid_to or (dates[1].isoformat() if len(dates) > 1 else None), date(2025, 6, 25))
        sysd = _parse_date(system_as_of, b)
        g1 = self.s.neo4j.graph(None, a, a, None)
        g2 = self.s.neo4j.graph(None, b, sysd, None)
        diff = compare_graphs(g1.nodes, g2.nodes)
        r1 = reconstruct_from_graph(g1.nodes, a, a)
        r2 = reconstruct_from_graph(g2.nodes, b, sysd)
        return {
            "tool": "compare_temporal_states",
            "from": a.isoformat(),
            "to": b.isoformat(),
            "system_as_of": sysd.isoformat(),
            "diff": diff,
            "before": r1["label"],
            "after": r2["label"],
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
        ("retain_memory", "Persist an operator fact into Hindsight", {"content": {"type": "string"}, "context": {"type": "string"}}),
        ("reflect_memory", "Synthesize historical memory", {"query": {"type": "string"}}),
        ("compare_temporal_states", "Diff two valid-time states", {"question": {"type": "string"}, "valid_from": {"type": "string"}, "valid_to": {"type": "string"}}),
    ]
]
