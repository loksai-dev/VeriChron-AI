"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { fmtDate } from "@/lib/utils";
import { PageHeader, Panel, EmptyState } from "@/components/ui/primitives";

const KINDS = ["all", "cloudtrail", "jira", "policy", "control_test", "audit_report"];

export default function EvidencePage() {
  const router = useRouter();
  const [rows, setRows] = useState<any[]>([]);
  const [kind, setKind] = useState("all");
  useEffect(() => {
    api.evidence().then(setRows).catch(() => setRows([]));
  }, []);
  const shown = kind === "all" ? rows : rows.filter((r) => r.kind === kind);

  return (
    <div className="p-8 max-w-[1200px]">
      <PageHeader title="Evidence" subtitle="Source-backed artifacts with valid time and system time" />
      <div className="flex gap-2 mb-4">
        {KINDS.map((k) => (
          <button key={k} onClick={() => setKind(k)} className={`h-7 px-2.5 rounded border text-[12px] ${kind === k ? "border-white/20 bg-white/[0.06]" : "border-white/10"}`}>
            {k === "all" ? "All" : k.replace("_", " ")}
          </button>
        ))}
      </div>
      {shown.length === 0 ? (
        <EmptyState title="No evidence" body="Upload policies, tickets, or logs from Settings → Ingest." />
      ) : (
        <div className="grid gap-3">
          {shown.map((e) => (
            <Panel key={e.id} className="p-4">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="text-[11px] uppercase tracking-wide text-ink-400">{e.kind} · {e.source}</div>
                  <div className="text-[14px] mt-1">{e.title}</div>
                  <p className="text-[13px] text-ink-400 mt-1">{e.summary}</p>
                </div>
                <div className="text-right font-mono text-[11px] text-ink-400">
                  <div>{e.id}</div>
                  <div>{e.content_hash}</div>
                  <div>{Math.round(e.confidence * 100)}% conf</div>
                </div>
              </div>
              <div className="mt-3 grid grid-cols-4 gap-3 text-[12px]">
                <div><span className="text-ink-400">Timestamp</span><div>{e.timestamp}</div></div>
                <div><span className="text-ink-400">Valid time</span><div>{fmtDate(e.valid_start)} → {fmtDate(e.valid_end)}</div></div>
                <div><span className="text-ink-400">System time</span><div>{fmtDate(e.system_start)}</div></div>
                <div><span className="text-ink-400">Entity</span><div className="font-mono">{e.entity_id}</div></div>
              </div>
              <div className="flex gap-2 mt-3">
                <button onClick={() => router.push("/timeline")} className="h-7 px-2 border border-white/10 rounded text-[12px]">View in timeline</button>
                <button onClick={() => router.push("/graph")} className="h-7 px-2 border border-white/10 rounded text-[12px]">View in graph</button>
                <button onClick={() => router.push("/assistant?q=" + encodeURIComponent(`What evidence proves that ${e.title} is authentic?`))} className="h-7 px-2 border border-white/10 rounded text-[12px]">Ask agent</button>
              </div>
            </Panel>
          ))}
        </div>
      )}
    </div>
  );
}
