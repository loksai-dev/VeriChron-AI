"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { PageHeader, Panel, StatusPill } from "@/components/ui/primitives";

export default function CompliancePage() {
  const router = useRouter();
  const [data, setData] = useState<any>(null);
  useEffect(() => {
    api.overview().then(setData);
  }, []);
  return (
    <div className="p-8 max-w-[1200px]">
      <PageHeader title="Compliance" subtitle="Framework coverage, residual risk, and control gaps" />
      <div className="grid grid-cols-2 gap-3 mb-6">
        <Panel className="p-5">
          <div className="text-[11px] uppercase text-ink-400">SOC 2 Type II</div>
          <div className="text-[32px] mt-2">92%</div>
          <p className="text-[13px] text-ink-400 mt-2">CC6.1 remediated after Q2 2025. CC7.1 tabletop overdue.</p>
        </Panel>
        <Panel className="p-5">
          <div className="text-[11px] uppercase text-ink-400">ISO/IEC 27001</div>
          <div className="text-[32px] mt-2">88%</div>
          <p className="text-[13px] text-ink-400 mt-2">Mapped to the same identity evidence; A.5.24 inherits IR gap.</p>
        </Panel>
      </div>
      <Panel>
        <div className="px-5 py-4 border-b border-white/[0.07] flex justify-between">
          <div className="text-[14px]">In-scope requirements</div>
          <button onClick={() => router.push("/assistant?q=" + encodeURIComponent("Find unresolved compliance gaps."))} className="text-[12px] border border-white/10 rounded px-2 h-7">
            Find unresolved gaps
          </button>
        </div>
        <table className="w-full text-[13px]">
          <thead className="text-[11px] uppercase text-ink-400">
            <tr className="border-b border-white/[0.07]">
              <th className="text-left px-5 py-2 font-medium">ID</th>
              <th className="text-left px-5 py-2 font-medium">Status</th>
              <th className="text-left px-5 py-2 font-medium">Evidence</th>
            </tr>
          </thead>
          <tbody>
            {(data?.matrix || []).map((row: any) => (
              <tr key={row.requirement_id} className="border-b border-white/[0.05]">
                <td className="px-5 py-3 font-mono text-[12px]">{row.requirement_id} · {row.name}</td>
                <td className="px-5"><StatusPill value={row.cells.current} /></td>
                <td className="px-5"><StatusPill value={row.cells.evidence} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </Panel>
    </div>
  );
}
