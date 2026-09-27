"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { fmtDate } from "@/lib/utils";
import { PageHeader, Panel, StatusPill, EmptyState } from "@/components/ui/primitives";

export default function ControlsPage() {
  const [rows, setRows] = useState<any[] | null>(null);
  useEffect(() => {
    api.controls().then(setRows).catch(() => setRows([]));
  }, []);
  return (
    <div className="p-8 max-w-[1200px]">
      <PageHeader title="Controls" subtitle="Control catalog with bitemporal validity" />
      <Panel>
        {!rows ? (
          <div className="p-8 text-[13px] text-ink-400">Loading controls…</div>
        ) : rows.length === 0 ? (
          <EmptyState title="No controls" body="Seed the demo graph or ingest a catalog." />
        ) : (
          <table className="w-full text-[13px]">
            <thead className="text-[11px] uppercase text-ink-400">
              <tr className="border-b border-white/[0.07]">
                {["Control", "Requirement", "Owner", "Coverage", "Valid", "System", "Status"].map((h) => (
                  <th key={h} className="text-left font-medium px-4 py-2">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((c) => (
                <tr key={c.id} className="border-b border-white/[0.05]">
                  <td className="px-4 py-3">
                    <div>{c.name}</div>
                    <div className="font-mono text-[11px] text-ink-400">{c.id}</div>
                  </td>
                  <td className="px-4 font-mono text-[12px]">{c.requirement_id}</td>
                  <td className="px-4">{c.owner}</td>
                  <td className="px-4">{Math.round(c.evidence_coverage * 100)}%</td>
                  <td className="px-4 font-mono text-[11px] text-ink-400">{fmtDate(c.valid_start)} → {fmtDate(c.valid_end)}</td>
                  <td className="px-4 font-mono text-[11px] text-ink-400">{fmtDate(c.system_start)}</td>
                  <td className="px-4"><StatusPill value={c.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Panel>
    </div>
  );
}
