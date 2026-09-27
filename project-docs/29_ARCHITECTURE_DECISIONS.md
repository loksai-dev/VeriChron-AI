# 29 — Architecture decisions

Status: **Accepted for this repository** unless noted.

## ADR-001 Hindsight for long-term memory

**Context:** Need retain/recall/reflect and a mental-model story for the hackathon brief.  
**Decision:** Implement `HindsightService` with mock bank + optional HTTP/SDK. Bank id `verichron-compliance`.  
**Reason:** Matches Hindsight vocabulary without blocking the demo on an extra container.  
**Alternatives:** Only Neo4j properties; LangChain memory; OpenClaw.  
**Tradeoffs:** Live Hindsight often disconnected; mental models not on the server.  
**Status:** Accepted (PARTIAL live).

## ADR-002 Neo4j for compliance relationships

**Context:** Controls, evidence, findings are relational, not bags of chunks.  
**Decision:** Neo4j 5 `:Entity` + type labels; Python ACME seed.  
**Reason:** Cypher neighborhood + typed edges (`VIOLATES`, `REMEDIATED_BY`).  
**Alternatives:** Postgres recursive CTE; RDF; only JSON.  
**Tradeoffs:** Temporal filter mostly in Python; Compose race on startup.  
**Status:** Accepted.

## ADR-003 Bitemporal model

**Context:** Reconstruct knowledge without future leakage.  
**Decision:** `valid_*` and `system_*` on entities; `visible_at` / `occurred_by`.  
**Reason:** Two questions: world vs books.  
**Alternatives:** Single event log; valid-time only.  
**Tradeoffs:** `occurred_by` ignores end dates; some APIs ignore as-of.  
**Status:** Accepted.

## ADR-004 Agent tool architecture

**Context:** Need visible tool calling like an operator agent.  
**Decision:** `AgentToolbox` + SSE from a hardcoded plan; Groq for final JSON.  
**Reason:** Streaming UX; avoid blocked `tool_choice` loops.  
**Alternatives:** Full Groq tools; LangGraph; OpenClaw.  
**Tradeoffs:** Plan always hits CC6.1; not a general planner.  
**Status:** Accepted.

## ADR-005 Groq model

**Context:** Need an LLM for classify/reason.  
**Decision:** `GROQ_API_KEY` + `openai/gpt-oss-120b` / `qwen/qwen3-32b`; mock JSON otherwise.  
**Reason:** Fast inference; demo works offline.  
**Alternatives:** OpenAI, local Ollama.  
**Tradeoffs:** Answers drift when live; list-shaped JSON coerced with `_as_text`.  
**Status:** Accepted.

## ADR-006 Docker-based local environment

**Context:** Judges need one command.  
**Decision:** Compose neo4j + backend + frontend.  
**Reason:** Repeatable ports 3000/8000/7474.  
**Alternatives:** Devcontainers; k8s.  
**Tradeoffs:** No Hindsight service; frontend image bakes `NEXT_PUBLIC_API_URL`.  
**Status:** Accepted.
