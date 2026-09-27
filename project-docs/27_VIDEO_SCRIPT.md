# 27 — Video script (≈3 minutes)

Grounded in `pipeline.py`, `acme.py`, and the streaming assistant. Do not claim a live Hindsight cluster unless health says `connected`.

| Time | Narration | Screen | Expected result |
| --- | --- | --- | --- |
| 0:00 | Compliance questions are time-travel problems. RAG mixes tomorrow’s binder with yesterday’s outage. | Overview | SOC 2 dashboard for ACME |
| 0:20 | VeriChron stores a knowledge graph and a memory bank. Every fact has valid time and system time. | Graph | Nodes CC6.1, AWS-IAM, findings |
| 0:40 | We retain the ACME story as memories: MFA on in January, IAM change April 10, failed test May 5. | Mental models / facts | mem-* documents |
| 1:00 | I ask the audit assistant what posture was on May 15, 2025. | Assistant, type question | SSE `thought` then tools |
| 1:20 | Watch Neo4j search and graph walk. Then Hindsight recall with May 15 as system time. | Tool chips | search_neo4j, traverse, search_hindsight |
| 1:40 | Reconstruct historical state labels PARTIALLY COMPLIANT. Evidence pack EV-PACK is listed as future/unknown. | reconstruct tool summary | unknown_future_evidence includes EV-PACK |
| 2:00 | Reflect climbs mental model → observation → raw fact. Groq (or the mock reasoner) writes the conclusion. | reflect + answer | Caveat about 2025-07-15 |
| 2:20 | Time machine: same valid date, later system date, and the July upload appears. That is the product. | Timeline | t-upload visible only later |
| 2:45 | Unresolved work remains: privileged review and UAR evidence. The MFA incident is closed. | Findings | F-PAM, F-UAR open |

Do not invent latency numbers or production SLAs.
