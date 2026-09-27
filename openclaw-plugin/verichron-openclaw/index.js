/**
 * OpenClaw tool plugin. Registers documented VeriChron tools that POST to FastAPI.
 * execute() never runs Cypher or shell. FastAPI enforces tenant, dates, and unknown controls.
 */
const TOOLS = [
  ["search_compliance_graph", "Search Neo4j at valid/system clocks. No silent date defaults."],
  ["traverse_control", "Bounded graph walk from control_id. Never invent CC6.1."],
  ["reconstruct_state", "Bitemporal reconstruction for a control."],
  ["compare_states", "Diff two valid-time states at one system_as_of."],
  ["get_evidence", "Evidence visible at the clocks."],
  ["analyze_evidence", "SUPPORTING vs CONTRADICTING; disclose conflicts."],
];

function params() {
  return {
    type: "object",
    properties: {
      tenant_id: { type: "string" },
      valid_as_of: { type: "string" },
      system_as_of: { type: "string" },
      query: { type: "string" },
      control_id: { type: "string" },
      first_valid_date: { type: "string" },
      second_valid_date: { type: "string" },
    },
    required: ["tenant_id"],
  };
}

async function callFastApi(name, args) {
  const base = process.env.VERICHRON_API_URL || "http://127.0.0.1:8000";
  const token = process.env.OPENCLAW_TOOL_TOKEN || "";
  const res = await fetch(`${base}/api/internal/openclaw/tools/${name}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-verichron-tool-token": token,
    },
    body: JSON.stringify(args || {}),
    signal: AbortSignal.timeout(25000),
  });
  const text = await res.text();
  let json;
  try {
    json = JSON.parse(text);
  } catch {
    json = { error: text.slice(0, 400), http: res.status };
  }
  return {
    content: [{ type: "text", text: JSON.stringify(json).slice(0, 8000) }],
    details: json,
  };
}

export default {
  id: "verichron-openclaw",
  name: "VeriChron compliance tools",
  register(api) {
    if (!api || typeof api.registerTool !== "function") {
      return;
    }
    for (const [name, description] of TOOLS) {
      api.registerTool({
        name,
        description,
        parameters: params(),
        async execute(_id, toolParams) {
          return callFastApi(name, toolParams);
        },
      });
    }
  },
};
