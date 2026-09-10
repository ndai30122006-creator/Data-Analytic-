import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { datasets } from "@app/shared/api/datasets";
import { lineage } from "@app/shared/api/lineage";
import { Button } from "@app/shared/components/ui/Button";
import { Card } from "@app/shared/components/ui/Card";
import { Badge } from "@app/shared/components/ui/Badge";
import { Input } from "@app/shared/components/ui/Input";
import { EmptyState, Skeleton, Toast } from "@app/shared/components/ui/Skeleton";
import { DataTable } from "@app/shared/src/components/DataTable";
import { PageHead } from "@app/shared/src/components/PageHead";
import { Tabs } from "@app/shared/src/components/ui/Tabs";
import { parseApiError } from "@app/shared/src/hooks/useErrorHandler";

const DETAIL_TABS = [
  { id: "overview", label: "Overview" },
  { id: "data", label: "Data" },
  { id: "schema", label: "Schema" },
  { id: "profile", label: "Profile" },
  { id: "quality", label: "Quality" },
  { id: "lineage", label: "Lineage" },
];

export default function Ingest() {
  const nav = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [msg, setMsg] = useState("");
  const [list, setList] = useState<any[]>([]);
  const [profile, setProfile] = useState("");
  const [quality, setQuality] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState<"name" | "rows">("name");
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [tab, setTab] = useState("overview");
  const [schemaCols, setSchemaCols] = useState<{ name: string; sample: string }[]>([]);
  const [lineageInfo, setLineageInfo] = useState<any | null>(null);

  const refresh = async () => {
    setLoading(true);
    try {
      const res = await datasets.list();
      setList(res.datasets ?? []);
    } catch (e: any) {
      const info = parseApiError(e);
      setMsg(info.message);
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => { refresh(); }, []);

  const filtered = useMemo(() => {
    const s = search.trim().toLowerCase();
    const rows = (list ?? []).filter((d: any) => !s || String(d.dataset_name ?? "").toLowerCase().includes(s));
    return [...rows].sort((a: any, b: any) =>
      sort === "name" ? String(a.dataset_name).localeCompare(String(b.dataset_name)) : (b.rows ?? 0) - (a.rows ?? 0)
    );
  }, [list, search, sort]);

  const selected = (list ?? []).find((d: any) => d.id === selectedId) ?? null;

  const select = async (id: number) => {
    setSelectedId(id);
    setTab("overview");
    setLineageInfo(null);
    try {
      const res = await datasets.getProfile(id);
      setProfile(typeof res.profile === "string" ? res.profile : JSON.stringify(res.profile, null, 2));
    } catch (e: any) {
      setProfile(parseApiError(e).message);
    }
    try {
      const r = await datasets.rows(id, { limit: 1 });
      setSchemaCols((r.columns ?? []).map((c: string) => ({
        name: c,
        sample: r.rows?.[0] ? String(r.rows[0][r.columns.indexOf(c)] ?? "") : "",
      })));
    } catch { setSchemaCols([]); }
  };

  const loadLineage = async () => {
    if (!selectedId) return;
    try {
      setLineageInfo(await lineage.get(selectedId));
    } catch (e: any) {
      setLineageInfo({ error: parseApiError(e).message });
    }
  };

  const upload = async () => {
    if (!file) return;
    setUploading(true);
    setMsg("Uploading...");
    try {
      const res = await datasets.ingestFile(file);
      setMsg(`Ingested: ${res.message} — dataset_id=${res.dataset_id}`);
      if (res.profile) setProfile(typeof res.profile === "string" ? res.profile : JSON.stringify(res.profile, null, 2));
      setQuality(res.quality ?? null);
      setFile(null);
      setShowUpload(false);
      await refresh();
      if (res.dataset_id) select(res.dataset_id);
    } catch (e: any) {
      setMsg(parseApiError(e).message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <PageHead
        path="ingest"
        title="Data"
        desc="Workspace dữ liệu — upload, duyệt, kiểm tra rows/schema/profile/quality/lineage."
        actions={<><Button onClick={() => setShowUpload((s) => !s)}>+ Ingest Dataset</Button><Button variant="ghost" onClick={refresh}>Refresh</Button></>}
      />
      {showUpload && (
        <Card style={{ borderStyle: "dashed" }}>
          <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
            <label style={{ flex: 1, minWidth: 220, padding: "14px 16px", border: "1px dashed var(--border-strong)", borderRadius: "var(--radius-input)", cursor: "pointer", fontSize: 12, color: file ? "var(--text)" : "var(--text-muted)" }}>
              {file ? `▣ ${file.name} (${(file.size / 1024).toFixed(1)} KB)` : "▢ Click để chọn .csv / .xlsx (tối đa 50MB)"}
              <input type="file" accept=".csv,.xlsx,.xls" onChange={(e) => setFile(e.target.files?.[0] ?? null)} style={{ display: "none" }} />
            </label>
            <Button onClick={upload} disabled={!file || uploading}>{uploading ? "Đang upload..." : "Upload & Ingest"}</Button>
          </div>
        </Card>
      )}
      {msg && <Toast message={msg} type={msg.startsWith("Ingested") ? "success" : "info"} onClose={() => setMsg("")} />}

      <Card>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
          <Input placeholder="Search datasets..." value={search} onChange={(e) => setSearch(e.target.value)} style={{ width: 220 }} />
          <select value={sort} onChange={(e) => setSort(e.target.value as any)}
            style={{ padding: 9, background: "var(--bg)", color: "var(--text)", border: "1px solid var(--border)", borderRadius: "var(--radius-input)", fontSize: 12 }}>
            <option value="name">Sort: name</option>
            <option value="rows">Sort: rows</option>
          </select>
          <span style={{ marginLeft: "auto", fontSize: 11, color: "var(--text-muted)" }}>{filtered.length} datasets</span>
        </div>
      </Card>

      <div style={{ display: "grid", gridTemplateColumns: "minmax(260px, 4fr) minmax(340px, 8fr)", gap: 20 }}>
        <Card>
          <h4 style={{ marginBottom: 8 }}>Datasets</h4>
          {loading ? <><Skeleton height={34} style={{ marginBottom: 8 }} /><Skeleton height={34} /></>
            : filtered.length === 0 ? <EmptyState title="Không có dataset" hint={search ? "Search không khớp" : "Bấm + Ingest Dataset"} />
            : filtered.map((d: any) => (
              <div key={d.id ?? d.dataset_name} onClick={() => d.id && select(d.id)}
                style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8, padding: "10px 8px", borderBottom: "1px solid var(--border)", fontSize: 12, cursor: "pointer", background: selectedId === d.id ? "rgba(45,212,191,0.07)" : "transparent", borderRadius: "var(--radius-input)" }}>
                <div>
                  <div style={{ fontWeight: 600 }}>{d.dataset_name}</div>
                  <div style={{ color: "var(--text-muted)", fontSize: 11 }}>{d.rows} rows × {d.cols} cols{d.version ? ` · v${d.version}` : ""}</div>
                </div>
                <Badge variant="neutral">detail</Badge>
              </div>
            ))}
        </Card>

        <Card>
          {!selected ? <EmptyState title="Chưa chọn dataset" hint="Click 1 dataset bên trái" /> : (
            <>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 8 }}>
                <div style={{ fontWeight: 700, fontSize: 14 }}>{selected.dataset_name}</div>
                <Badge variant="success">v{selected.version ?? 1}</Badge>
              </div>
              <div style={{ marginTop: 12 }}>
                <Tabs tabs={DETAIL_TABS} value={tab} onChange={(id) => { setTab(id); if (id === "lineage") loadLineage(); }} />
              </div>
              <div style={{ marginTop: 12 }}>
                {tab === "overview" && (
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(120px,1fr))", gap: 12, fontSize: 12 }}>
                    {[["rows", selected.rows], ["cols", selected.cols], ["version", selected.version ?? 1]].map(([k, v]) => (
                      <div key={k} style={{ border: "1px solid var(--border)", borderRadius: "var(--radius-input)", padding: 12 }}>
                        <div style={{ fontSize: 20, fontWeight: 800, fontFamily: "var(--font-mono)" }}>{v ?? "?"}</div>
                        <div style={{ color: "var(--text-muted)", fontSize: 11 }}>{k}</div>
                      </div>
                    ))}
                  </div>
                )}
                {tab === "data" && <DataTable key={selectedId} datasetId={selectedId!} />}
                {tab === "schema" && (
                  schemaCols.length === 0 ? <div style={{ fontSize: 12, color: "var(--text-muted)" }}>Không đọc được schema.</div> : (
                    <table style={{ borderCollapse: "collapse", width: "100%", fontSize: 12 }}>
                      <thead><tr style={{ textAlign: "left", color: "var(--text-muted)" }}><th style={{ padding: "6px 8px" }}>column</th><th style={{ padding: "6px 8px" }}>sample</th></tr></thead>
                      <tbody>
                        {schemaCols.map((c) => (
                          <tr key={c.name} style={{ borderTop: "1px solid var(--border)" }}>
                            <td style={{ padding: "6px 8px", fontFamily: "var(--font-mono)", fontWeight: 600 }}>{c.name}</td>
                            <td style={{ padding: "6px 8px", color: "var(--text-muted)" }}>{c.sample || <span style={{ opacity: 0.4 }}>null</span>}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )
                )}
                {tab === "profile" && (
                  <pre style={{ fontFamily: "var(--font-mono)", fontSize: 11, overflow: "auto", maxHeight: 380, margin: 0, whiteSpace: "pre-wrap" }}>{profile || "..."}</pre>
                )}
                {tab === "quality" && (
                  quality
                    ? <pre style={{ fontFamily: "var(--font-mono)", fontSize: 11, overflow: "auto", margin: 0 }}>{JSON.stringify(quality, null, 2)}</pre>
                    : <EmptyState title="Chưa có quality snapshot" hint="Quality chỉ có ngay sau khi upload — upload lại để xem" />
                )}
                {tab === "lineage" && (
                  !lineageInfo ? <div style={{ fontSize: 12, color: "var(--text-muted)" }}>Đang tải...</div>
                  : lineageInfo.error ? <div style={{ fontSize: 12, color: "var(--danger)" }}>{lineageInfo.error}</div>
                  : <div style={{ fontSize: 12, display: "flex", flexDirection: "column", gap: 6 }}>
                      <div>pipelines: <b>{lineageInfo.pipelines_count ?? 0}</b> · dashboards: <b>{lineageInfo.dashboards ?? 0}</b> · briefs: <b>{lineageInfo.briefs ?? 0}</b></div>
                      {(lineageInfo.nodes ?? []).length > 0 && (
                        <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                          {(lineageInfo.nodes ?? []).slice(0, 12).map((n: any) => (
                            <Badge key={n.id} variant="neutral">{n.kind}: {n.label}</Badge>
                          ))}
                        </div>
                      )}
                      <Button variant="ghost" size="sm" onClick={() => nav("/lineage")}>Mở Lineage</Button>
                    </div>
                )}
              </div>
            </>
          )}
        </Card>
      </div>
    </div>
  );
}
