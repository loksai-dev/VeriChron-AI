"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Activity,
  Bell,
  Box,
  Clock,
  FileSearch,
  GitBranch,
  LayoutDashboard,
  MessageSquare,
  Search,
  Settings,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Brain,
} from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useAppState } from "@/lib/state";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/", label: "Overview", icon: LayoutDashboard },
  { href: "/compliance", label: "Compliance", icon: ShieldCheck },
  { href: "/controls", label: "Controls", icon: Shield },
  { href: "/findings", label: "Findings", icon: ShieldAlert },
  { href: "/evidence", label: "Evidence", icon: FileSearch },
  { href: "/graph", label: "Knowledge Graph", icon: GitBranch },
  { href: "/timeline", label: "Timeline", icon: Clock },
  { href: "/assistant", label: "Audit Assistant", icon: MessageSquare },
  { href: "/mental-models", label: "Mental Models", icon: Brain },
  { href: "/activity", label: "Agent Activity", icon: Activity },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const path = usePathname();
  const router = useRouter();
  const { org, framework, setOrg, setFramework, validAsOf, search, setSearch } = useAppState();
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth({ demo_mode: true, services: [] }));
  }, []);

  return (
    <div className="min-h-screen grid grid-cols-[240px_1fr]">
      <aside className="border-r border-white/[0.07] bg-ink-950 flex flex-col">
        <div className="h-14 px-4 flex items-center gap-2.5 border-b border-white/[0.07]">
          <div className="h-7 w-7 rounded-[6px] border border-white/10 bg-ink-900 grid place-items-center">
            <Box className="h-3.5 w-3.5 text-ink-100" />
          </div>
          <div>
            <div className="text-[13px] font-medium tracking-tight">VERICHRON AI</div>
            <div className="text-[10px] text-ink-400 tracking-wide uppercase">Bitemporal Audit</div>
          </div>
        </div>
        <nav className="flex-1 py-3 px-2 space-y-0.5">
          {NAV.map((item) => {
            const active = item.href === "/" ? path === "/" : path.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-2.5 px-2.5 h-8 rounded-md text-[13px] transition-colors",
                  active ? "bg-white/[0.07] text-ink-50" : "text-ink-400 hover:text-ink-100 hover:bg-white/[0.03]"
                )}
              >
                <item.icon className="h-3.5 w-3.5" />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="p-2 border-t border-white/[0.07] space-y-0.5">
          <Link href="/settings" className="flex items-center gap-2.5 px-2.5 h-8 rounded-md text-[13px] text-ink-400 hover:text-ink-100">
            <Settings className="h-3.5 w-3.5" />
            Settings
          </Link>
          <div className="px-2.5 py-2 text-[11px] text-ink-400 space-y-1">
            <div className="uppercase tracking-wide mb-1">System status</div>
            <div className="flex justify-between"><span>DEMO MODE</span><span className={health?.demo_mode ? "text-status-info" : "text-ink-400"}>{health?.demo_mode ? "on" : "off"}</span></div>
            <div className="flex justify-between"><span>Neo4j</span><span className={health?.neo4j === "connected" ? "text-status-ok" : "text-status-warn"}>{health?.neo4j || "…"}</span></div>
            <div className="flex justify-between"><span>Hindsight</span><span className={health?.hindsight === "connected" ? "text-status-ok" : "text-status-warn"}>{health?.hindsight || "…"}</span></div>
            <div className="flex justify-between"><span>Groq</span><span className={health?.groq === "connected" ? "text-status-ok" : "text-status-warn"}>{health?.groq || "…"}</span></div>
          </div>
        </div>
      </aside>
      <div className="min-w-0 flex flex-col">
        <header className="h-14 border-b border-white/[0.07] bg-ink-950/80 backdrop-blur px-5 flex items-center gap-3">
          <select
            value={org}
            onChange={(e) => setOrg(e.target.value)}
            className="h-8 bg-transparent text-[13px] border border-white/10 rounded-md px-2"
          >
            <option>ACME Corporation</option>
            <option>ACME EU</option>
          </select>
          <select
            value={framework}
            onChange={(e) => setFramework(e.target.value)}
            className="h-8 bg-transparent text-[13px] border border-white/10 rounded-md px-2"
          >
            <option>SOC 2</option>
            <option>ISO 27001</option>
          </select>
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-2.5 top-2 h-3.5 w-3.5 text-ink-400" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && search.trim()) router.push(`/assistant?q=${encodeURIComponent(search)}`);
              }}
              placeholder="Search controls, findings, evidence…"
              className="w-full h-8 pl-8 pr-3 bg-ink-900 border border-white/10 rounded-md text-[13px] outline-none focus:border-white/20"
            />
          </div>
          <button
            onClick={() => router.push("/timeline")}
            className="h-8 px-3 rounded-md border border-white/10 text-[12px] inline-flex items-center gap-1.5 hover:bg-white/[0.04]"
          >
            <Clock className="h-3.5 w-3.5" />
            Time machine
            <span className="font-mono text-ink-400">{validAsOf}</span>
          </button>
          <button className="h-8 w-8 grid place-items-center rounded-md border border-white/10">
            <Bell className="h-3.5 w-3.5 text-ink-400" />
          </button>
          <div className="h-8 w-8 rounded-full bg-ink-800 border border-white/10 grid place-items-center text-[11px]">AC</div>
        </header>
        <main className="flex-1 overflow-auto">{children}</main>
      </div>
    </div>
  );
}
