# 17 — Hindsight operations

All examples from `MockHindsightService` (`hindsight_service.py`) unless a live server returns 200.

## retain

**Input:** content, context=`seed`, timestamp=`2025-04-10`, document_id=`mem-iam-apr`.

**Operation:** upsert `MemoryFact` into `MEMORY_FACTS`.

**Result:** `{id, status: retained, layer: raw_fact}`. Live path may add `live: {status, bank_id}`.

**Why:** durable narrative of the IAM change.

## recall

**Input:** query `CC6.1 May 15`, valid_as_of=2025-05-15, system_as_of=2025-05-15.

**Operation:** score + `visible_at`.

**Result:** facts without `mem-upload-jul`; observations with `system_start <= May 15`; up to two mental models (unfiltered by date).

**Why:** agent `search_hindsight` tool.

## reflect

**Input:** same May 15 query.

**Operation:** recall + hardcoded reflection paragraph.

**Result:** `{reflection, citations, ladder}`.

**Why:** shown as SSE tool `hindsight.reflect`; feeds `llm.reason`.

## mental model

**Input:** GET `/api/mental-models` or POST refresh `mm:soc2-cc61`.

**Operation:** `list_mental_models` / `refresh_mental_model` → `reflect(model.query)`.

**Result:** CC6.1 posture narrative including July pack warning.

**Why:** `/mental-models` UI.

**NOT IMPLEMENTED:** vector embeddings, Hindsight-native mental model HTTP CRUD (always mock objects).
