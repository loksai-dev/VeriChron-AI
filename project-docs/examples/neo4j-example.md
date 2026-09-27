# Example: Neo4j

```cypher
MATCH (c:Entity {id:'CC6.1'})-[r]->(x:Entity)
RETURN c.name, type(r), x.id, x.name
```

**Result structure** (driver → `GraphNode`):

```json
{
  "id": "CC6.1",
  "type": "Control",
  "name": "MFA Enforcement",
  "status": "remediated",
  "valid_start": "2025-01-01",
  "system_start": "2025-01-01"
}
```

API `GET /api/graph?valid_as_of=2025-05-15&system_as_of=2025-05-15` wraps `GraphPayload` plus:

```json
{
  "cypher": "MATCH (n:Entity) OPTIONAL MATCH (n)-[r]->(m:Entity) RETURN n, r, m",
  "execution_ms": 12,
  "source": "live"
}
```

`source` is `mock` when Bolt is down.
