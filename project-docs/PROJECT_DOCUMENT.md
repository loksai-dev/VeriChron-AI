# VeriChron AI — project document (actual implementation)

## WHAT

VeriChron is a **bitemporal compliance assistant**: Next.js console + FastAPI agent that answers what was *true* (valid time), what the organization *knew* (system time), and what it has *remembered* (Hindsight), grounded in a Neo4j graph of ACME SOC 2 CC6.1.

## WHY

GRC tools answer “now.” Auditors need “what was true on 15 May 2025 given what we knew on 1 May,” plus durable memory of exceptions and corrections across sessions.

## HOW

1. Ingest/seed ACME catalog into Neo4j (`POST /api/demo/seed`).
2. Seed/retain memories into **Hindsight Cloud** (`POST /v1/default/banks/{id}/memories`).
3. User query → `ComplianceAgent` plans tools (not a fixed CC6.1 script).
4. `search_hindsight` recall → **MEMORY CONTEXT** in Groq `reason()`.
5. Neo4j graph + `reconstruct_from_graph` for bitemporal visibility.
6. Answer + run trace (`/api/agent/runs/{id}`).

## HINDSIGHT

- Client: `RealHindsightService` (Bearer API key).
- Live retain / recall / reflect. Mock is **not** labeled healthy.
- `POST /api/memory/retain|recall|reflect` returns 503 if not live.
- Remember-intent uses `retain_memory` only.
- Recall empty/error does **not** silently swap in canned mock facts when Cloud is connected.

## NEO4J

- Live Bolt graph with temporal properties and extra edges: EVALUATED_BY, AFFECTS, CONTRADICTS, HAS_VERSION, DOCUMENTS.
- Reconstruction uses `neo4j.graph()` + `temporal_engine.reconstruct_from_graph`, not `demo.TIMELINE` as source of truth.

## BITEMPORAL

- `valid_as_of` and `system_as_of` remain separate query parameters.
- Historical language without a parseable date returns an explicit error (no silent July 15).
- Unspecified non-historical queries use the demo current snapshot 2025-07-15 (stated in the agent thought, not a hidden date substitution).

## AGENT

- `planner.plan_tools` selects a subset of tools from intent.
- Unknown ids (e.g. PAM-01) return “No matching control…” with empty `affected_controls`.
- Groq classify model: `llama-3.1-8b-instant` (avoids prior qwen3 404). Health splits reasoning vs classification.

## DEMO

Assistant presets: Remember MFA exception → ask reason → ask CC6.1 impact. Time machine May 15 vs knowledge dates.

## IMPACT

Persistent Cloud memory + graph + time-machine reconstruction. Limitations: one Cloud bank UUID (tenant isolation is metadata filtering), list APIs `/controls` `/findings` still serve the Python catalog, mental models still merge Cloud + seeded essays.
