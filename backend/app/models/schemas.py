from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


Severity = Literal["critical", "high", "medium", "low", "info"]
ComplianceStatus = Literal["compliant", "non_compliant", "at_risk", "unknown", "remediated"]
EntityType = Literal[
    "Regulation",
    "Requirement",
    "Policy",
    "Control",
    "Infrastructure",
    "Evidence",
    "AuditFinding",
    "Remediation",
    "JiraTicket",
    "Person",
    "Organization",
]


class TemporalFields(BaseModel):
    valid_start: date
    valid_end: Optional[date] = None
    system_start: date
    system_end: Optional[date] = None
    source: str
    entity_id: str
    fact_type: str
    confidence: float = Field(ge=0, le=1)


class GraphNode(BaseModel):
    id: str
    type: EntityType
    name: str
    status: Optional[str] = None
    description: str = ""
    owner: Optional[str] = None
    framework: Optional[str] = None
    properties: dict[str, Any] = Field(default_factory=dict)
    valid_start: Optional[date] = None
    valid_end: Optional[date] = None
    system_start: Optional[date] = None
    system_end: Optional[date] = None
    sources: list[str] = Field(default_factory=list)


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    type: str
    valid_start: Optional[date] = None
    valid_end: Optional[date] = None
    system_start: Optional[date] = None
    system_end: Optional[date] = None


class GraphPayload(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    causal_path: list[str] = Field(default_factory=list)


class Control(BaseModel):
    id: str
    name: str
    requirement_id: str
    framework: str
    status: ComplianceStatus
    owner: str
    evidence_coverage: float
    description: str
    valid_start: date
    valid_end: Optional[date] = None
    system_start: date
    system_end: Optional[date] = None
    source: str
    confidence: float


class Finding(BaseModel):
    id: str
    title: str
    control_id: str
    severity: Severity
    detected: date
    valid_start: date
    valid_end: Optional[date] = None
    system_start: date
    system_end: Optional[date] = None
    status: str
    owner: str
    remediation_id: Optional[str] = None
    summary: str
    root_cause: str
    affected_controls: list[str]
    evidence_ids: list[str]
    source: str
    confidence: float


class Evidence(BaseModel):
    id: str
    title: str
    kind: Literal["cloudtrail", "jira", "policy", "control_test", "audit_report"]
    source: str
    timestamp: datetime
    valid_start: date
    valid_end: Optional[date] = None
    system_start: date
    system_end: Optional[date] = None
    entity_id: str
    content_hash: str
    confidence: float
    summary: str
    content: str


class TimelineEvent(BaseModel):
    id: str
    title: str
    description: str
    valid_start: date
    valid_end: Optional[date] = None
    system_start: date
    system_end: Optional[date] = None
    entity_id: str
    fact_type: str
    status: Optional[str] = None
    source: str
    confidence: float


class MentalModel(BaseModel):
    id: str
    name: str
    query: str
    content: str
    last_refreshed: datetime
    evidence_count: int
    confidence: float
    status: ComplianceStatus
    supporting_evidence: list[str]
    recent_changes: list[str]
    versions: list[dict[str, Any]]
    layer: Literal["mental_model"] = "mental_model"


class Observation(BaseModel):
    id: str
    content: str
    supporting_facts: list[str]
    confidence: float
    valid_start: date
    system_start: date
    layer: Literal["observation"] = "observation"


class MemoryFact(BaseModel):
    id: str
    content: str
    entity_id: str
    fact_type: str
    source: str
    valid_start: date
    valid_end: Optional[date] = None
    system_start: date
    system_end: Optional[date] = None
    confidence: float
    layer: Literal["raw_fact"] = "raw_fact"


class AgentStage(BaseModel):
    name: str
    latency_ms: int
    detail: str
    status: Literal["ok", "error", "skipped"] = "ok"


class AgentRun(BaseModel):
    id: str
    query: str
    started_at: datetime
    total_ms: int
    stages: list[AgentStage]
    status: str
    error: Optional[str] = None
    memory_retrievals: int = 0
    neo4j_queries: int = 0
    hindsight_recalls: int = 0
    reflect_ops: int = 0
    llm_calls: int = 0


class QueryRequest(BaseModel):
    question: str
    valid_as_of: Optional[date] = None
    system_as_of: Optional[date] = None
    framework: str = "SOC 2"


class ReconstructRequest(BaseModel):
    valid_as_of: date
    system_as_of: date
    framework: str = "SOC 2"


class IngestRequest(BaseModel):
    filename: str
    content: str
    mime_hint: Optional[str] = None
    source: str = "upload"


class SourceRef(BaseModel):
    id: str
    kind: str
    title: str
    excerpt: str
    confidence: float


class AgentAnswer(BaseModel):
    conclusion: str
    compliance_status: ComplianceStatus
    affected_controls: list[str]
    evidence: list[SourceRef]
    timeline: list[TimelineEvent]
    root_cause: Optional[str] = None
    remediation: Optional[str] = None
    confidence: float
    sources: list[str]
    graph_path: list[str] = Field(default_factory=list)
    known_at_query_time: bool = True
    caveat: Optional[str] = None
    run: Optional[AgentRun] = None


class OverviewMetrics(BaseModel):
    overall_compliance: float
    framework: str
    active_controls: int
    open_findings: int
    critical_findings: int
    pending_remediations: int
    evidence_coverage: float
    as_of: date


class GapCell(BaseModel):
    current: ComplianceStatus
    last_audit: ComplianceStatus
    evidence: Literal["complete", "partial", "missing"]
    finding: Optional[str] = None
    remediation: Optional[str] = None


class ControlGapRow(BaseModel):
    requirement_id: str
    name: str
    cells: GapCell


class ServiceStatus(BaseModel):
    name: str
    mode: Literal["mock", "live"]
    healthy: bool
    detail: str


class SystemStatus(BaseModel):
    demo_mode: bool
    services: list[ServiceStatus]
