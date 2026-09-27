# OpenClaw integration plan (actual APIs)

Inspected 2026-09-27. Sources: https://docs.openclaw.ai/gateway/ , https://docs.openclaw.ai/gateway/openai-http-api , https://docs.openclaw.ai/gateway/tools-invoke-http-api , https://docs.openclaw.ai/plugins/building-plugins , https://hindsight.vectorize.io/sdks/integrations/openclaw , npm `@vectorize-io/hindsight-openclaw`.

## Current architecture (pre-change)

Next.js → FastAPI `/api/query` + `/api/query/stream` → `ComplianceAgent.iter_query` (planner + Groq + Neo4j + Cloud Hindsight HTTP). OpenClaw is **not** in the runtime path (`project-docs/01_PRODUCT_REQUIREMENTS.md`).

## Target architecture

```
Next.js
  → FastAPI (policy: tenant, dates, unknown control, remember retain)
    → OpenClaw Gateway 127.0.0.1:18789
         POST /v1/chat/completions  (must enable gateway.http.endpoints.chatCompletions)
         GET  /v1/models
         POST /tools/invoke         (health / sessions_list)
         Plugin @vectorize-io/hindsight-openclaw → Hindsight Cloud
         Plugin verichron-openclaw → FastAPI /api/internal/openclaw/tools/*
    → Observability recall via existing RealHindsightService (no second retain)
```

## Documented contracts (do not invent)

| Surface | Contract |
| --- | --- |
| Chat | `POST /v1/chat/completions`, model `openclaw` / `openclaw/default`, Bearer `OPENCLAW_GATEWAY_TOKEN` |
| Stream | SSE `data: {choices[0].delta}` then `data: [DONE]`; tool calls `finish_reason=tool_calls` |
| Session | `user` string or `x-openclaw-session-key` (not `subagent:`/`cron:`/`acp:`) |
| Model override | `x-openclaw-model` |
| Tools HTTP | `POST /tools/invoke` `{tool, args, sessionKey}` |
| Hindsight plugin | `openclaw plugins install @vectorize-io/hindsight-openclaw` then `npx --package @vectorize-io/hindsight-openclaw hindsight-openclaw-setup --mode cloud --token-env HINDSIGHT_CLOUD_TOKEN` |
| Knowledge tools | `enableKnowledgeTools` → `agent_knowledge_recall` / `agent_knowledge_reflect` (no `max_results`; use `max_tokens`, `include_chunks`) |
| Isolation | `dynamicBankId` + `dynamicBankGranularity` **or** `dynamicBankId: false` + `bankId` |
| Groq | OpenClaw provider `groq/` + `GROQ_API_KEY`; suggested `groq/openai/gpt-oss-120b` |
| Skills | workspace `SKILL.md` YAML frontmatter (AgentSkills) |
| Custom tools | `api.registerTool` + `openclaw.plugin.json` `contracts.tools` |

## Risks

- Chat Completions is **disabled by default**; config must set `gateway.http.endpoints.chatCompletions.enabled: true`.
- Plugin `bankId` must match FastAPI `HINDSIGHT_BANK_ID` or observability recall hits a different bank.
- autoRetain of assistant conclusions: set `retainRoles: ["user"]` so model output is not auto-verified as fact.
- Gateway bearer token is full operator access; bind loopback only.
- Groq “fast” aliases 404 on this account; pin `openai/gpt-oss-120b`.
- If gateway is down, **no silent mock**; 503 / honest disconnected unless `OPENCLAW_LEGACY_FALLBACK=true`.

## Files to add/modify

Add: `backend/app/openclaw/*`, `openclaw-plugin/verichron-openclaw/`, `openclaw/openclaw.json.example`, `openclaw/skills/verichron-compliance/SKILL.md`, tests, docs listed in the prompt.

Modify: `config.py`, `routes.py`, `factory.py`, `schemas.py`, `AppShell.tsx`, `activity/page.tsx`, `assistant/inner.tsx`, `.env.example`.

## Migration

1. Install OpenClaw CLI + Hindsight plugin + VeriChron tool plugin.
2. SecretRefs only: `HINDSIGHT_CLOUD_TOKEN`, `GROQ_API_KEY`, `OPENCLAW_GATEWAY_TOKEN`.
3. `OPENCLAW_ENABLED=true`. Rollback: `OPENCLAW_ENABLED=false` + `OPENCLAW_LEGACY_FALLBACK=true`.

## Acceptance tests

Gateway `/v1/models`; plugin inspect; retain unique token; restart FastAPI (gateway optional); recall; PAM-01 empty; date error; tenant filter; SSE types from actual chunks; memory-disabled session.
