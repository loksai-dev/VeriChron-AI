import type { HTMLAttributes } from "react";
import { cn, statusClass, statusLabel } from "@/lib/utils";

export function StatusPill({ value }: { value: string }) {
  return (
    <span className={cn("inline-flex items-center h-5 px-1.5 rounded border text-[11px] font-medium", statusClass(value))}>
      {statusLabel(value)}
    </span>
  );
}

export function PageHeader({ title, subtitle, actions }: { title: string; subtitle?: string; actions?: React.ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-4 mb-6">
      <div>
        <h1 className="text-[22px] font-medium tracking-tight">{title}</h1>
        {subtitle && <p className="text-[13px] text-ink-400 mt-1">{subtitle}</p>}
      </div>
      {actions}
    </div>
  );
}

export function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <div className="border border-dashed border-white/10 rounded-lg p-10 text-center">
      <div className="text-[14px]">{title}</div>
      <p className="text-[13px] text-ink-400 mt-1">{body}</p>
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="border border-status-bad/30 bg-status-bad/10 rounded-lg p-4 text-[13px] text-status-bad">{message}</div>
  );
}

export function Panel({
  children,
  className,
  ...props
}: { children: React.ReactNode; className?: string } & HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("rounded-lg border border-white/[0.07] bg-ink-900/60", className)} {...props}>
      {children}
    </div>
  );
}
