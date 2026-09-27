# OpenClaw architecture (as implemented)

```
Next.js UI
    │  POST /api/query[/stream]
    ▼
FastAPI policy (dates, unknown control, tenant, explicit retain)
    │  OPENCLAW_ENABLED
    ▼
OpenClaw Gateway  (127.0.0.1:18789, documented APIs)
    GET  /v1/models
    POST /v1/chat/completions   ← agent run + Hindsight plugin hooks
    POST /tools/invoke
    │
    ├─ @vectorize-io/hindsight-openclaw  → Hindsight Cloud retain/recall/reflect
    └─ client function tools (same names) executed in FastAPI
           /api/internal/openclaw/tools/*
                → Neo4j + temporal_engine (no unrestricted Cypher)
```

## File paths

| Path | Role |
| --- | --- |
| `backend/app/openclaw/client.py` | Gateway HTTP client |
| `backend/app/openclaw/agent.py` | Investigation workflow + SSE |
| `backend/app/openclaw/tools_http.py` | Validated tools |
| `backend/app/api/routes.py` | Feature-flag routing |
| `openclaw-plugin/verichron-openclaw/` | Optional native plugin |
| `openclaw/skills/verichron-compliance/SKILL.md` | Agent skill |
| `openclaw/openclaw.json.example` | Gateway config template |

## Auth

FastAPI → gateway: `Authorization: Bearer $OPENCLAW_GATEWAY_TOKEN` (full operator per OpenClaw docs). Bind loopback only.

Plugin → FastAPI: `x-verichron-tool-token`.

## Rollback

`OPENCLAW_ENABLED=false` and `OPENCLAW_LEGACY_FALLBACK=true` restores `ComplianceAgent.iter_query` (labeled LEGACY on stream).
