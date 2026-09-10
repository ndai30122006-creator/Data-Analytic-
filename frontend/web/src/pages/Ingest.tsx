import { useEffect, useState } from "react";
import { datasets } from "@app/shared/api/datasets";
import { Button } from "@app/shared/components/ui/Button";
import { Card } from "@app/shared/components/ui/Card";
import { Badge } from "@app/shared/components/ui/Badge";
import { EmptyState, Skeleton, Toast } from "@app/shared/components/ui/Skeleton";
import { DataTable } from "@app/shared/src/components/DataTable";
import { parseApiError } from "@app/shared/src/hooks/useErrorHandler";
import { PageHead } from "@app/shared/src/components/PageHead";

export default function Ingest() {
  const [file, setFile] = useState<File | null>(null);
  const [msg, setMsg] = useState("");
  const [list, setList] = useState<any[]>([]);
  const [profile, setProfile] = useState("");
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(null);

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

  const [uploading, setUploading] = useState(false);

  const upload = async () => {
    if (!file) return;
    setUploading(true);
    setMsg("Uploading...");
    try {
      const res = await datasets.ingestFile(file);
      setMsg(`Ingested: ${res.message} — dataset_id=${res.dataset_id}`);
      if (res.profile) setProfile(JSON.stringify(res.profile, null, 2));
      setFile(null);
      refresh();
    } catch (e: any) {
      const info = parseApiError(e);
      setMsg(info.message);
    } finally {
      setUploading(false);
    }
  };

  const viewProfile = async (id: number, name: string) => {
    try {
      setSelected(name);
      setSelectedId(id);
      const res = await datasets.getProfile(id);
      setProfile(JSON.stringify(res, null, 2));
    } catch (e: any) {
      setProfile(`Error: ${e.message}`);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <PageHead
        path="ingest"
        title="Ingest"
        desc="Upload CSV/Excel → raw.* trong DuckDB + profile JSON. LLM không bao giờ nhận raw rows."
        actions={<Button variant="ghost" onClick={refresh}>Refresh</Button>}
      />

      <Card style={{ borderStyle: "dashed" }}>
        <h4>01 · Chọn file → 02 · Upload</h4>
        <div style={{ display: "flex", gap: 12, alignItems: "center", marginTop: 12, flexWrap: "wrap" }}>
          <label style={{ flex: 1, minWidth: 220, padding: "14px 16px", border: "1px dashed var(--border-strong)", borderRadius: "var(--radius-input)", cursor: "pointer", fontSize: 12, color: file ? "var(--text)" : "var(--text-muted)" }}>
            {file ? `▣ ${file.name} (${(file.size / 1024).toFixed(1)} KB)` : "▢ Click để chọn .csv / .xlsx (tối đa 50MB)"}
            <input type="file" accept=".csv,.xlsx,.xls" onChange={(e) => setFile(e.target.files?.[0] ?? null)} style={{ display: "none" }} />
          </label>
          <Button onClick={upload} disabled={!file || uploading}>{uploading ? "Đang upload..." : "Upload & Ingest"}</Button>
        </div>
        {msg && <div style={{ marginTop: 12 }}><Toast message={msg} type={msg.startsWith("Error") || msg.startsWith("List error") ? "error" : msg.startsWith("Ingested") ? "success" : "info"} onClose={() => setMsg("")} /></div>}
      </Card>

      <div className="rise" style={{ display: "grid", gridTemplateColumns: "minmax(300px, 5fr) minmax(320px, 7fr)", gap: 20 }}>
        <Card>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
            <h4>Datasets</h4>
            <Badge variant="neutral">{list.length}</Badge>
          </div>
          {loading ? <><Skeleton height={34} style={{ marginBottom: 8 }} /><Skeleton height={34} style={{ marginBottom: 8 }} /><Skeleton height={34} /></>
            : list.length === 0 ? <EmptyState title="Chưa có dataset" hint="Upload file ở trên để bắt đầu" />
            : list.map((d: any) => (
              <div key={d.dataset_name}
                onClick={() => d.id && viewProfile(d.id, d.dataset_name)}
                style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8, padding: "10px 8px", borderBottom: "1px solid var(--border)", fontSize: 12, cursor: "pointer", background: selected === d.dataset_name ? "rgba(45,212,191,0.07)" : "transparent", borderRadius: "var(--radius-input)" }}>
                <div>
                  <div style={{ fontWeight: 600 }}>{d.dataset_name}</div>
                  <div style={{ color: "var(--text-muted)", fontSize: 11 }}>{d.rows} rows × {d.cols} cols{d.version ? ` · v${d.version}` : ""}</div>
                </div>
                <Badge variant="neutral">profile</Badge>
              </div>
            ))}
        </Card>
        <Card style={{ background: "#000" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
            <h4>Profile JSON</h4>
            {selected && <Badge variant="success">{selected}</Badge>}
          </div>
          <pre style={{ fontFamily: "var(--font-mono)", fontSize: 11, overflow: "auto", maxHeight: 420, margin: 0, whiteSpace: "pre-wrap" }}>{profile || "Click 1 dataset bên trái để xem profile (KHÔNG raw)."}</pre>
        </Card>
      </div>

      <Card>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
          <h4>Data rows — kiểm chứng dữ liệu thật</h4>
          {selected && <Badge variant="neutral">{selected}</Badge>}
        </div>
        {selectedId ? <DataTable key={selectedId} datasetId={selectedId} /> : <EmptyState title="Chưa chọn dataset" hint="Click 1 dataset ở trên để xem rows (sort/search/phân trang)" />}
      </Card>
    </div>
  );
}
