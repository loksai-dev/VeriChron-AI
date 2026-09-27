from __future__ import annotations

from functools import lru_cache

from app.config import get_settings
from app.data import demo
from app.logging_util import agent_log, configure_logging
from app.models.schemas import ServiceStatus, SystemStatus
from app.services.hindsight_service import MockHindsightService, RealHindsightService
from app.services.llm_service import MockLLMService, RealGroqService
from app.services.neo4j_service import MockNeo4jService, RealNeo4jService


NEO4J_CANDIDATES = [
    None,  # settings.neo4j_uri first
    "bolt://127.0.0.1:7687",
    "neo4j://127.0.0.1:7687",
    "bolt://localhost:7687",
    "bolt://neo4j:7687",
]


class Services:
    def __init__(self) -> None:
        configure_logging()
        settings = get_settings()
        self.settings = settings
        self.neo4j = MockNeo4jService()
        self.hindsight = MockHindsightService()
        self.llm = MockLLMService()
        self.modes = {"neo4j": "mock", "hindsight": "mock", "llm": "mock"}
        self.seeded_nodes = 0

        uris = []
        for candidate in NEO4J_CANDIDATES:
            uri = settings.neo4j_uri if candidate is None else candidate
            if uri not in uris:
                uris.append(uri)
        for uri in uris:
            try:
                real_n = RealNeo4jService(uri, settings.neo4j_user, settings.neo4j_password)
                if real_n.is_live():
                    self.neo4j = real_n
                    self.modes["neo4j"] = "live"
                    agent_log("NEO4J", f"Connected {uri}")
                    break
            except Exception as exc:
                agent_log("NEO4J", f"{uri} failed: {exc}")

        if getattr(self.neo4j, "is_live", lambda: False)():
            count = self.neo4j.count_nodes()
            if count == 0:
                agent_log("NEO4J", "Graph empty — seeding ACME catalog")
                self.seeded_nodes = self.neo4j.seed()
            else:
                self.seeded_nodes = count
                agent_log("NEO4J", f"Graph already populated ({count} nodes)")

        for url in (settings.hindsight_url, "http://127.0.0.1:8888", "http://localhost:8888"):
            try:
                real_h = RealHindsightService(url, settings.hindsight_bank_id)
                if real_h.is_live():
                    self.hindsight = real_h
                    self.modes["hindsight"] = "live"
                    break
                self.hindsight = real_h
            except Exception:
                pass
        self.hindsight.seed_bank()

        if settings.groq_api_key:
            try:
                real_l = RealGroqService(settings)
                ok, _ = real_l.status()
                if ok:
                    self.llm = real_l
                    self.modes["llm"] = "live"
            except Exception:
                pass

    def health_payload(self) -> dict:
        n_ok, n_d = self.neo4j.status()
        h_ok, h_d = self.hindsight.status()
        l_ok, l_d = self.llm.status()
        n_live = getattr(self.neo4j, "is_live", lambda: False)()
        h_live = getattr(self.hindsight, "is_live", lambda: False)()
        return {
            "neo4j": "connected" if n_live else "disconnected",
            "hindsight": "connected" if h_live else "disconnected",
            "groq": "connected" if l_ok and self.modes["llm"] == "live" else "disconnected",
            "agent": "ready",
            "demo_mode": self.settings.demo_mode,
            "seeded_nodes": self.seeded_nodes or len(demo.NODES),
            "details": {"neo4j": n_d, "hindsight": h_d, "groq": l_d},
            "services": [
                ServiceStatus(name="Neo4j", mode=self.modes["neo4j"], healthy=n_ok, detail=n_d).model_dump(),
                ServiceStatus(name="Hindsight", mode=self.modes["hindsight"], healthy=h_ok, detail=h_d).model_dump(),
                ServiceStatus(name="LLM", mode=self.modes["llm"], healthy=l_ok, detail=l_d).model_dump(),
            ],
        }

    def system_status(self) -> SystemStatus:
        n_ok, n_d = self.neo4j.status()
        h_ok, h_d = self.hindsight.status()
        l_ok, l_d = self.llm.status()
        return SystemStatus(
            demo_mode=self.settings.demo_mode,
            services=[
                ServiceStatus(name="Neo4j", mode=self.modes["neo4j"], healthy=n_ok, detail=n_d),
                ServiceStatus(name="Hindsight", mode=self.modes["hindsight"], healthy=h_ok, detail=h_d),
                ServiceStatus(name="LLM", mode=self.modes["llm"], healthy=l_ok, detail=l_d),
            ],
        )


@lru_cache
def get_services() -> Services:
    return Services()
