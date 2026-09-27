# 20 — Local development

## Clone

Use your existing folder, e.g. `C:\Users\itslo\OneDrive\Desktop\VERICHRON AI`.

## Environment

1. Copy `.env.example` to `.env` at the repo root.
2. Set `GROQ_API_KEY` if you want live LLM (optional).
3. Keep `NEO4J_PASSWORD` aligned with Compose (`password` in the example file — treat as `<REDACTED>` if you change it).
4. For local uvicorn talking to Docker Neo4j: `NEO4J_URI=bolt://localhost:7687`.

## Option A — Docker (all)

```bash
docker compose up --build
```

- UI http://localhost:3000
- API http://localhost:8000/docs
- Neo4j http://localhost:7474 (`neo4j` / your password)
- Health http://localhost:8000/api/health

If graph empty: `POST http://localhost:8000/api/demo/seed`

## Option B — Split local

Terminal 1 — Neo4j (Docker only is enough):

```bash
docker compose up neo4j
```

Terminal 2 — API:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Terminal 3 — UI:

```bash
cd frontend
npm install
npm run dev
```

`--reload` is required so Python agent changes apply.

## Verify

```bash
curl http://localhost:8000/api/health
curl http://localhost:3000
```

`neo4j: connected` means Bolt worked. `hindsight: disconnected` is expected without a Hindsight server. `groq: disconnected` if no key.

## Demo

1. Open `/assistant`.
2. Ask: `What was our compliance posture on May 15, 2025?`
3. Open `/timeline`, keep 2025-05-15, reconstruct.
4. Open `/graph`.
5. Open Neo4j Browser and `MATCH (n:Entity) RETURN count(n)`.
