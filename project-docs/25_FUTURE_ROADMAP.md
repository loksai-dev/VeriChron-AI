# 25 — Future roadmap

Items below are **not** in the current codebase unless marked otherwise.

## NOW

- Keep ACME seed + streaming assistant + Time Machine as the demo spine.
- Align ingest default ids with `CC6.1` / `AWS-IAM`.
- Align mental-model refresh id with `mm:soc2-cc61`.
- Wait-for Neo4j in Compose; reconnect factory without process restart.
- Document health honesty (`disconnected` + working mocks).

## NEXT

- Optional Hindsight container in Compose with real retain/recall.
- Use Groq tool calling only when it does not block SSE, or parallelize.
- Bitemporal Cypher parameters (not Python-only filters).
- Wire `/controls` to graph as-of.
- Automated API tests for May 15 leakage.

## LATER

- Production deployment (TLS, secrets manager, HA Neo4j).
- Multi-tenancy and RBAC.
- Real enterprise connectors (Jira, CloudTrail, GRC export).
- Advanced temporal reasoning (intervals, bitemporal SQL/Cypher millennia).
- Continuous monitoring / alerting.
- Audit export packages.
- Policy change detection beyond SUPERSEDES demo edge.
- More frameworks (ISO 27001, NIST) as first-class graphs.
