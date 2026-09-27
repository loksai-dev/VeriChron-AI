from __future__ import annotations

from datetime import date
from time import perf_counter
from typing import Any

from app.data import demo
from app.logging_util import agent_log
from app.models.schemas import GraphEdge, GraphNode, GraphPayload


ALLOWED_RELS = {
    "GOVERNS",
    "SATISFIED_BY",
    "IMPLEMENTS",
    "DEPENDS_ON",
    "EVIDENCED_BY",
    "VIOLATES",
    "REMEDIATED_BY",
    "SUPPORTS",
    "RESOLVES",
    "SUPERSEDES",
    "CAUSES",
    "ENABLES",
    "EVALUATED_BY",
    "AFFECTS",
    "CONTRADICTS",
    "HAS_VERSION",
    "DOCUMENTS",
}


def _iso(v) -> str | None:
    if v is None:
        return None
    if hasattr(v, "isoformat"):
        return v.isoformat()
    return str(v)[:10]


def _node_from_record(rec: dict) -> GraphNode:
    labels = rec.get("_labels") or []
    ntype = rec.get("type") or next((l for l in labels if l != "Entity"), "Evidence")
    sources = rec.get("sources") or []
    if isinstance(sources, str):
        sources = [sources]
    return GraphNode(
        id=rec.get("id") or "",
        type=ntype,  # type: ignore[arg-type]
        name=rec.get("name") or rec.get("id") or "",
        status=rec.get("status"),
        description=rec.get("description") or "",
        owner=rec.get("owner"),
        framework=rec.get("framework"),
        valid_start=rec.get("valid_start"),
        valid_end=rec.get("valid_end"),
        system_start=rec.get("system_start"),
        system_end=rec.get("system_end"),
        sources=list(sources),
        properties={k: rec[k] for k in rec if k not in {"id", "name", "type", "_labels"}},
    )


class MockNeo4jService:
    last_cypher = "MATCH (n:Entity) OPTIONAL MATCH (n)-[r]->(m) RETURN n, r, m  /* mock in-memory */"
    last_ms = 0
    source = "mock"

    def status(self) -> tuple[bool, str]:
        return True, "In-memory ACME graph (Neo4j not connected)"

    def is_live(self) -> bool:
        return False

    def count_nodes(self) -> int:
        return len(demo.NODES)

    def graph(self, entity_id: str | None, valid_as_of: date, system_as_of: date, types: list[str] | None) -> GraphPayload:
        t0 = perf_counter()
        nodes = [n for n in demo.NODES if demo.visible_at(n, valid_as_of, system_as_of)]
        if types and "All" not in types:
            nodes = [n for n in nodes if n.type in types]
        ids = {n.id for n in nodes}
        edges = [e for e in demo.EDGES if e.source in ids and e.target in ids and demo.visible_at(e, valid_as_of, system_as_of)]
        if entity_id:
            keep = {entity_id}
            changed = True
            while changed:
                changed = False
                for e in edges:
                    if e.source in keep or e.target in keep:
                        before = len(keep)
                        keep.add(e.source)
                        keep.add(e.target)
                        if len(keep) != before:
                            changed = True
            nodes = [n for n in nodes if n.id in keep]
            edges = [e for e in edges if e.source in keep and e.target in keep]
        self.last_ms = int((perf_counter() - t0) * 1000)
        self.last_cypher = (
            "MATCH (n:Entity) OPTIONAL MATCH (n)-[r]->(m) RETURN n,r,m "
            f"/* filtered valid={valid_as_of} system={system_as_of} entity={entity_id} */"
        )
        return GraphPayload(nodes=nodes, edges=edges, causal_path=list(demo.CAUSAL_PATH))

    def get_entity(self, entity_id: str) -> GraphNode | None:
        return next((n for n in demo.NODES if n.id == entity_id or n.name == entity_id), None)

    def write_node(self, node: GraphNode) -> None:
        existing = next((n for n in demo.NODES if n.id == node.id), None)
        if existing:
            demo.NODES.remove(existing)
        demo.NODES.append(node)

    def write_edge(self, edge: GraphEdge) -> None:
        existing = next((e for e in demo.EDGES if e.id == edge.id), None)
        if existing:
            demo.EDGES.remove(existing)
        demo.EDGES.append(edge)

    def seed(self) -> int:
        return len(demo.NODES)

    def stats(self) -> dict[str, Any]:
        from collections import Counter

        return {
            "labels": dict(Counter(n.type for n in demo.NODES)),
            "rels": dict(Counter(e.type for e in demo.EDGES)),
            "source": "mock",
        }

    def run_cypher_readonly(self, query: str) -> dict[str, Any]:
        payload = self.graph(None, date(2025, 7, 15), date(2025, 7, 15), None)
        return {"query": query, "nodes": len(payload.nodes), "relationships": len(payload.edges), "ms": self.last_ms, "source": "mock"}


class RealNeo4jService:
    def __init__(self, uri: str, user: str, password: str):
        from neo4j import GraphDatabase

        self.uri = uri
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
        self._ok = False
        self._detail = ""
        self.last_cypher = ""
        self.last_ms = 0
        self.source = "neo4j"
        try:
            self._driver.verify_connectivity()
            self._install_schema()
            self._ok = True
            self._detail = f"Connected {uri}"
        except Exception as exc:
            self._detail = str(exc)

    def is_live(self) -> bool:
        return self._ok

    def status(self) -> tuple[bool, str]:
        return self._ok, self._detail

    def _install_schema(self) -> None:
        with self._driver.session() as session:
            session.run("CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (n:Entity) REQUIRE n.id IS UNIQUE")

    def count_nodes(self) -> int:
        with self._driver.session() as session:
            rec = session.run("MATCH (n:Entity) RETURN count(n) AS c").single()
            return int(rec["c"]) if rec else 0

    def seed(self) -> int:
        if not self._ok:
            return 0
        agent_log("NEO4J", "Seed started (MERGE, idempotent)")
        with self._driver.session() as session:
            for node in demo.NODES:
                session.run(
                    """
                    MERGE (n:Entity {id: $id})
                    SET n.name = $name,
                        n.type = $type,
                        n.description = $description,
                        n.status = $status,
                        n.owner = $owner,
                        n.framework = $framework,
                        n.valid_start = $vs,
                        n.valid_end = $ve,
                        n.system_start = $ss,
                        n.system_end = $se,
                        n.tenant_id = $tenant
                    """,
                    id=node.id,
                    name=node.name,
                    type=node.type,
                    description=node.description,
                    status=node.status,
                    owner=node.owner,
                    framework=node.framework,
                    vs=_iso(node.valid_start),
                    ve=_iso(node.valid_end),
                    ss=_iso(node.system_start),
                    se=_iso(node.system_end),
                    tenant="acme",
                )
                session.run(
                    f"MATCH (n:Entity {{id: $id}}) SET n:{node.type}",
                    id=node.id,
                )
            for edge in demo.EDGES:
                rel = edge.type if edge.type in ALLOWED_RELS else "RELATED"
                session.run(
                    f"""
                    MATCH (a:Entity {{id: $src}}), (b:Entity {{id: $tgt}})
                    MERGE (a)-[r:{rel} {{id: $id}}]->(b)
                    SET r.valid_start = $vs, r.valid_end = $ve,
                        r.system_start = $ss, r.system_end = $se
                    """,
                    src=edge.source,
                    tgt=edge.target,
                    id=edge.id,
                    vs=_iso(edge.valid_start),
                    ve=_iso(edge.valid_end),
                    ss=_iso(edge.system_start),
                    se=_iso(edge.system_end),
                )
        n = self.count_nodes()
        agent_log("NEO4J", f"Seed complete — {n} nodes")
        return n

    def _temporal_ok(self, rec: dict, valid_as_of: date, system_as_of: date) -> bool:
        class T:
            pass

        o = T()
        o.valid_start = date.fromisoformat(str(rec["valid_start"])[:10]) if rec.get("valid_start") else None
        o.valid_end = date.fromisoformat(str(rec["valid_end"])[:10]) if rec.get("valid_end") else None
        o.system_start = date.fromisoformat(str(rec["system_start"])[:10]) if rec.get("system_start") else None
        o.system_end = date.fromisoformat(str(rec["system_end"])[:10]) if rec.get("system_end") else None
        return demo.visible_at(o, valid_as_of, system_as_of)

    def graph(self, entity_id: str | None, valid_as_of: date, system_as_of: date, types: list[str] | None) -> GraphPayload:
        if not self._ok:
            return MockNeo4jService().graph(entity_id, valid_as_of, system_as_of, types)
        t0 = perf_counter()
        if entity_id:
            query = (
                "MATCH (c:Entity {id: $eid}) "
                "OPTIONAL MATCH p = (c)-[r*1..4]-(x:Entity) "
                "RETURN c, r, x"
            )
            params = {"eid": entity_id}
        else:
            query = "MATCH (n:Entity) OPTIONAL MATCH (n)-[r]->(m:Entity) RETURN n, r, m"
            params = {}
        self.last_cypher = query + f" /* valid={valid_as_of} system={system_as_of} */"
        nodes_map: dict[str, GraphNode] = {}
        edges: list[GraphEdge] = []
        with self._driver.session() as session:
            result = session.run(query, **params)
            for rec in result:
                for key in ("n", "c", "m", "x"):
                    raw = rec.get(key)
                    if raw is None:
                        continue
                    data = dict(raw)
                    data["_labels"] = list(raw.labels)
                    if not self._temporal_ok(data, valid_as_of, system_as_of):
                        continue
                    node = _node_from_record(data)
                    if types and "All" not in types and node.type not in types:
                        continue
                    nodes_map[node.id] = node
                rels = rec.get("r")
                if rels is None:
                    continue
                seq = rels if isinstance(rels, list) else [rels]
                for rel in seq:
                    if rel is None:
                        continue
                    data = dict(rel)
                    if data.get("valid_start") and not self._temporal_ok(data, valid_as_of, system_as_of):
                        continue
                    edges.append(
                        GraphEdge(
                            id=data.get("id") or f"{rel.start_node['id']}-{rel.type}-{rel.end_node['id']}",
                            source=rel.start_node["id"],
                            target=rel.end_node["id"],
                            type=rel.type,
                            valid_start=data.get("valid_start"),
                            system_start=data.get("system_start"),
                        )
                    )
        ids = set(nodes_map)
        edges = [e for e in edges if e.source in ids and e.target in ids]
        self.last_ms = int((perf_counter() - t0) * 1000)
        agent_log("NEO4J", f"{len(nodes_map)} nodes / {len(edges)} relationships in {self.last_ms}ms")
        return GraphPayload(nodes=list(nodes_map.values()), edges=edges, causal_path=list(demo.CAUSAL_PATH))

    def get_entity(self, entity_id: str) -> GraphNode | None:
        if not self._ok:
            return MockNeo4jService().get_entity(entity_id)
        query = "MATCH (n:Entity {id: $id}) RETURN n, labels(n) AS labels"
        self.last_cypher = query
        with self._driver.session() as session:
            rec = session.run(query, id=entity_id).single()
            if not rec:
                rec = session.run("MATCH (n:Entity) WHERE n.name = $id RETURN n, labels(n) AS labels", id=entity_id).single()
            if not rec:
                return None
            data = dict(rec["n"])
            data["_labels"] = rec["labels"]
            return _node_from_record(data)

    def write_node(self, node: GraphNode) -> None:
        MockNeo4jService().write_node(node)
        if self._ok:
            self.seed()

    def write_edge(self, edge: GraphEdge) -> None:
        MockNeo4jService().write_edge(edge)
        if self._ok:
            self.seed()

    def stats(self) -> dict[str, Any]:
        if not self._ok:
            return MockNeo4jService().stats()
        with self._driver.session() as session:
            labels = {r["l"]: r["c"] for r in session.run("MATCH (n) UNWIND labels(n) AS l RETURN l, count(*) AS c")}
            rels = {r["t"]: r["c"] for r in session.run("MATCH ()-[r]->() RETURN type(r) AS t, count(*) AS c")}
        return {"labels": labels, "rels": rels, "source": "neo4j"}

    def run_cypher_readonly(self, query: str) -> dict[str, Any]:
        t0 = perf_counter()
        if not self._ok:
            return MockNeo4jService().run_cypher_readonly(query)
        if any(tok in query.upper() for tok in ("DELETE", "DETACH", "DROP", "CREATE CONSTRAINT", "MERGE")):
            return {"error": "Read-only explorer", "query": query}
        with self._driver.session() as session:
            records = list(session.run(query))
        ms = int((perf_counter() - t0) * 1000)
        self.last_cypher = query
        self.last_ms = ms
        return {"query": query, "rows": len(records), "ms": ms, "source": "neo4j"}
