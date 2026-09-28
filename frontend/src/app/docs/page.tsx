"use client";

import { useState } from "react";
import { PageHeader, Panel } from "@/components/ui/primitives";
import {
  BookOpen,
  Cpu,
  Database,
  GitBranch,
  Layers,
  Terminal,
  Shield,
  Clock,
  Copy,
  Check,
  ExternalLink,
  Search,
  Sparkles,
  FileCode,
  PlayCircle
} from "lucide-react";

type DocSection = "overview" | "bitemporal" | "architecture" | "openclaw_hindsight" | "api" | "demo_script";

export default function DocsPage() {
  const [activeTab, setActiveTab] = useState<DocSection>("overview");
  const [copiedCode, setCopiedCode] = useState<string | null>(null);
  const [searchFilter, setSearchFilter] = useState("");

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const tabs = [
    { id: "overview", label: "Overview & Vision", icon: BookOpen },
    { id: "bitemporal", label: "Bitemporal Model", icon: Clock },
    { id: "architecture", label: "System Architecture", icon: Layers },
    { id: "openclaw_hindsight", label: "OpenClaw & Memory", icon: Cpu },
    { id: "api", label: "API & Streaming", icon: Terminal },
    { id: "demo_script", label: "Hackathon Demo Script", icon: PlayCircle },
  ];

  return (
    <div className="p-8 max-w-[1400px] space-y-6">
      <PageHeader
        title="Project Documentation"
        subtitle="Complete technical architecture, bitemporal mathematics, multi-agent orchestration, and operational guides"
        actions={
          <div className="flex items-center gap-2">
            <span className="text-[12px] text-ink-400 font-mono">v1.2.0-stable</span>
            <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Live Verified
            </span>
          </div>
        }
      />

      {/* Navigation Tabs */}
      <div className="flex items-center gap-1 border-b border-white/[0.08] pb-1 overflow-x-auto">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as DocSection)}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-md text-[13px] font-medium transition-all ${
                isActive
                  ? "bg-white/[0.08] text-ink-50 shadow-sm border border-white/[0.1]"
                  : "text-ink-400 hover:text-ink-200 hover:bg-white/[0.02]"
              }`}
            >
              <Icon className={`h-4 w-4 ${isActive ? "text-emerald-400" : "text-ink-400"}`} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Main Tab Content */}
      <div className="grid grid-cols-1 gap-6">
        {/* OVERVIEW TAB */}
        {activeTab === "overview" && (
          <div className="space-y-6">
            <Panel className="p-6">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-[18px] font-medium text-ink-100">The Problem: Temporal Flattening in Compliance</h2>
                  <p className="text-[13px] text-ink-300 mt-2 max-w-3xl leading-relaxed">
                    Standard Governance, Risk, and Compliance (GRC) tools and RAG systems only index today’s documents. When an auditor asks 
                    <span className="text-emerald-400 font-mono text-[12px] ml-1 mr-1">“What was our posture on May 15, 2025?”</span>, 
                    conventional AI looks at the latest snapshot. If an updated MFA policy was uploaded in July 2025 stating it applied since January, 
                    standard RAG falsely asserts compliance on May 15. In regulatory audits (SOC 2, ISO 27001, HIPAA), presenting future-known 
                    records is an audit failure.
                  </p>
                </div>
                <div className="h-10 w-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 grid place-items-center shrink-0">
                  <Shield className="h-5 w-5 text-emerald-400" />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                <div className="p-4 rounded-lg bg-ink-950/60 border border-white/[0.05]">
                  <div className="text-[12px] uppercase text-emerald-400 font-mono tracking-wider font-semibold">1. Dual-Clock Indexing</div>
                  <div className="text-[14px] font-medium text-ink-100 mt-1">Valid Time vs. System Time</div>
                  <p className="text-[12px] text-ink-400 mt-1">
                    Every node and relationship is bounded by when it occurred in the real world vs. when it was recorded by the system.
                  </p>
                </div>

                <div className="p-4 rounded-lg bg-ink-950/60 border border-white/[0.05]">
                  <div className="text-[12px] uppercase text-emerald-400 font-mono tracking-wider font-semibold">2. Graph Grounding</div>
                  <div className="text-[14px] font-medium text-ink-100 mt-1">Neo4j Typed Relationships</div>
                  <p className="text-[12px] text-ink-400 mt-1">
                    Explicit typed edges: <code className="text-ink-200">GOVERNS</code>, <code className="text-ink-200">SATISFIED_BY</code>, <code className="text-ink-200">VIOLATES</code>, and <code className="text-ink-200">REMEDIATED_BY</code>.
                  </p>
                </div>

                <div className="p-4 rounded-lg bg-ink-950/60 border border-white/[0.05]">
                  <div className="text-[12px] uppercase text-emerald-400 font-mono tracking-wider font-semibold">3. Multi-Session Memory</div>
                  <div className="text-[14px] font-medium text-ink-100 mt-1">Hindsight Cloud Memory Banks</div>
                  <p className="text-[12px] text-ink-400 mt-1">
                    Durable retention, semantic recall, reflection, and evolving mental models that persist across audits.
                  </p>
                </div>
              </div>
            </Panel>

            <Panel className="p-6">
              <h3 className="text-[16px] font-medium text-ink-100 mb-4">Canonical ACME Scenario: SOC 2 CC6.1</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-[13px]">
                  <thead>
                    <tr className="border-b border-white/[0.07] text-left text-[11px] uppercase text-ink-400">
                      <th className="pb-2">Date</th>
                      <th className="pb-2">World Truth (Valid Time)</th>
                      <th className="pb-2">System Knowledge (System Time)</th>
                      <th className="pb-2">Reconstruction State</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/[0.04]">
                    <tr>
                      <td className="py-2.5 font-mono text-[12px] text-ink-300">2025-01-08</td>
                      <td className="py-2.5">MFA enforced for all engineers</td>
                      <td className="py-2.5">Okta export ingested and logged</td>
                      <td className="py-2.5"><span className="text-emerald-400">COMPLIANT</span></td>
                    </tr>
                    <tr>
                      <td className="py-2.5 font-mono text-[12px] text-ink-300">2025-04-12</td>
                      <td className="py-2.5">Engineer disables MFA condition for CI/CD deploy</td>
                      <td className="py-2.5">CloudTrail logs IAM event (unreviewed)</td>
                      <td className="py-2.5"><span className="text-red-400">NON-COMPLIANT (Silent Drift)</span></td>
                    </tr>
                    <tr>
                      <td className="py-2.5 font-mono text-[12px] text-ink-300 font-bold text-amber-400">2025-05-15</td>
                      <td className="py-2.5 font-medium text-amber-200">MFA is still disabled in AWS</td>
                      <td className="py-2.5 text-amber-200">Test has not run yet; no finding filed</td>
                      <td className="py-2.5"><span className="text-amber-400">AUDIT BLINDSPOT (Undetected)</span></td>
                    </tr>
                    <tr>
                      <td className="py-2.5 font-mono text-[12px] text-ink-300">2025-05-20</td>
                      <td className="py-2.5">MFA is still disabled</td>
                      <td className="py-2.5">Automated GRC scan fails</td>
                      <td className="py-2.5"><span className="text-red-400">DETECTED BREACH</span></td>
                    </tr>
                    <tr>
                      <td className="py-2.5 font-mono text-[12px] text-ink-300">2025-06-03</td>
                      <td className="py-2.5">MFA disabled; audit finding open</td>
                      <td className="py-2.5">Formal audit memo filed (FINDING-2025-01)</td>
                      <td className="py-2.5"><span className="text-red-400">DOCUMENTED FINDING</span></td>
                    </tr>
                    <tr>
                      <td className="py-2.5 font-mono text-[12px] text-ink-300">2025-07-08</td>
                      <td className="py-2.5">MFA re-enabled & enforced</td>
                      <td className="py-2.5">Jira ticket closed & verified</td>
                      <td className="py-2.5"><span className="text-emerald-400">REMEDIATED</span></td>
                    </tr>
                    <tr>
                      <td className="py-2.5 font-mono text-[12px] text-ink-300">2025-07-15</td>
                      <td className="py-2.5">Policy PDF claims valid since Jan 1</td>
                      <td className="py-2.5">Document first uploaded to GRC</td>
                      <td className="py-2.5"><span className="text-indigo-400">RETROACTIVE DOCUMENTATION</span></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </Panel>
          </div>
        )}

        {/* BITEMPORAL TAB */}
        {activeTab === "bitemporal" && (
          <div className="space-y-6">
            <Panel className="p-6">
              <h2 className="text-[18px] font-medium text-ink-100">Bitemporal Logic & The Invariance Rule</h2>
              <p className="text-[13px] text-ink-300 mt-2 leading-relaxed">
                VeriChron mathematically separates the timeline of the physical world from the recording timeline of the organization.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                <div className="p-5 rounded-lg bg-ink-950 border border-white/[0.07] space-y-3">
                  <div className="flex items-center gap-2 text-emerald-400 font-mono text-[13px] font-semibold">
                    <Clock className="h-4 w-4" /> Valid Time [valid_start, valid_end)
                  </div>
                  <p className="text-[12px] text-ink-300">
                    The interval during which the compliance state, policy, or configuration was physically true in the real world.
                  </p>
                  <div className="p-3 bg-ink-900 rounded font-mono text-[12px] text-ink-200">
                    valid_start: &quot;2025-04-12T00:00:00Z&quot;<br />
                    valid_end: &quot;2025-07-08T00:00:00Z&quot;
                  </div>
                </div>

                <div className="p-5 rounded-lg bg-ink-950 border border-white/[0.07] space-y-3">
                  <div className="flex items-center gap-2 text-indigo-400 font-mono text-[13px] font-semibold">
                    <Database className="h-4 w-4" /> System Time [system_start, system_end)
                  </div>
                  <p className="text-[12px] text-ink-300">
                    The interval during which the organization was aware of this fact in its databases, logs, or audit records.
                  </p>
                  <div className="p-3 bg-ink-900 rounded font-mono text-[12px] text-ink-200">
                    system_start: &quot;2025-05-20T10:15:00Z&quot;<br />
                    system_end: null (still active knowledge)
                  </div>
                </div>
              </div>

              <div className="mt-6 p-4 rounded-lg bg-ink-950/80 border border-emerald-500/20">
                <div className="text-[12px] uppercase font-mono text-emerald-400 font-bold mb-1">Visibility Invariant Formula</div>
                <p className="text-[13px] font-mono text-ink-200">
                  visible(E, τ_v, τ_s) ⟺ (valid_start(E) ≤ τ_v &lt; valid_end(E)) ∧ (system_start(E) ≤ τ_s &lt; system_end(E))
                </p>
                <p className="text-[12px] text-ink-400 mt-2">
                  Crucial guarantee: An artifact whose <code className="text-ink-200 font-mono">system_start &gt; τ_s</code> is shielded from 
                  ever reaching the agent context or historical graph traversal.
                </p>
              </div>
            </Panel>
          </div>
        )}

        {/* ARCHITECTURE TAB */}
        {activeTab === "architecture" && (
          <div className="space-y-6">
            <Panel className="p-6">
              <h2 className="text-[18px] font-medium text-ink-100">End-to-End System Topography</h2>
              <p className="text-[13px] text-ink-300 mt-2">
                Five decoupled layers operating in unison to deliver sub-second, grounded bitemporal compliance audits.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
                <div className="p-4 rounded-lg bg-ink-950/60 border border-white/[0.05]">
                  <div className="text-[13px] font-medium text-ink-100 flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-emerald-400"></span>
                    Frontend Console (Next.js 14 App Router)
                  </div>
                  <p className="text-[12px] text-ink-400 mt-1">
                    Port: <code className="text-ink-200">3000</code>. SSE streaming consumption, interactive React Flow graph, Recharts timeline, and audit assistant.
                  </p>
                </div>

                <div className="p-4 rounded-lg bg-ink-950/60 border border-white/[0.05]">
                  <div className="text-[13px] font-medium text-ink-100 flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-emerald-400"></span>
                    Application Layer (FastAPI)
                  </div>
                  <p className="text-[12px] text-ink-400 mt-1">
                    Port: <code className="text-ink-200">8000</code>. Bitemporal slice engine, ingestion pipelines, SSE event bus, and internal tool endpoints.
                  </p>
                </div>

                <div className="p-4 rounded-lg bg-ink-950/60 border border-white/[0.05]">
                  <div className="text-[13px] font-medium text-ink-100 flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-emerald-400"></span>
                    Multi-Agent Gateway (OpenClaw)
                  </div>
                  <p className="text-[12px] text-ink-400 mt-1">
                    Port: <code className="text-ink-200">18789</code>. Multi-agent execution loop with isolated run sessions and auto-failover to ComplianceAgent.
                  </p>
                </div>

                <div className="p-4 rounded-lg bg-ink-950/60 border border-white/[0.05]">
                  <div className="text-[13px] font-medium text-ink-100 flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-emerald-400"></span>
                    Cognitive Memory (Hindsight Cloud)
                  </div>
                  <p className="text-[12px] text-ink-400 mt-1">
                    Host: <code className="text-ink-200">api.hindsight.vectorize.io</code>. Dedicated memory bank holding episodic compliance facts and mental models.
                  </p>
                </div>
              </div>
            </Panel>
          </div>
        )}

        {/* OPENCLAW & MEMORY TAB */}
        {activeTab === "openclaw_hindsight" && (
          <div className="space-y-6">
            <Panel className="p-6">
              <h2 className="text-[18px] font-medium text-ink-100">OpenClaw Gateway & Hindsight Cloud Memory</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
                <div className="space-y-3">
                  <div className="text-[14px] font-medium text-ink-100">Dual-Orchestration & Fallback</div>
                  <p className="text-[12px] text-ink-300 leading-relaxed">
                    OpenClaw operates as the primary agent loop on loopback port 18789. When Groq rate limits (HTTP 429) or gateway drops occur, 
                    the application instantly triggers a zero-downtime failover to the native <code className="text-ink-200 font-mono">ComplianceAgent</code> pipeline, 
                    guaranteeing the auditor always receives a complete, sourced answer.
                  </p>
                  <div className="p-3 bg-ink-950 rounded border border-white/[0.07] font-mono text-[11px] text-ink-300">
                    session_user = f&quot;verichron:&#123;tenant_id&#125;:&#123;username&#125;:&#123;run_id&#125;&quot;<br />
                    # Resets prompt tokens per run to satisfy 8,000 TPM limit
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="text-[14px] font-medium text-ink-100">Hindsight 4-Primitive Memory</div>
                  <ul className="space-y-2 text-[12px] text-ink-300">
                    <li className="flex items-start gap-2">
                      <span className="font-mono text-emerald-400 font-bold">retain:</span>
                      <span>Stores unstructured facts and approved exceptions with valid/system timestamps.</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-mono text-emerald-400 font-bold">recall:</span>
                      <span>Semantically recalls memories matching query context into LLM prompts.</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-mono text-emerald-400 font-bold">reflect:</span>
                      <span>Synthesizes long-term trends and organizational posture changes over time.</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="font-mono text-emerald-400 font-bold">mental_models:</span>
                      <span>Persistent high-level models (e.g. ACME SOC 2 CC6.1) that evolve.</span>
                    </li>
                  </ul>
                </div>
              </div>
            </Panel>
          </div>
        )}

        {/* API REFERENCE TAB */}
        {activeTab === "api" && (
          <div className="space-y-6">
            <Panel className="p-6">
              <div className="flex items-center justify-between">
                <h2 className="text-[18px] font-medium text-ink-100">API Specifications & Streaming Endpoints</h2>
                <a
                  href="http://localhost:8000/docs"
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1.5 text-[12px] text-emerald-400 hover:text-emerald-300"
                >
                  Interactive Swagger Docs <ExternalLink className="h-3.5 w-3.5" />
                </a>
              </div>

              <div className="space-y-4 mt-6">
                {/* Endpoint 1 */}
                <div className="p-4 rounded-lg bg-ink-950 border border-white/[0.07] space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                        POST
                      </span>
                      <code className="text-[13px] font-mono text-ink-100">/api/query/stream</code>
                    </div>
                    <button
                      onClick={() =>
                        copyToClipboard(
                          `curl -N -X POST http://localhost:8000/api/query/stream -H "Content-Type: application/json" -d '{"question": "What was our compliance posture on May 15, 2025?", "valid_as_of": "2025-05-15T00:00:00Z", "system_as_of": "2025-05-15T00:00:00Z"}'`,
                          "curl_query_stream"
                        )
                      }
                      className="flex items-center gap-1 text-[11px] text-ink-400 hover:text-ink-200"
                    >
                      {copiedCode === "curl_query_stream" ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                      Copy curl
                    </button>
                  </div>
                  <p className="text-[12px] text-ink-400">
                    Streams Server-Sent Events (SSE) representing agent execution: <code>run_start</code>, <code>thought</code>, <code>tool_start</code>, <code>tool_result</code>, <code>answer</code>, and <code>done</code>.
                  </p>
                </div>

                {/* Endpoint 2 */}
                <div className="p-4 rounded-lg bg-ink-950 border border-white/[0.07] space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                        GET
                      </span>
                      <code className="text-[13px] font-mono text-ink-100">/api/health</code>
                    </div>
                    <button
                      onClick={() =>
                        copyToClipboard(`curl http://localhost:8000/api/health`, "curl_health")
                      }
                      className="flex items-center gap-1 text-[11px] text-ink-400 hover:text-ink-200"
                    >
                      {copiedCode === "curl_health" ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                      Copy curl
                    </button>
                  </div>
                  <p className="text-[12px] text-ink-400">
                    Returns detailed connectivity status for OpenClaw Gateway, Hindsight Cloud bank, Groq models, and Neo4j graph.
                  </p>
                </div>

                {/* Endpoint 3 */}
                <div className="p-4 rounded-lg bg-ink-950 border border-white/[0.07] space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                        POST
                      </span>
                      <code className="text-[13px] font-mono text-ink-100">/api/audit/reconstruct</code>
                    </div>
                    <p className="text-[12px] text-ink-400">
                      Reconstructs exact control state at given <code>valid_as_of</code> and <code>system_as_of</code> coordinates.
                    </p>
                  </div>
                </div>
              </div>
            </Panel>
          </div>
        )}

        {/* DEMO SCRIPT TAB */}
        {activeTab === "demo_script" && (
          <div className="space-y-6">
            <Panel className="p-6">
              <h2 className="text-[18px] font-medium text-ink-100">3-Minute Judge Demonstration Script</h2>
              <p className="text-[13px] text-ink-300 mt-2">
                Follow this exact sequence to demonstrate the full capability of VeriChron AI in under 3 minutes.
              </p>

              <div className="space-y-4 mt-6">
                <div className="p-4 rounded-lg bg-ink-950 border border-white/[0.07]">
                  <div className="flex items-center justify-between">
                    <div className="text-[13px] font-semibold text-emerald-400">Act 1: Durable Episodic Memory in Hindsight Cloud</div>
                    <span className="text-[11px] font-mono text-ink-400">0:00 - 0:45</span>
                  </div>
                  <ol className="list-decimal list-inside text-[12px] text-ink-300 space-y-1 mt-2">
                    <li>Go to <strong>Audit Assistant</strong> (<code className="text-ink-200">/assistant</code>).</li>
                    <li>Click preset: <em>&quot;Remember that the ACME MFA exception was approved by CISO for CI/CD deploy runner.&quot;</em></li>
                    <li>Observe instantaneous retention into Hindsight Cloud Bank (UUID: <code className="text-ink-200">6f3b938e...</code>).</li>
                    <li>Ask: <em>&quot;What was the reason for the ACME MFA exception?&quot;</em></li>
                    <li>Verify the agent recalls the memory in real time and attributes it to the CISO approval.</li>
                  </ol>
                </div>

                <div className="p-4 rounded-lg bg-ink-950 border border-white/[0.07]">
                  <div className="flex items-center justify-between">
                    <div className="text-[13px] font-semibold text-emerald-400">Act 2: The Bitemporal Time Machine</div>
                    <span className="text-[11px] font-mono text-ink-400">0:45 - 1:45</span>
                  </div>
                  <ol className="list-decimal list-inside text-[12px] text-ink-300 space-y-1 mt-2">
                    <li>Navigate to <strong>Timeline</strong> (<code className="text-ink-200">/timeline</code>).</li>
                    <li>Set <strong>Valid Time</strong> to <code className="text-ink-200">2025-05-15</code> and <strong>System Time</strong> to <code className="text-ink-200">2025-05-15</code>.</li>
                    <li>Click <strong>Reconstruct state</strong>: MFA Policy is INACTIVE, but Organization Knowledge shows no finding was detected yet.</li>
                    <li>Slide <strong>System Time</strong> to <code className="text-ink-200">2025-05-25</code>: State updates to DETECTED NON-COMPLIANT.</li>
                  </ol>
                </div>

                <div className="p-4 rounded-lg bg-ink-950 border border-white/[0.07]">
                  <div className="flex items-center justify-between">
                    <div className="text-[13px] font-semibold text-emerald-400">Act 3: Future Knowledge Shielding</div>
                    <span className="text-[11px] font-mono text-ink-400">1:45 - 2:45</span>
                  </div>
                  <ol className="list-decimal list-inside text-[12px] text-ink-300 space-y-1 mt-2">
                    <li>In <strong>Audit Assistant</strong>, ask: <em>&quot;What was our compliance posture on May 15, 2025?&quot;</em></li>
                    <li>Inspect the tool execution trace: observe <code className="text-ink-200 font-mono">reconstruct_historical_state</code> executing.</li>
                    <li>Show that the July 15 policy upload is shielded and excluded from May 15 audit evidence.</li>
                  </ol>
                </div>
              </div>
            </Panel>
          </div>
        )}
      </div>
    </div>
  );
}
