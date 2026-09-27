# OpenClaw / VeriChron tools

## Client tools on `/v1/chat/completions`

Declared in `backend/app/openclaw/client.py` `CLIENT_TOOLS` and executed in FastAPI (`tools_http.py`):

| Name | Required args | Behavior |
| --- | --- | --- |
| search_compliance_graph | tenant_id, valid_as_of, system_as_of | Parameterized Neo4j graph; empty on unknown id |
| traverse_control | tenant_id, dates, control_id | Bounded traversal; never injects CC6.1 |
| reconstruct_state | tenant_id, dates, control_id | `reconstruct_from_graph` |
| compare_states | tenant_id, first_valid_date, second_valid_date, system_as_of | ADDED/REMOVED/CHANGED |
| get_evidence | tenant_id, dates, control_id | Evidence + role |
| analyze_evidence | same | Conflicts disclosed |

Missing dates → HTTP 400 (no silent July 15). Tenant mismatch → 403.

No exec/shell/unrestricted Cypher.

## Hindsight plugin tools (official names)

When `enableKnowledgeTools: true` (docs):

- `agent_knowledge_recall` — `max_tokens`, `include_chunks` (no `max_results`)
- `agent_knowledge_reflect` — `budget` default `low`

Auto: `autoRecall`, `autoRetain` with `retainRoles: ["user"]`.

## Observability

FastAPI also calls existing `RealHindsightService.recall` **without retain** to attach memory IDs to the UI.
