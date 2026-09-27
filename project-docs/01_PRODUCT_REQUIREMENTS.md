# 01 — Product requirements

Status is taken from running code, not the marketing brief.

## Functional

| ID | Requirement | Status | Evidence in code |
| --- | --- | --- | --- |
| FR-001 | Compliance question answering | **IMPLEMENTED** | `POST /api/query`, `POST /api/query/stream`; `ComplianceAgent.query` |
| FR-002 | Historical state reconstruction | **IMPLEMENTED** | `POST /api/reconstruct`; `reconstruct_historical_state`; `visible_at` / `occurred_by` |
| FR-003 | Evidence retrieval | **IMPLEMENTED** | `GET /api/evidence`; tool `get_evidence`; graph `EVIDENCED_BY` |
| FR-004 | Knowledge graph traversal | **IMPLEMENTED** | `search_neo4j`, `traverse_compliance_graph`, `GET /api/graph` |
| FR-005 | Hindsight memory retrieval | **PARTIAL** | `search_hindsight` / `recall`; live HTTP often `disconnected`; in-process bank always present |
| FR-006 | Agent tool execution | **IMPLEMENTED** | `AgentToolbox.dispatch`; SSE `tool_start` / `tool_end` |
| FR-007 | Bitemporal filtering | **IMPLEMENTED** | `valid_as_of` + `system_as_of` on graph search and memory recall |
| FR-008 | Audit finding analysis | **IMPLEMENTED** | Findings in demo + graph; `analyze_compliance`; `/findings` UI |
| FR-009 | Remediation tracking | **PARTIAL** | Graph: `REMEDIATED_BY`, Jira `JIRA-4412`; no dedicated remediation API or ticket lifecycle |
| FR-010 | Timeline exploration | **IMPLEMENTED** | `GET /api/timeline`; `/timeline` Time Machine UI |

## Non-functional

| Area | Status | Notes |
| --- | --- | --- |
| Latency | **PARTIAL** | Sequential tools + Groq `reason`; no SLO, no caching |
| Reliability | **PARTIAL** | Factory fallbacks to mock; no retries/circuit breakers |
| Observability | **PARTIAL** | `GET /api/health` reports neo4j/hindsight/groq/demo_mode; `GET /api/agent/runs`; no APM |
| Security | **NOT IMPLEMENTED** | No API auth, no RBAC; CORS `*` |
| Reproducibility | **PARTIAL** | Demo seed is deterministic; live Groq answers vary |
| Explainability | **IMPLEMENTED** | Tool traces, evidence list, `as_known_on` vs `as_occurred_on` |

## Explicitly out of current product

- OpenClaw as a dependency (**NOT IMPLEMENTED** — VeriChron is a custom FastAPI agent)
- Multi-tenant Hindsight banks per customer (**PLANNED**)
- Real Jira/CloudTrail connectors (**PARTIAL** ingest parsers exist; no live connectors)
