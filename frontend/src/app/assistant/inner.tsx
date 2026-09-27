"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Loader2, Terminal } from "lucide-react";
import { streamQuery, type AgentAnswer } from "@/lib/api";
import { useAppState } from "@/lib/state";
import { fmtDate } from "@/lib/utils";
import { StatusPill } from "@/components/ui/primitives";

const PRESETS = [
  "Remember that the ACME MFA exception was approved by the security team on June 20, 2025 because of the legacy authentication dependency.",
  "What was the reason for the ACME MFA exception?",
  "Does that exception affect the CC6.1 compliance assessment?",
  "What was our compliance posture on May 15, 2025?",
  "What happened to PAM-01?",
];

type ToolRow = { name: string; status: "running" | "done"; summary?: string; ms?: number; input?: any };
type Turn = {
  id: string;
  question: string;
  thoughts: string[];
  tools: ToolRow[];
  answer: AgentAnswer | null;
};

export default function AssistantInner() {
  const params = useSearchParams();
  const router = useRouter();
  const { validAsOf, systemAsOf } = useAppState();
  const [q, setQ] = useState(params.get("q") || "");
  const [turns, setTurns] = useState<Turn[]>([]);
  const [memoryOn, setMemoryOn] = useState(true);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const bottom = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: "smooth" });
  }, [turns, busy]);

  async function ask(question: string) {
    const text = question.trim();
    if (!text || busy) return;
    setBusy(true);
    setErr("");
    setQ("");
    const turnId = `${Date.now()}`;
    setTurns((prev) => [...prev, { id: turnId, question: text, thoughts: [], tools: [], answer: null }]);

    const patch = (fn: (t: Turn) => Turn) =>
      setTurns((prev) => prev.map((t) => (t.id === turnId ? fn(t) : t)));

    try {
      await streamQuery(
        {
          question: text,
          valid_as_of: /^remember/i.test(text) ? undefined : /may 15/i.test(text) ? "2025-05-15" : validAsOf,
          system_as_of: /^remember/i.test(text) ? undefined : /may 15/i.test(text) ? "2025-05-15" : systemAsOf,
          framework: "SOC 2",
          memory_enabled: memoryOn,
        },
        (evt) => {
          if (evt.type === "thought") {
            patch((t) => ({ ...t, thoughts: [...t.thoughts, evt.text] }));
          }
          if (evt.type === "tool_start") {
            patch((t) => ({
              ...t,
              tools: [...t.tools, { name: evt.name, status: "running", input: evt.input }],
            }));
          }
          if (evt.type === "tool_end") {
            patch((t) => {
              const tools = [...t.tools];
              let idx = -1;
              for (let i = tools.length - 1; i >= 0; i--) {
                if (tools[i].name === evt.name && tools[i].status === "running") {
                  idx = i;
                  break;
                }
              }
              if (idx >= 0) tools[idx] = { ...tools[idx], status: "done", summary: evt.summary, ms: evt.ms };
              else tools.push({ name: evt.name, status: "done", summary: evt.summary, ms: evt.ms });
              return { ...t, tools };
            });
          }
          if (evt.type === "answer") {
            patch((t) => ({ ...t, answer: evt.data }));
          }
        }
      );
    } catch (e: any) {
      setErr(e.message || "Agent stream failed");
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    const initial = params.get("q");
    if (initial) ask(initial);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="h-[calc(100vh-56px)] flex flex-col">
      <div className="px-6 py-3 border-b border-white/[0.07] flex items-center gap-3">
        <Terminal className="h-4 w-4 text-ink-400" />
        <div>
          <div className="text-[14px]">Compliance agent</div>
          <div className="text-[11px] text-ink-400">OpenClaw orchestration · Neo4j tools · Hindsight Cloud</div>
        </div>
        <label className="ml-auto text-[11px] text-ink-400 inline-flex items-center gap-1.5">
          <input type="checkbox" checked={memoryOn} onChange={(e) => setMemoryOn(e.target.checked)} />
          Hindsight recall
        </label>
        {busy && (
          <div className="text-[12px] text-ink-400 inline-flex items-center gap-1.5">
            <Loader2 className="h-3.5 w-3.5 animate-spin" /> Agent working
          </div>
        )}
      </div>

      <div className="flex-1 overflow-auto px-6 py-5 space-y-6">
        {turns.length === 0 && !busy && (
          <div className="max-w-2xl">
            <p className="text-[14px] text-ink-300">Give the agent a job. It will think, call tools, then answer.</p>
            <div className="flex flex-wrap gap-2 mt-4">
              {PRESETS.map((p) => (
                <button key={p} onClick={() => ask(p)} className="text-left text-[12px] border border-white/10 rounded px-2 py-1.5 hover:bg-white/[0.04]">
                  {p}
                </button>
              ))}
            </div>
            <div className="grid grid-cols-2 gap-3 mt-6 text-[12px]">
              <div className="border border-white/10 rounded p-3">
                <div className="uppercase text-ink-400 mb-1">Without Hindsight</div>
                <p className="text-ink-300">The agent would lack prior operator facts (exception rationale). Graph + time still apply; historical “why we approved” is missing.</p>
              </div>
              <div className="border border-white/10 rounded p-3">
                <div className="uppercase text-ink-400 mb-1">With Hindsight</div>
                <p className="text-ink-300">Use Remember… then ask the reason. Recalled memories appear as MEMORY CONTEXT in Groq and in the Memory inspector (Used in answer YES/NO).</p>
              </div>
            </div>
          </div>
        )}

        {turns.map((turn) => (
          <div key={turn.id} className="max-w-3xl space-y-3">
            <div className="flex justify-end">
              <div className="rounded-lg bg-white/[0.07] px-3 py-2 text-[13px] max-w-[80%]">{turn.question}</div>
            </div>
            <div className="rounded-lg border border-white/[0.08] bg-ink-950/80 overflow-hidden">
              <div className="px-3 py-2 text-[11px] uppercase tracking-wide text-ink-400 border-b border-white/[0.06]">Agent trace</div>
              <div className="p-3 space-y-2 font-mono text-[12px]">
                {turn.thoughts.map((th, i) => (
                  <div key={i} className="text-ink-400">
                    <span className="text-status-info mr-2">think</span>
                    {th}
                  </div>
                ))}
                {turn.tools.map((tool, i) => (
                  <div key={`${tool.name}-${i}`} className="rounded border border-white/[0.06] px-2 py-1.5">
                    <div className="flex justify-between gap-3">
                      <span>
                        <span className={tool.status === "running" ? "text-status-warn" : "text-status-ok"}>
                          {tool.status === "running" ? "▸" : "✓"}
                        </span>{" "}
                        <span className="text-ink-100">{tool.name}</span>
                      </span>
                      <span className="text-ink-500">{tool.status === "running" ? "running…" : `${tool.ms ?? 0}ms`}</span>
                    </div>
                    {tool.summary && <div className="text-ink-400 mt-0.5 pl-4">{tool.summary}</div>}
                  </div>
                ))}
              </div>
              {turn.answer && (
                <div className="border-t border-white/[0.06] p-4 space-y-3 font-sans">
                  <div className="flex items-center gap-2">
                    <StatusPill value={turn.answer.compliance_status} />
                    <span className="text-[12px] text-ink-400">{Math.round(turn.answer.confidence * 100)}% · {turn.answer.run?.id}</span>
                  </div>
                  {turn.answer.intent && (
                    <p className="text-[11px] text-ink-400">Intent {turn.answer.intent} · tools {(turn.answer.selected_tools || []).join(", ")} · valid {turn.answer.valid_as_of} / system {turn.answer.system_as_of}</p>
                  )}
                  <p className="text-[14px] leading-relaxed">{turn.answer.conclusion}</p>
                  {(turn.answer.memories_used || []).length > 0 && (
                    <div className="rounded border border-white/10 p-2 space-y-1">
                      <div className="text-[11px] uppercase text-ink-400">Memory inspector (Hindsight)</div>
                      {(turn.answer.memories_used as any[]).map((m) => (
                        <div key={m.memory_id || m.text} className="text-[11px] font-mono text-ink-300">
                          {m.memory_id} · used={m.used_in_answer ? "YES" : "NO"} · {m.source} · {m.kind || "recall"}
                          <div className="text-ink-400 font-sans pl-2">{(m.text || "").slice(0, 180)}</div>
                        </div>
                      ))}
                    </div>
                  )}
                  {turn.answer.caveat && <p className="text-[12px] text-status-warn">{turn.answer.caveat}</p>}
                  {turn.answer.root_cause && (
                    <p className="text-[13px]"><span className="text-ink-400">Root cause · </span>{turn.answer.root_cause}</p>
                  )}
                  {turn.answer.remediation && (
                    <p className="text-[13px]"><span className="text-ink-400">Remediation · </span>{turn.answer.remediation}</p>
                  )}
                  {turn.answer.graph_path?.length > 0 && (
                    <p className="text-[12px] font-mono text-ink-400">{turn.answer.graph_path.join(" → ")}</p>
                  )}
                  <div className="flex flex-wrap gap-2">
                    {(turn.answer.evidence || []).slice(0, 5).map((e) => (
                      <span key={e.id} className="text-[11px] border border-white/10 rounded px-1.5 py-0.5">{e.id}</span>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => router.push("/graph")} className="h-7 px-2 border border-white/10 rounded text-[11px]">Graph</button>
                    <button onClick={() => router.push("/timeline")} className="h-7 px-2 border border-white/10 rounded text-[11px]">Time machine</button>
                    <button onClick={() => router.push("/evidence")} className="h-7 px-2 border border-white/10 rounded text-[11px]">Evidence</button>
                  </div>
                  {(turn.answer.timeline || []).length > 0 && (
                    <ol className="text-[12px] text-ink-400 space-y-1">
                      {turn.answer.timeline.map((ev) => (
                        <li key={ev.id}><span className="font-mono mr-2">{fmtDate(ev.valid_start)}</span>{ev.title}</li>
                      ))}
                    </ol>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
        {err && <div className="text-status-bad text-[13px]">{err}</div>}
        <div ref={bottom} />
      </div>

      <div className="border-t border-white/[0.07] p-4">
        <div className="flex gap-2 max-w-3xl">
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && ask(q)}
            placeholder="Ask the agent to investigate…"
            className="flex-1 h-10 bg-ink-900 border border-white/10 rounded px-3 text-[13px]"
          />
          <button onClick={() => ask(q)} disabled={busy} className="h-10 px-4 rounded bg-ink-50 text-ink-950 text-[13px] font-medium">
            {busy ? "Working" : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}
