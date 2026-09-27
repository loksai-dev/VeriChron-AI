# 18 — Configuration

Pydantic Settings (`backend/app/config.py`) reads `.env` from repo root or `backend/.env`. Extra env keys are ignored.

**Never commit real secrets. Values below are names only.**

| Variable | Default | Used for |
| --- | --- | --- |
| `DEMO_MODE` | `true` | Reported on `/api/health`. Does **not** skip Neo4j connection attempts. |
| `APP_ENV` | `development` | Stored; not a feature flag in routes |
| `CORS_ORIGINS` | `http://localhost:3000` | CORS allow list (comma-separated) |
| `GROQ_API_KEY` | empty | Enables `RealGroqService` when client constructs |
| `GROQ_REASONING_MODEL` | `openai/gpt-oss-120b` | Reasoning model id |
| `GROQ_FAST_MODEL` | `qwen/qwen3-32b` | Classify / faster calls |
| `NEO4J_URI` | `bolt://localhost:7687` | Bolt URI (Compose overrides to `bolt://neo4j:7687`) |
| `NEO4J_USER` | `neo4j` | Auth |
| `NEO4J_PASSWORD` | `password` | Auth — change in production; treat as `<REDACTED>` |
| `HINDSIGHT_URL` | `http://localhost:8888` | Health/recall/reflect HTTP |
| `HINDSIGHT_BANK_ID` | `verichron-compliance` | Bank id |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Browser API base |
| `API_INTERNAL_URL` | `http://backend:8000` | Docker frontend build/runtime (server-side if used) |

**Not implemented:** `HINDSIGHT_API_KEY`, JWT secrets, encryption keys.

`.env.example` lists `HINDSIGHT_URL=http://hindsight:8888` but Compose has **no** `hindsight` service — local default in Settings is localhost:8888.
