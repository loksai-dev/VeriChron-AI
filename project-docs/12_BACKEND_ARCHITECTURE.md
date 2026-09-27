# 12 — Backend architecture

FastAPI app `backend/app/main.py` version 1.1.0. Lifespan: `get_services()` (connect + optional Neo4j seed + Hindsight seed_bank).

```
routes.py
  ├─ ComplianceAgent (pipeline.py) ─ AgentToolbox (tools.py)
  │     ├─ neo4j_service
  │     ├─ hindsight_service
  │     └─ llm_service
  ├─ IngestionPipeline
  └─ demo/acme catalogs (direct for /controls, /findings, /evidence, /overview)
```

| Area | Module |
| --- | --- |
| Config | `config.py` Pydantic Settings |
| Models | `models/schemas.py` |
| Factory | `services/factory.py` |
| Neo4j | `services/neo4j_service.py` |
| Hindsight | `services/hindsight_service.py` |
| LLM | `services/llm_service.py` (Groq or mock) |
| Logging | `logging_util.py` |
| CORS | origins from `CORS_ORIGINS` plus `http://127.0.0.1:3000` and `http://frontend:3000` |

## Error handling

- Finding 404, mental-model 404, agent run 404
- Unknown tools return `{error}`
- Groq/Neo4j/Hindsight failures → mock or fallback
- No global exception handler / request IDs beyond agent logs
