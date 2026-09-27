# 04 — Agent tools

Source: `backend/app/agents/tools.py`. Dispatch: `AgentToolbox.dispatch(name, arguments)` — unknown names return `{"error": "unknown tool ..."}`.

| Tool name | Purpose | Input | Output | Function | External dependency |
| --- | --- | --- | --- | --- | --- |
| `search_neo4j` | Keyword search on graph, bitemporal filter | `query`, `valid_as_of`, `system_as_of` | `{hits, as_of}` | `search_neo4j` | Neo4jService |
| `get_entity` | One node by id | `entity_id` | node dict or `{error}` | `get_entity` | Neo4jService |
| `traverse_compliance_graph` | BFS depth 4, allowed rels | `start_id` | `{start, hops}` | `traverse_compliance_graph` | Neo4jService |
| `search_hindsight` | Recall memories | `query`, `valid_as_of`, `system_as_of` | `{memories}` | `search_hindsight` | HindsightService.recall |
| `reconstruct_historical_state` | Posture + known vs occurred | `as_of` | reconstruction dict | `reconstruct_historical_state` | neo4j + hindsight |
| `get_evidence` | Evidence known at system date | `entity_id`, `system_as_of` | `{items}` | `get_evidence` | neo4j + hindsight |
| `analyze_compliance` | Gaps/posture/diff from reconstruct | `question`, `as_of` | synthesis dict | `analyze_compliance` | neo4j + hindsight (via reconstruct) |
| `get_control_status` | One control node as of date | `control_id`, `as_of` | `{control, as_of}` | `get_control_status` | Neo4jService |

`traverse_compliance_graph` calls `neo4j.graph("CC6.1", 2025-07-15, 2025-07-15)` then orders ids using `demo.CAUSAL_PATH`. Seed/write-time allowed relationship types live in `neo4j_service.ALLOWED_RELS` (includes IMPLEMENTS, SUPPORTS, RESOLVES, SUPERSEDES, CAUSES, EVALUATED_BY, …).

`GROQ_TOOLS` mirrors these eight names. `ComplianceAgent.iter_query` does not call an LLM tool loop.
