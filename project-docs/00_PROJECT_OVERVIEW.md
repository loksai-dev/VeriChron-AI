# 00 — Project overview

## One sentence

VeriChron AI is a desktop-first compliance console that reconstructs **what was true** (valid time) versus **what ACME recorded** (system time) using a Neo4j graph, an in-process Hindsight-style memory bank, and a tool-running agent.

## One paragraph

Auditors and GRC teams cannot answer “what was our SOC 2 posture on 15 May 2025?” from a chatbot that only sees today’s documents. VeriChron stores compliance entities as a typed graph and as timestamped memories. An agent (`ComplianceAgent` in `backend/app/agents/pipeline.py`) runs tools (`search_neo4j`, `search_hindsight`, `reconstruct_historical_state`, and others) then asks Groq—if a key is present—or a deterministic mock LLM to write a sourced assessment. The Next.js UI is an enterprise shell (overview, graph, time machine, streaming audit assistant). Demo tenant is **ACME Corporation**, framework **SOC 2**, primary control **CC6.1 MFA Enforcement**.

## Technical description

- **Frontend:** Next.js 14 App Router, Tailwind, React Flow, Recharts — `frontend/src/`.
- **Backend:** FastAPI — `backend/app/main.py`, routes in `backend/app/api/routes.py`.
- **Orchestration:** `Services` factory (`backend/app/services/factory.py`) chooses live Neo4j / Hindsight HTTP / Groq when they connect, otherwise mock implementations.
- **Catalog:** `backend/app/data/acme.py` (re-exported as `app.data.demo`).
- **Not in Docker Compose:** a Hindsight server. Compose runs `neo4j`, `backend`, `frontend` only.

## Problem

Traditional RAG retrieves similar text *now*. It does not distinguish world time from knowledge time, so later evidence (e.g. a 15 July 2025 upload) can leak into a May 15 reconstruction.

## Target users

Internal audit, GRC, security engineering, hackathon judges evaluating bitemporal compliance AI.

## Core use case

Reconstruct ACME’s CC6.1 posture on a chosen date, show agent tool traces, and prove July evidence is excluded from May 15 system time.

## Why RAG is insufficient

Similarity search has no first-class `valid_*` / `system_*` filters and no typed `VIOLATES` / `REMEDIATED_BY` edges.

## Why temporal reasoning

`demo.visible_at` / `demo.occurred_by` in `acme.py` implement two clocks so historical questions do not use future-known artifacts.

## Why a knowledge graph

Neo4j (or the in-memory graph) stores GOVERNS → SATISFIED_BY → DEPENDS_ON → EVIDENCED_BY → VIOLATES → REMEDIATED_BY.

## Why long-term memory

Hindsight-style layers (facts, observations, mental models) hold narrative memories (`HINDSIGHT_MEMORIES` in `acme.py`) with their own system_start (July pack is 2025-07-15).

## Component roles (actual)

| Piece | Role in this repo |
| --- | --- |
| Hindsight | `MockHindsightService` always; `RealHindsightService` if HTTP `/health` on `HINDSIGHT_URL` succeeds. Seed via `retain()`. Recall/reflect often stay on mock even when live HTTP fails. |
| Neo4j | `RealNeo4jService` when Bolt connects; MERGE seed of ACME nodes; `graph()` runs Cypher. |
| LLM | `RealGroqService` if `GROQ_API_KEY` constructs a client; else `MockLLMService`. Streaming agent loop uses a **fixed tool plan**; Groq is used for `reason()` / `classify()`, not for live tool selection in `iter_query`. |
| Agent | `ComplianceAgent.iter_query` / `query` / `reconstruct`. |
