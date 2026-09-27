# VeriChron architecture

```mermaid
flowchart TB
  subgraph ui [Next.js]
    Overview
    TimeMachine
    Graph
    Assistant
  end

  subgraph api [FastAPI]
    IngestAPI["/api/ingest"]
    QueryAPI["/api/query"]
    ReconAPI["/api/audit/reconstruct"]
  end

  subgraph agent [Agent]
    Intent --> Temporal
    Temporal --> Neo
    Neo --> Recall
    Recall --> Fusion
    Fusion --> Reflect
    Reflect --> LLM
    LLM --> Assess
  end

  subgraph memory [Memory - Hindsight]
    MM[Mental models]
    OBS[Observations]
    FACTS[Raw facts]
    MM --> OBS --> FACTS
  end

  subgraph graph [Neo4j]
    R[Regulation] --> REQ[Requirement]
    REQ --> CTL[Control]
    CTL --> INF[Infrastructure]
    CTL --> EV[Evidence]
    F[Finding] --> CTL
    F --> REM[Remediation]
  end

  ui --> api
  QueryAPI --> agent
  IngestAPI --> Parser --> Extract --> graph
  Extract --> Retain["hindsight.retain()"]
  Recall --> memory
  Reflect --> memory
  Neo --> graph
```

## Bitemporal rule

A fact is visible for reconstruction only if:

- `valid_start <= as_of_valid` and (`valid_end` is null or `>= as_of_valid`)
- `system_start <= as_of_system` and (`system_end` is null or `>= as_of_system`)

Never answer a historical question with artifacts whose `system_start` is in the future of the query.
