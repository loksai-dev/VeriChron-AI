# 23 — Security

## Implemented

- Secrets intended via `.env` (not documented with real values here).
- CORS allow-list from `CORS_ORIGINS` plus two hardcoded local origins.
- Neo4j credentials from env (default password in example files).
- In-memory agent runs (lost on restart; not a security boundary).

## Not implemented (recommendations only)

| Control | Status |
| --- | --- |
| API authentication | NOT IMPLEMENTED |
| RBAC | NOT IMPLEMENTED |
| Tenant isolation | NOT IMPLEMENTED (single ACME bank/graph) |
| Memory isolation | NOT IMPLEMENTED (shared `MEMORY_FACTS`) |
| TLS termination | NOT IMPLEMENTED in Compose |
| PII redaction | NOT IMPLEMENTED |
| Audit log of who queried | PARTIAL (`AgentRun` in process memory) |
| Secret scanning in CI | NOT IMPLEMENTED |
| `HINDSIGHT_API_KEY` | NOT IMPLEMENTED |

Logging (`logging_util.py`) can print questions and tool summaries — **do not log production evidence to shared consoles**.

Treat default Neo4j `password` as a demo credential, not production.
