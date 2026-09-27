# 14 — Demo scenarios

Supported by `acme.py`, tools, `/assistant`, `/timeline`, `/graph`. Pass `valid_as_of` / `system_as_of` when asking historical questions (see 13).

## 1 — Posture on 15 May 2025

- **Question:** What was our compliance posture on May 15, 2025?
- **Behavior:** `_extract_as_of` → 2025-05-15. Reconstruct **PARTIALLY COMPLIANT**.
- **Tools:** full fixed plan + reflect.
- **Graph:** CC6.1 neighborhood (July 15 load for traverse).
- **Memory:** facts with system_start ≤ May 15; not `mem-upload-jul`.
- **Answer:** MFA off for one IAM group; July pack excluded (caveat).
- **UI:** Assistant trace; Timeline both clocks on 2025-05-15.

## 2 — Why CC6.1 non-compliant

- **Question:** Why was CC6.1 non-compliant during Q2 2025? (send dates 2025-05-15)
- **Behavior:** reflect root-cause IAM 2025-04-10; analyze posture.
- **Tools:** same plan.
- **Graph:** CAUSAL_PATH.
- **Answer:** PutGroupPolicy removed MFA; finding F-MFA.
- **UI:** Graph page + assistant.

## 3 — What changed May 15 vs June 25

- **Question:** What changed between May 15 and June 25?
- **Behavior:** `analyze_compliance` **diff** branch if question contains `between`, `may 15`, and `june 25`.
- **Expected:** May MFA disabled / test failed / finding open vs June enabled / passed / remediated.
- **UI:** Assistant; timeline scrub.

## 4 — Unresolved findings

- **Question:** Show unresolved compliance findings. / Find unresolved compliance gaps.
- **Behavior:** `analyze_compliance` gaps: **F-PAM**, **F-UAR** (`status==open`). F-MFA is remediated.
- **UI:** Findings page lists all three; agent emphasizes open two.

## 5 — Evidence for MFA remediation

- **Question:** What evidence supports the MFA remediation?
- **Behavior:** `get_evidence` (all known at system date); search_neo4j for MFA; EV-JIRA, EV-TEST-PASS, EV-PACK if system time is July 15.
- **May 15 system time:** EV-PACK not known; EV-JIRA and fail test are.
- **UI:** Evidence page + graph EVIDENCED_BY.

**Not supported as a separate product feature:** ISO 27001, multi-org, live ticket updates.
