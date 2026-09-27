# 30 — Project structure

Caches omitted (`node_modules`, `.next`, `__pycache__`, `.venv`, Neo4j volume).

```
VERICHRON AI/
  .env.example
  docker-compose.yml
  README.md
  backend/
    Dockerfile
    requirements.txt
    app/
      main.py                 # FastAPI app, CORS, /api router
      config.py               # Settings
      logging_util.py
      api/routes.py           # HTTP API
      agents/pipeline.py      # ComplianceAgent
      agents/tools.py         # AgentToolbox + GROQ_TOOLS
      services/factory.py
      services/neo4j_service.py
      services/hindsight_service.py
      services/llm_service.py
      models/schemas.py
      data/acme.py            # Demo graph + memories
      data/demo.py            # Re-export
      ingestion/pipeline.py
      neo4j/schema.cypher     # Sample (different ids)
      neo4j/seed.py
      hindsight/__init__.py
  frontend/
    Dockerfile
    package.json
    src/app/                  # App Router pages
    src/components/layout/AppShell.tsx
    src/components/graph/GraphCanvas.tsx
    src/lib/api.ts
    src/lib/state.tsx
  project-docs/               # This documentation package
```

Optional `docs/architecture.md` may exist at repo root from earlier README; **this package is the complete current-implementation set.**
