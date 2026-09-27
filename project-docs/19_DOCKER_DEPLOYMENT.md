# 19 — Docker deployment

File: `docker-compose.yml`. Services: **neo4j**, **backend**, **frontend**. No Hindsight container.

```bash
docker compose build
docker compose up
docker compose up --build
docker compose down
docker compose logs
docker compose logs backend
docker compose logs neo4j
```

| Service | Image / build | Ports | Notes |
| --- | --- | --- | --- |
| neo4j | `neo4j:5.26-community` | 7474, 7687 | `NEO4J_AUTH=neo4j/password`; volume `neo4j_data` |
| backend | `./backend` Dockerfile | 8000 | `env_file: .env`; `NEO4J_URI=bolt://neo4j:7687`; mounts `./backend/app` |
| frontend | `./frontend` multi-stage | 3000 | `NEXT_PUBLIC_API_URL=http://localhost:8000` (browser talks to host) |

## Health checks

- **neo4j:** `wget` spider `http://localhost:7474`
- **backend:** Python urllib `http://localhost:8000/api/health`
- **frontend:** none

`depends_on: neo4j` does **not** wait for the Neo4j healthcheck. Backend may start before Bolt is ready; factory retries several URIs at process start only (`lru_cache` — **no later reconnect** without restart).

Backend Dockerfile CMD: `uvicorn app.main:app --host 0.0.0.0 --port 8000` (**no `--reload`**). Frontend production: `node server.js` (standalone Next).
