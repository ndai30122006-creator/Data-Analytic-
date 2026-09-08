import { useState } from "react";
import { brief } from "@app/shared/api/brief";
import { Button } from "@app/shared/components/ui/Button";
import { Card } from "@app/shared/components/ui/Card";
import { Badge } from "@app/shared/components/ui/Badge";
import { Input } from "@app/shared/components/ui/Input";
import PageHead from "../components/PageHead";

export default function Brief() {
  const [datasetId, setDatasetId] = useState(1);
  const [content, setContent] = useState("");
  const [modelUsed, setModelUsed] = useState("");
  const [history, setHistory] = useState<any[]>([]);
  const [version, setVersion] = useState<number | "">("");

  const create = async () => {
    try {
      const res = await brief.create(datasetId);
      setContent(res.content ?? JSON.stringify(res, null, 2));
      setModelUsed(res.model_used ?? "");
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
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <PageHead
        path="brief"
        title="Brief"
        desc="1-click narrative tiếng Việt từ profile. Có BYOK key thì dùng LLM, không thì rule-based."
        actions={<><Button onClick={create}>Generate Brief</Button><Button variant="ghost" onClick={exportMd} disabled={!content}>Export MD</Button></>}
      />

      <div style={{ display: "grid", gridTemplateColumns: "minmax(320px, 1fr) 300px", gap: 20 }}>
        <Card style={{ background: "#000" }}>
          <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 12, flexWrap: "wrap" }}>
            <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "var(--text-muted)" }}>Dataset ID
              <Input type="number" value={datasetId} onChange={(e) => setDatasetId(Number(e.target.value))} style={{ width: 90 }} />
            </label>
            <Button variant="ghost" size="sm" onClick={list}>History</Button>
            {modelUsed && <Badge variant={modelUsed.startsWith("rule-based") ? "neutral" : "success"}>{modelUsed}</Badge>}
          </div>
          <pre style={{ fontFamily: "var(--font-mono)", fontSize: 12, overflow: "auto", maxHeight: 420, whiteSpace: "pre-wrap", margin: 0 }}>{content || "Brief tiếng Việt sẽ hiện ở đây (fallback rule-based nếu không BYOK)"}</pre>
        </Card>
        <Card>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
            <h4>Versions</h4>
            <Badge variant="neutral">{history.length}</Badge>
          </div>
          {history.length === 0 ? <div style={{ opacity: 0.5, fontSize: 12, color: "var(--text-muted)" }}>Chưa có brief</div> : history.map((b: any, i: number) => (
            <div key={i} style={{ padding: "6px 0", borderBottom: "1px solid var(--border)", fontSize: 12 }}>
              <span style={{ fontWeight: 600 }}>v{b.version ?? i+1}</span> <span style={{ color: "var(--text-muted)" }}>{b.model_used ?? ""}</span>
            </div>
          ))}
          <div style={{ marginTop: 12, display: "flex", gap: 6 }}>
            <Input type="number" placeholder="version" value={version} onChange={(e) => setVersion(e.target.value === "" ? "" : Number(e.target.value))} style={{ width: 80 }} />
            <Button variant="ghost" size="sm" onClick={getVersion}>View</Button>
          </div>
        </Card>
      </div>
    </div>
  );
}
