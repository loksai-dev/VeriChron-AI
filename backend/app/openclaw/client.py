from __future__ import annotations

import json
from typing import Any, Iterator

import httpx

from app.config import Settings
from app.logging_util import agent_log


CLIENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": name,
            "description": desc,
            "parameters": {
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "valid_as_of": {"type": "string", "description": "ISO date YYYY-MM-DD; required; no silent default"},
                    "system_as_of": {"type": "string", "description": "ISO date YYYY-MM-DD; required; independent of valid_as_of"},
                    "query": {"type": "string"},
                    "control_id": {"type": "string"},
                    "first_valid_date": {"type": "string"},
                    "second_valid_date": {"type": "string"},
                },
                "required": ["tenant_id", "valid_as_of", "system_as_of"] if name not in {"compare_states"} else ["tenant_id", "first_valid_date", "second_valid_date", "system_as_of"],
            },
        },
    }
    for name, desc in [
        ("search_compliance_graph", "Search the Neo4j compliance graph at the given bitemporal clocks."),
        ("traverse_control", "Bounded traversal from a control_id. Never invent CC6.1."),
        ("reconstruct_state", "Reconstruct control state at valid_as_of known at system_as_of."),
        ("compare_states", "Diff two valid-time states at one system_as_of."),
        ("get_evidence", "Evidence nodes visible at the clocks, with roles."),
        ("analyze_evidence", "Classify supporting/contradicting evidence; disclose conflicts."),
    ]
]


class OpenClawGatewayClient:
    """Typed client for documented OpenClaw Gateway HTTP APIs only."""

    def __init__(self, settings: Settings):
        self.base = settings.openclaw_gateway_url.rstrip("/")
        self.token = settings.openclaw_gateway_token
        self.agent = settings.openclaw_agent
        self.model_override = settings.openclaw_model
        self.timeout = settings.openclaw_timeout_s

    def _headers(self) -> dict[str, str]:
        h = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        if self.model_override:
            h["x-openclaw-model"] = self.model_override
        return h

    def health(self) -> dict[str, Any]:
        try:
            r = httpx.get(f"{self.base}/v1/models", headers=self._headers(), timeout=8.0)
            if r.status_code == 200:
                ids = [m.get("id") for m in (r.json().get("data") or [])]
                return {"status": "connected", "http": 200, "models": ids[:12], "detail": f"GET /v1/models ok ({len(ids)} agents)"}
            if r.status_code in {401, 403}:
                return {"status": "degraded", "http": r.status_code, "detail": "Gateway reachable but auth failed"}
            return {"status": "degraded", "http": r.status_code, "detail": r.text[:200]}
        except Exception as exc:
            return {"status": "disconnected", "http": 0, "detail": str(exc)[:240]}

    def invoke_tool(self, tool: str, args: dict | None = None, session_key: str | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"tool": tool, "args": args or {}}
        if session_key:
            body["sessionKey"] = session_key
        r = httpx.post(f"{self.base}/tools/invoke", headers=self._headers(), json=body, timeout=self.timeout)
        try:
            payload = r.json()
        except Exception:
            payload = {"raw": r.text[:500]}
        return {"http": r.status_code, "body": payload}

    def chat(self, messages: list[dict], *, user: str, session_key: str | None, stream: bool, tools: list | None, tool_choice: str = "auto") -> httpx.Response:
        headers = self._headers()
        if session_key:
            headers["x-openclaw-session-key"] = session_key
        headers["x-openclaw-message-channel"] = "verichron"
        body: dict[str, Any] = {
            "model": self.agent,
            "user": user,
            "messages": messages,
            "stream": stream,
            "tool_choice": tool_choice,
        }
        if tools:
            body["tools"] = tools
        return httpx.post(
            f"{self.base}/v1/chat/completions",
            headers=headers,
            json=body,
            timeout=self.timeout,
            stream=stream,
        )

    def parse_sse_bytes(self, raw: bytes) -> Iterator[dict[str, Any]]:
        text = raw.decode("utf-8", errors="replace")
        for block in text.split("\n\n"):
            line = next((ln for ln in block.split("\n") if ln.startswith("data: ")), None)
            if not line:
                continue
            data = line[6:].strip()
            if data == "[DONE]":
                yield {"type": "done"}
                continue
            try:
                yield json.loads(data)
            except json.JSONDecodeError:
                agent_log("OPENCLAW", f"non-json sse: {data[:120]}")
