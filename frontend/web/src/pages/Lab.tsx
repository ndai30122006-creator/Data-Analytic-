import { useState } from "react";
import { analysis } from "@app/shared/src/api/analysis";

const types = ["ttest_independent", "ttest_onesample", "ttest_paired", "anova", "mannwhitney", "kruskal", "bootstrap", "ab_test"] as const;

export default function Lab() {
  const [analysisType, setAnalysisType] = useState("ttest_independent");
  const [paramsText, setParamsText] = useState(JSON.stringify({ group_a: [1,2,3,4,5], group_b: [2,3,4,5,6] }, null, 2));
  const [datasetName, setDatasetName] = useState("inline");
  const [result, setResult] = useState("");

  const run = async () => {
    try {
      const params = JSON.parse(paramsText || "{}");
      const res = await analysis.run({ dataset_name: datasetName, analysis_type: analysisType, params });
      setResult(JSON.stringify(res, null, 2));
    } catch (e: any) {
      setResult(`Error: ${e.message}`);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <h2>Lab — Statistics (via core/statistical_tests)</h2>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "end" }}>
        <label style={{ display: "flex", flexDirection: "column", fontSize: 12 }}>Dataset
          <input value={datasetName} onChange={(e) => setDatasetName(e.target.value)} style={{ padding: 6, marginTop: 4, width: 140, background: "rgba(0,0,0,0.3)", color: "white", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 6 }} />
        </label>
        <label style={{ display: "flex", flexDirection: "column", fontSize: 12 }}>Analysis type
          <select value={analysisType} onChange={(e) => setAnalysisType(e.target.value)} style={{ padding: 6, marginTop: 4, background: "rgba(0,0,0,0.3)", color: "white", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 6 }}>
            {types.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </label>
        <button onClick={run} style={{ padding: "8px 14px", background: "#8B5CF6", color: "white", border: 0, borderRadius: 6, cursor: "pointer" }}>Run Analysis</button>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <div>
          <label style={{ fontWeight: 600, fontSize: 12 }}>Params JSON</label>
          <textarea value={paramsText} onChange={(e) => setParamsText(e.target.value)} rows={12} style={{ width: "100%", marginTop: 8, fontFamily: "monospace", fontSize: 11, padding: 12, background: "rgba(0,0,0,0.4)", color: "#E5E7EB", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8 }} />
          <div style={{ fontSize: 11, opacity: 0.5, marginTop: 6 }}>Ví dụ anova: {"{"}groups:[[1,2,3],[4,5,6]]{"}"} — bootstrap: {"{"}"data":[1,2,3],"n_iter":1000{"}"} — ab_test: {"{"}"successes_a":10,"total_a":100,...{"}"}</div>
        </div>
        <pre style={{ background: "rgba(0,0,0,0.4)", padding: 12, borderRadius: 8, fontSize: 11, overflow: "auto", maxHeight: 400, border: "1px solid rgba(255,255,255,0.06)" }}>{result || "Results: p-value, effect size, CI sẽ hiện ở đây"}</pre>
      </div>
    </div>
  );
}
