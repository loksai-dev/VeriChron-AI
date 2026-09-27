"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "@/lib/api";
import { useAppState } from "@/lib/state";
import { EmptyState, ErrorState, PageHeader, Panel, StatusPill } from "@/components/ui/primitives";

export default function OverviewPage() {
  const router = useRouter();
  const { setValidAsOf, setSystemAsOf } = useAppState();
  const [data, setData] = useState<any>(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    api.overview().then(setData).catch((e) => setErr(String(e.message || e)));
  }, []);

  if (err) return <div className="p-8"><ErrorState message={`API unavailable — start the backend on :8000. ${err}`} /></div>;
  if (!data) return <div className="p-8 text-[13px] text-ink-400">Loading posture…</div>;

  const m = data.metrics;
  const cards = [
    { k: "Overall compliance", v: `${Math.round(m.overall_compliance * 100)}%`, s: data.source || "graph", href: "/controls" },
    { k: "Active controls", v: m.active_controls, s: "in scope", href: "/controls" },
    { k: "Open findings", v: m.open_findings, s: `${m.critical_findings} critical`, href: "/findings" },
    { k: "Pending remediations", v: m.pending_remediations, s: "tracked", href: "/findings" },
    { k: "Evidence coverage", v: `${Math.round(m.evidence_coverage * 100)}%`, s: `${data.evidence_count ?? "?"} records`, href: "/evidence" },
  ];

  return (
    <div className="p-8 max-w-[1280px]">
      <PageHeader
        title="Compliance Overview"
        subtitle="Real-time and historical compliance posture"
        actions={
          <button onClick={() => router.push("/timeline")} className="h-8 px-3 rounded-md border border-white/10 text-[12px]">
            Open time machine
          </button>
        }
      />
      <p className="text-[13px] text-ink-400 -mt-4 mb-6 max-w-3xl">
        VeriChron reconstructs what your compliance status <em>was</em>, what the organization <em>knew</em> at that time, and why it changed.
      </p>
      <div className="grid grid-cols-5 gap-3 mb-6">
        {cards.map((c) => (
          <Panel key={c.k} className="p-4 cursor-pointer hover:bg-white/[0.02]" onClick={() => router.push(c.href)}>
            <div className="text-[11px] uppercase tracking-wide text-ink-400">{c.k}</div>
            <div className="text-[26px] mt-2 tracking-tight">{c.v}</div>
            <div className="text-[12px] text-ink-400 mt-1">{c.s}</div>
          </Panel>
        ))}
      </div>
      <Panel className="p-5 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="text-[14px]">Compliance posture timeline</div>
            <div className="text-[12px] text-ink-400">World state vs organizational knowledge · 2024–2026</div>
          </div>
        </div>
        <div className="h-56">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data.series}>
              <XAxis dataKey="date" tick={{ fill: "#8a867c", fontSize: 11 }} tickFormatter={(v) => (v ? String(v).slice(0, 7) : "")} axisLine={false} tickLine={false} />
              <YAxis domain={[60, 100]} tick={{ fill: "#8a867c", fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: "#161614", border: "1px solid rgba(255,255,255,0.08)", fontSize: 12 }} />
              <Area type="monotone" dataKey="compliance" name="Valid time" stroke="#1f7a4d" fill="#1f7a4d" fillOpacity={0.15} />
              <Area type="monotone" dataKey="known" name="System time" stroke="#175cd3" fill="#175cd3" fillOpacity={0.08} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div className="flex gap-2 mt-3 flex-wrap">
          {["2025-01-01", "2025-04-10", "2025-05-15", "2025-06-25", "2025-07-15"].map((d) => (
            <button
              key={d}
              onClick={() => {
                setValidAsOf(d);
                setSystemAsOf(d);
                router.push("/timeline");
              }}
              className="text-[12px] h-7 px-2.5 rounded border border-white/10 hover:bg-white/[0.04]"
            >
              {d}
            </button>
          ))}
        </div>
      </Panel>
      <Panel>
        <div className="px-5 py-4 border-b border-white/[0.07]">
          <div className="text-[14px]">Control gap matrix</div>
          <div className="text-[12px] text-ink-400">SOC 2 TSC · current vs last audit</div>
        </div>
        {!data.matrix?.length ? (
          <EmptyState title="No controls in scope" body="Ingest a framework catalog to populate the matrix." />
        ) : (
          <table className="w-full text-[13px]">
            <thead className="text-ink-400 text-[11px] uppercase tracking-wide">
              <tr className="border-b border-white/[0.07]">
                {["Requirement", "Current", "Last audit", "Evidence", "Finding", "Remediation"].map((h) => (
                  <th key={h} className="text-left font-medium px-5 py-2">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.matrix.map((row: any) => (
                <tr key={row.requirement_id} className="border-b border-white/[0.05] hover:bg-white/[0.02]">
                  <td className="px-5 py-3 font-mono text-[12px]">
                    {row.requirement_id}
                    <div className="text-ink-400 font-sans">{row.name}</div>
                  </td>
                  <td className="px-5"><StatusPill value={row.cells.current} /></td>
                  <td className="px-5"><StatusPill value={row.cells.last_audit} /></td>
                  <td className="px-5"><StatusPill value={row.cells.evidence} /></td>
                  <td className="px-5 font-mono text-[12px] text-ink-400">{row.cells.finding || "—"}</td>
                  <td className="px-5 font-mono text-[12px] text-ink-400">{row.cells.remediation || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Panel>
      <div className="grid grid-cols-3 gap-3 mt-6">
        <Panel className="p-4">
          <div className="text-[13px] mb-2">Recent compliance changes</div>
          {(data.recent_changes || []).map((e: any) => (
            <div key={e.id} className="text-[12px] py-1 border-b border-white/[0.05]">
              <span className="font-mono text-ink-400 mr-2">{e.valid_start}</span>
              {e.title}
            </div>
          ))}
        </Panel>
        <Panel className="p-4">
          <div className="text-[13px] mb-2">Knowledge graph preview</div>
          <p className="text-[12px] text-ink-400">SOC 2 → CC6.1 → MFA Enforcement → AWS IAM → CloudTrail → Finding → Enable MFA</p>
          <button onClick={() => router.push("/graph")} className="mt-3 h-7 px-2 border border-white/10 rounded text-[12px]">Open graph</button>
        </Panel>
        <Panel className="p-4">
          <div className="text-[13px] mb-2">Recent agent runs</div>
          <p className="text-[12px] text-ink-400">Execution traces live on Agent Activity after you ask a question.</p>
          <button onClick={() => router.push("/activity")} className="mt-3 h-7 px-2 border border-white/10 rounded text-[12px]">Open traces</button>
        </Panel>
      </div>
    </div>
  );
}
