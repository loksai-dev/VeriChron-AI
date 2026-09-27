# 07 — Bitemporal model

Two clocks on graph nodes, edges, evidence, findings, memories, and timeline events (`TemporalFields` / per-entity fields in `schemas.py`).

| Clock | Fields | Meaning in this product |
| --- | --- | --- |
| **VALID TIME** | `valid_start`, `valid_end` | When the fact was true in the world |
| **SYSTEM TIME** | `system_start`, `system_end` | When ACME’s system of record knew it |

`None` end date means still open.

## Filters

`demo.in_interval(start, end, as_of)` — inclusive range.

`demo.visible_at(obj, valid_as_of, system_as_of)` — **both** clocks must contain the query dates.

`demo.occurred_by` — used for timeline reconstruction (world events that had occurred by valid time **and** were known by system time). Inspect `acme.py` for the exact implementation.

## Historical queries

- Graph UI / `GET /api/graph`: `visible_at` on nodes and edges.
- Timeline API: `visible_at` on `TIMELINE`.
- Agent `reconstruct_historical_state`: `occurred_by` for events; `visible_at` for evidence with **the same date** for both clocks (`day, day`).
- Hindsight recall: `visible_at` on facts when both dates provided.

## Example: 15 May 2025

Assume `valid_as_of = system_as_of = 2025-05-15`.

**What was actually true (valid time)?** MFA gap from 2025-04-10 IAM change; failed test 2025-05-05; finding 2025-05-12. Control test PASS (2025-06-25) and IAM fix (2025-06-20) have not occurred yet.

**What did the system know?** Artifacts with `system_start <= 2025-05-15`: CloudTrail (`EV-CT-MFA` 2025-04-10), snapshot (`EV-IAM-SNAP` 2025-05-05), fail test, Jira ticket. Not known: `EV-PACK` and `EV-UAR` (`system_start` 2025-07-15), finding `F-UAR`.

**What evidence existed later?** July 15 GRC upload (`EV-PACK`) describes the April–June gap (`valid_start` 2025-04-10) but must not appear in May 15 **knowledge**.

Agent caveat on May 15 questions (hardcoded in `pipeline.py`):

> Future evidence from 2025-07-15 (remediation pack / UAR CSV) is excluded from May 15 organizational knowledge.

## How future contamination is prevented

1. Filter by `system_start` / `system_end` whenever `visible_at` is used.
2. `mem-upload-jul` memory has `system_start=2025-07-15`.
3. Reconstruct lists `unknown_future_evidence` where `system_start > day`.

**Limitations:** `traverse_compliance_graph` loads the graph at **2025-07-15** always, so neighborhood Cypher is **not** bitemporal. Catalog APIs (`/controls`, `/findings`, `/evidence`) ignore as-of. Reconstruction uses demo Python lists, not only Neo4j.
