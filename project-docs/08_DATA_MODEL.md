# 08 — Data model

Source of truth: `backend/app/models/schemas.py` + instances in `backend/app/data/acme.py`.

Temporal fields (where present): `valid_start`, `valid_end`, `system_start`, `system_end`.

## Entities that exist

| Entity | Purpose | Key properties | Relationships (from seed) | Example id |
| --- | --- | --- | --- | --- |
| Organization | Demo tenant | name ACME Corporation | (node only; no HAS_ORG edges) | `org:acme` |
| Regulation | Framework | SOC 2 | GOVERNS → requirements | `SOC2` |
| Requirement | TSC criterion | CC6.1 / CC6.2 / CC7.1 / CC7.2 | SATISFIED_BY → controls | `REQ-CC6.1` |
| Policy | Written policy | status, owner, valid window | IMPLEMENTS → control; SUPERSEDES old MFA policy | `POL-MFA` |
| Control | Operable control | status, owner, framework | DEPENDS_ON infra; EVIDENCED_BY | `CC6.1` |
| Infrastructure | Tech | AWS IAM, EKS, SSO, CloudTrail | (targets of DEPENDS_ON) | `AWS-IAM` |
| Evidence | Artifact | kind, hash, summary | EVIDENCED_BY / SUPPORTS | `EV-CT-MFA` |
| AuditFinding | Finding | severity, status | VIOLATES control; REMEDIATED_BY; CAUSES | `F-MFA` |
| Remediation | Fix work | status, owner | RESOLVES finding; EVIDENCED_BY Jira | `REM-MFA` |
| JiraTicket | Ticket | SEC-1842 | ENABLES remediation | `SEC-1842` |
| Person | Owner identity | Priya Shah | (no OWNS edges in seed) | `person:priya` |

## Catalog models (API lists, not always graph)

`Control`, `Finding`, `Evidence`, `TimelineEvent`, `MentalModel`, `Observation`, `MemoryFact` — used by REST list endpoints and the agent.

## Example (Control CC6.1)

- Purpose: MFA enforcement on production IAM
- Status in catalog (today): `remediated`
- valid_start 2025-01-01; system_start 2025-01-01
- Edges: SATISFIED_BY from REQ-CC6.1; DEPENDS_ON AWS-IAM and SSO
