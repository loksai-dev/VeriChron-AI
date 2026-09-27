# Example: compliance answer

Typical `AgentAnswer` after May 15 posture question (field names from `schemas.py`):

```json
{
  "conclusion": "On 2025-05-15 ACME CC6.1 was PARTIALLY COMPLIANT because MFA was disabled for one production IAM group.",
  "compliance_status": "at_risk",
  "affected_controls": ["CC6.1", "REQ-CC6.1"],
  "evidence": [
    {
      "id": "EV-CT-MFA",
      "kind": "cloudtrail",
      "title": "CloudTrail MFA Events",
      "excerpt": "PutGroupPolicy on prod-admins removed MFA condition.",
      "confidence": 0.99
    }
  ],
  "root_cause": "IAM configuration change on 2025-04-10 disabled MFA.",
  "remediation": "Enable MFA / SEC-1842 (completed later, 2025-06-20).",
  "confidence": 0.9,
  "graph_path": ["REQ-CC6.1", "CC6.1", "AWS-IAM", "EV-CT-MFA", "EV-TEST-FAIL", "F-MFA", "SEC-1842", "REM-MFA"],
  "caveat": "Future evidence from 2025-07-15 (remediation pack / UAR CSV) is excluded from May 15 organizational knowledge."
}
```

Exact `conclusion` wording depends on Groq vs mock. Caveat is **hardcoded** when `as_of == 2025-05-15`. Graph path may still list REM-MFA because traverse uses July 15 graph — treat path as topology, not as-of membership.
