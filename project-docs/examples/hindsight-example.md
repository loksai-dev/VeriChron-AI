# Example: Hindsight retain → recall → reflect

## retain

Input: `HINDSIGHT_MEMORIES` item `mem-iam-apr`.

Result: `{ "id": "mem-iam-apr", "status": "retained", "layer": "raw_fact" }`.

## recall

Input: query `CC6.1`, valid_as_of=`2025-05-15`, system_as_of=`2025-05-15`.

Result includes facts whose `visible_at` holds. `mem-upload-jul` has `system_start=2025-07-15` → **absent**.

## reflect

Input: same query / May 15 date.

Result (mock): reflection stating PARTIALLY COMPLIANT, known April–May artifacts, not known July pack; `ladder`: mental_model → observation → raw_fact.

Live 200 JSON from `/v1/banks/verichron-compliance/reflect` replaces this only when `is_live()`.
