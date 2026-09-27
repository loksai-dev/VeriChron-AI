from __future__ import annotations

import re
from typing import Any

KNOWN_CONTROLS = {"CC6.1", "PAM", "QAR", "SEC-MON", "REQ-CC6.1", "REQ-CC6.2", "REQ-CC7.1", "REQ-CC7.2"}
HYPHEN_ID = re.compile(r"\b([A-Z]{2,}(?:-[A-Z0-9.]+)+)\b")
ID_RE = re.compile(r"\b([A-Z]{2,}(?:-\d+(?:\.\d+)?)?|[A-Z]{2,}\d{2,})\b")


def extract_entity_id(question: str) -> str | None:
    hyphen = HYPHEN_ID.search(question)
    if hyphen:
        return hyphen.group(1)
    q = question.upper()
    for cid in ("CC6.1", "CC6.2", "CC7.1", "CC7.2", "PAM", "QAR", "SEC-MON"):
        if cid in q:
            return "SEC-MON" if cid == "SEC-MON" else cid
    m = ID_RE.search(question)
    if m:
        token = m.group(1)
        if token not in {"SOC", "IAM", "MFA", "AWS", "GRC", "API", "ACME", "NORTHSTAR"}:
            return token
    return None


def is_remember_intent(question: str) -> bool:
    q = question.lower().strip()
    return q.startswith("remember") or "remember that" in q or q.startswith("retain ")


def plan_tools(question: str, intent: str, entity_id: str | None) -> list[tuple[str, dict[str, Any]]]:
    """Select a subset of tools. Never force CC6.1 unless that entity is in the question."""
    q = question.lower()
    if is_remember_intent(question):
        return [("retain_memory", {"content": question, "context": "operator"})]

    start = None
    if entity_id and entity_id in KNOWN_CONTROLS:
        start = entity_id
    if not start:
        if "cc6.1" in q or "mfa" in q:
            start = "CC6.1"
        elif "pam" in q:
            start = "PAM"
        elif "uar" in q or "qar" in q or "access review" in q:
            start = "QAR"

    tools: list[tuple[str, dict[str, Any]]] = []
    need_memory = True
    need_graph = "graph" in q or "evidence" in q or "why" in q or "control" in q or "cc6" in q or "pam" in q or "finding" in q or "posture" in q or "policy" in q
    need_recon = "was" in q or "on " in q or "as of" in q or "posture" in q or "state" in q or "may" in q or "april" in q
    need_evidence = "evidence" in q or "prove" in q or "test" in q or "finding" in q or need_recon
    need_compare = "between" in q or "changed" in q or "diff" in q
    need_reflect = "learned" in q or "historically" in q or "pattern" in q or "recurring" in q

    if need_memory:
        tools.append(("search_hindsight", {"query": question}))
    if need_graph:
        tools.append(("search_neo4j", {"query": question}))
        if start:
            tools.append(("traverse_compliance_graph", {"start_id": start}))
        elif entity_id:
            tools.append(("get_entity", {"entity_id": entity_id}))
    if need_compare:
        tools.append(("compare_temporal_states", {"question": question}))
    elif need_recon:
        tools.append(("reconstruct_historical_state", {}))
    if need_evidence:
        tools.append(("get_evidence", {"entity_id": start} if start else {}))
    if need_reflect:
        tools.append(("reflect_memory", {"query": question}))
    if not tools:
        tools.append(("search_hindsight", {"query": question}))
        tools.append(("search_neo4j", {"query": question}))
    return tools
