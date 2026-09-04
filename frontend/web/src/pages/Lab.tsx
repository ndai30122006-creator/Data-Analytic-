import { useState } from "react";
import { analysis } from "@app/shared/src/api/analysis";

export default function Lab() {
  const [type, setType] = useState("ttest_independent");
  const [res, setRes] = useState("");
  const run = async () => {
    const r = await analysis.run({ dataset_name: "demo", analysis_type: type, params: {} });
    setRes(JSON.stringify(r, null, 2));
  };
  return (
    <div>
      <h2>Lab — Statistics</h2>
      <select value={type} onChange={(e) => setType(e.target.value)} style={{ padding: 6, marginRight: 8 }}>
        <option value="ttest_independent">T-test</option>
        <option value="anova">ANOVA</option>
        <option value="bootstrap">Bootstrap</option>
      </select>
      <button onClick={run} style={{ padding: "6px 12px" }}>
        Run
      </button>
      <pre style={{ marginTop: 12, background: "rgba(255,255,255,0.06)", padding: 12 }}>{res || "No result"}</pre>
    </div>
  );
}
