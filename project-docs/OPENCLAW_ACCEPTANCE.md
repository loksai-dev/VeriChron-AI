# OpenClaw acceptance (honest)

CLI version: **OpenClaw 2026.6.35**. Official plugin 0.12 docs list OpenClaw 2026.7–2026.9.

## Checklist

| # | Criterion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | OpenClaw gateway connected | **FAIL** | `openclaw gateway status`: Runtime stopped, `ECONNREFUSED 127.0.0.1:18789`, no prior `openclaw.json` until this session copied the example |
| 2 | Official Hindsight plugin on real Cloud | **UNVERIFIED** | Install command documented; plugin not confirmed loaded because gateway is not running |
| 3 | Unique memory survives restart | **PASS (FastAPI Cloud path)** | Prior Cloud retain/recall IDs; OpenClaw process restart **UNVERIFIED** |
| 4 | Recall changes the answer | **PASS (FastAPI+Cloud)** when Hindsight live; OpenClaw-orchestrated **UNVERIFIED** (skipped e2e while gateway down) |
| 5 | Different tool sequences | **PASS (policy + client tools)**; OpenClaw model selection **UNVERIFIED** |
| 6 | Neo4j/temporal stored records | **PASS** | `/api/internal/openclaw/tools/*` hits live Neo4j; dates required |
| 7 | Tenant isolation | **PASS (unit)** | `memories_for_tenant`; tool 403 on tenant mismatch |
| 8 | Next.js → FastAPI → OpenClaw | **FAIL** until gateway is up; FastAPI client + UI wired |
| 9 | Judge demo without mock fallbacks | **PARTIAL** | Disconnected OpenClaw returns an honest error, not mock graph/memory |
| 10 | Tests | **24 passed, 2 skipped** (`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`) | Skips: gateway models, memory-to-OpenClaw causality |

## Pytest

```
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest tests -q
# 24 passed, 2 skipped
```

## What was implemented without claiming the gateway is live

- Feature-flagged `/api/query` → `OpenClawInvestigationAgent`
- Documented HTTP client (`/v1/models`, `/v1/chat/completions`, `/tools/invoke`)
- Validated Neo4j tools (no silent dates, no CC6.1 for PAM-01)
- Skill + example `openclaw.json` + VeriChron plugin package
- UI: OpenClaw health, recall toggle, memory kind
- Legacy path only if `use_legacy_agent` or `OPENCLAW_LEGACY_FALLBACK`

## To turn FAIL #1 into PASS

Follow `project-docs/OPENCLAW_SETUP.md`, set `OPENCLAW_GATEWAY_TOKEN`, run `openclaw gateway --port 18789`, then `GET /api/health` must show `services.openclaw.status=connected`.
