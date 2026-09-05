import { useEffect, useState } from "react";
import { dashboards } from "@app/shared/src/api/dashboards";
import { datasets } from "@app/shared/src/api/datasets";
import { Button } from "@app/shared/src/components/ui/Button";
import { Card } from "@app/shared/src/components/ui/Card";
import { Input, Textarea } from "@app/shared/src/components/ui/Input";
import { echartsDarkTheme } from "@app/shared/src/utils/chartTheme";

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
      setOutput(`Generated from dataset ${datasetId} (fallback 4 charts, theme accent sync)`);
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

      <Card style={{ display: "flex", gap: 8, alignItems: "end", flexWrap: "wrap" }}>
        <label style={{ display: "flex", flexDirection: "column", fontSize: 12, color: "var(--text-muted)" }}>Dataset ID / mart
          <Input type="number" value={datasetId} onChange={(e) => setDatasetId(Number(e.target.value))} style={{ marginTop: 4, width: 120 }} />
        </label>
        <Button onClick={handleGenerate}>Generate (4-6 charts)</Button>
        <Button onClick={handleCreate} variant="ghost" style={{ background: "var(--accent)", color: "white" }}>Save Dashboard</Button>
        <Button variant="ghost" onClick={refresh}>Refresh</Button>
      </Card>

      {datasetsList.length > 0 && <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Datasets: {datasetsList.map((d: any) => `${d.dataset_name}#${d.id ?? "?"}`).join(", ")}</div>}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1.2fr", gap: 16 }}>
        <Card>
          <h4>Dashboards ({dashboardsList.length})</h4>
          {dashboardsList.length === 0 ? <div style={{ opacity: 0.5, fontSize: 13, color: "var(--text-muted)" }}>Chưa có dashboard</div> : dashboardsList.map((d: any) => (
            <div key={d.id} onClick={() => handleLoad(d.id)} style={{ padding: "8px", cursor: "pointer", background: selectedId === d.id ? "rgba(139,92,246,0.15)" : "transparent", borderRadius: "var(--radius-input)", borderBottom: "1px solid var(--border)" }}>
              <div style={{ fontWeight: 600, fontSize: 13 }}>{d.name} <span style={{ opacity: 0.5, fontSize: 11 }}>#{d.id}</span></div>
              <div style={{ fontSize: 11, color: "var(--text-muted)" }}>{d.created_at ?? ""}</div>
            </div>
          ))}
        </Card>
        <Card>
          <label style={{ fontWeight: 600, fontSize: 13 }}>DashboardSpec JSON (6 types: kpi/bar/hist/box/line/scatter)</label>
          <Textarea value={specText} onChange={(e) => setSpecText(e.target.value)} rows={14} className="mono" placeholder='{"name":"demo","source":"mart.demo","charts":[{"type":"bar","x":"col"}]}' style={{ marginTop: 8 }} />
        </Card>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px,1fr))", gap: 12 }}>
        {(["kpi", "bar", "hist", "box", "line", "scatter"] as const).map((t) => (
          <Card key={t} style={{ background: "rgba(255,255,255,0.02)" }}>
            <div style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase" }}>{t} <span style={{ color: echartsDarkTheme.color[0], fontSize: 10 }}>● accent</span></div>
            <div style={{ marginTop: 8, height: 60, display: "flex", alignItems: "center", justifyContent: "center", background: "rgba(0,0,0,0.2)", borderRadius: "var(--radius-input)", fontSize: 11, color: "var(--text-muted)", border: "1px solid var(--border)" }}>ECharts {t} — dark theme</div>
          </Card>
        ))}
      </div>

      <Card style={{ background: "rgba(0,0,0,0.2)" }}>
        <pre style={{ fontFamily: "var(--font-mono)", fontSize: 11, overflow: "auto", maxHeight: 200, margin: 0 }}>{output || "Output: generate/load/create"}</pre>
      </Card>
    </div>
  );
}
