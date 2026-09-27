# 05 — Hindsight architecture

## What is implemented

Hindsight is abstracted as `HindsightService` in `backend/app/services/hindsight_service.py`.

| Layer | Storage | How it is filled |
| --- | --- | --- |
| RAW FACTS | `demo.MEMORY_FACTS` (`MemoryFact`) | Seed from `HINDSIGHT_MEMORIES`; `retain()` |
| OBSERVATIONS | `demo.OBSERVATIONS` | Static seed; recall returns first 4 filtered by `system_start` |
| MENTAL MODELS | `demo.MENTAL_MODELS` | Seed `mm:soc2-cc61`; `create_mental_model` / `refresh_mental_model` |

This is an **in-process analog** of vectorize-io Hindsight, not a running Hindsight container.

## Client and connection

`RealHindsightService`:

- `GET {HINDSIGHT_URL}/health` (2s timeout) via `httpx`
- Bank: `HINDSIGHT_BANK_ID` default `verichron-compliance`
- `retain`: tries `from hindsight import Hindsight` then `client.retain(bank_id=...)`; **always** also writes to mock
- `recall`: `POST /v1/banks/{bank_id}/recall` if `_ok`
- `reflect`: `POST /v1/banks/{bank_id}/reflect` if `_ok`

**No `HINDSIGHT_API_KEY` exists in `config.py`.**

Docker Compose does **not** start Hindsight. `.env.example` sets `HINDSIGHT_URL=http://hindsight:8888`, which will not resolve unless you add that service. Factory also tries `http://127.0.0.1:8888` and `http://localhost:8888`.

Typical health: `"hindsight": "disconnected"` while tools still work via mock.

## Bank IDs

Single bank string `verichron-compliance`. **No tenant isolation.**

## Operations

### retain

`MockHindsightService.retain`: upserts `MemoryFact`. Special case: `document_id == "mem-upload-jul"` forces `valid_start=2025-04-10`, `system_start=2025-07-15`.

### recall

Keyword scoring on tokens (`cc6.1`, `mfa`, `iam`, …) plus `visible_at` when both dates passed.

### reflect

Hand-written strings for May 15 / why / gaps; citations from recall. Ladder reported as `["mental_model", "observation", "raw_fact"]`.

### mental models

`list_mental_models` returns Python list. Refresh updates `content` from `reflect(model.query)`.

**Ingest bug / mismatch:** `IngestionPipeline` calls `refresh_mental_model("mm:soc2-access")` but seeded id is `mm:soc2-cc61`. Refresh after ingest usually no-ops (`except Exception: pass`).

## Error handling / fallback

Live HTTP failures fall through to `_mock.recall` / `_mock.reflect`. Mental-model APIs always use mock methods even on `RealHindsightService`.

## Conceptual ladder (product)

```
RAW FACTS (MEMORY_FACTS)
  ↓  (observations are seeded, not derived by an algorithm)
OBSERVATIONS
  ↓  (mental model text is authored / refreshed via reflect)
MENTAL MODELS
```

**PLANNED / NOT IMPLEMENTED:** automatic observation synthesis from facts; live Hindsight mental-model API.
