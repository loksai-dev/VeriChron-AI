# Example: agent run

**Question:** `What was our compliance posture on May 15, 2025?`

**Dates:** valid_as_of=2025-05-15, system_as_of=2025-05-15 (from `_extract_as_of` or request).

## Tool calls (actual plan)

1. `search_neo4j` — query string, dates ISO. Output: node/relationship counts, `node_ids`, `cypher`, `source` mock|live.
2. `traverse_compliance_graph` — `start_id=CC6.1`. Output: `path` from `CAUSAL_PATH` intersection.
3. `search_hindsight` — memories array, `count`.
4. `reconstruct_historical_state` — `as_of=2025-05-15`. Output: `label=PARTIALLY COMPLIANT`, `known_evidence`, `unknown_future_evidence` including EV-PACK / EV-UAR.
5. `get_evidence` — records with `system_start <= 2025-05-15`.
6. `analyze_compliance` — `kind=posture`, reason MFA disabled.

Then `hindsight.reflect` — May 15 paragraph.

## Reasoning

`llm.reason` receives intent, dates, analysis, reconstruct subset, reflection, path.

## Final answer shape

`AgentAnswer.conclusion` (string), `compliance_status` often `at_risk` for this question, `caveat` about 2025-07-15, `graph_path` causal ids, `run.stages` named after tools.

SSE types: `run` → `thought` → `tool_start`/`tool_end` × N → `answer` → `done`.
