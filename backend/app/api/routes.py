from datetime import date
from typing import Optional
import json

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse

from app.data import demo
from app.models.schemas import (
    CompareRequest,
    ControlGapRow,
    GapCell,
    IngestRequest,
    MemoryRecallRequest,
    MemoryRetainRequest,
    OverviewMetrics,
    QueryRequest,
    ReconstructRequest,
)
from app.services.factory import get_services

router = APIRouter()
_agent = None
_openclaw = None
_ingest = None


def legacy_agent():
    """Explicit legacy ComplianceAgent.iter_query path (not OpenClaw)."""
    global _agent
    if _agent is None:
        from app.agents.pipeline import ComplianceAgent

        _agent = ComplianceAgent(get_services())
    return _agent


def openclaw_agent():
    global _openclaw
    if _openclaw is None:
        from app.openclaw.agent import OpenClawInvestigationAgent
        from app.openclaw.client import OpenClawGatewayClient

        svc = get_services()
        _openclaw = OpenClawInvestigationAgent(svc, OpenClawGatewayClient(svc.settings))
    return _openclaw


def resolve_agent(req: QueryRequest):
    settings = get_services().settings
    if req.use_legacy_agent or (not settings.openclaw_enabled and settings.openclaw_legacy_fallback):
        return legacy_agent(), "legacy"
    if settings.openclaw_enabled:
        oc = openclaw_agent()
        if oc.client.health().get("status") == "connected":
            return oc, "openclaw"
        return legacy_agent(), "legacy-openclaw-down"
    if settings.openclaw_legacy_fallback:
        return legacy_agent(), "legacy"
    return None, "disabled"


def agent():
    return legacy_agent()


def ingest():
    global _ingest
    if _ingest is None:
        from app.ingestion.pipeline import IngestionPipeline

        _ingest = IngestionPipeline(get_services())
    return _ingest


@router.get("/health")
def health():
    return get_services().health_payload()


@router.get("/system-status")
def system_status():
    return get_services().system_status()


@router.post("/memory/retain")
def memory_retain(req: MemoryRetainRequest):
    h = get_services().hindsight
    if not getattr(h, "is_live", lambda: False)():
        raise HTTPException(503, "Hindsight is not connected (MOCK MODE is not used for this API)")
    return h.retain(req.content, context=req.context, timestamp=None, document_id=None, metadata={"source": "api"})


@router.post("/memory/recall")
def memory_recall(req: MemoryRecallRequest):
    h = get_services().hindsight
    if not getattr(h, "is_live", lambda: False)():
        raise HTTPException(503, "Hindsight is not connected")
    return h.recall(req.query, valid_as_of=req.valid_as_of, system_as_of=req.system_as_of)


@router.post("/memory/reflect")
def memory_reflect(req: MemoryRecallRequest):
    h = get_services().hindsight
    if not getattr(h, "is_live", lambda: False)():
        raise HTTPException(503, "Hindsight is not connected")
    return h.reflect(req.query, valid_as_of=req.valid_as_of, system_as_of=req.system_as_of)


@router.post("/audit/compare")
def audit_compare(req: CompareRequest):
    from app.agents.tools import AgentToolbox

    tools = AgentToolbox(get_services())
    return tools.compare_temporal_states(
        question="",
        valid_from=req.valid_from.isoformat(),
        valid_to=req.valid_to.isoformat(),
        system_as_of=(req.system_as_of or req.valid_to).isoformat(),
    )


@router.post("/ingest")
async def ingest_json(req: IngestRequest):
    return ingest().ingest(req)


@router.post("/ingest/upload")
async def ingest_upload(file: UploadFile = File(...)):
    raw = (await file.read()).decode("utf-8", errors="ignore")
    return ingest().ingest(IngestRequest(filename=file.filename or "upload.txt", content=raw, source="upload"))


@router.post("/query")
def query(req: QueryRequest):
    impl, mode = resolve_agent(req)
    if impl is None:
        raise HTTPException(503, "OpenClaw is the primary orchestrator and is disabled; legacy fallback is off.")
    if mode == "openclaw":
        return impl.query(req.question, req.valid_as_of, req.system_as_of, req.framework, memory_enabled=req.memory_enabled)
    return impl.query(req.question, req.valid_as_of, req.system_as_of, req.framework)


@router.post("/query/stream")
def query_stream(req: QueryRequest):
    impl, mode = resolve_agent(req)
    if impl is None:
        raise HTTPException(503, "OpenClaw is the primary orchestrator and is disabled; legacy fallback is off.")

    def events():
        kwargs = {}
        if mode == "openclaw":
            gen = impl.iter_query(req.question, req.valid_as_of, req.system_as_of, req.framework, memory_enabled=req.memory_enabled)
        else:
            note = (
                "OpenClaw gateway is disconnected. Using the live FastAPI agent (Neo4j + Hindsight Cloud + Groq). Not mock memory."
                if mode == "legacy-openclaw-down"
                else "LEGACY PATH: ComplianceAgent.iter_query (OpenClaw not used for this request)."
            )
            yield f"data: {json.dumps({'type': 'thought', 'text': note}, default=str)}\n\n"
            gen = impl.iter_query(req.question, req.valid_as_of, req.system_as_of, req.framework)
        for evt in gen:
            yield f"data: {json.dumps(evt, default=str)}\n\n"

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )


@router.post("/audit/reconstruct")
def reconstruct(req: ReconstructRequest):
    return agent().reconstruct(req)


@router.post("/compliance/analyze")
def analyze(req: QueryRequest):
    return agent().query(req.question, req.valid_as_of, req.system_as_of, req.framework)


@router.get("/controls")
def controls():
    return demo.CONTROLS


@router.get("/findings")
def findings(id: Optional[str] = None):
    if id:
        item = next((f for f in demo.FINDINGS if f.id == id), None)
        if not item:
            raise HTTPException(404, "Finding not found")
        return item
    return demo.FINDINGS


@router.get("/evidence")
def evidence(kind: Optional[str] = None):
    items = demo.EVIDENCE
    if kind:
        items = [e for e in items if e.kind == kind]
    return items


@router.get("/timeline")
def timeline(
    valid_as_of: date = Query(default=date(2026, 3, 15)),
    system_as_of: date = Query(default=date(2026, 3, 15)),
):
    events = [e for e in demo.TIMELINE if demo.visible_at(e, valid_as_of, system_as_of)]
    return {"valid_as_of": valid_as_of, "system_as_of": system_as_of, "events": events, "all": demo.TIMELINE}


@router.get("/graph")
def graph_all(
    valid_as_of: date = Query(default=date(2025, 7, 15)),
    system_as_of: date = Query(default=date(2025, 7, 15)),
    types: Optional[str] = None,
):
    t = types.split(",") if types else None
    svc = get_services().neo4j
    payload = svc.graph(None, valid_as_of, system_as_of, t)
    data = payload.model_dump(mode="json")
    data["cypher"] = getattr(svc, "last_cypher", "")
    data["execution_ms"] = getattr(svc, "last_ms", 0)
    data["source"] = getattr(svc, "source", "unknown")
    return data


@router.get("/graph/{entity_id}")
def graph_entity(
    entity_id: str,
    valid_as_of: date = Query(default=date(2025, 7, 15)),
    system_as_of: date = Query(default=date(2025, 7, 15)),
):
    svc = get_services().neo4j
    payload = svc.graph(entity_id, valid_as_of, system_as_of, None)
    entity = svc.get_entity(entity_id)
    data = payload.model_dump(mode="json")
    data["entity"] = entity.model_dump(mode="json") if entity else None
    data["cypher"] = getattr(svc, "last_cypher", "")
    data["execution_ms"] = getattr(svc, "last_ms", 0)
    data["source"] = getattr(svc, "source", "unknown")
    return data


@router.get("/mental-models")
def mental_models():
    h = get_services().hindsight
    return {
        "models": h.list_mental_models(),
        "observations": h.observations(),
        "facts": h.facts(),
    }


@router.post("/mental-models/{model_id}/refresh")
def refresh_model(model_id: str):
    try:
        return get_services().hindsight.refresh_mental_model(model_id)
    except KeyError:
        raise HTTPException(404, "Mental model not found")


@router.get("/agent-runs")
def agent_runs():
    settings = get_services().settings
    if settings.openclaw_enabled:
        try:
            return openclaw_agent().runs + legacy_agent().runs
        except Exception:
            return legacy_agent().runs
    return legacy_agent().runs


@router.get("/agent/runs/{run_id}")
def agent_run(run_id: str):
    item = None
    if get_services().settings.openclaw_enabled:
        item = openclaw_agent().run_index.get(run_id)
    if not item:
        item = legacy_agent().run_index.get(run_id)
    if not item:
        raise HTTPException(404, "Run not found")
    return item


@router.get("/neo4j/stats")
def neo4j_stats():
    return get_services().neo4j.stats()


@router.get("/overview")
def overview():
    svc = get_services()
    g = svc.neo4j.graph(None, date(2025, 7, 15), date(2025, 7, 15), None)
    controls = [n for n in g.nodes if n.type == "Control"]
    findings = [n for n in g.nodes if n.type == "AuditFinding"]
    evidence = [n for n in g.nodes if n.type == "Evidence"]
    remediations = [n for n in g.nodes if n.type == "Remediation"]
    open_findings = [f for f in findings if (f.status or "") not in {"remediated", "complete", "done"}]
    good = [c for c in controls if (c.status or "") in {"compliant", "remediated"}]
    overall = (len(good) / len(controls)) if controls else 0.0
    coverage = (len(evidence) / max(len(controls) * 2, 1))
    coverage = min(1.0, coverage)
    reqs = [n for n in g.nodes if n.type == "Requirement"]
    matrix = []
    for r in reqs:
        matrix.append(
            ControlGapRow(
                requirement_id=r.id,
                name=r.name,
                cells=GapCell(
                    current="unknown",
                    last_audit="unknown",
                    evidence="partial" if evidence else "missing",
                    finding=open_findings[0].id if open_findings else None,
                    remediation=remediations[0].id if remediations else None,
                ),
            )
        )
    live_facts = []
    try:
        live_facts = svc.hindsight.facts() or []
    except Exception:
        live_facts = []
    return {
        "metrics": OverviewMetrics(
            overall_compliance=round(overall, 2),
            framework="SOC 2",
            active_controls=len(controls),
            open_findings=len(open_findings),
            critical_findings=sum(1 for f in findings if "critical" in f"{f.name} {f.status}".lower()),
            pending_remediations=sum(1 for n in remediations if (n.status or "") != "complete"),
            evidence_coverage=round(coverage, 2),
            as_of=date(2025, 7, 15),
        ),
        "source": getattr(svc.neo4j, "source", "unknown"),
        "memory_count": len(live_facts),
        "evidence_count": len(evidence),
        "series": [
            {"date": n.valid_start.isoformat() if getattr(n, "valid_start", None) else "", "compliance": 70, "known": 65}
            for n in sorted((x for x in g.nodes if x.type == "Evidence" and x.valid_start), key=lambda x: x.valid_start)[:12]
        ]
        or demo.POSTURE_SERIES,
        "recent_changes": [
            {"id": n.id, "title": n.name, "valid_start": n.valid_start.isoformat() if n.valid_start else ""}
            for n in evidence[-4:]
        ],
        "matrix": matrix
        or [
            ControlGapRow(
                requirement_id=c.id,
                name=c.name,
                cells=GapCell(current="unknown", last_audit="unknown", evidence="partial"),
            )
            for c in controls[:6]
        ],
    }


@router.post("/demo/seed")
def seed():
    n = get_services().neo4j.seed()
    return {"seeded_nodes": n}


@router.get("/demo/narrative")
def narrative():
    return {
        "acts": [
            {"id": 1, "title": "Historical ingestion", "body": "Policies, CloudTrail, Jira and control tests populate Neo4j and Hindsight retain()."},
            {"id": 2, "title": "Gap discovery", "body": "Ask for unresolved gaps. Agent fuses graph + memory. Control gap matrix updates."},
            {"id": 3, "title": "Bitemporal proof", "body": "Set the time machine to 15 May 2025. Reconstruct what was true vs what was known."},
        ],
        "question_posture": "What was our compliance posture on May 15, 2025?",
        "question_why": "Why was CC6.1 non-compliant during Q2 2025?",
        "question_gaps": "Find unresolved compliance gaps.",
    }
