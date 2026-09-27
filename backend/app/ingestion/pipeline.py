from __future__ import annotations

import csv
import json
import re
from datetime import date, datetime, timezone
from io import StringIO
from uuid import uuid4

from app.models.schemas import Evidence, GraphEdge, GraphNode, IngestRequest
from app.services.factory import Services


DATE_RE = re.compile(r"(20\d{2}-\d{2}-\d{2})")


def _guess_kind(filename: str, content: str) -> str:
    name = filename.lower()
    if name.endswith(".csv"):
        return "csv"
    if name.endswith(".json"):
        return "json"
    if "jira" in name or "SEC-" in content:
        return "jira"
    if "cloudtrail" in name or "eventName" in content:
        return "cloudtrail"
    if name.endswith(".md") or content.strip().startswith("#"):
        return "markdown"
    return "text"


def _dates(content: str) -> date:
    m = DATE_RE.search(content)
    if m:
        return date.fromisoformat(m.group(1))
    return date.today()


class IngestionPipeline:
    def __init__(self, services: Services):
        self.s = services

    def ingest(self, req: IngestRequest) -> dict:
        kind = req.mime_hint or _guess_kind(req.filename, req.content)
        parsed = self._parse(kind, req.content)
        entity_id = parsed.get("entity_id") or f"ingest:{uuid4().hex[:8]}"
        vs = parsed.get("valid_start") or _dates(req.content)
        node = GraphNode(
            id=entity_id,
            type=parsed.get("type", "Evidence"),
            name=parsed.get("name") or req.filename,
            description=parsed.get("summary") or req.content[:240],
            status="ingested",
            sources=[req.source],
            valid_start=vs,
            system_start=date.today(),
        )
        self.s.neo4j.write_node(node)
        if parsed.get("relates_to"):
            edge = GraphEdge(
                id=f"ing-e-{uuid4().hex[:6]}",
                source=parsed["relates_to"],
                target=entity_id,
                type=parsed.get("rel_type", "EVIDENCED_BY"),
                valid_start=vs,
                system_start=date.today(),
            )
            self.s.neo4j.write_edge(edge)

        evidence = Evidence(
            id=entity_id if entity_id.startswith("ev:") else f"ev:{uuid4().hex[:8]}",
            title=node.name,
            kind=parsed.get("evidence_kind", "audit_report"),
            source=req.source,
            timestamp=datetime.now(timezone.utc),
            valid_start=vs,
            system_start=date.today(),
            entity_id=parsed.get("relates_to") or entity_id,
            content_hash=f"sha256:{uuid4().hex[:12]}",
            confidence=0.8,
            summary=node.description,
            content=req.content[:4000],
        )
        from app.data import demo

        demo.EVIDENCE.append(evidence)

        retained = self.s.hindsight.retain(
            content=req.content[:8000],
            context=req.source,
            timestamp=vs.isoformat(),
            document_id=evidence.id,
            metadata={"entity_id": evidence.entity_id, "fact_type": "ingest", "filename": req.filename},
        )
        model = None
        try:
            model = self.s.hindsight.refresh_mental_model("mm:soc2-access")
        except Exception:
            pass

        return {
            "filename": req.filename,
            "parser": kind,
            "entity": node.model_dump(mode="json"),
            "evidence": evidence.model_dump(mode="json"),
            "hindsight": retained,
            "mental_model_refreshed": model.id if model else None,
            "pipeline": [
                "parser",
                "entity_extraction",
                "relationship_extraction",
                "temporal_extraction",
                "neo4j_write",
                "hindsight_retain",
                "observation",
                "mental_model_refresh",
            ],
        }

    def _parse(self, kind: str, content: str) -> dict:
        if kind == "json":
            try:
                data = json.loads(content)
                if isinstance(data, list):
                    data = data[0] if data else {}
                return {
                    "name": data.get("title") or data.get("eventName") or "JSON artifact",
                    "summary": json.dumps(data)[:240],
                    "entity_id": data.get("id"),
                    "relates_to": data.get("control_id") or "ctl:mfa",
                    "valid_start": date.fromisoformat(data["valid_start"]) if data.get("valid_start") else None,
                    "type": "Evidence",
                    "evidence_kind": "cloudtrail" if "eventName" in data else "audit_report",
                }
            except json.JSONDecodeError:
                pass
        if kind == "csv":
            reader = csv.DictReader(StringIO(content))
            row = next(reader, {})
            return {
                "name": row.get("title") or "CSV row",
                "summary": str(row)[:240],
                "relates_to": row.get("control_id") or "ctl:mfa",
                "type": "Evidence",
            }
        if kind == "jira":
            m = re.search(r"SEC-\d+", content)
            return {
                "name": m.group(0) if m else "Jira ticket",
                "summary": content.split("\n")[0][:240],
                "relates_to": "finding:cc6.1-q2",
                "type": "JiraTicket",
                "rel_type": "ENABLES",
                "evidence_kind": "jira",
            }
        if kind == "cloudtrail":
            return {
                "name": "CloudTrail event",
                "summary": content[:240],
                "relates_to": "infra:aws-iam",
                "type": "Evidence",
                "evidence_kind": "cloudtrail",
            }
        title = content.strip().split("\n")[0].lstrip("# ").strip() or "Document"
        return {
            "name": title[:80],
            "summary": content[:240],
            "relates_to": "ctl:mfa",
            "type": "Policy" if "policy" in content.lower() else "Evidence",
            "evidence_kind": "policy" if "policy" in content.lower() else "audit_report",
        }
