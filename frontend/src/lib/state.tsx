"use client";

import { createContext, useContext, useMemo, useState } from "react";

type AppState = {
  org: string;
  framework: string;
  validAsOf: string;
  systemAsOf: string;
  search: string;
  setOrg: (v: string) => void;
  setFramework: (v: string) => void;
  setValidAsOf: (v: string) => void;
  setSystemAsOf: (v: string) => void;
  setSearch: (v: string) => void;
};

const Ctx = createContext<AppState | null>(null);

export function AppStateProvider({ children }: { children: React.ReactNode }) {
  const [org, setOrg] = useState("ACME Corporation");
  const [framework, setFramework] = useState("SOC 2");
  const [validAsOf, setValidAsOf] = useState("2025-05-15");
  const [systemAsOf, setSystemAsOf] = useState("2025-05-15");
  const [search, setSearch] = useState("");
  const value = useMemo(
    () => ({ org, framework, validAsOf, systemAsOf, search, setOrg, setFramework, setValidAsOf, setSystemAsOf, setSearch }),
    [org, framework, validAsOf, systemAsOf, search]
  );
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useAppState() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("AppState missing");
  return ctx;
}
