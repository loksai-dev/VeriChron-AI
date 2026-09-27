# Hindsight memory proof (how to run; fill runtime rows when gateway is up)

Bank id (non-secret): value of `HINDSIGHT_BANK_ID` (UUID in local env, not committed here).

## A. Retain

```
POST /api/query
{"question":"Remember that the ACME MFA exception TOKEN_X was approved on June 20, 2025 because of legacy authentication."}
```

Expect `hindsight_retain` SSE, `live=true`, Cloud confirmation. Then `POST /api/memory/recall` with the token; expect `source=hindsight-cloud` and a memory id.

## B. Restart + recall

Restart uvicorn. Restart `openclaw gateway`. Repeat recall question. Expect observability recall IDs and (if gateway connected) OpenClaw completion that uses the reason.

## C. Clocks

Ask whether the exception changes CC6.1 at `valid_as_of=2025-05-15` `system_as_of=2025-05-01`. A June 20 approval must **not** be treated as known on May 1.

## Memory-disabled comparison

Assistant checkbox **Hindsight recall** off sends `memory_enabled: false` (fresh `verichron-nomem` user session). Same question, no observability recall inject. Compare traces; do not use canned copy as the only evidence.

## Status of this workspace after implementation

| Step | Result |
| --- | --- |
| Cloud retain/recall via FastAPI | Previously PASS in this repo (memory IDs on Cloud) |
| OpenClaw gateway `/v1/models` | See OPENCLAW_DEMO.md after `openclaw gateway` |
| Cross-restart + OpenClaw tool sequence | Unverified until gateway stays up |
