import { useState } from "react";
import { analysis } from "@app/shared/api/analysis";
import { Button } from "@app/shared/components/ui/Button";
import { Card } from "@app/shared/components/ui/Card";
import { Input, Textarea } from "@app/shared/components/ui/Input";
import { PageHead } from "@app/shared/src/components/PageHead";

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
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <PageHead
        path="lab"
        title="Lab"
        desc="Statistics engine (t-test, ANOVA, bootstrap...) — chạy inline hoặc trên dataset đã ingest."
        actions={<Button onClick={run}>Run Analysis</Button>}
      />
      <Card>
        <h4>Cấu hình</h4>
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap", alignItems: "end", marginTop: 8 }}>
          <label style={{ display: "flex", flexDirection: "column", fontSize: 12, color: "var(--text-muted)" }}>Dataset
            <Input value={datasetName} onChange={(e) => setDatasetName(e.target.value)} style={{ marginTop: 4, width: 160 }} />
          </label>
          <label style={{ display: "flex", flexDirection: "column", fontSize: 12, color: "var(--text-muted)" }}>Analysis type
            <select value={analysisType} onChange={(e) => setAnalysisType(e.target.value)} style={{ padding: 9, marginTop: 4, background: "var(--bg)", color: "var(--text)", border: "1px solid var(--border)", borderRadius: "var(--radius-input)", fontFamily: "var(--font-mono)", fontSize: 12 }}>
              {types.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </label>
        </div>
      </Card>
      <div style={{ display: "grid", gridTemplateColumns: "minmax(300px, 1fr) minmax(320px, 1fr)", gap: 20 }}>
        <Card>
          <h4>Params JSON</h4>
          <Textarea value={paramsText} onChange={(e) => setParamsText(e.target.value)} rows={12} className="mono" style={{ marginTop: 8 }} />
          <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 6 }}>Ví dụ anova: {"{"}groups:[[1,2,3],[4,5,6]]{"}"} — bootstrap: {"{"}"data":[1,2,3],"n_iter":1000{"}"}</div>
        </Card>
        <Card style={{ background: "#000" }}>
          <h4 style={{ marginBottom: 8 }}>Result</h4>
          <pre style={{ fontFamily: "var(--font-mono)", fontSize: 11, overflow: "auto", maxHeight: 400, margin: 0, whiteSpace: "pre-wrap" }}>{result || "Results: p-value, effect size, CI sẽ hiện ở đây"}</pre>
        </Card>
      </div>
    </div>
  );
}
