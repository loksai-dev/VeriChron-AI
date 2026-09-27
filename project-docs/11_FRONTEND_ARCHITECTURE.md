# 11 — Frontend architecture

Next.js 14 App Router, Tailwind. Shell: `frontend/src/components/layout/AppShell.tsx`.

**No screenshots are checked into the repository.**

## Pages (routes)

| Path | File | Behavior |
| --- | --- | --- |
| `/` | `src/app/page.tsx` | Overview metrics from `/api/overview` |
| `/compliance` | `compliance/page.tsx` | Gap matrix from overview |
| `/controls` | `controls/page.tsx` | `/api/controls` |
| `/findings` | `findings/page.tsx` | `/api/findings` |
| `/evidence` | `evidence/page.tsx` | `/api/evidence` |
| `/graph` | `graph/page.tsx` | React Flow via `GraphCanvas.tsx` + `/api/graph` |
| `/timeline` | `timeline/page.tsx` | Time machine; reconstruct API |
| `/assistant` | `assistant/page.tsx` + `inner.tsx` | SSE tool trace |
| `/mental-models` | `mental-models/page.tsx` | `/api/mental-models` |
| `/activity` | `activity/page.tsx` | `/api/agent-runs` |
| `/settings` | `settings/page.tsx` | Exists; **not** in primary NAV |

## State

`AppStateProvider` (`lib/state.tsx`): org, framework, `validAsOf` / `systemAsOf` (default **2025-05-15**), search. Not Redux.

## API

`lib/api.ts`: `api.*` JSON helpers and `streamQuery` for SSE. Base `NEXT_PUBLIC_API_URL` or `http://localhost:8000`.

## Graph / timeline / agent / evidence

- Graph: React Flow canvas; Cypher string from backend when live.
- Timeline: valid vs system date controls; filtered events.
- Agent: live `thought` / `tool_start` / `tool_end` / `answer`.
- Evidence: table of demo evidence kinds.

**Does not exist:** auth screens, multi-tenant switcher, editing GRC records, OpenClaw UI.
