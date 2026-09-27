# 22 — Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `/api/health` neo4j disconnected; graph still works | MockNeo4jService; `is_live()` is false | Start Neo4j; restart backend so factory reconnects |
| Empty Neo4j Browser | Seed never ran or Bolt failed at startup | `POST /api/demo/seed`; wait for Neo4j health; restart backend |
| Docker backend starts before Neo4j | `depends_on` without condition | Retry `docker compose restart backend` |
| hindsight disconnected | No Hindsight service; `.env` points at `http://hindsight:8888` | Ignore for demo (in-process bank) or run Hindsight locally on 8888 |
| groq disconnected / shallow answers | Empty `GROQ_API_KEY` or model error | Set key; confirm Groq model ids still valid |
| Invalid API key | Groq 401 | Replace key; factory falls back to mock |
| Agent always July 15 | Question lacks `May 15` and body dates omitted | Send `valid_as_of` or use UI defaults |
| July pack appears in May answer | system_as_of after 2025-07-15 | Set both clocks to 2025-05-15 |
| Traverse shows remediations in May story | `traverse_compliance_graph` loads graph at 2025-07-15 | Use reconstruct/evidence tools for as-of; treat path as illustration |
| Upload does not refresh mental model | Refresh id `mm:soc2-access` vs `mm:soc2-cc61` | Refresh from `/mental-models` with the real id |
| Frontend compile / blank assistant | Broken `api.ts` export | Ensure `export const api = {` exists |
| CORS errors | Origin not in list | Add to `CORS_ORIGINS` |
| uvicorn --reload not used | Docker CMD has no reload | Local uvicorn `--reload` or rebuild image |
| `hindsight` Python import fails | Not in `requirements.txt` | Live retain uses httpx; Python SDK retain is optional |
