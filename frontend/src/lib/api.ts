export type ComplianceStatus = "compliant" | "non_compliant" | "at_risk" | "unknown" | "remediated";

export type SourceRef = {
  id: string;
  kind: string;
  title: string;
  excerpt: string;
  confidence: number;
};

export type TimelineEvent = {
  id: string;
  title: string;
  description: string;
  valid_start: string;
  valid_end?: string | null;
  system_start: string;
  system_end?: string | null;
  entity_id: string;
  fact_type: string;
  status?: string | null;
  source: string;
  confidence: number;
};

export type AgentStage = {
  name: string;
  latency_ms: number;
  detail: string;
  status: string;
};

export type AgentRun = {
  id: string;
  query: string;
  started_at: string;
  total_ms: number;
  stages: AgentStage[];
  status: string;
  memory_retrievals: number;
  neo4j_queries: number;
  hindsight_recalls: number;
  reflect_ops: number;
  llm_calls: number;
};

export type AgentAnswer = {
  conclusion: string;
  compliance_status: ComplianceStatus;
  affected_controls: string[];
  evidence: SourceRef[];
  timeline: TimelineEvent[];
  root_cause?: string | null;
  remediation?: string | null;
  confidence: number;
  sources: string[];
  graph_path: string[];
  caveat?: string | null;
  run?: AgentRun | null;
  memories_used?: any[];
  intent?: string | null;
  selected_tools?: string[];
  valid_as_of?: string | null;
  system_as_of?: string | null;
  memory_source?: string | null;
  orchestrator?: string | null;
};

export type GraphNode = {
  id: string;
  type: string;
  name: string;
  status?: string | null;
  description: string;
  owner?: string | null;
  valid_start?: string | null;
  valid_end?: string | null;
  system_start?: string | null;
  system_end?: string | null;
  sources: string[];
};

export type GraphEdge = {
  id: string;
  source: string;
  target: string;
  type: string;
};

export type GraphPayload = {
  nodes: GraphNode[];
  edges: GraphEdge[];
  causal_path: string[];
  cypher?: string;
  execution_ms?: number;
  source?: string;
};

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), 60000);
  try {
    const res = await fetch(`${API}${path}`, {
      ...init,
      signal: ctrl.signal,
      headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    });
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    return (await res.json()) as T;
  } finally {
    clearTimeout(t);
  }
}

export async function streamQuery(
  body: object,
  onEvent: (evt: any) => void
): Promise<void> {
  const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const res = await fetch(`${API}/api/query/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok || !res.body) throw new Error(`${res.status} ${res.statusText}`);
  const reader = res.body.getReader();
  const dec = new TextDecoder();
  let buf = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    const chunks = buf.split("\n\n");
    buf = chunks.pop() || "";
    for (const chunk of chunks) {
      const line = chunk.split("\n").find((l) => l.startsWith("data: "));
      if (!line) continue;
      onEvent(JSON.parse(line.slice(6)));
    }
  }
}

export const api = {
  overview: () => req<any>("/api/overview"),
  health: () => req<any>("/api/health"),
  controls: () => req<any[]>("/api/controls"),
  findings: () => req<any[]>("/api/findings"),
  evidence: () => req<any[]>("/api/evidence"),
  timeline: (valid: string, system: string) =>
    req<any>(`/api/timeline?valid_as_of=${valid}&system_as_of=${system}`),
  graph: (valid: string, system: string, types?: string) =>
    req<any>(`/api/graph?valid_as_of=${valid}&system_as_of=${system}${types ? `&types=${types}` : ""}`),
  graphEntity: (id: string, valid: string, system: string) =>
    req<any>(`/api/graph/${encodeURIComponent(id)}?valid_as_of=${valid}&system_as_of=${system}`),
  run: (id: string) => req<any>(`/api/agent/runs/${id}`),
  mental: () => req<any>("/api/mental-models"),
  runs: () => req<AgentRun[]>("/api/agent-runs"),
  query: (body: object) => req<AgentAnswer>("/api/query", { method: "POST", body: JSON.stringify(body) }),
  reconstruct: (body: object) => req<any>("/api/audit/reconstruct", { method: "POST", body: JSON.stringify(body) }),
  ingest: (body: object) => req<any>("/api/ingest", { method: "POST", body: JSON.stringify(body) }),
  refreshModel: (id: string) => req<any>(`/api/mental-models/${id}/refresh`, { method: "POST" }),
  narrative: () => req<any>("/api/demo/narrative"),
  memoryRetain: (body: object) => req<any>("/api/memory/retain", { method: "POST", body: JSON.stringify(body) }),
  memoryRecall: (body: object) => req<any>("/api/memory/recall", { method: "POST", body: JSON.stringify(body) }),
};
