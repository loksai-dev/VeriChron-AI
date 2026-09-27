# 06 — Neo4j architecture

## Connection

`Settings`: `NEO4J_URI` (default `bolt://localhost:7687`), `NEO4J_USER`, `NEO4J_PASSWORD`.

`Services` tries: settings URI, `bolt://127.0.0.1:7687`, `neo4j://127.0.0.1:7687`, `bolt://localhost:7687`, `bolt://neo4j:7687`.

Compose: `neo4j:5.26-community`, `NEO4J_AUTH=neo4j/password`, ports 7474 / 7687, volume `neo4j_data`. Backend override `NEO4J_URI=bolt://neo4j:7687`.

Database: default Neo4j database (no custom DB name in code).

## Seed (what actually populates the graph)

`RealNeo4jService.seed()` MERGEs `demo.NODES` / `demo.EDGES` from `acme.py`.

- Constraint: `CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (n:Entity) REQUIRE n.id IS UNIQUE`
- Each node: `MERGE (n:Entity {id})` then `SET n:<EntityType>` (e.g. `:Control`)
- Relationships: only types in `ALLOWED_RELS`; unknown types become `RELATED`

If Bolt is down: `MockNeo4jService` uses the same Python lists.

`POST /api/demo/seed` and `python -m app.neo4j.seed` call `neo4j.seed()`.

## File `backend/app/neo4j/schema.cypher`

A **smaller, different** sample graph (`reg:soc2`, `ctl:mfa`, `infra:aws-iam`). **Not** the ACME ids used by the agent (`CC6.1`, `AWS-IAM`, …). Do not treat it as the live schema unless you ran it by hand.

## Labels

Always `:Entity` plus one of: `Regulation`, `Requirement`, `Policy`, `Control`, `Infrastructure`, `Evidence`, `AuditFinding`, `Remediation`, `JiraTicket`, `Person`, `Organization`.

## Relationship types in ACME seed

`GOVERNS`, `SATISFIED_BY`, `IMPLEMENTS`, `SUPERSEDES`, `DEPENDS_ON`, `EVIDENCED_BY`, `SUPPORTS`, `VIOLATES`, `REMEDIATED_BY`, `RESOLVES`, `CAUSES`, `ENABLES`.

`EVALUATED_BY` is in `ALLOWED_RELS` but **not** used in `acme.py` edges.

## Properties (typical)

`id`, `name`, `type`, `status`, `description`, `owner`, `framework`, `sources`, `valid_start`, `valid_end`, `system_start`, `system_end`.

Indexes: uniqueness on `Entity.id` only. No extra indexes in seed.

## Queries in code

`RealNeo4jService.graph`: neighborhood Cypher around an entity, or full `MATCH (n:Entity) OPTIONAL MATCH (n)-[r]->(m:Entity) RETURN n, r, m`, then filter `visible_at` in Python.

`get_entity`: `MATCH (n:Entity {id: $id})`.

## Agent usage

`search_neo4j` → `graph(CC6.1)` if query contains CC6.1/MFA else full graph.

`traverse_compliance_graph` → `graph("CC6.1")` with hardcoded dates **2025-07-15 / 2025-07-15** (not the user’s as-of). Path prefers `demo.CAUSAL_PATH`.

## Visual (actual ACME causal path)

```
SOC2 —GOVERNS→ REQ-CC6.1 —SATISFIED_BY→ CC6.1 —DEPENDS_ON→ AWS-IAM
CC6.1 —EVIDENCED_BY→ EV-CT-MFA / EV-TEST-FAIL / EV-PACK
F-MFA —VIOLATES→ CC6.1
F-MFA —REMEDIATED_BY→ REM-MFA
SEC-1842 —ENABLES→ REM-MFA
```
