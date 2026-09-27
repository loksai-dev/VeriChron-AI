from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Protocol
from uuid import uuid4

import httpx

from app.data import demo
from app.logging_util import agent_log
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


def _iso_ts(value: str | None) -> str | None:
    if not value:
        return None
    raw = str(value).strip()
    if len(raw) == 10:
        return f"{raw}T00:00:00Z"
    return raw


def normalize_recall(payload: dict[str, Any]) -> dict[str, Any]:
    """Map Hindsight Cloud recall JSON onto the facts/observations shape the agent expects."""
    results = payload.get("results") or payload.get("facts") or []
    facts: list[dict[str, Any]] = []
    for item in results:
        if not isinstance(item, dict):
            continue
        text = item.get("text") or item.get("content") or ""
        occurred = (item.get("occurred_start") or item.get("mentioned_at") or "")[:10]
        facts.append(
            {
                "id": item.get("id") or "",
                "content": text,
                "entity_id": ((item.get("entities") or [None])[0] if item.get("entities") else None) or item.get("entity_id") or "",
                "fact_type": item.get("type") or "world",
                "source": "hindsight-cloud",
                "valid_start": occurred or None,
                "system_start": occurred or None,
                "confidence": 0.95,
                "layer": "raw_fact",
            }
        )
    observations = []
    entities = payload.get("entities") or {}
    if isinstance(entities, dict):
        for name, ent in list(entities.items())[:8]:
            obs_list = (ent or {}).get("observations") or []
            for obs in obs_list[:2]:
                observations.append(
                    {
                        "id": f"obs:{name}",
                        "content": obs.get("text") if isinstance(obs, dict) else str(obs),
                        "supporting_facts": [],
                        "confidence": 0.9,
                        "layer": "observation",
                    }
                )
    out = dict(payload)
    out["facts"] = facts
    out["observations"] = observations or out.get("observations") or []
    out["mental_models"] = out.get("mental_models") or []
    out["source"] = "hindsight-cloud"
    return out


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
            "source": "mock",
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
        return {"reflection": text, "citations": recalled["facts"][:5], "ladder": ["mental_model", "observation", "raw_fact"], "source": "mock"}

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
    """Hindsight Cloud (or self-host) HTTP client: retain / recall / reflect."""

    def __init__(self, base_url: str, bank_id: str, api_key: str = ""):
        self.base_url = base_url.rstrip("/")
        self.bank_id = bank_id
        self.api_key = api_key.strip()
        self._mock = MockHindsightService()
        self._ok = False
        self._detail = ""
        self._headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if self.api_key:
            self._headers["Authorization"] = f"Bearer {self.api_key}"
            self._headers["X-Bank-Id"] = bank_id
        self._probe()

    def _bank(self, suffix: str) -> str:
        return f"{self.base_url}/v1/default/banks/{self.bank_id}{suffix}"

    def _probe(self) -> None:
        try:
            r = httpx.get(f"{self.base_url}/health", headers=self._headers, timeout=20.0)
            if r.status_code < 500:
                self._ok = True
                self._detail = f"Hindsight Cloud {self.base_url} bank={self.bank_id}"
            else:
                self._detail = f"Hindsight health HTTP {r.status_code}"
        except Exception as exc:
            self._detail = f"Unreachable ({exc}); using memory fallback for reads"

    def is_live(self) -> bool:
        return self._ok

    def status(self) -> tuple[bool, str]:
        return self._ok, self._detail

    def _request(self, method: str, url: str, json_body: dict | None, timeout: float) -> httpx.Response:
        return httpx.request(method, url, headers=self._headers, json=json_body, timeout=timeout)

    def seed_bank(self) -> int:
        n = self._mock.seed_bank()
        if not self._ok:
            return n
        items = []
        for mem in demo.HINDSIGHT_MEMORIES:
            ts = mem["timestamp"]
            extra = ""
            if mem["document_id"] == "mem-upload-jul":
                extra = " This evidence entered the GRC system of record on 2025-07-15 (system time). It must not be treated as known on 2025-05-15."
            items.append(
                {
                    "content": mem["content"] + extra,
                    "context": "verichron-acme-seed",
                    "document_id": mem["document_id"],
                    "timestamp": _iso_ts(ts),
                    "metadata": {"entity_id": "CC6.1", "fact_type": "seed"},
                }
            )
        try:
            agent_log("HINDSIGHT", f"Seeding {len(items)} memories to Cloud bank")
            r = self._request("POST", self._bank("/memories"), {"items": items, "async": True}, 30.0)
            if r.status_code >= 400:
                agent_log("HINDSIGHT", f"Seed retain HTTP {r.status_code}: {r.text[:240]}")
            else:
                agent_log("HINDSIGHT", "Cloud retain queued")
            self._ensure_mental_model()
        except Exception as exc:
            agent_log("HINDSIGHT", f"Seed retain failed: {exc}")
        return n

    def _ensure_mental_model(self) -> None:
        try:
            r = self._request("GET", self._bank("/mental-models"), None, 15.0)
            if r.status_code == 200:
                items = (r.json() or {}).get("items") or []
                if any(i.get("id") == "soc2-cc61-access" for i in items):
                    return
            self._request(
                "POST",
                self._bank("/mental-models"),
                {
                    "id": "soc2-cc61-access",
                    "name": "SOC 2 CC6.1 Access Control Posture",
                    "source_query": "What is the current and historical SOC 2 CC6.1 access control posture for ACME, including May 15 2025?",
                },
                20.0,
            )
        except Exception as exc:
            agent_log("HINDSIGHT", f"Mental model ensure skipped: {exc}")

    def retain(self, content: str, **kwargs) -> dict[str, Any]:
        local = self._mock.retain(content, **kwargs)
        if not self._ok:
            return local
        item: dict[str, Any] = {
            "content": content,
            "context": kwargs.get("context") or "verichron",
            "document_id": kwargs.get("document_id"),
            "timestamp": _iso_ts(kwargs.get("timestamp")),
        }
        meta = kwargs.get("metadata")
        if meta:
            item["metadata"] = meta
        item = {k: v for k, v in item.items() if v is not None}
        try:
            r = self._request("POST", self._bank("/memories"), {"items": [item], "async": False}, 60.0)
            local["live"] = {"http": r.status_code, "ok": r.status_code < 400, "bank_id": self.bank_id}
            if r.status_code >= 400:
                agent_log("HINDSIGHT", f"retain HTTP {r.status_code}: {r.text[:200]}")
                local["live"]["body"] = r.text[:200]
            else:
                try:
                    local["live"]["response"] = r.json()
                except Exception:
                    pass
        except Exception as exc:
            local["live"] = {"ok": False, "error": str(exc)}
        return local

    def recall(self, query: str, **kwargs) -> dict[str, Any]:
        fallback = self._mock.recall(query, **kwargs)
        if not self._ok:
            return fallback
        body: dict[str, Any] = {"query": query, "budget": "mid", "max_tokens": 2048}
        vd: date | None = kwargs.get("valid_as_of")
        sd: date | None = kwargs.get("system_as_of")
        if sd:
            body["query_timestamp"] = f"{sd.isoformat()}T12:00:00Z"
        if vd:
            body["temporal_window"] = {
                "start": f"{vd.isoformat()}T00:00:00Z",
                "end": f"{vd.isoformat()}T23:59:59Z",
            }
        try:
            r = self._request("POST", self._bank("/memories/recall"), body, 25.0)
            if r.status_code == 200:
                live = normalize_recall(r.json() if r.content else {})
                live["source"] = "hindsight-cloud"
                live["http"] = 200
                return live
            agent_log("HINDSIGHT", f"recall HTTP {r.status_code}: {r.text[:200]}")
            return {"facts": [], "observations": [], "source": "hindsight-error", "http": r.status_code, "error": r.text[:200]}
        except Exception as exc:
            agent_log("HINDSIGHT", f"recall failed: {exc}")
            return {"facts": [], "observations": [], "source": "hindsight-error", "error": str(exc)}

    def reflect(self, query: str, **kwargs) -> dict[str, Any]:
        fallback = self._mock.reflect(query, **kwargs)
        if not self._ok:
            return fallback
        temporal = ""
        vd = kwargs.get("valid_as_of")
        sd = kwargs.get("system_as_of")
        if vd or sd:
            temporal = (
                f" Temporal constraint: valid time {vd}, system time {sd}. "
                "Do not use facts the organization only learned after system time. "
                "July 15 2025 evidence pack is unknown on May 15 2025."
            )
        body = {
            "query": (query or "") + temporal,
            "budget": "low",
            "max_tokens": 2048,
            "include": {"facts": {}},
        }
        try:
            r = self._request("POST", self._bank("/reflect"), body, 45.0)
            if r.status_code == 200:
                data = r.json() if r.content else {}
                text = data.get("text") or data.get("reflection") or ""
                based = data.get("based_on") or {}
                memories = []
                if isinstance(based, dict):
                    memories = based.get("memories") or based.get("facts") or []
                return {
                    "reflection": text or "(Hindsight reflect returned an empty synthesis.)",
                    "citations": memories[:8],
                    "ladder": ["mental_model", "observation", "raw_fact"],
                    "source": "hindsight-cloud",
                    "raw": {"keys": list(data.keys())},
                }
            agent_log("HINDSIGHT", f"reflect HTTP {r.status_code}: {r.text[:200]}")
        except Exception as exc:
            agent_log("HINDSIGHT", f"reflect failed: {exc}")
        return {"reflection": "", "citations": [], "source": "hindsight-error", "error": "reflect failed"}

    def create_mental_model(self, name: str, source_query: str) -> MentalModel:
        model = self._mock.create_mental_model(name, source_query)
        if self._ok:
            try:
                self._request(
                    "POST",
                    self._bank("/mental-models"),
                    {"name": name, "source_query": source_query},
                    20.0,
                )
            except Exception:
                pass
        return model

    def list_mental_models(self) -> list[MentalModel]:
        local = self._mock.list_mental_models()
        if not self._ok:
            return local
        try:
            r = self._request("GET", self._bank("/mental-models"), None, 15.0)
            if r.status_code != 200:
                return local
            items = (r.json() or {}).get("items") or []
            extra: list[MentalModel] = []
            for it in items:
                extra.append(
                    MentalModel(
                        id=it.get("id") or f"mm:{uuid4().hex[:6]}",
                        name=it.get("name") or "Cloud mental model",
                        query=it.get("source_query") or "",
                        content=(it.get("content") or "")[:4000],
                        last_refreshed=datetime.now(timezone.utc),
                        evidence_count=0,
                        confidence=0.9,
                        status="unknown",
                        supporting_evidence=[],
                        recent_changes=["Hindsight Cloud"],
                        versions=[],
                    )
                )
            by_id = {m.id: m for m in local}
            for m in extra:
                by_id[m.id] = m
            return list(by_id.values())
        except Exception:
            return local

    def refresh_mental_model(self, model_id: str) -> MentalModel:
        aliases = [model_id, "soc2-cc61-access", "mm:soc2-cc61"]
        last_err: Exception | None = None
        if self._ok:
            for mid in aliases:
                try:
                    r = self._request("POST", self._bank(f"/mental-models/{mid}/refresh"), {}, 20.0)
                    if r.status_code < 400:
                        break
                except Exception as exc:
                    last_err = exc
        for mid in aliases:
            try:
                return self._mock.refresh_mental_model(mid)
            except KeyError:
                continue
        if last_err:
            raise last_err
        raise KeyError(model_id)

    def observations(self) -> list[Observation]:
        return self._mock.observations()

    def facts(self) -> list[MemoryFact]:
        return self._mock.facts()
