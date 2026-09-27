# 15 — Demo data

Tenant: ACME (`org:acme`). Framework: SOC 2. Catalog: `backend/app/data/acme.py` (re-export `app.data.demo`).

## Timeline

| Date (valid) | Event | Entity | Valid | System | Evidence / notes |
| --- | --- | --- | --- | --- | --- |
| 2025-01-01 | MFA policy active | CC6.1 | 01-01 → 04-09 | 2025-01-01 | mem-mfa-jan |
| 2025-04-10 | IAM MFA disabled | AWS-IAM | 04-10 → 06-19 | 2025-04-10 | EV-CT-MFA |
| 2025-05-05 | Control test FAIL | CC6.1 | 05-05 | 2025-05-05 | EV-TEST-FAIL; snapshot system 05-05 |
| 2025-05-12 | Finding F-MFA | F-MFA | 05-12 → 06-20 | 2025-05-12 | EV-JIRA |
| 2025-05-15 | Partial posture | CC6.1 | 05-15 | 2025-05-15 | mem-posture-may |
| 2025-06-20 | IAM remediated | REM-MFA | 06-20 | 2025-06-20 | SEC-1842 done |
| 2025-06-25 | Control test PASS | CC6.1 | 06-25 | 2025-06-25 | EV-TEST-PASS |
| 2025-07-15 | Evidence uploaded | EV-PACK | valid 04-10→06-20 | **2025-07-15** | EV-PACK, EV-UAR, F-UAR system time |

`POSTURE_SERIES` is a synthetic score series for charts (72 on May 15, 90 on June 25).

## How data enters Neo4j

`RealNeo4jService.seed()` MERGE of `NODES`/`EDGES`. Mock service reads lists in memory.

## How data enters Hindsight

`seed_bank()` → `retain()` for each `HINDSIGHT_MEMORIES` item. `mem-upload-jul` special-cased for system time July 15.

Open findings remaining after MFA close: F-PAM (system 2025-06-01), F-UAR (system 2025-07-15).
