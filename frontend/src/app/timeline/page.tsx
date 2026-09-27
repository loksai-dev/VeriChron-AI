"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useAppState } from "@/lib/state";
import { fmtDate } from "@/lib/utils";
import { PageHeader, Panel, StatusPill } from "@/components/ui/primitives";

export default function TimelinePage() {
  const { validAsOf, systemAsOf, setValidAsOf, setSystemAsOf } = useAppState();
  const [recon, setRecon] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function reconstruct() {
    setLoading(true);
    try {
      const data = await api.reconstruct({ valid_as_of: validAsOf, system_as_of: systemAsOf, framework: "SOC 2" });
      setRecon(data);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    reconstruct();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [validAsOf, systemAsOf]);

  return (
    <div className="p-8 max-w-[1200px]">
      <PageHeader title="Compliance Time Machine" subtitle="Valid time is when it was true. System time is when it was known." />
      <Panel className="p-5 mb-6">
        <div className="grid grid-cols-2 gap-6">
          <label className="text-[13px]">
            <div className="text-[11px] uppercase text-ink-400 mb-1">Valid time</div>
            <input type="date" value={validAsOf} onChange={(e) => setValidAsOf(e.target.value)} className="h-9 w-full bg-ink-950 border border-white/10 rounded px-2" />
            <p className="text-[12px] text-ink-400 mt-2">World state — what was actually true.</p>
          </label>
          <label className="text-[13px]">
            <div className="text-[11px] uppercase text-ink-400 mb-1">System time</div>
            <input type="date" value={systemAsOf} onChange={(e) => setSystemAsOf(e.target.value)} className="h-9 w-full bg-ink-950 border border-white/10 rounded px-2" />
            <p className="text-[12px] text-ink-400 mt-2">Organizational knowledge — what had been recorded.</p>
          </label>
        </div>
        <div className="flex gap-2 mt-4 flex-wrap">
          {["2025-01-01", "2025-02-01", "2025-03-01", "2025-04-01", "2025-05-01", "2025-05-15", "2025-06-01", "2025-06-25", "2025-07-15"].map((d) => (
            <button key={d} onClick={() => { setValidAsOf(d); setSystemAsOf(d); }} className={`h-7 px-2.5 border rounded text-[12px] ${validAsOf === d ? "border-white/30 bg-white/[0.06]" : "border-white/10"}`}>{d}</button>
          ))}
          <button onClick={reconstruct} className="ml-auto h-8 px-3 rounded bg-ink-50 text-ink-950 text-[12px] font-medium">
            {loading ? "Reconstructing…" : "Reconstruct state"}
          </button>
        </div>
      </Panel>

      {recon && (
        <>
          <div className="mb-4">
            <div className="text-[18px]">{recon.headline}</div>
            <p className="text-[13px] text-ink-400 mt-1">{recon.narrative}</p>
            <div className="mt-2"><StatusPill value={recon.compliance_status} /> <span className="text-[13px] text-ink-400 ml-2">score {recon.score}%</span></div>
          </div>
          <div className="grid grid-cols-2 gap-4 mb-6">
            <Panel className="p-4">
              <div className="text-[11px] uppercase text-ink-400">Valid time</div>
              <div className="text-[15px] mt-2">MFA Policy</div>
              <p className="text-[13px] mt-1">Active: {recon.mfa_policy.active}</p>
            </Panel>
            <Panel className="p-4">
              <div className="text-[11px] uppercase text-ink-400">System time</div>
              <div className="text-[15px] mt-2">Evidence recorded</div>
              <p className="text-[13px] mt-1">{recon.mfa_policy.evidence_recorded}</p>
              <p className="text-[12px] text-ink-400 mt-1">{recon.mfa_policy.known ? "Policy document is in the graph." : "Policy document not yet retained — knowledge lag."}</p>
            </Panel>
          </div>
          <Panel className="p-5 mb-6">
            <div className="text-[14px] mb-2">Known evidence</div>
            <div className="text-[12px] font-mono text-ink-400">{(recon.evidence || []).map((e: any) => e.id || e.title).join(" · ") || "—"}</div>
            <div className="text-[14px] mt-4 mb-2">Unknown / future evidence</div>
            <div className="text-[12px] font-mono text-ink-400">{(recon.unknown_future_evidence || []).map((e: any) => e.id).join(" · ") || "none"}</div>
          </Panel>
          <Panel className="p-5 mb-6">
            <div className="text-[14px] mb-4">Historical events</div>
            <div className="relative pl-4 border-l border-white/10 space-y-5">
              {(recon.timeline || []).map((e: any) => (
                <div key={e.id}>
                  <div className="text-[12px] font-mono text-ink-400">{fmtDate(e.valid_start)}</div>
                  <div className="text-[14px]">{e.title}</div>
                  <p className="text-[12px] text-ink-400">{e.description}</p>
                  <div className="text-[11px] text-ink-500 mt-1">valid {fmtDate(e.valid_start)} → {fmtDate(e.valid_end)} · system {fmtDate(e.system_start)}</div>
                </div>
              ))}
            </div>
          </Panel>
          <Panel>
            <div className="px-5 py-3 border-b border-white/[0.07] text-[14px]">Controls known at this system time</div>
            <table className="w-full text-[13px]">
              <tbody>
                {(recon.controls || []).map((c: any) => (
                  <tr key={c.id} className="border-b border-white/[0.05]">
                    <td className="px-5 py-2">{c.name}</td>
                    <td className="px-5">{c.known ? <StatusPill value={c.status} /> : <span className="text-ink-400 text-[12px]">not in system of record</span>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Panel>
        </>
      )}
    </div>
  );
}
