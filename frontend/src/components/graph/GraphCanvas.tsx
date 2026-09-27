"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  type Node,
  type Edge,
  MarkerType,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { api, type GraphPayload } from "@/lib/api";
import { useAppState } from "@/lib/state";
import { fmtDate } from "@/lib/utils";
import { PageHeader, Panel } from "@/components/ui/primitives";

const FILTERS = ["All", "Control", "Policy", "Evidence", "AuditFinding", "Remediation"];

function typeColor(t: string) {
  const map: Record<string, string> = {
    Regulation: "#8a867c",
    Requirement: "#175cd3",
    Control: "#1f7a4d",
    Infrastructure: "#6b675f",
    Evidence: "#a37b12",
    AuditFinding: "#b42318",
    Remediation: "#175cd3",
    Policy: "#eceae4",
    JiraTicket: "#8a867c",
  };
  return map[t] || "#eceae4";
}

export default function GraphPage() {
  const { validAsOf, systemAsOf } = useAppState();
  const [data, setData] = useState<GraphPayload | null>(null);
  const [filter, setFilter] = useState("All");
  const [selected, setSelected] = useState<any>(null);
  const [causal, setCausal] = useState(false);

  const load = useCallback(() => {
    const types = filter === "All" ? undefined : filter;
    api.graph(validAsOf, systemAsOf, types).then(setData);
  }, [validAsOf, systemAsOf, filter]);

  useEffect(() => {
    load();
  }, [load]);

  const { nodes, edges } = useMemo(() => {
    if (!data) return { nodes: [] as Node[], edges: [] as Edge[] };
    const path = new Set(data.causal_path || []);
    const grouped: Record<string, number> = {};
    const ns: Node[] = data.nodes.map((n, i) => {
      grouped[n.type] = (grouped[n.type] || 0) + 1;
      const col = ["Regulation", "Requirement", "Policy", "Control", "Infrastructure", "Evidence", "AuditFinding", "JiraTicket", "Remediation", "Person"].indexOf(n.type);
      const x = Math.max(col, 0) * 200 + 40;
      const y = grouped[n.type] * 90;
      const onPath = path.has(n.id);
      return {
        id: n.id,
        position: { x, y },
        data: { label: n.name, raw: n },
        style: {
          background: "#161614",
          color: "#eceae4",
          border: `1px solid ${causal && onPath ? "#b42318" : typeColor(n.type)}`,
          borderRadius: 8,
          fontSize: 12,
          width: 160,
          opacity: causal && !onPath ? 0.28 : 1,
          boxShadow: causal && onPath ? "0 0 0 1px #b42318" : undefined,
        },
      };
    });
    const es: Edge[] = data.edges.map((e) => {
      const onPath = path.has(e.source) && path.has(e.target);
      return {
        id: e.id,
        source: e.source,
        target: e.target,
        label: e.type,
        markerEnd: { type: MarkerType.ArrowClosed, color: causal && onPath ? "#b42318" : "#6b675f" },
        style: { stroke: causal && onPath ? "#b42318" : "#3c3a36" },
        labelStyle: { fill: "#8a867c", fontSize: 9 },
      };
    });
    return { nodes: ns, edges: es };
  }, [data, causal]);

  return (
    <div className="h-[calc(100vh-56px)] flex">
      <div className="flex-1 min-w-0 p-5 flex flex-col">
        <PageHeader
          title="Knowledge Graph"
          subtitle="Explicit compliance relationships · Neo4j traversal"
          actions={
            <button onClick={() => setCausal((v) => !v)} className="h-8 px-3 rounded-md border border-white/10 text-[12px]">
              {causal ? "Clear root cause" : "Trace root cause"}
            </button>
          }
        />
        <div className="flex gap-2 mb-3">
          {FILTERS.map((f) => (
            <button key={f} onClick={() => setFilter(f)} className={`h-7 px-2.5 rounded border text-[12px] ${filter === f ? "bg-white/[0.06] border-white/20" : "border-white/10"}`}>
              {f === "AuditFinding" ? "Findings" : f}
            </button>
          ))}
        </div>
        {data?.cypher && (
          <Panel className="p-3 mb-3 text-[11px] font-mono text-ink-400">
            <div className="flex justify-between text-ink-200 font-sans text-[12px] mb-1">
              <span>Cypher ({data.source})</span>
              <span>{data.execution_ms}ms · {data.nodes?.length || 0} nodes · {data.edges?.length || 0} rels</span>
            </div>
            {data.cypher}
          </Panel>
        )}
        <Panel className="flex-1 min-h-0 h-full overflow-hidden">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            fitView
            onNodeClick={(_, n) => {
              const raw = n.data.raw as any;
              setSelected(raw);
              api.graphEntity(raw.id, validAsOf, systemAsOf).then((g) => {
                if (g.entity) setSelected({ ...raw, ...g.entity, cypher: g.cypher, relationships: g.edges });
              });
            }}
            proOptions={{ hideAttribution: true }}
          >
            <Background color="#2a2926" gap={18} />
            <MiniMap pannable style={{ background: "#0f0f0e" }} />
            <Controls />
          </ReactFlow>
        </Panel>
      </div>
      <aside className="w-[320px] border-l border-white/[0.07] p-5 overflow-auto">
        {selected ? (
          <div className="space-y-3 text-[13px]">
            <div className="text-[11px] uppercase text-ink-400">{selected.type}</div>
            <div className="text-[16px]">{selected.name}</div>
            <div className="font-mono text-[11px] text-ink-400">{selected.id}</div>
            <p className="text-ink-300">{selected.description}</p>
            <div>Status · {selected.status || "—"}</div>
            <div>
              <div className="text-[11px] uppercase text-ink-400">Valid time</div>
              {fmtDate(selected.valid_start)} → {fmtDate(selected.valid_end)}
            </div>
            <div>
              <div className="text-[11px] uppercase text-ink-400">System time</div>
              {fmtDate(selected.system_start)} → {fmtDate(selected.system_end)}
            </div>
            <div>
              <div className="text-[11px] uppercase text-ink-400">Relationships</div>
              {(selected.relationships || []).slice(0, 8).map((r: any) => (
                <div key={r.id} className="font-mono text-[11px]">{r.type} → {r.target}</div>
              ))}
            </div>
          </div>
        ) : (
          <p className="text-[13px] text-ink-400">Select a node. Trace root cause highlights CC6.1 → MFA → IAM → evidence → finding → ticket.</p>
        )}
      </aside>
    </div>
  );
}
