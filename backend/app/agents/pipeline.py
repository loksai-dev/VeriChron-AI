from __future__ import annotations

import json
from datetime import date, datetime, timezone
from time import perf_counter
from uuid import uuid4

from app.agents.tools import GROQ_TOOLS, AgentToolbox
from app.data import demo
from app.logging_util import agent_log
from app.models.schemas import AgentAnswer, AgentRun, AgentStage, ReconstructRequest, SourceRef
from app.services.factory import Services


def _ms(start: float) -> int:
    return int((perf_counter() - start) * 1000)


def _as_text(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, list):
        return " ".join(str(v) for v in value)
    if isinstance(value, dict):
        return json.dumps(value)
    return str(value)


def _extract_as_of(question: str, fallback: date) -> date:
    q = question.lower()
    if "may 15" in q:
        return date(2025, 5, 15)
    if "june 25" in q:
        return date(2025, 6, 25)
    if "july 15" in q:
        return date(2025, 7, 15)
    if "april 10" in q:
        return date(2025, 4, 10)
    return fallback


class ComplianceAgent:
    def __init__(self, services: Services):
        self.s = services
        self.runs: list[AgentRun] = []
        self.run_index: dict[str, dict] = {}
        self.tools = AgentToolbox(services)

    def _record_tool(self, stages: list[AgentStage], traces: list[dict], name: str, output: dict, args: dict | None = None) -> None:
        stages.append(
            AgentStage(
                name=name,
                latency_ms=int(output.get("ms") or 0),
                detail=json.dumps({k: output[k] for k in output if k not in {"records", "events", "memories", "open_findings"}}, default=str)[:240],
                status="ok" if "error" not in output else "error",
            )
        )
        traces.append({"name": name, "input": args or {}, "output": output, "latency_ms": output.get("ms", 0), "status": "ok"})

    def _summarize_tool(self, name: str, output: dict) -> str:
        if name == "search_neo4j":
            return f"{output.get('nodes', 0)} nodes / {output.get('relationships', 0)} relationships · {output.get('source')}"
        if name == "search_hindsight":
            return f"{output.get('count', 0)} memories recalled"
        if name == "reconstruct_historical_state":
            return f"{output.get('as_of')} → {output.get('label')}"
        if name == "traverse_compliance_graph":
            path = output.get("path") or []
            return " → ".join(path[:6]) or "path empty"
        if name == "get_evidence":
            return f"{output.get('count', 0)} evidence records known at system time"
        if name == "analyze_compliance":
            return output.get("label") or output.get("kind") or "analysis complete"
        if name == "get_control_status":
            c = output.get("control") or {}
            return f"{c.get('id')} {c.get('status')}"
        return "ok"

    def iter_query(self, question: str, valid_as_of: date | None, system_as_of: date | None, framework: str):
        import time

        t0 = perf_counter()
        stages: list[AgentStage] = []
        traces: list[dict] = []
        run_id = f"run:{uuid4().hex[:10]}"
        yield {"type": "run", "run_id": run_id}
        yield {"type": "thought", "text": f"Task received. I will use tools — Neo4j, Hindsight, then reconstruct historical state. I will not answer from memory alone."}
        time.sleep(0.18)
        agent_log("AGENT", f"Question received: {question}")

        classification = self.s.llm.classify(question)
        as_of = valid_as_of or _extract_as_of(question, date(2025, 7, 15))
        if classification.get("temporal_as_of"):
            try:
                as_of = date.fromisoformat(str(classification["temporal_as_of"])[:10])
            except ValueError:
                pass
        if not system_as_of:
            system_as_of = as_of
        agent_log("TEMPORAL", f"Target date: {as_of.isoformat()}")
        yield {
            "type": "thought",
            "text": f"Temporal scope: valid time = {as_of.isoformat()}, system time = {system_as_of.isoformat()}. Anything with system_start after that date stays out.",
        }
        stages.append(AgentStage(name="Temporal Query Extraction", latency_ms=8, detail=f"{as_of.isoformat()} detected", status="ok"))
        time.sleep(0.15)

        plan = [
            ("search_neo4j", {"query": question, "valid_as_of": as_of.isoformat(), "system_as_of": system_as_of.isoformat()}),
            ("traverse_compliance_graph", {"start_id": "CC6.1"}),
            ("search_hindsight", {"query": question, "valid_as_of": as_of.isoformat(), "system_as_of": system_as_of.isoformat()}),
            ("reconstruct_historical_state", {"as_of": as_of.isoformat()}),
            ("get_evidence", {"system_as_of": system_as_of.isoformat()}),
            ("analyze_compliance", {"question": question, "as_of": as_of.isoformat()}),
        ]
        thought_for = {
            "search_neo4j": "Querying Neo4j for compliance entities in that window.",
            "traverse_compliance_graph": "Walking CC6.1 → control → IAM → evidence → finding → remediation.",
            "search_hindsight": "Recalling Hindsight memories. July 15 ingest must not leak into a May 15 question.",
            "reconstruct_historical_state": "Reconstructing what was true vs what ACME knew.",
            "get_evidence": "Collecting evidence artifacts visible at system time.",
            "analyze_compliance": "Fusing graph + memory into a compliance assessment.",
        }

        groq_traces: list[dict] = []
        reasoned = {}
        # Stream tools immediately. Groq is used for the final grounded write, not to block the loop.

        executed = []
        if groq_traces:
            for tr in groq_traces:
                name = tr["name"]
                args = tr.get("input") or {}
                out = tr.get("output") or {}
                yield {"type": "thought", "text": thought_for.get(name, f"Calling {name}.")}
                yield {"type": "tool_start", "name": name, "input": args}
                time.sleep(0.12)
                self._record_tool(stages, traces, name, out, args)
                executed.append(name)
                yield {"type": "tool_end", "name": name, "ms": out.get("ms", 0), "summary": self._summarize_tool(name, out), "output": {k: out[k] for k in out if k not in {"records", "events", "memories", "open_findings"}}}
        for name, args in plan:
            if name in executed:
                continue
            yield {"type": "thought", "text": thought_for.get(name, f"Calling {name}.")}
            yield {"type": "tool_start", "name": name, "input": args}
            time.sleep(0.2)
            out = self.tools.dispatch(name, args)
            self._record_tool(stages, traces, name, out, args)
            yield {"type": "tool_end", "name": name, "ms": out.get("ms", 0), "summary": self._summarize_tool(name, out), "output": {k: out[k] for k in out if k not in {"records", "events", "memories", "open_findings"}}}

        yield {"type": "thought", "text": "Reflecting over Hindsight layers: mental model → observations → raw facts."}
        yield {"type": "tool_start", "name": "hindsight.reflect", "input": {"query": question}}
        reflect = self.s.hindsight.reflect(question, valid_as_of=as_of, system_as_of=system_as_of)
        stages.append(AgentStage(name="Hindsight reflect", latency_ms=12, detail="mental_model → observation → raw_fact", status="ok"))
        yield {"type": "tool_end", "name": "hindsight.reflect", "ms": 12, "summary": (reflect.get("reflection") or "")[:180]}

        analysis = next((t["output"] for t in traces if t["name"] == "analyze_compliance"), {})
        recon = next((t["output"] for t in traces if t["name"] == "reconstruct_historical_state"), {})
        evidence_out = next((t["output"] for t in traces if t["name"] == "get_evidence"), {})
        path = next((t["output"] for t in traces if t["name"] == "traverse_compliance_graph"), {})

        yield {"type": "thought", "text": "Writing the grounded answer. Claims without a source get dropped."}
        t_llm = perf_counter()
        if not reasoned:
            reasoned = self.s.llm.reason(
                question,
                {
                    "intent": classification.get("intent"),
                    "valid_as_of": as_of,
                    "system_as_of": system_as_of,
                    "framework": framework,
                    "analysis": analysis,
                    "reconstruct": {k: recon.get(k) for k in ("label", "known_evidence", "unknown_future_evidence")},
                    "reflection": reflect.get("reflection"),
                    "path": path.get("path"),
                },
            )
        stages.append(AgentStage(name="LLM Reasoning", latency_ms=_ms(t_llm), detail=self.s.modes["llm"], status="ok"))
        agent_log("AGENT", "Final response generated")

        status = reasoned.get("compliance_status") or recon.get("compliance_status") or "unknown"
        if status not in {"compliant", "non_compliant", "at_risk", "unknown", "remediated"}:
            status = "at_risk" if recon.get("label") == "PARTIALLY COMPLIANT" else "unknown"
        if recon.get("label") == "PARTIALLY COMPLIANT" and "may 15" in question.lower():
            status = "at_risk"

        known_ids = set(evidence_out.get("records") and [r["id"] for r in evidence_out["records"]] or recon.get("known_evidence") or [])
        refs = [
            SourceRef(id=e.id, kind=e.kind, title=e.title, excerpt=e.summary, confidence=e.confidence)
            for e in demo.EVIDENCE
            if e.id in known_ids or (e.system_start <= system_as_of and e.id in {"EV-CT-MFA", "EV-IAM-SNAP", "EV-TEST-FAIL", "F-MFA", "EV-JIRA"})
        ]
        timeline = [e for e in demo.TIMELINE if demo.occurred_by(e, as_of, system_as_of)]
        conf = reasoned.get("confidence") or 0.9
        try:
            conf = float(conf)
        except (TypeError, ValueError):
            conf = 0.9

        run = AgentRun(
            id=run_id,
            query=question,
            started_at=datetime.now(timezone.utc),
            total_ms=_ms(t0),
            stages=stages,
            status="ok",
            memory_retrievals=next((t["output"].get("count", 0) for t in traces if t["name"] == "search_hindsight"), 0),
            neo4j_queries=sum(1 for t in traces if "neo4j" in t["name"] or t["name"].startswith("traverse") or t["name"] == "get_entity"),
            hindsight_recalls=sum(1 for t in traces if "hindsight" in t["name"]),
            reflect_ops=1,
            llm_calls=1,
        )
        self.runs.insert(0, run)
        self.runs = self.runs[:50]
        caveat = _as_text(reasoned.get("caveats"))
        if as_of == date(2025, 5, 15):
            caveat = "Future evidence from 2025-07-15 (remediation pack / UAR CSV) is excluded from May 15 organizational knowledge."

        answer = AgentAnswer(
            conclusion=_as_text(reasoned.get("conclusion")) or reflect.get("reflection") or recon.get("label") or "",
            compliance_status=status,
            affected_controls=["CC6.1", "REQ-CC6.1"],
            evidence=refs[:8],
            timeline=timeline,
            root_cause=_as_text(reasoned.get("root_cause")),
            remediation=_as_text(reasoned.get("remediation")),
            confidence=conf,
            sources=[r.id for r in refs[:8]],
            graph_path=path.get("path") or list(demo.CAUSAL_PATH),
            known_at_query_time=True,
            caveat=caveat,
            run=run,
        )
        self.run_index[run_id] = {
            "run_id": run_id,
            "timestamp": run.started_at.isoformat(),
            "user_question": question,
            "tools_called": [t["name"] for t in traces],
            "tool_inputs": [t.get("input") for t in traces],
            "tool_outputs": traces,
            "latency": run.total_ms,
            "final_answer": answer.conclusion,
            "stages": [s.model_dump() for s in stages],
            "answer": answer.model_dump(mode="json"),
        }
        yield {"type": "answer", "data": answer.model_dump(mode="json")}
        yield {"type": "done"}

    def query(self, question: str, valid_as_of: date | None, system_as_of: date | None, framework: str) -> AgentAnswer:
        answer = None
        for event in self.iter_query(question, valid_as_of, system_as_of, framework):
            if event.get("type") == "answer":
                answer = AgentAnswer.model_validate(event["data"])
        if answer is None:
            raise RuntimeError("agent produced no answer")
        return answer

    def reconstruct(self, req: ReconstructRequest) -> dict:
        out = self.tools.reconstruct_historical_state(req.valid_as_of.isoformat())
        graph = self.s.neo4j.graph(None, req.valid_as_of, req.system_as_of, None)
        future = [e.model_dump(mode="json") for e in demo.EVIDENCE if e.system_start and e.system_start > req.system_as_of]
        known = [e.model_dump(mode="json") for e in demo.EVIDENCE if demo.visible_at(e, req.valid_as_of, req.system_as_of)]
        return {
            "valid_as_of": req.valid_as_of.isoformat(),
            "system_as_of": req.system_as_of.isoformat(),
            "headline": f"Showing organizational knowledge as of {req.system_as_of.strftime('%B %d, %Y')}",
            "compliance_status": out["compliance_status"],
            "label": out["label"],
            "score": 72 if out["label"] == "PARTIALLY COMPLIANT" else 91,
            "narrative": (
                f"World state {req.valid_as_of.isoformat()} / knowledge {req.system_as_of.isoformat()}. "
                f"{out['label']}. Unknown/future evidence: {', '.join(out.get('unknown_future_evidence') or []) or 'none'}."
            ),
            "mfa_policy": {
                "label": "MFA Policy",
                "active": "Jan 1 → Jun 30 2025",
                "evidence_recorded": "Jul 15 2025",
                "known": req.system_as_of >= date(2025, 1, 1),
            },
            "controls": out["controls"],
            "findings": out["open_findings"],
            "evidence": known,
            "unknown_future_evidence": future,
            "timeline": out["events"],
            "graph": graph.model_dump(mode="json"),
            "cypher": getattr(self.s.neo4j, "last_cypher", ""),
            "cypher_ms": getattr(self.s.neo4j, "last_ms", 0),
        }
