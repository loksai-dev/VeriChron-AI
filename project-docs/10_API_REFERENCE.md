# 10 — API reference

Router prefix `/api` (`backend/app/main.py`). **Authentication: none.**

Root: `GET /` → `{name, tagline}`.

| Method | Path | Purpose | Request | Response | File |
| --- | --- | --- | --- | --- | --- |
| GET | `/api/health` | Dependency connectivity | — | neo4j/hindsight/groq connected\|disconnected, demo_mode, seeded_nodes | routes.py `health` |
| GET | `/api/system-status` | Service modes | — | `SystemStatus` | `system_status` |
| POST | `/api/ingest` | JSON ingest | `IngestRequest` | pipeline dict | `ingest_json` |
| POST | `/api/ingest/upload` | File ingest | multipart file | same | `ingest_upload` |
| POST | `/api/query` | Agent (blocking) | `QueryRequest` | `AgentAnswer` | `query` |
| POST | `/api/query/stream` | Agent SSE | `QueryRequest` | `text/event-stream` | `query_stream` |
| POST | `/api/audit/reconstruct` | Time machine payload | `ReconstructRequest` | reconstruction dict | `reconstruct` |
| POST | `/api/compliance/analyze` | Alias of query | `QueryRequest` | `AgentAnswer` | `analyze` |
| GET | `/api/controls` | Control catalog | — | `demo.CONTROLS` (not Neo4j) | `controls` |
| GET | `/api/findings` | Findings; optional `?id=` | query | list or one | `findings` |
| GET | `/api/evidence` | Evidence; optional `?kind=` | query | list | `evidence` |
| GET | `/api/timeline` | Time machine events | `valid_as_of`, `system_as_of` (default **2026-03-15**) | events + all | `timeline` |
| GET | `/api/graph` | Graph snapshot | dates, `types` | GraphPayload + cypher | `graph_all` |
| GET | `/api/graph/{entity_id}` | Neighborhood | dates | graph + entity | `graph_entity` |
| GET | `/api/mental-models` | Memory layers | — | models, observations, facts | `mental_models` |
| POST | `/api/mental-models/{model_id}/refresh` | Refresh MM | — | MentalModel or 404 | `refresh_model` |
| GET | `/api/agent-runs` | Recent runs | — | `AgentRun[]` | `agent_runs` |
| GET | `/api/agent/runs/{run_id}` | Run detail | — | index dict or 404 | `agent_run` |
| GET | `/api/neo4j/stats` | Node counts | — | stats() | `neo4j_stats` |
| GET | `/api/overview` | Dashboard metrics | — | hardcoded 0.91 + demo | `overview` |
| POST | `/api/demo/seed` | Re-seed Neo4j | — | seeded_nodes | `seed` |
| GET | `/api/demo/narrative` | Demo copy | — | acts + questions | `narrative` |

`QueryRequest`: `question`, optional `valid_as_of`, `system_as_of`, `framework` default `"SOC 2"`.

`ReconstructRequest`: required `valid_as_of`, `system_as_of`.

## curl examples

```bash
curl -s http://localhost:8000/api/health

curl -s -X POST http://localhost:8000/api/query ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"Why was CC6.1 non-compliant in May 2025?\",\"valid_as_of\":\"2025-05-15\",\"system_as_of\":\"2025-05-15\"}"

curl -s -N -X POST http://localhost:8000/api/query/stream ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"What was our compliance posture on May 15, 2025?\"}"

curl -s -X POST http://localhost:8000/api/audit/reconstruct ^
  -H "Content-Type: application/json" ^
  -d "{\"valid_as_of\":\"2025-05-15\",\"system_as_of\":\"2025-05-15\"}"
```
