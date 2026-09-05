import { useEffect, useState } from "react";
import { dashboards } from "@app/shared/src/api/dashboards";
import { datasets } from "@app/shared/src/api/datasets";

export default function Dashboard() {
  const [datasetId, setDatasetId] = useState(1);
  const [datasetsList, setDatasetsList] = useState<any[]>([]);
  const [dashboardsList, setDashboardsList] = useState<any[]>([]);
  const [specText, setSpecText] = useState("");
  const [output, setOutput] = useState("");
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const refresh = async () => {
    try {
      const [ds, dbs] = await Promise.all([datasets.list().catch(() => ({ datasets: [] }) as any), dashboards.list()]);
      setDatasetsList(ds.datasets ?? []);
      setDashboardsList(dbs.dashboards ?? []);
    } catch (e: any) {
      setOutput(`Refresh error: ${e.message}`);
    }
  };

  useEffect(() => { refresh(); }, []);

  const handleGenerate = async () => {
    try {
      const res = await dashboards.generate(datasetId);
      setSpecText(JSON.stringify(res.spec ?? res, null, 2));
      setOutput(`Generated from dataset ${datasetId} (fallback 4 charts if no LLM)`);
    } catch (e: any) {
      setOutput(`Generate error: ${e.message}`);
    }
  };

  const handleCreate = async () => {
    try {
      const spec = JSON.parse(specText || "{}");
      const name = spec.name || `dash-${Date.now()}`;
      const res = await dashboards.create({ ...spec, name });
      setOutput(`Created dashboard: ${JSON.stringify(res, null, 2)}`);
      refresh();
    } catch (e: any) {
      setOutput(`Create error: ${e.message}`);
    }
  };

  const handleLoad = async (id: number) => {
    try {
      setSelectedId(id);
      const res = await dashboards.get(id);
      setSpecText(JSON.stringify(res.spec ?? res, null, 2));
      const data = await dashboards.data(id).catch(() => null);
      setOutput(`Loaded #${id} — data: ${JSON.stringify(data, null, 2).slice(0, 400)}`);
    } catch (e: any) {
      setOutput(`Load error: ${e.message}`);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <h2>Dashboard — AI Generate & ECharts</h2>

      <div style={{ display: "flex", gap: 8, alignItems: "end", flexWrap: "wrap" }}>
        <label style={{ display: "flex", flexDirection: "column", fontSize: 12 }}>Dataset ID / mart
          <input type="number" value={datasetId} onChange={(e) => setDatasetId(Number(e.target.value))} style={{ padding: 6, marginTop: 4, width: 120, background: "rgba(0,0,0,0.3)", color: "white", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 6 }} />
        </label>
        <button onClick={handleGenerate} style={{ padding: "8px 14px", background: "#8B5CF6", color: "white", border: 0, borderRadius: 6, cursor: "pointer" }}>Generate (4-6 charts)</button>
        <button onClick={handleCreate} style={{ padding: "8px 14px", background: "#3B82F6", color: "white", border: 0, borderRadius: 6, cursor: "pointer" }}>Save Dashboard</button>
        <button onClick={refresh} style={{ padding: "8px 14px", background: "rgba(255,255,255,0.08)", color: "white", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 6 }}>Refresh</button>
      </div>

      {datasetsList.length > 0 && <div style={{ fontSize: 11, opacity: 0.5 }}>Datasets: {datasetsList.map((d: any) => `${d.dataset_name}#${d.id ?? "?"}`).join(", ")}</div>}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1.2fr", gap: 16 }}>
        <div style={{ border: "1px solid rgba(255,255,255,0.08)", borderRadius: 8, padding: 12 }}>
          <h4 style={{ margin: "0 0 8px" }}>Dashboards ({dashboardsList.length})</h4>
          {dashboardsList.length === 0 ? <div style={{ opacity: 0.5, fontSize: 13 }}>Chưa có dashboard</div> : dashboardsList.map((d: any) => (
            <div key={d.id} onClick={() => handleLoad(d.id)} style={{ padding: "8px", cursor: "pointer", background: selectedId === d.id ? "rgba(139,92,246,0.15)" : "transparent", borderRadius: 6, borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
              <div style={{ fontWeight: 600, fontSize: 13 }}>{d.name} <span style={{ opacity: 0.5, fontSize: 11 }}>#{d.id}</span></div>
              <div style={{ fontSize: 11, opacity: 0.6 }}>{d.created_at ?? ""}</div>
            </div>
          ))}
        </div>
        <div>
          <label style={{ fontWeight: 600, fontSize: 13 }}>DashboardSpec JSON (6 types: kpi/bar/hist/box/line/scatter)</label>
          <textarea value={specText} onChange={(e) => setSpecText(e.target.value)} rows={14} style={{ width: "100%", marginTop: 8, fontFamily: "monospace", fontSize: 11, padding: 12, background: "rgba(0,0,0,0.4)", color: "#E5E7EB", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8 }} placeholder='{"name":"demo","source":"mart.demo","charts":[{"type":"bar","x":"col"}]}' />
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px,1fr))", gap: 12 }}>
        {(["kpi", "bar", "hist", "box", "line", "scatter"] as const).map((t) => (
          <div key={t} style={{ border: "1px solid rgba(255,255,255,0.08)", borderRadius: 8, padding: 12, background: "rgba(255,255,255,0.02)" }}>
            <div style={{ fontSize: 11, opacity: 0.6, textTransform: "uppercase" }}>{t}</div>
            <div style={{ marginTop: 8, height: 60, display: "flex", alignItems: "center", justifyContent: "center", background: "rgba(0,0,0,0.3)", borderRadius: 6, fontSize: 11, opacity: 0.5 }}>ECharts placeholder</div>
          </div>
        ))}
      </div>

      <pre style={{ background: "rgba(0,0,0,0.4)", padding: 12, borderRadius: 8, fontSize: 11, overflow: "auto", maxHeight: 200, border: "1px solid rgba(255,255,255,0.06)" }}>{output || "Output: generate/load/create"}</pre>
    </div>
  );
}
