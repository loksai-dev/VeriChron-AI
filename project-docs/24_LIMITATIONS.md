# 24 — Limitations

Be explicit: this is a **hackathon / demo** system with production-shaped UI, not a certified GRC platform.

## Mock vs live

- Groq, Neo4j, Hindsight each have mock implementations.
- Health `connected` requires live Bolt / Hindsight HTTP / Groq key.
- Tools still run when services are disconnected (in-process data).

## Incomplete integrations

- Hindsight server is optional and usually disconnected.
- `hindsight` Python package is not in `requirements.txt`.
- Mental models never call live Hindsight APIs.
- Ingest parsers use wrong default entity ids (`ctl:mfa`, `infra:aws-iam`).
- Mental model refresh id mismatch (`mm:soc2-access`).

## Demo data

- Single tenant ACME, SOC 2 subset (CC6.x / CC7.x).
- Overview metrics `overall_compliance=0.91` and `evidence_coverage=0.88` are **hardcoded**.
- `/controls`, `/findings`, `/evidence` ignore Neo4j and as-of.

## Temporal

- `occurred_by` ignores `valid_end` (events remain “occurred” after they ended).
- `traverse_compliance_graph` always as-of 2025-07-15.
- Temporal parse only special-cases four English phrases.

## Agent

- Fixed tool plan; Groq does not select tools in `iter_query`.
- `affected_controls` always CC6.1 / REQ-CC6.1.
- Sequential tools + sleeps (~0.2s) for demo pacing.
- Agent state not persisted.

## Retrieval

- Hindsight recall is keyword scoring, not embeddings (mock).
- Neo4j search is graph fetch, not full-text index.

## Performance

- Full graph MATCH returned then filtered in Python.
- No pagination.
- SSE holds the request until all tools finish.

## Tests / ops

- No automated tests, no auth, no multi-instance session affinity for `run_index`.
