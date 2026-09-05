import { useEffect, useState } from "react";
import { datasets } from "@app/shared/src/api/datasets";

export default function Ingest() {
  const [file, setFile] = useState<File | null>(null);
  const [msg, setMsg] = useState("");
  const [list, setList] = useState<any[]>([]);
  const [profile, setProfile] = useState("");

  const refresh = async () => {
    try {
      const res = await datasets.list();
      setList(res.datasets ?? []);
    } catch (e: any) {
      setMsg(`List error: ${e.message}`);
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
      <div style={{ border: "1px dashed rgba(255,255,255,0.15)", borderRadius: 8, padding: 16, background: "rgba(255,255,255,0.02)" }}>
        <input type="file" accept=".csv,.xlsx,.xls" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        <button onClick={upload} disabled={!file} style={{ marginLeft: 12, padding: "8px 14px", background: file ? "#8B5CF6" : "rgba(255,255,255,0.1)", color: "white", border: 0, borderRadius: 6, cursor: file ? "pointer" : "not-allowed" }}>Upload & Ingest</button>
        <div style={{ marginTop: 8, fontSize: 12, opacity: 0.6 }}>{msg}</div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1.2fr", gap: 16 }}>
        <div style={{ border: "1px solid rgba(255,255,255,0.08)", borderRadius: 8, padding: 12 }}>
          <h4 style={{ margin: "0 0 8px" }}>Datasets ({list.length}) — preview 20 rows profile</h4>
          {list.length === 0 ? <div style={{ opacity: 0.5, fontSize: 13 }}>Chưa có dataset</div> : list.map((d: any) => (
            <div key={d.dataset_name} style={{ display: "flex", justifyContent: "space-between", padding: "6px 0", borderBottom: "1px solid rgba(255,255,255,0.06)", fontSize: 12 }}>
              <span>{d.dataset_name} <span style={{ opacity: 0.5 }}>{d.rows}×{d.cols}</span></span>
              <button onClick={() => d.id && viewProfile(d.id)} style={{ padding: "4px 8px", fontSize: 11, background: "rgba(255,255,255,0.08)", color: "white", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 4, cursor: "pointer" }}>Profile</button>
            </div>
          ))}
        </div>
        <pre style={{ background: "rgba(0,0,0,0.4)", padding: 12, borderRadius: 8, fontSize: 11, overflow: "auto", maxHeight: 300, border: "1px solid rgba(255,255,255,0.06)" }}>{profile || "Profile JSON (KHÔNG raw) sẽ hiện ở đây"}</pre>
      </div>
    </div>
  );
}
