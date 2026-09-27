# OpenClaw setup (reproducible)

Pinned CLI observed here: **OpenClaw 2026.6.35** (`npx --yes openclaw --version`). Official Hindsight plugin docs target OpenClaw 2026.7–2026.9 for plugin 0.12.0 — treat version skew as a risk.

## Secrets (do not commit)

```
HINDSIGHT_API_KEY / HINDSIGHT_CLOUD_TOKEN   # Cloud token, SecretRef
GROQ_API_KEY
OPENCLAW_GATEWAY_TOKEN                      # gateway bearer
OPENCLAW_TOOL_TOKEN                         # FastAPI tool routes
HINDSIGHT_BANK_ID                           # same UUID in plugin bankId
```

## Commands

```powershell
npx --yes openclaw --version
npx --yes openclaw plugins install @vectorize-io/hindsight-openclaw
npx --yes --package @vectorize-io/hindsight-openclaw hindsight-openclaw-setup --mode cloud --token-env HINDSIGHT_API_KEY
npx --yes openclaw plugins install ./openclaw-plugin/verichron-openclaw
```

Copy `openclaw/openclaw.json.example` into `%USERPROFILE%\.openclaw\openclaw.json` (or `OPENCLAW_CONFIG_PATH`). Set:

- `gateway.http.endpoints.chatCompletions.enabled: true`
- `hindsight-openclaw.config.dynamicBankId: false`
- `hindsight-openclaw.config.bankId` = `HINDSIGHT_BANK_ID`
- `retainRoles: ["user"]` so assistant conclusions are not auto-retained as facts
- `enableKnowledgeTools: true`
- `agents.defaults.model.primary: groq/openai/gpt-oss-120b`
- `gateway.bind: loopback`
- `gateway.auth.mode: token` + env `OPENCLAW_GATEWAY_TOKEN`

Start:

```powershell
$env:GROQ_API_KEY="..."          # already in your shell, do not paste into git
$env:HINDSIGHT_API_KEY="..."
$env:OPENCLAW_GATEWAY_TOKEN="..."
npx --yes openclaw gateway --port 18789
npx --yes openclaw gateway status
curl.exe -sS http://127.0.0.1:18789/v1/models -H "Authorization: Bearer $env:OPENCLAW_GATEWAY_TOKEN"
```

Copy skill into the agent workspace configured in `openclaw.json`:

`openclaw/skills/verichron-compliance/SKILL.md`

## Docker

Keep Neo4j/backend/frontend in `docker-compose.yml`. Run OpenClaw on the **host loopback** (default bind). Do not publish 18789 to the internet. Containers reach Hindsight Cloud; they do not need the gateway unless you add a private network later.

## Rollback

`OPENCLAW_ENABLED=false` `OPENCLAW_LEGACY_FALLBACK=true`
