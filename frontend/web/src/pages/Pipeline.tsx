import { useState } from "react";
import { pipelines } from "@app/shared/src/api/pipelines";

export default function Pipeline() {
  const [spec, setSpec] = useState(JSON.stringify({ name: "demo", source: "raw.t", target: "mart.t", steps: [] }, null, 2));
  const [res, setRes] = useState("");
  const preview = async () => {
    const r = await pipelines.preview(JSON.parse(spec));
    setRes(JSON.stringify(r, null, 2));
  };
  const run = async () => {
    const created = await pipelines.create(JSON.parse(spec));
    const r = await pipelines.run((created as any).pipeline_id);
    setRes(JSON.stringify(r, null, 2));
  };
  return (
    <div>
      <h2>Pipeline — ETL/ELT</h2>
      <textarea value={spec} onChange={(e) => setSpec(e.target.value)} style={{ width: "100%", height: 120, fontFamily: "monospace" }} />
      <div style={{ marginTop: 8, display: "flex", gap: 8 }}>
        <button onClick={preview} style={{ padding: "6px 12px" }}>
          Dry-run
        </button>
        <button onClick={run} style={{ padding: "6px 12px" }}>
          Run
        </button>
      </div>
      <pre style={{ marginTop: 12, background: "rgba(255,255,255,0.06)", padding: 12 }}>{res || "No result"}</pre>
    </div>
  );
}
