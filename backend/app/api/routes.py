from datetime import date
from typing import Optional
import json

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse

from app.data import demo
from app.models.schemas import (
    ControlGapRow,
    GapCell,
    IngestRequest,
    OverviewMetrics,
    QueryRequest,
    ReconstructRequest,
)
from app.services.factory import get_services

router = APIRouter()
_agent = None
_ingest = None


def agent():
    global _agent
    if _agent is None:
        from app.agents.pipeline import ComplianceAgent

        _agent = ComplianceAgent(get_services())
    return _agent


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


@router.post("/ingest")
async def ingest_json(req: IngestRequest):
    return ingest().ingest(req)


@router.post("/ingest/upload")
async def ingest_upload(file: UploadFile = File(...)):
    raw = (await file.read()).decode("utf-8", errors="ignore")
    return ingest().ingest(IngestRequest(filename=file.filename or "upload.txt", content=raw, source="upload"))


@router.post("/query")
def query(req: QueryRequest):
    return agent().query(req.question, req.valid_as_of, req.system_as_of, req.framework)


@router.post("/query/stream")
def query_stream(req: QueryRequest):
    def events():
        for evt in agent().iter_query(req.question, req.valid_as_of, req.system_as_of, req.framework):
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
    return agent().runs


@router.get("/agent/runs/{run_id}")
def agent_run(run_id: str):
    item = agent().run_index.get(run_id)
    if not item:
        raise HTTPException(404, "Run not found")
    return item


@router.get("/neo4j/stats")
def neo4j_stats():
    return get_services().neo4j.stats()


@router.get("/overview")
def overview():
    open_findings = [f for f in demo.FINDINGS if f.status == "open"]
    return {
        "metrics": OverviewMetrics(
            overall_compliance=0.91,
            framework="SOC 2",
            active_controls=len(demo.CONTROLS),
            open_findings=len(open_findings),
            critical_findings=sum(1 for f in open_findings if f.severity == "critical"),
            pending_remediations=sum(1 for n in demo.NODES if n.type == "Remediation" and n.status != "complete"),
            evidence_coverage=0.88,
            as_of=demo.AS_OF_CURRENT,
        ),
        "series": demo.POSTURE_SERIES,
        "recent_changes": [e.model_dump(mode="json") for e in demo.TIMELINE[-4:]],
        "matrix": [
            ControlGapRow(requirement_id="CC6.1", name="Logical Access", cells=GapCell(current="remediated", last_audit="non_compliant", evidence="complete", finding="F-MFA", remediation="REM-MFA")),
            ControlGapRow(requirement_id="CC6.2", name="Credentials / PAM", cells=GapCell(current="at_risk", last_audit="compliant", evidence="partial", finding="F-PAM", remediation="REM-PAM")),
            ControlGapRow(requirement_id="CC7.1", name="Detection", cells=GapCell(current="compliant", last_audit="compliant", evidence="complete")),
            ControlGapRow(requirement_id="CC7.2", name="Monitoring", cells=GapCell(current="compliant", last_audit="compliant", evidence="complete")),
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
