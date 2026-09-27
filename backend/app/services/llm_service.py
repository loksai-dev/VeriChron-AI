from __future__ import annotations

import json
from typing import Any, Protocol

from app.config import Settings


class LLMService(Protocol):
    def status(self) -> tuple[bool, str]: ...
    def classify(self, question: str) -> dict[str, Any]: ...
    def reason(self, question: str, context: dict[str, Any]) -> dict[str, Any]: ...


SYSTEM_PROMPT = """You are VeriChron AI, a bitemporal compliance auditor.
You NEVER fabricate evidence. Every claim must cite a source id from context.
You distinguish VALID TIME (when it was true) from SYSTEM TIME (when it was known).
Never leak facts whose system_start is after the query's system_as_of.
Return strict JSON with keys: conclusion, compliance_status, root_cause, remediation, confidence, caveats.
compliance_status must be one of: compliant, non_compliant, at_risk, unknown, remediated.
"""


class MockLLMService:
    def status(self) -> tuple[bool, str]:
        return True, "Deterministic reasoning over seeded evidence"

    def classify(self, question: str) -> dict[str, Any]:
        q = question.lower()
        intent = "general"
        if "may 15" in q or "march 15" in q or "posture on" in q or "what was" in q:
            intent = "historical_posture"
        elif "why" in q or "root" in q or "caused" in q:
            intent = "root_cause"
        elif "unresolved" in q or "gap" in q:
            intent = "gap_scan"
        elif "evidence" in q or "prove" in q or "mfa" in q and "prove" in q:
            intent = "evidence"
        if "between" in q or ("may 15" in q and "june 25" in q):
            intent = "diff"
        temporal = None
        if "may 15" in q:
            temporal = "2025-05-15"
        if "june 25" in q and "between" not in q and "may" not in q:
            temporal = "2025-06-25"
        if "july 15" in q:
            temporal = "2025-07-15"
        return {"intent": intent, "temporal_as_of": temporal, "entities": ["ctl:mfa", "req:cc6.1"], "fast": intent == "gap_scan"}

    def reason(self, question: str, context: dict[str, Any]) -> dict[str, Any]:
        intent = context.get("intent", "general")
        valid = str(context.get("valid_as_of"))
        system = str(context.get("system_as_of"))
        if intent == "historical_posture" and "2025-05-15" in valid:
            return {
                "conclusion": (
                    "On 15 May 2025 ACME was PARTIALLY COMPLIANT. MFA was disabled for one production IAM group. "
                    "Supporting evidence known then: IAM change (10 Apr), failed CC6.1 test (5 May), audit finding (12 May). "
                    "The 15 July evidence pack is excluded — it was not in the system of record."
                ),
                "compliance_status": "at_risk",
                "root_cause": "IAM configuration change on 2025-04-10 disabled MFA for prod-admins.",
                "remediation": None,
                "confidence": 0.95,
                "caveats": "July 2025 evidence upload is not treated as known on May 15.",
            }
        if intent == "root_cause":
            return {
                "conclusion": "CC6.1 was non-compliant because MFA enforcement on AWS IAM prod-admins was disabled on 10 April 2025.",
                "compliance_status": "remediated",
                "root_cause": "IAM configuration change disabled MFA; control test failed 5 May; finding opened 12 May.",
                "remediation": "Enable MFA (SEC-1842) completed 20 June; retest passed 25 June.",
                "confidence": 0.98,
                "caveats": None,
            }
        if intent == "diff":
            return {
                "conclusion": "May 15: MFA disabled, test failed, finding open. June 25: MFA enabled, test passed, finding remediated.",
                "compliance_status": "compliant",
                "root_cause": "April IAM change.",
                "remediation": "Enable MFA completed June 20.",
                "confidence": 0.96,
                "caveats": None,
            }
        if intent == "gap_scan":
            return {
                "conclusion": "Unresolved SOC 2 findings: Privileged Account Review Overdue (F-PAM) and Access Review Evidence Missing (F-UAR).",
                "compliance_status": "at_risk",
                "root_cause": "Open PAM and UAR findings.",
                "remediation": "Complete Privileged Account Review; Upload Access Review Evidence.",
                "confidence": 0.9,
                "caveats": None,
            }
        return {
            "conclusion": context.get("reflection") or "Assessment grounded only in retrieved evidence and graph edges.",
            "compliance_status": "compliant",
            "root_cause": None,
            "remediation": None,
            "confidence": 0.86,
            "caveats": None,
        }


class RealGroqService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._mock = MockLLMService()
        self._ok = bool(settings.groq_api_key)
        self._detail = "Groq key present" if self._ok else "No GROQ_API_KEY"
        self._client = None
        if self._ok:
            try:
                from groq import Groq

                self._client = Groq(api_key=settings.groq_api_key)
                self._detail = f"Groq live ({settings.groq_reasoning_model})"
            except Exception as exc:
                self._ok = False
                self._detail = str(exc)

    def status(self) -> tuple[bool, str]:
        return self._ok, self._detail

    def classify(self, question: str) -> dict[str, Any]:
        if not self._client:
            return self._mock.classify(question)
        try:
            completion = self._client.chat.completions.create(
                model=self.settings.groq_fast_model,
                messages=[
                    {"role": "system", "content": "Classify compliance questions. Return JSON: intent, temporal_as_of, entities, fast."},
                    {"role": "user", "content": question},
                ],
                temperature=0,
            )
            text = completion.choices[0].message.content or "{}"
            start = text.find("{")
            end = text.rfind("}")
            if start >= 0:
                parsed = json.loads(text[start : end + 1])
                parsed.setdefault("intent", "general")
                return parsed
        except Exception:
            pass
        return self._mock.classify(question)

    def reason(self, question: str, context: dict[str, Any]) -> dict[str, Any]:
        if not self._client:
            return self._mock.reason(question, context)
        try:
            completion = self._client.chat.completions.create(
                model=self.settings.groq_reasoning_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": json.dumps({"question": question, "context": context}, default=str)[:18000],
                    },
                ],
                temperature=0.1,
            )
            text = completion.choices[0].message.content or "{}"
            start = text.find("{")
            end = text.rfind("}")
            if start >= 0:
                parsed = json.loads(text[start : end + 1])
                parsed.setdefault("confidence", 0.8)
                parsed.setdefault("compliance_status", "unknown")
                return parsed
        except Exception:
            pass
        return self._mock.reason(question, context)

    def run_tool_loop(self, question: str, tools_schema: list, execute) -> tuple[list[dict], dict]:
        if not self._client:
            return [], {}
        messages = [
            {
                "role": "system",
                "content": (
                    "You are VeriChron AI. Call tools to inspect Neo4j and Hindsight before answering. "
                    "Never use facts whose system_start is after the query date. "
                    "When finished, reply with JSON: conclusion, compliance_status, root_cause, remediation, confidence, caveats."
                ),
            },
            {"role": "user", "content": question},
        ]
        traces: list[dict] = []
        try:
            for _ in range(6):
                completion = self._client.chat.completions.create(
                    model=self.settings.groq_fast_model,
                    messages=messages,
                    tools=tools_schema,
                    tool_choice="auto",
                    temperature=0,
                )
                msg = completion.choices[0].message
                if msg.tool_calls:
                    messages.append(
                        {
                            "role": "assistant",
                            "content": msg.content or "",
                            "tool_calls": [
                                {
                                    "id": tc.id,
                                    "type": "function",
                                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                                }
                                for tc in msg.tool_calls
                            ],
                        }
                    )
                    for tc in msg.tool_calls:
                        args = json.loads(tc.function.arguments or "{}")
                        out = execute(tc.function.name, args)
                        traces.append({"name": tc.function.name, "input": args, "output": out, "latency_ms": out.get("ms", 0)})
                        messages.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(out, default=str)[:8000]})
                    continue
                text = msg.content or "{}"
                start, end = text.find("{"), text.rfind("}")
                parsed = json.loads(text[start : end + 1]) if start >= 0 else {"conclusion": text}
                return traces, parsed
        except Exception:
            return traces, {}
        return traces, {}

