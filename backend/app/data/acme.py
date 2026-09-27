from __future__ import annotations

from datetime import date, datetime, timezone

from app.models.schemas import (
    Control,
    Evidence,
    Finding,
    GraphEdge,
    GraphNode,
    MemoryFact,
    MentalModel,
    Observation,
    TimelineEvent,
)

ORG = "org:acme"
AS_OF_CURRENT = date(2025, 7, 15)


def d(y: int, m: int, day: int) -> date:
    return date(y, m, day)


def N(**kw) -> GraphNode:
    return GraphNode(**kw)


def E(**kw) -> GraphEdge:
    return GraphEdge(**kw)


NODES: list[GraphNode] = [
    N(id=ORG, type="Organization", name="ACME Corporation", description="Enterprise tenant for VeriChron SOC 2 demo.", status="active", sources=["seed"], valid_start=d(2018, 1, 1), system_start=d(2024, 11, 1)),
    N(id="SOC2", type="Regulation", name="SOC 2", framework="SOC 2", description="Trust Services Criteria — security.", status="in_scope", sources=["seed"], valid_start=d(2024, 1, 1), system_start=d(2024, 11, 1)),
    N(id="REQ-CC6.1", type="Requirement", name="CC6.1 Logical Access Controls", framework="SOC 2", description="Logical access security over protected information assets.", status="partial_may_2025", sources=["tsc"], valid_start=d(2024, 1, 1), system_start=d(2024, 11, 1)),
    N(id="REQ-CC6.2", type="Requirement", name="CC6.2 Credential Management", framework="SOC 2", description="Register and authorize users before issuing credentials.", status="compliant", sources=["tsc"], valid_start=d(2024, 1, 1), system_start=d(2024, 11, 1)),
    N(id="REQ-CC7.1", type="Requirement", name="CC7.1 Detection of Security Events", framework="SOC 2", description="Detect security events and anomalies.", status="at_risk", sources=["tsc"], valid_start=d(2024, 1, 1), system_start=d(2024, 11, 1)),
    N(id="REQ-CC7.2", type="Requirement", name="CC7.2 Monitoring", framework="SOC 2", description="Monitor system components for anomalies.", status="compliant", sources=["tsc"], valid_start=d(2024, 1, 1), system_start=d(2024, 11, 1)),
    N(id="POL-MFA", type="Policy", name="MFA Access Policy", description="Phishing-resistant MFA required for production IAM.", status="active", owner="Priya Shah", sources=["ev:policy-mfa"], valid_start=d(2025, 1, 1), valid_end=d(2025, 6, 30), system_start=d(2025, 1, 1)),
    N(id="POL-PAM", type="Policy", name="Privileged Access Policy", description="Privileged accounts reviewed quarterly; vaulted credentials.", status="active", owner="Marcus Lee", sources=["seed"], valid_start=d(2025, 1, 1), system_start=d(2025, 1, 15)),
    N(id="POL-UAR", type="Policy", name="User Access Review Policy", description="Managers attest production access each quarter.", status="active", owner="Jordan Hale", sources=["seed"], valid_start=d(2025, 1, 1), system_start=d(2025, 3, 1)),
    N(id="POL-IR", type="Policy", name="Incident Response Policy", description="24h containment SLA and annual tabletop.", status="active", owner="Riley Okonkwo", sources=["seed"], valid_start=d(2024, 6, 1), system_start=d(2024, 11, 1)),
    N(id="POL-MFA-2024", type="Policy", name="MFA Access Policy 2024", description="Superseded by 2025 MFA Access Policy.", status="superseded", sources=["seed"], valid_start=d(2024, 1, 1), valid_end=d(2024, 12, 31), system_start=d(2025, 1, 1)),
    N(id="CC6.1", type="Control", name="MFA Enforcement", description="SSO + AWS IAM MFA for production groups.", status="remediated", owner="Priya Shah", framework="SOC 2", sources=["ev:cloudtrail-mfa"], valid_start=d(2025, 1, 1), system_start=d(2025, 1, 1)),
    N(id="PAM", type="Control", name="Privileged Account Management", description="Vault and review of break-glass and admin roles.", status="at_risk", owner="Marcus Lee", framework="SOC 2", sources=["seed"], valid_start=d(2025, 1, 1), system_start=d(2025, 1, 15)),
    N(id="QAR", type="Control", name="Quarterly Access Review", description="Manager attestation of production access.", status="at_risk", owner="Jordan Hale", framework="SOC 2", sources=["ev:uar-csv"], valid_start=d(2025, 1, 1), system_start=d(2025, 3, 1)),
    N(id="SEC-MON", type="Control", name="Security Monitoring", description="CloudTrail + SIEM detections for IAM mutations.", status="compliant", owner="Sam Ortiz", framework="SOC 2", sources=["ev:siem-report"], valid_start=d(2024, 6, 1), system_start=d(2024, 11, 1)),
    N(id="AWS-IAM", type="Infrastructure", name="AWS IAM", description="Production account IAM groups and permission boundaries.", status="degraded_apr_2025", sources=["ev:iam-snapshot"], valid_start=d(2023, 1, 1), system_start=d(2024, 11, 1)),
    N(id="EKS-PROD", type="Infrastructure", name="Production Kubernetes", description="EKS production cluster with IRSA.", status="active", sources=["seed"], valid_start=d(2023, 6, 1), system_start=d(2024, 11, 1)),
    N(id="SSO", type="Infrastructure", name="Corporate SSO", description="Workforce IdP enforcing MFA factors for AWS.", status="active", sources=["seed"], valid_start=d(2022, 1, 1), system_start=d(2024, 11, 1)),
    N(id="CLOUDTRAIL", type="Infrastructure", name="CloudTrail", description="Organization trail with log-file validation.", status="active", sources=["ev:cloudtrail-mfa"], valid_start=d(2023, 1, 1), system_start=d(2024, 11, 1)),
    N(id="EV-CT-MFA", type="Evidence", name="CloudTrail MFA Events", description="PutGroupPolicy removing MFA condition on prod-admins.", status="verified", sources=["cloudtrail"], valid_start=d(2025, 4, 10), valid_end=d(2025, 6, 20), system_start=d(2025, 4, 10)),
    N(id="EV-IAM-SNAP", type="Evidence", name="IAM Configuration Snapshot", description="prod-admins without aws:MultiFactorAuthPresent.", status="verified", sources=["aws-config"], valid_start=d(2025, 4, 10), valid_end=d(2025, 6, 20), system_start=d(2025, 5, 5)),
    N(id="EV-UAR", type="Evidence", name="Access Review CSV", description="Q1 pack present; Q2 pack missing until July upload window.", status="partial", sources=["grc"], valid_start=d(2025, 1, 1), system_start=d(2025, 7, 15)),
    N(id="EV-SIEM", type="Evidence", name="Security Monitoring Report", description="SIEM detections for IAM policy mutations.", status="verified", sources=["siem"], valid_start=d(2025, 1, 1), system_start=d(2025, 2, 1)),
    N(id="EV-JIRA", type="Evidence", name="Jira Remediation Ticket", description="SEC-1842 restore MFA on prod-admins.", status="done", sources=["jira"], valid_start=d(2025, 5, 12), valid_end=d(2025, 6, 20), system_start=d(2025, 5, 12)),
    N(id="EV-TEST-FAIL", type="Evidence", name="CC6.1 Control Test FAIL", description="Automated MFA probe succeeded without second factor.", status="failed", sources=["grc"], valid_start=d(2025, 5, 5), system_start=d(2025, 5, 5)),
    N(id="EV-TEST-PASS", type="Evidence", name="CC6.1 Control Test PASS", description="Retest after IAM fix; console denied without MFA.", status="passed", sources=["grc"], valid_start=d(2025, 6, 25), system_start=d(2025, 6, 25)),
    N(id="EV-PACK", type="Evidence", name="Remediation evidence pack", description="Uploaded to GRC on 2025-07-15 documenting Apr–Jun MFA gap.", status="ingested", sources=["upload"], valid_start=d(2025, 4, 10), valid_end=d(2025, 6, 20), system_start=d(2025, 7, 15)),
    N(id="F-MFA", type="AuditFinding", name="MFA Disabled for Production IAM Group", description="prod-admins allowed password-only console access.", status="remediated", owner="Priya Shah", sources=["ev-test-fail"], valid_start=d(2025, 5, 12), valid_end=d(2025, 6, 20), system_start=d(2025, 5, 12), system_end=d(2025, 6, 25)),
    N(id="F-PAM", type="AuditFinding", name="Privileged Account Review Overdue", description="Q2 privileged review not completed.", status="open", owner="Marcus Lee", sources=["seed"], valid_start=d(2025, 6, 1), system_start=d(2025, 6, 1)),
    N(id="F-UAR", type="AuditFinding", name="Access Review Evidence Missing", description="Q2 UAR CSV not in the GRC system of record.", status="open", owner="Jordan Hale", sources=["seed"], valid_start=d(2025, 6, 15), system_start=d(2025, 7, 15)),
    N(id="REM-MFA", type="Remediation", name="Enable MFA", description="Re-apply MFA condition; remove exception group.", status="complete", owner="Priya Shah", sources=["EV-JIRA"], valid_start=d(2025, 6, 20), system_start=d(2025, 6, 20)),
    N(id="REM-PAM", type="Remediation", name="Complete Privileged Account Review", description="Finish Q2 PAM campaign.", status="in_progress", owner="Marcus Lee", sources=["seed"], valid_start=d(2025, 6, 1), system_start=d(2025, 6, 1)),
    N(id="REM-UAR", type="Remediation", name="Upload Access Review Evidence", description="Export Q2 CSV into VeriChron.", status="in_progress", owner="Jordan Hale", sources=["seed"], valid_start=d(2025, 6, 15), system_start=d(2025, 7, 15)),
    N(id="SEC-1842", type="JiraTicket", name="SEC-1842 Enable MFA", description="Restore aws:MultiFactorAuthPresent on prod-admins.", status="done", owner="Priya Shah", sources=["jira"], valid_start=d(2025, 5, 12), valid_end=d(2025, 6, 20), system_start=d(2025, 5, 12)),
    N(id="person:priya", type="Person", name="Priya Shah", description="Staff identity engineer.", status="active", sources=["hris"], valid_start=d(2021, 4, 1), system_start=d(2024, 11, 1)),
    N(id="EXC-MFA", type="Exception", name="MFA exception (legacy auth)", description="Approved June 20 2025 for remaining legacy authentication dependency. Affects CC6.1 residual risk.", status="approved", owner="Security", sources=["seed"], valid_start=d(2025, 6, 20), system_start=d(2025, 6, 20)),
    N(id="EV-CONFLICT", type="Evidence", name="Vendor attestation: MFA always on", description="Third-party letter claiming prod-admins always required MFA — contradicts CloudTrail and failed control test.", status="disputed", sources=["vendor"], valid_start=d(2025, 5, 1), system_start=d(2025, 5, 20)),
    N(id="AUD-Q2", type="Audit", name="Q2 2025 internal audit", description="Internal audit covering CC6.1 logical access.", status="closed", sources=["internal-audit"], valid_start=d(2025, 5, 1), system_start=d(2025, 5, 12)),
    N(id="POL-MFA-V2025", type="PolicyVersion", name="MFA Access Policy 2025 v1", description="Versioned policy artifact for POL-MFA.", status="active", sources=["seed"], valid_start=d(2025, 1, 1), valid_end=d(2025, 6, 30), system_start=d(2025, 1, 1)),
]

EDGES: list[GraphEdge] = [
    E(id="e-gov-61", source="SOC2", target="REQ-CC6.1", type="GOVERNS", valid_start=d(2024, 1, 1), system_start=d(2024, 11, 1)),
    E(id="e-gov-62", source="SOC2", target="REQ-CC6.2", type="GOVERNS", valid_start=d(2024, 1, 1), system_start=d(2024, 11, 1)),
    E(id="e-gov-71", source="SOC2", target="REQ-CC7.1", type="GOVERNS", valid_start=d(2024, 1, 1), system_start=d(2024, 11, 1)),
    E(id="e-gov-72", source="SOC2", target="REQ-CC7.2", type="GOVERNS", valid_start=d(2024, 1, 1), system_start=d(2024, 11, 1)),
    E(id="e-sat-mfa", source="REQ-CC6.1", target="CC6.1", type="SATISFIED_BY", valid_start=d(2025, 1, 1), system_start=d(2025, 1, 1)),
    E(id="e-sat-pam", source="REQ-CC6.2", target="PAM", type="SATISFIED_BY", valid_start=d(2025, 1, 1), system_start=d(2025, 1, 15)),
    E(id="e-sat-uar", source="REQ-CC6.2", target="QAR", type="SATISFIED_BY", valid_start=d(2025, 1, 1), system_start=d(2025, 3, 1)),
    E(id="e-sat-71", source="REQ-CC7.1", target="SEC-MON", type="SATISFIED_BY", valid_start=d(2024, 6, 1), system_start=d(2024, 11, 1)),
    E(id="e-sat-72", source="REQ-CC7.2", target="SEC-MON", type="SATISFIED_BY", valid_start=d(2024, 6, 1), system_start=d(2024, 11, 1)),
    E(id="e-impl-mfa", source="POL-MFA", target="CC6.1", type="IMPLEMENTS", valid_start=d(2025, 1, 1), system_start=d(2025, 1, 1)),
    E(id="e-impl-pam", source="POL-PAM", target="PAM", type="IMPLEMENTS", valid_start=d(2025, 1, 1), system_start=d(2025, 1, 15)),
    E(id="e-impl-uar", source="POL-UAR", target="QAR", type="IMPLEMENTS", valid_start=d(2025, 1, 1), system_start=d(2025, 3, 1)),
    E(id="e-impl-ir", source="POL-IR", target="SEC-MON", type="IMPLEMENTS", valid_start=d(2024, 6, 1), system_start=d(2024, 11, 1)),
    E(id="e-sup-mfa", source="POL-MFA", target="POL-MFA-2024", type="SUPERSEDES", valid_start=d(2025, 1, 1), system_start=d(2025, 1, 1)),
    E(id="e-dep-iam", source="CC6.1", target="AWS-IAM", type="DEPENDS_ON", valid_start=d(2025, 1, 1), system_start=d(2025, 1, 1)),
    E(id="e-dep-sso", source="CC6.1", target="SSO", type="DEPENDS_ON", valid_start=d(2025, 1, 1), system_start=d(2025, 1, 1)),
    E(id="e-dep-eks", source="PAM", target="EKS-PROD", type="DEPENDS_ON", valid_start=d(2025, 1, 1), system_start=d(2025, 1, 15)),
    E(id="e-dep-ct", source="SEC-MON", target="CLOUDTRAIL", type="DEPENDS_ON", valid_start=d(2024, 6, 1), system_start=d(2024, 11, 1)),
    E(id="e-ev-ct", source="CC6.1", target="EV-CT-MFA", type="EVIDENCED_BY", valid_start=d(2025, 4, 10), system_start=d(2025, 4, 10)),
    E(id="e-ev-snap", source="CC6.1", target="EV-IAM-SNAP", type="EVIDENCED_BY", valid_start=d(2025, 4, 10), system_start=d(2025, 5, 5)),
    E(id="e-ev-fail", source="CC6.1", target="EV-TEST-FAIL", type="EVIDENCED_BY", valid_start=d(2025, 5, 5), system_start=d(2025, 5, 5)),
    E(id="e-ev-pass", source="CC6.1", target="EV-TEST-PASS", type="EVIDENCED_BY", valid_start=d(2025, 6, 25), system_start=d(2025, 6, 25)),
    E(id="e-ev-pack", source="CC6.1", target="EV-PACK", type="EVIDENCED_BY", valid_start=d(2025, 4, 10), system_start=d(2025, 7, 15)),
    E(id="e-ev-uar", source="QAR", target="EV-UAR", type="EVIDENCED_BY", valid_start=d(2025, 1, 1), system_start=d(2025, 7, 15)),
    E(id="e-ev-siem", source="SEC-MON", target="EV-SIEM", type="EVIDENCED_BY", valid_start=d(2025, 1, 1), system_start=d(2025, 2, 1)),
    E(id="e-ev-jira", source="REM-MFA", target="EV-JIRA", type="EVIDENCED_BY", valid_start=d(2025, 5, 12), system_start=d(2025, 5, 12)),
    E(id="e-sup-ct", source="EV-CT-MFA", target="CC6.1", type="SUPPORTS", valid_start=d(2025, 4, 10), system_start=d(2025, 4, 10)),
    E(id="e-sup-fail", source="EV-TEST-FAIL", target="CC6.1", type="SUPPORTS", valid_start=d(2025, 5, 5), system_start=d(2025, 5, 5)),
    E(id="e-vio-mfa", source="F-MFA", target="CC6.1", type="VIOLATES", valid_start=d(2025, 5, 12), system_start=d(2025, 5, 12)),
    E(id="e-vio-pam", source="F-PAM", target="PAM", type="VIOLATES", valid_start=d(2025, 6, 1), system_start=d(2025, 6, 1)),
    E(id="e-vio-uar", source="F-UAR", target="QAR", type="VIOLATES", valid_start=d(2025, 6, 15), system_start=d(2025, 7, 15)),
    E(id="e-rem-mfa", source="F-MFA", target="REM-MFA", type="REMEDIATED_BY", valid_start=d(2025, 6, 20), system_start=d(2025, 6, 20)),
    E(id="e-rem-pam", source="F-PAM", target="REM-PAM", type="REMEDIATED_BY", valid_start=d(2025, 6, 1), system_start=d(2025, 6, 1)),
    E(id="e-rem-uar", source="F-UAR", target="REM-UAR", type="REMEDIATED_BY", valid_start=d(2025, 6, 15), system_start=d(2025, 7, 15)),
    E(id="e-res-mfa", source="REM-MFA", target="F-MFA", type="RESOLVES", valid_start=d(2025, 6, 20), system_start=d(2025, 6, 20)),
    E(id="e-cause", source="F-MFA", target="F-UAR", type="CAUSES", valid_start=d(2025, 6, 15), system_start=d(2025, 7, 15)),
    E(id="e-jira-en", source="SEC-1842", target="REM-MFA", type="ENABLES", valid_start=d(2025, 5, 12), system_start=d(2025, 5, 12)),
    E(id="e-eval-fail", source="CC6.1", target="EV-TEST-FAIL", type="EVALUATED_BY", valid_start=d(2025, 5, 5), system_start=d(2025, 5, 5)),
    E(id="e-eval-pass", source="CC6.1", target="EV-TEST-PASS", type="EVALUATED_BY", valid_start=d(2025, 6, 25), system_start=d(2025, 6, 25)),
    E(id="e-exc-aff", source="EXC-MFA", target="CC6.1", type="AFFECTS", valid_start=d(2025, 6, 20), system_start=d(2025, 6, 20)),
    E(id="e-contra", source="EV-CONFLICT", target="EV-TEST-FAIL", type="CONTRADICTS", valid_start=d(2025, 5, 1), system_start=d(2025, 5, 20)),
    E(id="e-ver", source="POL-MFA", target="POL-MFA-V2025", type="HAS_VERSION", valid_start=d(2025, 1, 1), system_start=d(2025, 1, 1)),
    E(id="e-audit", source="AUD-Q2", target="F-MFA", type="DOCUMENTS", valid_start=d(2025, 5, 12), system_start=d(2025, 5, 12)),
]

CAUSAL_PATH = ["REQ-CC6.1", "CC6.1", "AWS-IAM", "EV-CT-MFA", "EV-TEST-FAIL", "F-MFA", "SEC-1842", "REM-MFA"]

CONTROLS: list[Control] = [
    Control(id="CC6.1", name="MFA Enforcement", requirement_id="CC6.1", framework="SOC 2", status="remediated", owner="Priya Shah", evidence_coverage=0.95, description="Disabled 2025-04-10 through 2025-06-20 for prod-admins.", valid_start=d(2025, 1, 1), system_start=d(2025, 1, 1), source="control-catalog", confidence=0.99),
    Control(id="PAM", name="Privileged Account Management", requirement_id="CC6.2", framework="SOC 2", status="at_risk", owner="Marcus Lee", evidence_coverage=0.62, description="Q2 privileged review overdue.", valid_start=d(2025, 1, 1), system_start=d(2025, 1, 15), source="grc", confidence=0.88),
    Control(id="QAR", name="Quarterly Access Review", requirement_id="CC6.2", framework="SOC 2", status="at_risk", owner="Jordan Hale", evidence_coverage=0.55, description="Q2 CSV missing from GRC until July 15 system time.", valid_start=d(2025, 1, 1), system_start=d(2025, 3, 1), source="grc", confidence=0.86),
    Control(id="SEC-MON", name="Security Monitoring", requirement_id="CC7.2", framework="SOC 2", status="compliant", owner="Sam Ortiz", evidence_coverage=0.97, description="Org CloudTrail + SIEM IAM detections.", valid_start=d(2024, 6, 1), system_start=d(2024, 11, 1), source="siem", confidence=0.98),
]

FINDINGS: list[Finding] = [
    Finding(id="F-MFA", title="MFA Disabled for Production IAM Group", control_id="CC6.1", severity="critical", detected=d(2025, 5, 12), valid_start=d(2025, 5, 12), valid_end=d(2025, 6, 20), system_start=d(2025, 5, 12), system_end=d(2025, 6, 25), status="remediated", owner="Priya Shah", remediation_id="REM-MFA", summary="CC6.1 partially failed in May 2025 because prod-admins lost MFA.", root_cause="On 2025-04-10 IAM configuration removed MFA for one production group.", affected_controls=["CC6.1", "REQ-CC6.1"], evidence_ids=["EV-CT-MFA", "EV-IAM-SNAP", "EV-TEST-FAIL", "EV-JIRA"], source="internal-audit", confidence=0.98),
    Finding(id="F-PAM", title="Privileged Account Review Overdue", control_id="PAM", severity="high", detected=d(2025, 6, 1), valid_start=d(2025, 6, 1), system_start=d(2025, 6, 1), status="open", owner="Marcus Lee", remediation_id="REM-PAM", summary="Privileged review campaign not completed for Q2.", root_cause="Owner capacity after IAM incident.", affected_controls=["PAM"], evidence_ids=["EV-SIEM"], source="grc", confidence=0.9),
    Finding(id="F-UAR", title="Access Review Evidence Missing", control_id="QAR", severity="medium", detected=d(2025, 6, 15), valid_start=d(2025, 6, 15), system_start=d(2025, 7, 15), status="open", owner="Jordan Hale", remediation_id="REM-UAR", summary="Q2 access review CSV not in the system of record until July 15.", root_cause="Export not uploaded to GRC.", affected_controls=["QAR"], evidence_ids=["EV-UAR"], source="grc", confidence=0.87),
]

EVIDENCE: list[Evidence] = [
    Evidence(id="EV-CT-MFA", title="CloudTrail MFA Events", kind="cloudtrail", source="cloudtrail", timestamp=datetime(2025, 4, 10, 18, 11, tzinfo=timezone.utc), valid_start=d(2025, 4, 10), valid_end=d(2025, 6, 20), system_start=d(2025, 4, 10), entity_id="AWS-IAM", content_hash="sha256:ct-mfa-0410", confidence=0.99, summary="PutGroupPolicy on prod-admins removed MFA condition.", content="eventName=PutGroupPolicy group=prod-admins"),
    Evidence(id="EV-IAM-SNAP", title="IAM Configuration Snapshot", kind="control_test", source="aws-config", timestamp=datetime(2025, 5, 5, 9, 0, tzinfo=timezone.utc), valid_start=d(2025, 4, 10), valid_end=d(2025, 6, 20), system_start=d(2025, 5, 5), entity_id="AWS-IAM", content_hash="sha256:iam-snap", confidence=0.97, summary="Snapshot confirms MFA disabled for one production IAM group.", content="prod-admins: MultiFactorAuthPresent=false"),
    Evidence(id="EV-TEST-FAIL", title="CC6.1 control test FAIL", kind="control_test", source="grc", timestamp=datetime(2025, 5, 5, 14, 0, tzinfo=timezone.utc), valid_start=d(2025, 5, 5), system_start=d(2025, 5, 5), entity_id="CC6.1", content_hash="sha256:ct-fail", confidence=0.97, summary="Automated SOC 2 CC6.1 test detected MFA failure.", content="Result=FAIL"),
    Evidence(id="EV-TEST-PASS", title="CC6.1 control test PASS", kind="control_test", source="grc", timestamp=datetime(2025, 6, 25, 16, 0, tzinfo=timezone.utc), valid_start=d(2025, 6, 25), system_start=d(2025, 6, 25), entity_id="CC6.1", content_hash="sha256:ct-pass", confidence=0.99, summary="Control test passed after IAM fix.", content="Result=PASS"),
    Evidence(id="EV-JIRA", title="Jira Remediation Ticket", kind="jira", source="jira", timestamp=datetime(2025, 5, 12, 11, 0, tzinfo=timezone.utc), valid_start=d(2025, 5, 12), valid_end=d(2025, 6, 20), system_start=d(2025, 5, 12), entity_id="REM-MFA", content_hash="sha256:sec-1842", confidence=0.96, summary="SEC-1842 Enable MFA.", content="Done 2025-06-20"),
    Evidence(id="EV-UAR", title="Access Review CSV", kind="audit_report", source="grc", timestamp=datetime(2025, 7, 15, 10, 0, tzinfo=timezone.utc), valid_start=d(2025, 1, 1), system_start=d(2025, 7, 15), entity_id="QAR", content_hash="sha256:uar", confidence=0.9, summary="UAR file entered VeriChron on 2025-07-15.", content="q2-access-review.csv"),
    Evidence(id="EV-SIEM", title="Security Monitoring Report", kind="audit_report", source="siem", timestamp=datetime(2025, 2, 1, 0, 0, tzinfo=timezone.utc), valid_start=d(2025, 1, 1), system_start=d(2025, 2, 1), entity_id="SEC-MON", content_hash="sha256:siem", confidence=0.94, summary="IAM mutation detections healthy.", content="detections=ok"),
    Evidence(id="EV-PACK", title="Remediation evidence pack", kind="audit_report", source="upload", timestamp=datetime(2025, 7, 15, 10, 0, tzinfo=timezone.utc), valid_start=d(2025, 4, 10), valid_end=d(2025, 6, 20), system_start=d(2025, 7, 15), entity_id="CC6.1", content_hash="sha256:pack", confidence=0.92, summary="Evidence documenting the MFA gap uploaded 2025-07-15.", content="pack.pdf"),
]

TIMELINE: list[TimelineEvent] = [
    TimelineEvent(id="t-mfa-on", title="MFA policy active", description="MFA enforcement active for production IAM users.", valid_start=d(2025, 1, 1), valid_end=d(2025, 4, 9), system_start=d(2025, 1, 1), entity_id="CC6.1", fact_type="control_status", status="ACTIVE", source="sso", confidence=0.98),
    TimelineEvent(id="t-iam", title="IAM configuration changed", description="MFA disabled for one production IAM group.", valid_start=d(2025, 4, 10), valid_end=d(2025, 6, 19), system_start=d(2025, 4, 10), entity_id="AWS-IAM", fact_type="config_change", status="DEGRADED", source="cloudtrail", confidence=0.99),
    TimelineEvent(id="t-test-fail", title="Control test detects MFA failure", description="Automated CC6.1 test failed.", valid_start=d(2025, 5, 5), system_start=d(2025, 5, 5), entity_id="CC6.1", fact_type="control_test", status="FAIL", source="grc", confidence=0.97),
    TimelineEvent(id="t-finding", title="Audit finding created", description="Finding: MFA Disabled for Production IAM Group.", valid_start=d(2025, 5, 12), valid_end=d(2025, 6, 20), system_start=d(2025, 5, 12), entity_id="F-MFA", fact_type="finding", status="OPEN", source="internal-audit", confidence=0.95),
    TimelineEvent(id="t-posture", title="Posture partially compliant", description="As of 15 May 2025 ACME is partially compliant on CC6.1.", valid_start=d(2025, 5, 15), system_start=d(2025, 5, 15), entity_id="CC6.1", fact_type="posture", status="PARTIAL", source="agent", confidence=0.94),
    TimelineEvent(id="t-fix", title="IAM configuration remediated", description="Engineering restored MFA on prod-admins.", valid_start=d(2025, 6, 20), system_start=d(2025, 6, 20), entity_id="REM-MFA", fact_type="remediation", status="COMPLETE", source="jira", confidence=0.99),
    TimelineEvent(id="t-test-pass", title="Control test passes", description="CC6.1 retest passed.", valid_start=d(2025, 6, 25), system_start=d(2025, 6, 25), entity_id="CC6.1", fact_type="control_test", status="PASS", source="grc", confidence=0.99),
    TimelineEvent(id="t-upload", title="Evidence uploaded", description="Remediation evidence pack entered the compliance system.", valid_start=d(2025, 4, 10), valid_end=d(2025, 6, 20), system_start=d(2025, 7, 15), entity_id="EV-PACK", fact_type="ingestion", status="RECORDED", source="upload", confidence=0.92),
]

HINDSIGHT_MEMORIES = [
    {"document_id": "mem-mfa-jan", "timestamp": "2025-01-01", "content": "MFA enforcement was active for production IAM users beginning January 1, 2025."},
    {"document_id": "mem-iam-apr", "timestamp": "2025-04-10", "content": "On April 10, 2025, the production IAM configuration changed and MFA was disabled for one IAM group."},
    {"document_id": "mem-test-may", "timestamp": "2025-05-05", "content": "On May 5, 2025, automated SOC 2 CC6.1 control testing detected an MFA failure."},
    {"document_id": "mem-finding-may", "timestamp": "2025-05-12", "content": "On May 12, 2025, an audit finding was created: MFA Disabled for Production IAM Group."},
    {"document_id": "mem-posture-may", "timestamp": "2025-05-15", "content": "On May 15, 2025 ACME compliance posture for CC6.1 was PARTIALLY COMPLIANT because MFA was disabled for one production IAM group."},
    {"document_id": "mem-fix-jun", "timestamp": "2025-06-20", "content": "On June 20, 2025, the IAM configuration was remediated and MFA was re-enabled."},
    {"document_id": "mem-pass-jun", "timestamp": "2025-06-25", "content": "On June 25, 2025, the control test passed."},
    {"document_id": "mem-upload-jul", "timestamp": "2025-07-15", "content": "On July 15, 2025, evidence documenting the remediation was uploaded."},
]

MEMORY_FACTS: list[MemoryFact] = [
    MemoryFact(id=m["document_id"], content=m["content"], entity_id="CC6.1", fact_type="observation", source="hindsight", valid_start=date.fromisoformat(m["timestamp"]), system_start=date.fromisoformat(m["timestamp"]), confidence=0.97)
    for m in HINDSIGHT_MEMORIES
]
# July upload is known only at system 2025-07-15
MEMORY_FACTS[-1] = MemoryFact(id="mem-upload-jul", content=HINDSIGHT_MEMORIES[-1]["content"], entity_id="EV-PACK", fact_type="ingestion", source="upload", valid_start=d(2025, 4, 10), system_start=d(2025, 7, 15), confidence=0.92)

OBSERVATIONS: list[Observation] = [
    Observation(id="obs-partial-may", content="On May 15 2025 CC6.1 was partially compliant: MFA off for one IAM group; finding open; July evidence pack not yet known.", supporting_facts=["mem-iam-apr", "mem-test-may", "mem-finding-may"], confidence=0.96, valid_start=d(2025, 5, 15), system_start=d(2025, 5, 15)),
    Observation(id="obs-closed-jun", content="By June 25 2025 MFA was re-enabled, test passed, MFA finding remediated.", supporting_facts=["mem-fix-jun", "mem-pass-jun"], confidence=0.97, valid_start=d(2025, 6, 25), system_start=d(2025, 6, 25)),
    Observation(id="obs-open", content="Unresolved: Privileged Account Review Overdue (F-PAM) and Access Review Evidence Missing (F-UAR, system-known July 15).", supporting_facts=["mem-upload-jul"], confidence=0.9, valid_start=d(2025, 6, 1), system_start=d(2025, 6, 1)),
]

MENTAL_MODELS: list[MentalModel] = [
    MentalModel(
        id="mm:soc2-cc61",
        name="SOC 2 CC6.1 Access Control Posture",
        query="What is the current and historical SOC 2 CC6.1 access control posture for ACME?",
        content="CC6.1 MFA Enforcement was active from 2025-01-01, failed after the 2025-04-10 IAM change, was PARTIALLY COMPLIANT on 2025-05-15, remediated 2025-06-20, retested 2025-06-25. Evidence pack entered the system 2025-07-15 and must not be treated as known on May 15.",
        last_refreshed=datetime(2025, 7, 15, 12, 0, tzinfo=timezone.utc),
        evidence_count=8,
        confidence=0.97,
        status="remediated",
        supporting_evidence=["EV-CT-MFA", "EV-TEST-FAIL", "EV-TEST-PASS", "EV-PACK"],
        recent_changes=["Evidence pack uploaded 2025-07-15", "Retest pass 2025-06-25"],
        versions=[{"version": 1, "at": "2025-05-15", "note": "Partial"}, {"version": 2, "at": "2025-07-15", "note": "Post-upload refresh"}],
    ),
]

POSTURE_SERIES = [
    {"date": "2025-01-01", "compliance": 94, "known": 94},
    {"date": "2025-04-01", "compliance": 94, "known": 94},
    {"date": "2025-04-10", "compliance": 78, "known": 88},
    {"date": "2025-05-01", "compliance": 76, "known": 82},
    {"date": "2025-05-05", "compliance": 74, "known": 74},
    {"date": "2025-05-15", "compliance": 72, "known": 72},
    {"date": "2025-06-01", "compliance": 72, "known": 72},
    {"date": "2025-06-25", "compliance": 90, "known": 90},
    {"date": "2025-07-15", "compliance": 91, "known": 91},
]


def in_interval(start: date | None, end: date | None, as_of: date) -> bool:
    if start is None:
        return True
    if start > as_of:
        return False
    if end is not None and end < as_of:
        return False
    return True


def visible_at(obj, valid_as_of: date, system_as_of: date) -> bool:
    return in_interval(obj.valid_start, obj.valid_end, valid_as_of) and in_interval(
        obj.system_start, obj.system_end, system_as_of
    )


def occurred_by(obj, valid_as_of: date, system_as_of: date) -> bool:
    if obj.valid_start and obj.valid_start > valid_as_of:
        return False
    if obj.system_start and obj.system_start > system_as_of:
        return False
    return True
