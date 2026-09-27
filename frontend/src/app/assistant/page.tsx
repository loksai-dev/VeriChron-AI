"use client";

import { Suspense } from "react";
import AssistantInner from "./inner";

export default function AssistantPage() {
  return (
    <Suspense fallback={<div className="p-8 text-[13px] text-ink-400">Loading assistant…</div>}>
      <AssistantInner />
    </Suspense>
  );
}
