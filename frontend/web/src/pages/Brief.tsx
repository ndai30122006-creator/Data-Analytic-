import { useState } from "react";
import { brief } from "@app/shared/src/api/brief";
import { datasets } from "@app/shared/src/api/datasets";

export default function Brief() {
  const [datasetId, setDatasetId] = useState(1);
  const [content, setContent] = useState("");
  const [history, setHistory] = useState<any[]>([]);
  const [version, setVersion] = useState<number | "">("");

  const create = async () => {
    try {
      const res = await brief.create(datasetId);
      setContent(res.content ?? JSON.stringify(res, null, 2));
      list();
    } catch (e: any) {
      setContent(`Error: ${e.message}`);
    }
  };
  const list = async () => {
    try {
      const res = await brief.list(datasetId);
      setHistory(res.briefs ?? res ?? []);
    } catch (e: any) {
      setContent(`List error: ${e.message}`);
    }
  };
  const getVersion = async () => {
    if (version === "") return;
    try {
      const res = await brief.get(datasetId, Number(version));
      setContent(res.content ?? JSON.stringify(res, null, 2));
    } catch (e: any) {
      setContent(`Get error: ${e.message}`);
    }
  };
  const exportMd = () => {
    const blob = new Blob([content], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = `brief-${datasetId}.md`; a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <h2>Brief — AI Narrative (profile-only)</h2>
      <div style={{ display: "flex", gap: 8, alignItems: "end", flexWrap: "wrap" }}>
        <label style={{ display: "flex", flexDirection: "column", fontSize: 12 }}>Dataset ID
          <input type="number" value={datasetId} onChange={(e) => setDatasetId(Number(e.target.value))} style={{ padding: 6, marginTop: 4, width: 100, background: "rgba(0,0,0,0.3)", color: "white", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 6 }} />
        </label>
        <button onClick={create} style={{ padding: "8px 14px", background: "#8B5CF6", color: "white", border: 0, borderRadius: 6, cursor: "pointer" }}>Generate Brief (1-click)</button>
        <button onClick={list} style={{ padding: "8px 14px", background: "rgba(255,255,255,0.08)", color: "white", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 6, cursor: "pointer" }}>History</button>
        <button onClick={exportMd} disabled={!content} style={{ padding: "8px 14px", background: "#3B82F6", color: "white", border: 0, borderRadius: 6, cursor: content ? "pointer" : "not-allowed" }}>Export MD</button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 300px", gap: 16 }}>
        <pre style={{ background: "rgba(0,0,0,0.4)", padding: 12, borderRadius: 8, fontSize: 12, overflow: "auto", maxHeight: 400, whiteSpace: "pre-wrap", border: "1px solid rgba(255,255,255,0.06)" }}>{content || "Brief tiếng Việt sẽ hiện ở đây (fallback rule-based nếu không BYOK)"}</pre>
        <div style={{ border: "1px solid rgba(255,255,255,0.08)", borderRadius: 8, padding: 12 }}>
          <h4 style={{ margin: "0 0 8px", fontSize: 13 }}>History versions</h4>
          {history.length === 0 ? <div style={{ opacity: 0.5, fontSize: 12 }}>Chưa có brief</div> : history.map((b: any, i: number) => (
            <div key={i} style={{ padding: "6px 0", borderBottom: "1px solid rgba(255,255,255,0.06)", fontSize: 12 }}>
              <span style={{ fontWeight: 600 }}>v{b.version ?? i+1}</span> <span style={{ opacity: 0.5 }}>{b.model_used ?? ""}</span>
            </div>
          ))}
          <div style={{ marginTop: 12, display: "flex", gap: 6 }}>
            <input type="number" placeholder="version" value={version} onChange={(e) => setVersion(e.target.value === "" ? "" : Number(e.target.value))} style={{ width: 80, padding: 6, background: "rgba(0,0,0,0.3)", color: "white", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 6, fontSize: 12 }} />
            <button onClick={getVersion} style={{ padding: "6px 10px", fontSize: 12, background: "rgba(255,255,255,0.08)", color: "white", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 6, cursor: "pointer" }}>View</button>
          </div>
        </div>
      </div>
    </div>
  );
}
