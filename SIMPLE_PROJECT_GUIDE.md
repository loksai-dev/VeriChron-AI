# VeriChron AI — Simple End-to-End Guide

> **A clean, clear explanation of what VeriChron AI is, why it matters, and how every piece works together.**

---

## 1. What is VeriChron AI? (In Plain English)

Most AI chatbots only know what is true **today**.

If you ask a normal AI compliance tool:  
> *"Were we compliant with our security policy on May 15, 2025?"*

It will search your current files, find an updated security policy uploaded in July, and say: *"Yes, you are compliant."*

**That is wrong.** In an audit (SOC 2, ISO 27001), using evidence you didn't actually have on that date is considered audit failure.

**VeriChron AI fixes this.** It is a **"Time Machine for Security Compliance"**. It tracks two separate timelines:
1. **What actually happened in the real world** (Valid Time).
2. **When the company actually learned about it** (System Time).

With VeriChron, you can ask about any date in the past, and it will answer based **only on what was true and known on that exact day**—without leaking future knowledge.

---

## 2. The Core Problem: The Story of ACME Corp

To understand why this is needed, look at what happened to our demo company (**ACME Corp**) in 2025:

```
Jan 8, 2025       Apr 12, 2025           May 15, 2025          May 20, 2025       Jul 8, 2025        Jul 15, 2025
    |                  |                      |                     |                  |                  |
[MFA Active]    [Engineer turns]       [Auditor asks:]       [Automated scan]     [MFA fixed &]      [New policy PDF]
[Compliant ]    [off MFA condition]    [Are we compliant?]   [detects failure]    [re-enabled ]      [uploaded to GRC]
                (Nobody noticed!)      (Blindspot!)          (Now we know!)       (Resolved   )      (Backdated claim)
```

- **On April 12**: An engineer turned off Multi-Factor Authentication (MFA) to fix a deploy script.
- **On May 15**: An auditor asks: *"Was MFA enforced today?"*
  - **In Reality (Valid Time)**: No, MFA was off! The company was non-compliant.
  - **In Company Records (System Time)**: The company hadn't run its monthly scan yet. GRC records still showed green!
- **On May 20**: The automated scan runs and detects the failure.
- **On July 15**: Someone uploads a new policy document claiming MFA was mandated all year.

**VeriChron proves that on May 15, the organization was physically non-compliant, but had not yet detected it.** It prevents the July 15 document from lying about the past.

---

## 3. How the System Works End-to-End

Here is how all 5 technologies connect together:

```
 ┌─────────────────────────────────────────────────────────────┐
 │                      1. USER INTERFACE                      │
 │   Next.js 14 Web Console (http://localhost:3000)            │
 │   • Overview Dashboard  • Time Machine  • Audit Assistant   │
 └──────────────────────────────┬──────────────────────────────┘
                                │ (HTTP / Server-Sent Events)
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │                     2. APPLICATION API                      │
 │   FastAPI Backend (http://localhost:8000)                   │
 │   • Bitemporal Math Engine • Enforces "No Future Leaks"     │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │                3. MULTI-AGENT ORCHESTRATOR                  │
 │   OpenClaw Gateway (:18789) + Fallback Agent                │
 │   • Decides which tools to run                              │
 │   • Inspects the graph and calls memory                     │
 └───────────────┬──────────────────────────────┬──────────────┘
                 │                              │
                 ▼                              ▼
 ┌──────────────────────────────┐ ┌────────────────────────────┐
 │      4. KNOWLEDGE GRAPH      │ │    5. LONG-TERM MEMORY     │
 │   Neo4j / In-Memory Graph    │ │   Hindsight Cloud          │
 │   • Knows connections:       │ │   • Remembers human notes: │
 │     Policy -> Control ->     │ │     "CISO approved MFA     │
 │     System -> Evidence       │ │      exception for deploy" │
 └───────────────┬──────────────┘ └─────────────┬──────────────┘
                 │                              │
                 └──────────────┬───────────────┘
                                │ Grounded Context
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │                     6. REASONING ENGINE                     │
 │   Groq Ultra-Fast LLM (openai/gpt-oss-120b)                 │
 │   • Evaluates evidence • Returns clear, honest verdict      │
 └─────────────────────────────────────────────────────────────┘
```

---

## 4. The 5 Technologies in Simple Terms

| Technology | What it is | What it does in VeriChron |
| :--- | :--- | :--- |
| **Next.js 14** | Modern web dashboard | Gives auditors a clean UI to slide through time, inspect graphs, and chat with the AI assistant. |
| **FastAPI** | Fast Python backend | Calculates the bitemporal math (checks whether dates match both valid time and system time). |
| **OpenClaw** | Multi-agent gateway | An autonomous AI agent runtime that chooses the right tools (`search_neo4j`, `search_hindsight`, `reconstruct`). |
| **Hindsight Cloud** | Durable memory bank | Remembers exceptions, approvals, and context across months and years (not lost when chat closes). |
| **Neo4j** | Graph database | Maps relationships: Which Policy governs which Control, and which Evidence proves or violates it. |
| **Groq** | Lightning-fast AI inference | Runs open-weight AI models (`gpt-oss-120b`) in milliseconds to write the final audit assessment. |

---

## 5. What You Can Click & Try Right Now

The entire application is running live on your computer right now:

### Screen 1: The Bitemporal Time Machine
👉 Open: [http://localhost:3000/timeline](http://localhost:3000/timeline)
- You will see two sliders: **Valid Date** (World Time) and **System Date** (Knowledge Time).
- Set **Valid Time** = `2025-05-15` and **System Time** = `2025-05-15`.
- Click **Reconstruct state**:
  - Notice MFA Policy shows **INACTIVE** (it was disabled in AWS on April 12).
  - But System Knowledge shows **UNDETECTED** (the scan hadn't happened yet).
- Now slide **System Time** forward to `2025-05-25`:
  - Watch the status switch to **DETECTED FAILURE**!

---

### Screen 2: The Audit Assistant
👉 Open: [http://localhost:3000/assistant](http://localhost:3000/assistant)
- **Test 1 (Memory Retention)**: Click the button:  
  `"Remember that the ACME MFA exception was approved by CISO for CI/CD deploy runner."`  
  *Watch the agent save this directly to Hindsight Cloud memory.*
- **Test 2 (Memory Recall)**: Type:  
  `"What was the reason for the ACME MFA exception?"`  
  *Watch the agent recall the approval from the cloud memory bank and answer accurately.*
- **Test 3 (Bitemporal Audit)**: Type:  
  `"What was our compliance posture on May 15, 2025?"`  
  *Watch the agent inspect the timeline, shield future July evidence, and tell the honest truth.*

---

### Screen 3: The Documentation Hub
👉 Open: [http://localhost:3000/docs](http://localhost:3000/docs)
- A built-in guide inside the web app with tabs for Architecture, Bitemporal Math, API endpoints, and a 3-minute Hackathon Script.

---

## 6. How to Run the Project (3 Quick Commands)

If you ever restart your computer, here is how you run the whole stack:

```powershell
# 1. Start OpenClaw Agent Gateway
npx --yes openclaw gateway run --port 18789 --bind loopback --token verichron-gateway-token

# 2. Start Python Backend (in a new terminal)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir backend

# 3. Start Frontend (in a new terminal)
cd frontend
npm run dev
```

Then open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 7. Summary: Why VeriChron Wins

1. **No Lies, No Hallucinations**: It never uses evidence from the future to judge the past.
2. **Durable Memory**: It remembers human conversations, approvals, and exceptions forever via Hindsight Cloud.
3. **Graph Grounded**: Every claim links back to a real control, policy, or log in Neo4j.
4. **Resilient**: If the multi-agent gateway is busy, it automatically falls back to the native agent with zero downtime.
