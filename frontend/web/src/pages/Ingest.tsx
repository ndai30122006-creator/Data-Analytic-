import { useEffect, useState } from "react";
import { datasets } from "@app/shared/src/api/datasets";
import { Button } from "@app/shared/src/components/ui/Button";
import { Card } from "@app/shared/src/components/ui/Card";
import { EmptyState, Skeleton, Toast } from "@app/shared/src/components/ui/Skeleton";

export default function Ingest() {
  const [file, setFile] = useState<File | null>(null);
  const [msg, setMsg] = useState("");
  const [list, setList] = useState<any[]>([]);
  const [profile, setProfile] = useState("");
  const [loading, setLoading] = useState(false);

  const refresh = async () => {
    setLoading(true);
    try {
      const res = await datasets.list();
      setList(res.datasets ?? []);
    } catch (e: any) {
      setMsg(`List error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => { refresh(); }, []);

  const upload = async () => {
    if (!file) return;
    setMsg("Uploading...");
    try {
      const res = await datasets.ingestFile(file);
      setMsg(`Ingested: ${res.message} — dataset_id=${res.dataset_id}`);
      if (res.profile) setProfile(JSON.stringify(res.profile, null, 2));
      refresh();
    } catch (e: any) {
      setMsg(`Error: ${e.message}`);
    }
  };

  const viewProfile = async (id: number) => {
    try {
      const res = await datasets.getProfile(id);
      setProfile(JSON.stringify(res, null, 2));
    } catch (e: any) {
      setProfile(`Error: ${e.message}`);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <h2>Ingest — Datasets (raw → DuckDB)</h2>
      <Card style={{ borderStyle: "dashed" }}>
        <input type="file" accept=".csv,.xlsx,.xls" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        <Button onClick={upload} disabled={!file} style={{ marginLeft: 12, background: file ? "var(--accent)" : "rgba(255,255,255,0.1)" }}>Upload & Ingest</Button>
        {msg && <div style={{ marginTop: 8 }}><Toast message={msg} type={msg.startsWith("Error") || msg.startsWith("List error") ? "error" : msg.startsWith("Ingested") ? "success" : "info"} onClose={() => setMsg("")} /></div>}
      </Card>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1.2fr", gap: 16 }}>
        <Card>
          <h4>Datasets ({list.length}) — preview 20 rows profile</h4>
          {loading ? <><Skeleton height={18} style={{ marginBottom: 8 }} /><Skeleton height={18} style={{ marginBottom: 8 }} /><Skeleton height={18} /></> : list.length === 0 ? <EmptyState title="Chưa có dataset" hint="Upload CSV/Excel ở trên để bắt đầu" /> : list.map((d: any) => (
            <div key={d.dataset_name} style={{ display: "flex", justifyContent: "space-between", padding: "6px 0", borderBottom: "1px solid var(--border)", fontSize: 12 }}>
              <span>{d.dataset_name} <span style={{ opacity: 0.5 }}>{d.rows}×{d.cols}</span></span>
              <Button variant="ghost" size="sm" onClick={() => d.id && viewProfile(d.id)}>Profile</Button>
            </div>
          ))}
        </Card>
        <Card style={{ background: "rgba(0,0,0,0.2)" }}>
          <pre style={{ fontFamily: "var(--font-mono)", fontSize: 11, overflow: "auto", maxHeight: 300, margin: 0 }}>{profile || "Profile JSON (KHÔNG raw) sẽ hiện ở đây"}</pre>
        </Card>
      </div>
    </div>
  );
}
