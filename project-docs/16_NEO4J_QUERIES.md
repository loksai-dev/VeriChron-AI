# 16 — Neo4j queries

Against the **ACME seed** (`:Entity` + type labels, ids like `CC6.1`). Not the sample ids in `schema.cypher`.

Browser: http://localhost:7474 user `neo4j` / password from env (example uses `password`).

```cypher
// All nodes
MATCH (n:Entity) RETURN n LIMIT 100

// All relationships
MATCH (a:Entity)-[r]->(b:Entity) RETURN type(r), a.id, b.id LIMIT 200

// Controls
MATCH (c:Control) RETURN c.id, c.name, c.status

// Findings
MATCH (f:AuditFinding) RETURN f.id, f.name, f.status

// Evidence
MATCH (e:Evidence) RETURN e.id, e.name, e.system_start

// CC6.1 traversal (matches ALLOWED depth idea)
MATCH (c:Entity {id:'CC6.1'})
OPTIONAL MATCH p = (c)-[*1..4]-(x:Entity)
RETURN p LIMIT 50

// Causal-style path used by the demo
MATCH (a:Entity {id:'REQ-CC6.1'})-[r]-(b)
RETURN a, r, b

// Historical filter must be applied in app Python (visible_at).
// Properties are ISO date strings or dates depending on driver coercion:
MATCH (n:Entity)
WHERE n.system_start <= date('2025-05-15')
  AND (n.valid_start IS NULL OR n.valid_start <= date('2025-05-15'))
RETURN n.id, n.name

// Remediation
MATCH (f:AuditFinding)-[:REMEDIATED_BY]->(r:Remediation)
RETURN f.id, r.id, r.status
```

Code’s live query (full graph) is approximately:

```cypher
MATCH (n:Entity) OPTIONAL MATCH (n)-[r]->(m:Entity) RETURN n, r, m
```

`GET /api/graph` returns `cypher` and `execution_ms` from the last Neo4j call.
