"""Seed Neo4j with the VeriChron demo graph. Safe to run when Neo4j is down — prints skip."""
from app.services.factory import get_services

if __name__ == "__main__":
    svc = get_services()
    n = svc.neo4j.seed()
    print(f"Seeded {n} nodes via {svc.modes['neo4j']} Neo4j service")
