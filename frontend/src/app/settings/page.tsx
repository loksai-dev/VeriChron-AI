"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { PageHeader, Panel } from "@/components/ui/primitives";

const SAMPLE = `# Incident note
On 2025-04-12 Terraform applied an IAM group policy that dropped MFA.
Ticket SEC-1842 opened 2025-06-04.`;

export default function SettingsPage() {
  const [health, setHealth] = useState<any>(null);
  const [file, setFile] = useState("incident-note.md");
  const [content, setContent] = useState(SAMPLE);
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    api.health().then(setHealth);
  }, []);

  return (
    <div className="p-8 max-w-[800px]">
      <PageHeader title="Settings" subtitle="Service mode, ingest, and demo seed" />
      <Panel className="p-5 mb-4">
        <div className="text-[14px] mb-3">System status</div>
        {(health?.services || []).map((s: any) => (
          <div key={s.name} className="flex justify-between text-[13px] py-1 border-b border-white/[0.05]">
            <span>{s.name}</span>
            <span className="text-ink-400">{s.mode} · {s.detail}</span>
          </div>
        ))}
        <p className="text-[12px] text-ink-400 mt-3">UI never talks to Neo4j, Hindsight, or Groq directly. DEMO_MODE keeps the product complete if they are down.</p>
      </Panel>
      <Panel className="p-5">
        <div className="text-[14px] mb-2">Act 1 — Historical ingestion</div>
        <input value={file} onChange={(e) => setFile(e.target.value)} className="w-full h-8 bg-ink-950 border border-white/10 rounded px-2 text-[12px] mb-2" />
        <textarea value={content} onChange={(e) => setContent(e.target.value)} className="w-full h-40 bg-ink-950 border border-white/10 rounded p-2 text-[12px] font-mono" />
        <button
          onClick={async () => setResult(await api.ingest({ filename: file, content, source: "upload" }))}
          className="mt-3 h-8 px-3 rounded bg-ink-50 text-ink-950 text-[12px]"
        >
          Ingest → parse → Neo4j → retain()
        </button>
        {result && <pre className="mt-3 text-[11px] text-ink-400 overflow-auto">{JSON.stringify(result, null, 2)}</pre>}
      </Panel>
    </div>
  );
}
