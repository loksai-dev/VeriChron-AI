import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import type { ComplianceStatus } from "./api";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function statusLabel(s: ComplianceStatus | string) {
  const map: Record<string, string> = {
    compliant: "Compliant",
    non_compliant: "Non-compliant",
    at_risk: "At risk",
    unknown: "Unknown",
    remediated: "Remediated",
    complete: "Complete",
    partial: "Partial",
    missing: "Missing",
  };
  return map[s] || s;
}

export function statusClass(s: string) {
  if (s === "compliant" || s === "complete" || s === "ok" || s === "ACTIVE" || s === "PASS")
    return "text-status-ok bg-status-ok/10 border-status-ok/20";
  if (s === "at_risk" || s === "partial" || s === "warn" || s === "DEGRADED")
    return "text-status-warn bg-status-warn/10 border-status-warn/20";
  if (s === "non_compliant" || s === "missing" || s === "FAIL" || s === "OPEN" || s === "critical")
    return "text-status-bad bg-status-bad/10 border-status-bad/20";
  if (s === "remediated" || s === "COMPLETE" || s === "info")
    return "text-status-info bg-status-info/10 border-status-info/20";
  return "text-ink-400 bg-white/5 border-white/10";
}

export function fmtDate(value?: string | null) {
  if (!value) return "open";
  return value.slice(0, 10);
}
