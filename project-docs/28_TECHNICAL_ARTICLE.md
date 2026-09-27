# 28 — Technical article

## Problem

GRC systems answer “are we compliant now?” Internal audit asks “what did we know on 15 May?” Similarity search over the current corpus cannot enforce **system time**. A July evidence pack about an April outage will contaminate a May reconstruction unless the store records when the organization ingested it.

## Architecture

VeriChron is a Next.js console on FastAPI. `Services` in `factory.py` attaches live Neo4j, optional Hindsight HTTP, and Groq when they answer; otherwise in-process mocks. The ACME catalog in `acme.py` is the narrative spine.

## Hindsight

The integration is a protocol: `retain`, `recall`, `reflect`, mental models. Without a server, `MockHindsightService` stores `MemoryFact` rows and scores recall with keywords plus `visible_at`. Live mode POSTs `/v1/banks/{bank}/recall|reflect` and tries the `hindsight` SDK for retain. Mental-model objects remain in Python lists.

## Neo4j

Nodes are `:Entity` plus a type label. Seed MERGE from ACME. Queries in `RealNeo4jService` pull neighborhoods or the full graph, then Python applies bitemporal filters. The agent’s “search” is this graph fetch, not Elasticsearch.

## Bitemporal memory

Valid time: when the world was in that state. System time: when the fact entered ACME’s record. `EV-PACK` is valid from April but system-known 15 July. `visible_at` requires both clocks. `occurred_by` is a weaker filter (start dates only).

## Agent tools

Eight toolbox functions. The streaming path runs a **fixed** six-tool plan plus `reflect`, then one `llm.reason`. That is an engineering choice so the UI can stream tool cards immediately.

## Demo

ACME SOC 2 CC6.1: MFA disabled 10 April 2025, partial on 15 May, fixed 20 June, retested 25 June, pack uploaded 15 July. Open leftovers: PAM review and UAR evidence.

## Lessons learned

- Empty Neo4j at first run looks like a mock product; seed on empty graph.
- LLM-chosen tools can stall SSE; a deterministic plan is more demo-honest.
- Dual clocks only work if every artifact has `system_start`.
- Catalog REST endpoints that skip as-of will contradict the agent if you are not careful.

No benchmarks. Not production-ready (no auth, no tests, single tenant).
