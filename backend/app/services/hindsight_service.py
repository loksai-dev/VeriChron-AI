from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Protocol
from uuid import uuid4

from app.data import demo
from app.models.schemas import MemoryFact, MentalModel, Observation


class HindsightService(Protocol):
    def status(self) -> tuple[bool, str]: ...
    def retain(self, content: str, *, context: str, timestamp: str | None, document_id: str | None, metadata: dict[str, str] | None = None) -> dict[str, Any]: ...
    def recall(self, query: str, *, valid_as_of: date | None = None, system_as_of: date | None = None) -> dict[str, Any]: ...
    def reflect(self, query: str, *, valid_as_of: date | None = None, system_as_of: date | None = None) -> dict[str, Any]: ...
    def create_mental_model(self, name: str, source_query: str) -> MentalModel: ...
    def list_mental_models(self) -> list[MentalModel]: ...
    def refresh_mental_model(self, model_id: str) -> MentalModel: ...
    def observations(self) -> list[Observation]: ...
    def facts(self) -> list[MemoryFact]: ...


class MockHindsightService:
    def status(self) -> tuple[bool, str]:
        return True, "In-process memory bank (Hindsight server not connected)"

    def is_live(self) -> bool:
        return False

    def seed_bank(self) -> int:
        for item in demo.HINDSIGHT_MEMORIES:
            existing = next((f for f in demo.MEMORY_FACTS if f.id == item["document_id"]), None)
            if existing:
                continue
            self.retain(
                item["content"],
                context="seed",
                timestamp=item["timestamp"],
                document_id=item["document_id"],
                metadata={"entity_id": "CC6.1", "fact_type": "seed"},
            )
        return len(demo.MEMORY_FACTS)

    def retain(self, content: str, *, context: str, timestamp: str | None, document_id: str | None, metadata: dict[str, str] | None = None) -> dict[str, Any]:
        fid = document_id or f"mem:{uuid4().hex[:8]}"
        demo.MEMORY_FACTS[:] = [f for f in demo.MEMORY_FACTS if f.id != fid]
        vs = date.fromisoformat(timestamp[:10]) if timestamp else date.today()
        se = None
        ss = vs
        if fid == "mem-upload-jul":
            ss = date(2025, 7, 15)
            vs = date(2025, 4, 10)
        fact = MemoryFact(
            id=fid,
            content=content[:800],
            entity_id=(metadata or {}).get("entity_id", "CC6.1"),
            fact_type=(metadata or {}).get("fact_type", "seed"),
            source=context,
            valid_start=vs,
            system_start=ss,
            system_end=se,
            confidence=0.97,
        )
        demo.MEMORY_FACTS.append(fact)
        return {"id": fact.id, "status": "retained", "layer": "raw_fact"}

    def recall(self, query: str, *, valid_as_of: date | None = None, system_as_of: date | None = None) -> dict[str, Any]:
        q = query.lower()
        facts = demo.MEMORY_FACTS
        if valid_as_of and system_as_of:
            facts = [f for f in facts if demo.visible_at(f, valid_as_of, system_as_of)]
        scored = []
        for f in facts:
            score = 0.0
            blob = (f.content + f.entity_id + f.fact_type).lower()
            for token in ("cc6.1", "mfa", "iam", "finding", "may", "posture", "gap", "evidence"):
                if token in q and token in blob:
                    score += 0.2
            if "cc6" in q and "cc6" in blob:
                score += 0.3
            if score == 0 and any(t in blob for t in q.split() if len(t) > 3):
                score = 0.15
            if score:
                scored.append((score, f))
        scored.sort(key=lambda x: x[0], reverse=True)
        selected = [f for _, f in scored[:8]] or facts[:5]
        obs = demo.OBSERVATIONS
        if valid_as_of and system_as_of:
            obs = [o for o in obs if o.system_start <= system_as_of]
        return {
            "facts": [f.model_dump(mode="json") for f in selected],
            "observations": [o.model_dump(mode="json") for o in obs[:4]],
            "mental_models": [m.model_dump(mode="json") for m in demo.MENTAL_MODELS[:2]],
        }

    def reflect(self, query: str, *, valid_as_of: date | None = None, system_as_of: date | None = None) -> dict[str, Any]:
        recalled = self.recall(query, valid_as_of=valid_as_of, system_as_of=system_as_of)
        q = query.lower()
        if valid_as_of == date(2025, 5, 15) or "may 15" in q:
            text = (
                "As of 2025-05-15 ACME CC6.1 was PARTIALLY COMPLIANT. MFA was disabled for one production IAM group. "
                "Known: 10 Apr IAM change, 5 May failed test, 12 May finding. "
                "Not known: 15 Jul evidence pack (system_start 2025-07-15)."
            )
        elif "why" in q or "root" in q or "non-compliant" in q:
            text = (
                "Root cause: IAM configuration change on 2025-04-10 disabled MFA. "
                "Path: CC6.1 → MFA Enforcement → AWS IAM → CloudTrail → failed test → finding → Enable MFA."
            )
        elif "gap" in q or "unresolved" in q:
            text = "Unresolved: F-PAM Privileged Account Review Overdue; F-UAR Access Review Evidence Missing. CC6.1 MFA finding is remediated."
        else:
            text = "CC6.1 remediated June 2025. Residual: PAM review and UAR evidence."
        return {"reflection": text, "citations": recalled["facts"][:5], "ladder": ["mental_model", "observation", "raw_fact"]}

    def create_mental_model(self, name: str, source_query: str) -> MentalModel:
        model = MentalModel(
            id=f"mm:{uuid4().hex[:6]}",
            name=name,
            query=source_query,
            content=self.reflect(source_query)["reflection"],
            last_refreshed=datetime.now(timezone.utc),
            evidence_count=len(demo.EVIDENCE),
            confidence=0.9,
            status="compliant",
            supporting_evidence=[e.id for e in demo.EVIDENCE[:3]],
            recent_changes=["Created from reflect()"],
            versions=[{"version": 1, "at": date.today().isoformat(), "note": "create_mental_model"}],
        )
        demo.MENTAL_MODELS.append(model)
        return model

    def list_mental_models(self) -> list[MentalModel]:
        return list(demo.MENTAL_MODELS)

    def refresh_mental_model(self, model_id: str) -> MentalModel:
        model = next((m for m in demo.MENTAL_MODELS if m.id == model_id), None)
        if not model:
            raise KeyError(model_id)
        reflected = self.reflect(model.query)
        model.content = reflected["reflection"]
        model.last_refreshed = datetime.now(timezone.utc)
        model.versions.append(
            {"version": len(model.versions) + 1, "at": date.today().isoformat(), "note": "Incremental refresh"}
        )
        return model

    def observations(self) -> list[Observation]:
        return list(demo.OBSERVATIONS)

    def facts(self) -> list[MemoryFact]:
        return list(demo.MEMORY_FACTS)


class RealHindsightService:
    def __init__(self, base_url: str, bank_id: str):
        self.base_url = base_url.rstrip("/")
        self.bank_id = bank_id
        self._mock = MockHindsightService()
        self._client = None
        self._ok = False
        self._detail = ""
        try:
            import httpx

            r = httpx.get(f"{self.base_url}/health", timeout=2.0)
            self._ok = r.status_code < 500
            self._detail = f"Hindsight {base_url} bank={bank_id}"
        except Exception as exc:
            self._detail = f"Unreachable ({exc}); using memory fallback for reads"

    def is_live(self) -> bool:
        return self._ok

    def seed_bank(self) -> int:
        n = self._mock.seed_bank()
        if self._ok:
            for item in demo.HINDSIGHT_MEMORIES:
                self.retain(
                    item["content"],
                    context="seed",
                    timestamp=item["timestamp"],
                    document_id=item["document_id"],
                    metadata={"entity_id": "CC6.1", "fact_type": "seed"},
                )
        return n

    def status(self) -> tuple[bool, str]:
        return self._ok, self._detail

    def _try_client_retain(self, **kwargs) -> dict[str, Any] | None:
        try:
            from hindsight import Hindsight

            client = Hindsight(base_url=self.base_url)
            client.retain(bank_id=self.bank_id, **kwargs)
            return {"status": "retained", "bank_id": self.bank_id}
        except Exception:
            return None

    def retain(self, content: str, **kwargs) -> dict[str, Any]:
        live = self._try_client_retain(
            content=content,
            context=kwargs.get("context"),
            timestamp=kwargs.get("timestamp"),
            document_id=kwargs.get("document_id"),
        )
        local = self._mock.retain(content, **kwargs)
        if live:
            local["live"] = live
        return local

    def recall(self, query: str, **kwargs) -> dict[str, Any]:
        if self._ok:
            try:
                import httpx

                r = httpx.post(
                    f"{self.base_url}/v1/banks/{self.bank_id}/recall",
                    json={"query": query},
                    timeout=8.0,
                )
                if r.status_code == 200:
                    data = r.json()
                    data.setdefault("facts", [])
                    return data
            except Exception:
                pass
        return self._mock.recall(query, **kwargs)

    def reflect(self, query: str, **kwargs) -> dict[str, Any]:
        if self._ok:
            try:
                import httpx

                r = httpx.post(
                    f"{self.base_url}/v1/banks/{self.bank_id}/reflect",
                    json={"query": query},
                    timeout=30.0,
                )
                if r.status_code == 200:
                    return r.json()
            except Exception:
                pass
        return self._mock.reflect(query, **kwargs)

    def create_mental_model(self, name: str, source_query: str) -> MentalModel:
        return self._mock.create_mental_model(name, source_query)

    def list_mental_models(self) -> list[MentalModel]:
        return self._mock.list_mental_models()

    def refresh_mental_model(self, model_id: str) -> MentalModel:
        return self._mock.refresh_mental_model(model_id)

    def observations(self) -> list[Observation]:
        return self._mock.observations()

    def facts(self) -> list[MemoryFact]:
        return self._mock.facts()
