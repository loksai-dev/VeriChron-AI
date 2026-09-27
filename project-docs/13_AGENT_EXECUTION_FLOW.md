# 13 — Agent execution flow

Question: **Why was CC6.1 non-compliant in May 2025?**

Implementation: `ComplianceAgent.iter_query` in `backend/app/agents/pipeline.py`.

## STEP 1 — Receive

SSE `run` with `run_id`. Thought: will use Neo4j, Hindsight, reconstruct; will not answer from memory alone.

## STEP 2 — Temporal scope

`llm.classify(question)`. `_extract_as_of` sees `may 15` **only if that substring is present**. The question “in May 2025” **does not** match `may 15`; fallback is **2025-07-15** unless the client sends `valid_as_of`.

For a correct May reconstruction the UI or curl **must** pass `"valid_as_of": "2025-05-15"`. Assistant `state.tsx` defaults dates to 2025-05-15.

If body dates are set: valid time = 2025-05-15; system time defaults to the same.

## STEP 3–8 — Tools (always this order)

| Step | Tool | Typical result |
| --- | --- | --- |
| 3 | `search_neo4j` | Hits CC6.1 neighborhood if query contains CC6.1/MFA |
| 4 | `traverse_compliance_graph` | Path from `CAUSAL_PATH`: REQ-CC6.1 → CC6.1 → AWS-IAM → EV-CT-MFA → EV-TEST-FAIL → F-MFA → SEC-1842 → REM-MFA. Graph loaded at **July 15**. |
| 5 | `search_hindsight` | Memories passing `visible_at`; July upload excluded if system_as_of is May 15 |
| 6 | `reconstruct_historical_state` | Label **PARTIALLY COMPLIANT** if IAM change occurred and fix has not (`t-iam` without `t-fix`) |
| 7 | `get_evidence` | Evidence with `system_start <= system_as_of` (plan does not pass `entity_id`) |
| 8 | `analyze_compliance` | `kind: posture` + MFA disabled reason when partial |

Then **STEP 8b** `hindsight.reflect` — canned May 15 root-cause text if dates/query match.

## STEP 9 — LLM

`llm.reason` with intent, dates, analysis, reconstruct snippet, reflection, path. Groq if live; else mock JSON with conclusion fields.

## STEP 10 — Final `AgentAnswer`

- `compliance_status` forced toward `at_risk` when reconstruct label is PARTIALLY COMPLIANT and question contains `may 15`
- `caveat` about July 15 evidence if `as_of == 2025-05-15`
- `affected_controls`: always `["CC6.1", "REQ-CC6.1"]`
- SSE `answer` + `done`

**Limitation:** without explicit dates or the phrase “May 15”, this question reconstructs **July 15** (compliant after remediations).
