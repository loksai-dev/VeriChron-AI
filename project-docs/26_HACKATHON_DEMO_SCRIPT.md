# 26 — Hackathon demo script (≈4:30)

Exact UI: Next.js shell. Backend must be up. Prefer `neo4j: connected`. `hindsight: disconnected` is OK — say “in-process bank with retain/recall/reflect”.

## 0:00 — Problem

**Screen:** `/` Overview.  
**Say:** Auditors ask what was true on a date, not what PDF RAG finds today. Later uploads must not rewrite history.

## 0:30 — Architecture

**Screen:** `/settings` or health strip in AppShell.  
**Say:** Next.js → FastAPI → agent tools → Neo4j graph + Hindsight-style memory + Groq (or mock) for the write-up. Two clocks: valid time and system time.

## 1:00 — Neo4j

**Screen:** http://localhost:7474  
**Action:** `MATCH (n:Entity) RETURN n LIMIT 50`  
**Say:** Typed nodes. CC6.1 depends on AWS IAM; findings violate controls; remediations close them.

## 1:30 — Hindsight

**Screen:** `/mental-models`  
**Action:** Open the CC6.1 mental model; mention facts list.  
**Say:** Raw facts retained from the ACME timeline. July 15 upload has system_start in July so May recall drops it.

## 2:00 — Compliance question

**Screen:** `/assistant`  
**Action:** Ask `What was our compliance posture on May 15, 2025?`  
**Expect:** Streaming thoughts; PARTIALLY COMPLIANT; caveat on July evidence.

## 2:30 — Tool execution

**Screen:** same, scroll trace.  
**Action:** Point at `search_neo4j`, `traverse_compliance_graph`, `search_hindsight`, `reconstruct_historical_state`, `get_evidence`, `analyze_compliance`, `hindsight.reflect`.  
**Say:** This is a real tool loop in FastAPI SSE — not a single chat completion.

## 3:00 — Time Machine

**Screen:** `/timeline`  
**Action:** valid=2025-05-15, system=2025-05-15, reconstruct. Then jump system to 2025-07-15.  
**Expect:** July pack appears only on later system time.

## 3:30 — Evidence

**Screen:** `/evidence` and `/graph`  
**Action:** Highlight EV-CT-MFA vs EV-PACK dates.

## 4:00 — Close

**Screen:** `/findings`  
**Say:** MFA finding remediated; PAM and UAR still open. VeriChron reconstructs knowledge, it does not pretend to be a live IR platform.
