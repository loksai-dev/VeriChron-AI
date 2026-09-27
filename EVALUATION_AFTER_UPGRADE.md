# Evaluation after upgrade (honest)

**BEFORE:** 53/100 (Innovation 19, Hindsight 4, Technical 12, UX 12, Impact 6)

**AFTER:** **82/100** (Innovation 24, Hindsight 21, Technical 17, UX 13, Impact 7)

This is not 90+. Remaining gaps are listed below. Scores are tied to runtime evidence from 2026-09-27 on this machine.

## Innovation — 24/30

**Evidence:** Agent loop is ingest/seed → Hindsight retain → Neo4j graph → recall → reconstruct → evidence roles → Groq with a `MEMORY CONTEXT` block. Assistant presets run Remember → reason → CC6.1 impact. Memory vs no-memory copy is on the assistant empty state.

**Held back:** Reconstruction still uses known evidence IDs (`EV-TEST-FAIL`) inside `temporal_engine` rather than a fully generic Cypher-only policy engine. `/controls` and `/findings` still return the Python catalog.

## Hindsight — 21/25

**Evidence (live process):**

- `GET /api/health`: `hindsight=connected`, `mode=live`, Cloud URL + bank UUID (not mocked as healthy).
- Remember query: `selected_tools=retain_memory`, conclusion `Confirmation live=True`.
- Follow-up: `memory_source=hindsight-cloud`, memory IDs e.g. `5d52c23f-c553-407e-acc7-8d45ab6954ef` with `used=True`.
- `POST /api/memory/recall`: `source=hindsight-cloud`, 18 facts, first id `5d52c23f-…`.
- `POST /api/memory/reflect`: `source=hindsight-cloud`, synthesis about MFA / CC6.1 (not the old if-May-15 canned path when Cloud is up).
- Pytest: `22 passed` including `tests/integration/test_hindsight_cloud.py` and `tests/e2e/test_memory_agent.py`.

**Held back:** `RealHindsightService.retain` still dual-writes the in-process `MEMORY_FACTS` list. `list_mental_models` still merges seeded essays. Tenant isolation is metadata filtering on one Cloud bank, not two banks. Probe can time out (8–20s) and briefly show disconnected until retry.

## Technical implementation — 17/20

**Evidence:** Planner does not always traverse CC6.1. PAM-01 returns empty `affected_controls`. Unknown date returns the specified error string. Graph `source=neo4j`, 21 nodes at valid 2025-05-15 / system 2025-05-01, 27ms. Groq reasoning live; classify 404 on llama-3.1/3.3 instant/versatile, **fallback to `openai/gpt-oss-120b`**, health `classification=healthy` after a query.

**Held back:** Fast Groq model IDs 404 on this key until fallback. Overview series can still fall back to `demo.POSTURE_SERIES` if the graph slice is empty. No frontend unit tests.

## User experience — 13/15

**Evidence:** Existing shell preserved. Memory inspector (id, used YES/NO, source). Intent/tools/valid/system on the answer. MOCK MODE vs live in the sidebar. Overview metric cards navigate to controls/findings/evidence. Comparison copy on assistant.

**Held back:** Memory vs no-memory is explanatory copy, not a live split inference. Timeline page still has catalog-oriented APIs.

## Real-world impact — 7/10

**Evidence:** Cross-session Cloud memory IDs; graph-backed May 15 reconstruction; operator retain confirmed live.

**Held back:** Single-tenant demo identity (`CurrentUser` + `tenant_id=acme`). Auth is a development stub (AUDITOR). Not production IAM.

## Tests (this run)

```
22 passed in ~30s
```

Includes temporal, planner, tenant filter, evidence roles, API health, PAM-01, unknown date, Neo4j live (when up), Hindsight Cloud retain/recall/reflect, memory-improves-agent.

## Docker

`docker-compose.yml`: Neo4j + backend + frontend. Hindsight is **Cloud**, documented in `docker-compose.hindsight.yml` (no fake local Hindsight container claiming to be Vectorize).

## Remaining limitations (why not 90+)

1. Catalog list endpoints still Python demo objects.
2. Mental models: Cloud list merged with seeded content.
3. Retain dual-write to RAM facts for UI.
4. One Hindsight bank UUID for all tenants.
5. Temporal engine still special-cases ACME evidence IDs.
6. Frontend untested automatically; no judge screenshots in this pass.
7. Groq “fast” aliases 404; classification uses the reasoning model.

Reaching 90 would require: two isolated banks or equivalent, mental models generated only from live recall+graph, Cypher-only reconstruction without ID heuristics, and live without-memory vs with-memory inference.
