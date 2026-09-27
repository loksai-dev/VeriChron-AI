# 21 — Testing

Pytest lives at repo root (`pytest.ini`, `pythonpath = backend`).

```
pip install -r backend/requirements.txt
pytest tests -q
```

| File | What it proves |
| --- | --- |
| `tests/test_temporal.py` | Date parse; historical language without date errors; valid/system stay distinct when both provided |
| `tests/test_planner.py` | Remember-only plan; PAM entity; evidence tools |
| `tests/test_graph_and_tenant.py` | Unknown id; bank naming; reconstruct source neo4j-graph |
| `tests/test_evidence.py` | CONTRADICTING role; compare ADDED/CHANGED |
| `tests/test_tenant.py` | ACME vs NORTHSTAR memory filter |
| `tests/test_groq.py` | Fast model is not qwen3-32b; classify works without key via mock fallback |
| `tests/test_api.py` | Health JSON shape; PAM-01 empty controls; unknown date message |
| `tests/integration/test_hindsight_cloud.py` | Live retain/recall/reflect (skips without `HINDSIGHT_API_KEY`) |
| `tests/e2e/test_memory_agent.py` | Remember then ask reason (skips if Hindsight down) |

Frontend: no Jest suite in this repo. Manual: assistant Memory inspector, overview metric clicks.

Docker: `docker compose up` for Neo4j/API/UI. Hindsight is Cloud (`.env`), not a local container.
