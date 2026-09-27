# VeriChron AI — Upgrade plan (53 → 90+ target)

Inspected 2026-09-27 after Hindsight Cloud wiring. **Do not rebuild the UI.** Targeted backend + agent + tests + inspector.

## Current architecture

Next.js 14 console → FastAPI `/api` → `ComplianceAgent` → Neo4j (live) + Hindsight Cloud HTTP (live when `HINDSIGHT_API_KEY` set) + Groq.

## Defects (evaluator baseline)

| ID | Defect | Status at audit |
| --- | --- | --- |
| D1 | Hindsight mocked | Cloud retain/recall/reflect **live**; mock still dual-writes RAM |
| D2 | Chat does not retain “Remember…” | Agent turn retain exists; **no remember-intent tool** |
| D3 | Memory not in Groq | Snippets started; **must be labeled MEMORY CONTEXT** |
| D4 | Hardcoded reflect | Live HTTP if 200; mock if/else still exists |
| D5 | Hardcoded CC6.1 plan | Still always traverse CC6.1 |
| D6 | Reconstruct from `demo.TIMELINE` | Graph is live; reconstruct still Python lists |
| D7 | Silent date fallback | `_extract_as_of(..., July 15)` |
| D8 | Unknown control → CC6.1 | `affected_controls` hardcoded |
| D9 | Groq classify 404 | `qwen/qwen3-32b` |
| D10 | Hardcoded overview 0.91 | `routes.overview` |
| D11 | No tests | Missing |
| D12 | Mental models / UI mock vs live | Mixed |

## Planned fixes (this increment)

1. Planner: intent + entity + dates → subset of tools (retain-only for remember).
2. Temporal parser: no silent July 15; historical language without date → error.
3. Reconstruct/compare from **Neo4j `graph()`** (authoritative when live).
4. Memory REST + remember path; Groq SYSTEM_PROMPT **MEMORY CONTEXT**; used-in-answer IDs.
5. Groq classify model `llama-3.1-8b-instant`; health splits reasoning vs classification.
6. Overview from Neo4j stats + findings.
7. Graph extras: Exception, CONTRADICTS, EVALUATED_BY, tenant_id.
8. Tests (unit + Cloud integration skippable).
9. Assistant Memory Inspector; honest health.
10. Docs: PROJECT_DOCUMENT.md, EVALUATION_AFTER_UPGRADE.md.

## Files to modify

`pipeline.py`, `tools.py`, `llm_service.py`, `factory.py`, `config.py`, `routes.py`, `neo4j_service.py`, `hindsight_service.py`, `acme.py`, `schemas.py`, `assistant/inner.tsx`, `api.ts`, `AppShell.tsx`, `page.tsx`, `mental-models/page.tsx`, `.env.example`

## Files to add

`UPGRADE_PLAN.md`, `app/temporal.py`, `app/identity.py`, `app/agents/planner.py`, `app/services/temporal_engine.py`, `tests/`, `docker-compose.hindsight.yml`, `project-docs/PROJECT_DOCUMENT.md`, `EVALUATION_AFTER_UPGRADE.md`

## Migration

Keep ACME seed MERGE. Cloud bank already seeded. Re-seed Neo4j on new labels.

## Validation

`GET /api/health`, retain/recall/query runtime, `pytest tests -q`, Memory Inspector on assistant.
