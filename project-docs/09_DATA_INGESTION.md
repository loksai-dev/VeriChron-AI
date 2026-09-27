# 09 — Data ingestion

## Demo seed (primary)

```
acme.py NODES/EDGES/MEMORIES
  → factory: neo4j.seed() if live graph empty
  → hindsight.seed_bank() → retain() each HINDSIGHT_MEMORIES item
```

Not a streaming enterprise connector.

## HTTP ingest

`IngestionPipeline.ingest` (`backend/app/ingestion/pipeline.py`).

```
IngestRequest (filename, content, mime_hint, source)
  → _guess_kind / mime_hint
  → _parse (json, csv, jira, cloudtrail, markdown, text)
  → GraphNode write_node
  → optional GraphEdge write_edge (default EVIDENCED_BY)
  → Evidence appended to demo.EVIDENCE
  → hindsight.retain
  → refresh_mental_model("mm:soc2-access")  # id mismatch; usually skipped
```

Sources: `POST /api/ingest` JSON; `POST /api/ingest/upload` file. Temporal: first `20xx-xx-xx` in content or today.

Parsers are **heuristic**, not full ETL. JSON default `relates_to` is `ctl:mfa` (legacy id, **not** `CC6.1`). CloudTrail default target `infra:aws-iam` (not `AWS-IAM`). Jira relates to `finding:cc6.1-q2` (not `F-MFA`).

## Neo4j vs Hindsight

| Path | Neo4j | Hindsight |
| --- | --- | --- |
| Startup seed | MERGE ACME graph | retain memories |
| Upload | write_node / write_edge | retain snippet |
| Agent | read graph | recall / reflect |

**NOT IMPLEMENTED:** live Jira OAuth, live CloudTrail, scheduled sync.
