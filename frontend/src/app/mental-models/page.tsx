"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { PageHeader, Panel, StatusPill } from "@/components/ui/primitives";

export default function MentalModelsPage() {
  const [data, setData] = useState<any>(null);
  const [open, setOpen] = useState<any>(null);
  useEffect(() => {
    api.mental().then(setData);
  }, []);

  async function refresh(id: string) {
    await api.refreshModel(id);
    setData(await api.mental());
  }

  return (
    <div className="p-8 max-w-[1200px]">
      <PageHeader title="Mental Models" subtitle="Derived from Hindsight recall + graph findings. Seeded catalog remains labeled until Cloud refresh succeeds." />
      <div className="grid grid-cols-2 gap-3 mb-8">
        {(data?.models || []).map((m: any) => (
          <Panel key={m.id} className="p-5 cursor-pointer hover:bg-white/[0.02]" onClick={() => setOpen(m)}>
            <div className="flex justify-between">
              <div className="text-[15px]">{m.name}</div>
              <StatusPill value={m.status} />
            </div>
            <p className="text-[12px] text-ink-400 mt-2 line-clamp-2">{m.content}</p>
            <div className="flex gap-4 mt-3 text-[12px] text-ink-400">
              <span>Refreshed {m.last_refreshed?.slice(0, 10)}</span>
              <span>{m.evidence_count} evidence</span>
              <span>{Math.round(m.confidence * 100)}%</span>
            </div>
          </Panel>
        ))}
      </div>
      {open && (
        <Panel className="p-5">
          <div className="flex justify-between mb-3">
            <div className="text-[16px]">{open.name}</div>
            <button onClick={() => refresh(open.id)} className="h-8 px-3 border border-white/10 rounded text-[12px]">Refresh</button>
          </div>
          <p className="text-[13px] leading-relaxed">{open.content}</p>
          <div className="mt-4 text-[12px]">
            <div className="uppercase text-ink-400 mb-1">Supporting evidence</div>
            {(open.supporting_evidence || []).join(" · ")}
          </div>
          <div className="mt-3 text-[12px]">
            <div className="uppercase text-ink-400 mb-1">Recent changes</div>
            {(open.recent_changes || []).join(" · ")}
          </div>
          <div className="mt-3 text-[12px]">
            <div className="uppercase text-ink-400 mb-1">Historical versions</div>
            {(open.versions || []).map((v: any) => (
              <div key={v.version} className="font-mono">v{v.version} · {v.at} · {v.note}</div>
            ))}
          </div>
        </Panel>
      )}
      <div className="grid grid-cols-2 gap-4 mt-8">
        <Panel className="p-4">
          <div className="text-[13px] mb-2">Layer 2 · Observations</div>
          {(data?.observations || []).map((o: any) => (
            <p key={o.id} className="text-[12px] text-ink-300 mb-2">{o.content}</p>
          ))}
        </Panel>
        <Panel className="p-4">
          <div className="text-[13px] mb-2">Layer 3 · Raw facts</div>
          {(data?.facts || []).slice(0, 6).map((f: any) => (
            <p key={f.id} className="text-[12px] text-ink-400 mb-2 font-mono">{f.id}: {f.content.slice(0, 120)}</p>
          ))}
        </Panel>
      </div>
    </div>
  );
}
