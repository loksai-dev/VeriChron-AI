"use client";

import { useEffect, useState } from "react";
import { api, type AgentRun } from "@/lib/api";
import { PageHeader, Panel, EmptyState } from "@/components/ui/primitives";

export default function ActivityPage() {
  const [runs, setRuns] = useState<AgentRun[]>([]);
  useEffect(() => {
    api.runs().then(setRuns).catch(() => setRuns([]));
  }, []);

  return (
    <div className="p-8 max-w-[1000px]">
      <PageHeader title="Agent Activity" subtitle="Observability for graph, memory, reflect, and LLM stages" />
      {runs.length === 0 ? (
        <EmptyState title="No executions yet" body="Run a question in Audit Assistant or reconstruct a historical state." />
      ) : (
        <div className="space-y-3">
          {runs.map((r) => (
            <Panel key={r.id} className="p-4">
              <div className="flex justify-between text-[13px]">
                <div className="font-medium">{r.query}</div>
                <div className="font-mono text-ink-400">{r.total_ms}ms</div>
              </div>
              <div className="mt-3 space-y-1">
                {r.stages.map((s) => (
                  <details key={s.name} className="text-[12px] border-b border-white/[0.05] py-1">
                    <summary className="grid grid-cols-[1fr_80px_1fr] cursor-pointer">
                      <span>✓ {s.name}</span>
                      <span className="font-mono">{s.latency_ms}ms</span>
                      <span className="truncate text-ink-500">{s.detail}</span>
                    </summary>
                    <pre className="mt-1 text-[11px] text-ink-400 whitespace-pre-wrap">{s.detail}</pre>
                  </details>
                ))}
              </div>
              <div className="flex gap-4 mt-3 text-[11px] text-ink-500">
                <span>Neo4j {r.neo4j_queries}</span>
                <span>Recall {r.hindsight_recalls}</span>
                <span>Reflect {r.reflect_ops}</span>
                <span>LLM {r.llm_calls}</span>
              </div>
            </Panel>
          ))}
        </div>
      )}
    </div>
  );
}
