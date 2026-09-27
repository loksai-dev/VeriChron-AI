"use client";

import dynamic from "next/dynamic";

const GraphCanvas = dynamic(() => import("@/components/graph/GraphCanvas"), { ssr: false });

export default function GraphPage() {
  return <GraphCanvas />;
}
