import { useEffect, useState } from "react";
import { dashboards } from "@app/shared/api/dashboards";
import { datasets } from "@app/shared/api/datasets";
import { Button } from "@app/shared/components/ui/Button";
import { Card } from "@app/shared/components/ui/Card";
import { Badge } from "@app/shared/components/ui/Badge";
import { Input, Textarea } from "@app/shared/components/ui/Input";
import { Chart } from "@app/shared/components/Chart";
import PageHead from "../components/PageHead";

export default function Dashboard() {
  const [datasetId, setDatasetId] = useState(1);
  const [datasetsList, setDatasetsList] = useState<any[]>([]);
  const [dashboardsList, setDashboardsList] = useState<any[]>([]);
  const [specText, setSpecText] = useState("");
  const [output, setOutput] = useState("");
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [realCharts, setRealCharts] = useState<any[]>([]);

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
      setRealCharts([]);
      setOutput(`Generated from dataset ${datasetId} [${(res as any).model_used ?? "rule-based"}] — save dashboard rồi chọn để xem real-data`);
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
      const charts = (data as any)?.charts ?? [];
      setRealCharts(charts);
      setOutput(`Loaded #${id} — ${charts.length} charts real-data (DuckDB 1 query/chart)`);
    } catch (e: any) {
      setOutput(`Load error: ${e.message}`);
    }
  };

  const toOptions = (c: any) => {
    if (c.type === "kpi" && typeof c.value === "number") return { series: [c.value] } as any;
    const opt: any = {};
    if (c.series) opt.series = c.series;
    if (c.categories) opt.xaxis = { categories: c.categories };
    return opt;
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <PageHead
        path="dashboard"
        title="Dashboard"
        desc="AI đề xuất 4-6 charts từ profile → lưu → xem real-data (mỗi chart 1 query DuckDB)."
        actions={<><Button onClick={handleGenerate}>Generate</Button><Button variant="ghost" onClick={refresh}>Refresh</Button></>}
      />

      <Card>
        <h4>Nguồn generate</h4>
        <div style={{ display: "flex", gap: 12, alignItems: "end", flexWrap: "wrap", marginTop: 8 }}>
          <label style={{ display: "flex", flexDirection: "column", fontSize: 12, color: "var(--text-muted)" }}>Dataset ID / mart
            <Input type="number" value={datasetId} onChange={(e) => setDatasetId(Number(e.target.value))} style={{ marginTop: 4, width: 120 }} />
          </label>
          <Button onClick={handleCreate}>Save Dashboard</Button>
        </div>
        {datasetsList.length > 0 && <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 8 }}>Datasets: {datasetsList.map((d: any) => `${d.dataset_name}#${d.id ?? "?"}`).join(", ")}</div>}
      </Card>

      <div style={{ display: "grid", gridTemplateColumns: "minmax(280px, 4fr) minmax(320px, 6fr)", gap: 20 }}>
        <Card>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
            <h4>Saved</h4>
            <Badge variant="neutral">{dashboardsList.length}</Badge>
          </div>
          {dashboardsList.length === 0 ? <div style={{ opacity: 0.5, fontSize: 13, color: "var(--text-muted)" }}>Chưa có dashboard</div> : dashboardsList.map((d: any) => (
            <div key={d.id} onClick={() => handleLoad(d.id)} style={{ padding: "8px", cursor: "pointer", background: selectedId === d.id ? "rgba(45,212,191,0.15)" : "transparent", borderRadius: "var(--radius-input)", borderBottom: "1px solid var(--border)" }}>
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

      <div className="rise" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px,1fr))", gap: 20 }}>
        {realCharts.length > 0 ? realCharts.map((c: any, i: number) => (
          <Card key={c.id ?? i} style={{ padding: 0, overflow: "hidden" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 14px", borderBottom: "1px solid var(--border)" }}>
              <span style={{ fontSize: 12, fontWeight: 600 }}>{c.title ?? c.type}</span>
              <Badge variant="success">{c.type}</Badge>
            </div>
            <div style={{ padding: 12 }}>
              <Chart type={c.type} height={150} options={toOptions(c)} />
            </div>
          </Card>
        )) : ((["kpi", "bar", "hist", "box", "line", "scatter"] as const).map((t) => (
          <Card key={t} style={{ padding: 0, overflow: "hidden", opacity: 0.75 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 14px", borderBottom: "1px solid var(--border)" }}>
              <span style={{ fontSize: 12, color: "var(--text-muted)" }}>{t} · mock</span>
              <Badge variant="neutral">preview</Badge>
            </div>
            <div style={{ padding: 12 }}>
              <Chart type={t} height={150} />
            </div>
          </Card>
        )))}
      </div>

      <Card style={{ background: "#000" }}>
        <h4 style={{ marginBottom: 8 }}>Output</h4>
        <pre style={{ fontFamily: "var(--font-mono)", fontSize: 11, overflow: "auto", maxHeight: 200, margin: 0 }}>{output || "Generate → Save → click dashboard để xem real-data."}</pre>
      </Card>
    </div>
  );
}
