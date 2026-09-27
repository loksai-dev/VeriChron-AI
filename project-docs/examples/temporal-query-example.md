# Example: temporal query

**Reconstruct** `POST /api/audit/reconstruct`

```json
{
  "valid_as_of": "2025-05-15",
  "system_as_of": "2025-05-15",
  "framework": "SOC 2"
}
```

`reconstruct_historical_state("2025-05-15")`:

- Events with `occurred_by`: includes `t-iam`, `t-test-fail`, `t-finding`, `t-posture`. Excludes `t-fix` (valid_start 2025-06-20), `t-upload` (system_start July).
- `mfa_gap` true → label **PARTIALLY COMPLIANT**.
- `unknown_future_evidence`: ids with `system_start > 2025-05-15` (EV-PACK, EV-UAR, EV-TEST-PASS, …).

Repeat with `system_as_of=2025-07-15` and the same valid date: July pack is **known** even though the world on May 15 had not uploaded it — that is the bitemporal point (knowledge vs world). For “what did we know then”, keep both dates on May 15.
