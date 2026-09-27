"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { fmtDate } from "@/lib/utils";
import { PageHeader, Panel, StatusPill, EmptyState } from "@/components/ui/primitives";

export default function FindingsPage() {
  const router = useRouter();
  const [rows, setRows] = useState<any[]>([]);
  const [open, setOpen] = useState<any>(null);
  useEffect(() => {
    api.findings().then(setRows).catch(() => setRows([]));
  }, []);

  return (
    <div className="p-8 max-w-[1400px] flex gap-4">
      <div className="flex-1 min-w-0">
        <PageHeader title="Findings" subtitle="Enterprise audit findings with temporal bounds" />
        <Panel>
          {rows.length === 0 ? (
            <EmptyState title="No findings" body="Ingest audit memos or run gap discovery." />
          ) : (
            <table className="w-full text-[13px]">
              <thead className="text-[11px] uppercase text-ink-400">
                <tr className="border-b border-white/[0.07]">
                  {["Finding", "Control", "Severity", "Detected", "Valid period", "Status", "Owner", "Remediation"].map((h) => (
                    <th key={h} className="text-left font-medium px-3 py-2">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((f) => (
                  <tr key={f.id} onClick={() => setOpen(f)} className="border-b border-white/[0.05] cursor-pointer hover:bg-white/[0.03]">
                    <td className="px-3 py-3">{f.title}</td>
                    <td className="px-3 font-mono text-[11px]">{f.control_id}</td>
                    <td className="px-3"><StatusPill value={f.severity === "critical" ? "non_compliant" : f.severity === "medium" ? "at_risk" : "info"} /></td>
                    <td className="px-3 font-mono text-[11px]">{fmtDate(f.detected)}</td>
                    <td className="px-3 font-mono text-[11px] text-ink-400">{fmtDate(f.valid_start)} → {fmtDate(f.valid_end)}</td>
                    <td className="px-3"><StatusPill value={f.status === "open" ? "at_risk" : "remediated"} /></td>
                    <td className="px-3">{f.owner}</td>
                    <td className="px-3 font-mono text-[11px]">{f.remediation_id || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </Panel>
      </div>
      {open && (
        <aside className="w-[360px] shrink-0 rounded-lg border border-white/[0.07] bg-ink-900 p-5 space-y-4 h-fit">
          <div className="flex justify-between">
            <div className="text-[14px]">Finding summary</div>
            <button onClick={() => setOpen(null)} className="text-ink-400 text-[12px]">Close</button>
          </div>
          <p className="text-[13px] text-ink-200">{open.summary}</p>
          <section>
            <div className="text-[11px] uppercase text-ink-400 mb-1">Root cause</div>
            <p className="text-[13px]">{open.root_cause}</p>
          </section>
          <section>
            <div className="text-[11px] uppercase text-ink-400 mb-1">Affected controls</div>
            <div className="font-mono text-[12px]">{open.affected_controls?.join(" · ")}</div>
          </section>
          <section>
            <div className="text-[11px] uppercase text-ink-400 mb-1">Evidence</div>
            <div className="font-mono text-[12px]">{open.evidence_ids?.join(" · ")}</div>
          </section>
          <section>
            <div className="text-[11px] uppercase text-ink-400 mb-1">Remediation</div>
            <p className="text-[13px]">{open.remediation_id}</p>
          </section>
          <div className="flex flex-col gap-2">
            <button onClick={() => router.push("/graph")} className="h-8 border border-white/10 rounded text-[12px]">Related graph</button>
            <button onClick={() => router.push("/assistant?q=" + encodeURIComponent("Why was CC6.1 non-compliant during Q2 2025?"))} className="h-8 border border-white/10 rounded text-[12px]">AI analysis</button>
            <button onClick={() => router.push("/timeline")} className="h-8 border border-white/10 rounded text-[12px]">Timeline</button>
          </div>
        </aside>
      )}
    </div>
  );
}
