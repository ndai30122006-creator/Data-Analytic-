import { useEffect, useMemo, useState } from "react";
import { dashboards } from "@app/shared/api/dashboards";
import { datasets } from "@app/shared/api/datasets";
import { Button } from "@app/shared/components/ui/Button";
import { Card } from "@app/shared/components/ui/Card";
import { Badge } from "@app/shared/components/ui/Badge";
import { Input, Textarea } from "@app/shared/components/ui/Input";
import { Chart } from "@app/shared/components/Chart";
import { DataTable } from "@app/shared/src/components/DataTable";
import { parseApiError } from "@app/shared/src/hooks/useErrorHandler";
import { EmptyState } from "@app/shared/src/components/ui/Skeleton";
import { PageHead } from "@app/shared/src/components/PageHead";

export default function Dashboard() {
  const [datasetId, setDatasetId] = useState(1);
  const [datasetsList, setDatasetsList] = useState<any[]>([]);
  const [dashboardsList, setDashboardsList] = useState<any[]>([]);
  const [specText, setSpecText] = useState("");
  const [output, setOutput] = useState("");
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [generating, setGenerating] = useState(false);
  const [selectedName, setSelectedName] = useState("");
  const [realCharts, setRealCharts] = useState<any[]>([]);
  const [hidden, setHidden] = useState<Record<string, boolean>>({});
  const [refreshSec, setRefreshSec] = useState(0);
  const [filter, setFilter] = useState("");
  const [editMode, setEditMode] = useState(false);

  // 12-col hierarchy: kpi nho, line rong, con lai vua
  const spanFor = (t: string) => {
    if (t === "kpi") return 3;
    if (t === "line") return 8;
    if (t === "scatter") return 4;
    return 6;
  };
  const matchFilter = (c: any) => {
    const s = filter.trim().toLowerCase();
    if (!s) return true;
    return `${c.title ?? ""} ${c.type ?? ""}`.toLowerCase().includes(s);
  };

  const exportSpec = () => {
    try {
      const spec = JSON.parse(specText || "{}");
      const blob = new Blob([JSON.stringify(spec, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${selectedName || "dashboard"}.json`;
      document.body.appendChild(a);
      a.click();
      setTimeout(() => { URL.revokeObjectURL(url); a.remove(); }, 1000);
    } catch {
      setOutput("Spec JSON loi — khong export duoc.");
    }
  };

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
    setGenerating(true);
    try {
      const res = await dashboards.generate(datasetId);
      setSpecText(JSON.stringify(res.spec ?? res, null, 2));
      setRealCharts([]);
      setOutput(`Generated from dataset ${datasetId} [${(res as any).model_used ?? "rule-based"}] — save dashboard rồi chọn để xem real-data`);
    } catch (e: any) {
      const info = parseApiError(e);
      setOutput(`${info.message}${info.traceId ? ` (trace ${info.traceId})` : ""}`);
    } finally {
      setGenerating(false);
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

  const loadData = async (id: number, silent = false) => {
    const data = await dashboards.data(id).catch(() => null);
    const charts = (data as any)?.charts ?? [];
    setRealCharts(charts);
    if (!silent) setOutput(`Loaded #${id} — ${charts.length} charts real-data (DuckDB 1 query/chart)`);
  };

  const handleLoad = async (id: number) => {
    try {
      setSelectedId(id);
      setHidden({});
      const res = await dashboards.get(id);
      setSelectedName(res.name ?? "");
      setSpecText(JSON.stringify(res.spec ?? res, null, 2));
      await loadData(id);
    } catch (e: any) {
      setOutput(`Load error: ${e.message}`);
    }
  };

  // Auto-refresh theo lich
  useEffect(() => {
    if (!refreshSec || !selectedId) return;
    const t = setInterval(() => { loadData(selectedId, true); }, refreshSec * 1000);
    return () => clearInterval(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [refreshSec, selectedId]);

  const move = (i: number, dir: -1 | 1) => {
    setRealCharts((cs) => {
      const j = i + dir;
      if (j < 0 || j >= cs.length) return cs;
      const next = [...cs];
      [next[i], next[j]] = [next[j], next[i]];
      return next;
    });
  };

  const saveLayout = async () => {
    if (!selectedId) { setOutput("Chua chon dashboard de luu layout."); return; }
    try {
      const spec = JSON.parse(specText || "{}");
      const orderIds = realCharts.map((c: any) => c.id).filter(Boolean);
      const hiddenIds = new Set(
        realCharts.filter((c: any, i: number) => hidden[`${i}-${c.id ?? c.type}`]).map((c: any) => c.id)
      );
      const charts = (spec.charts ?? [])
        .filter((c: any) => !c.id || !hiddenIds.has(c.id))
        .map((c: any, i: number) => ({ c, pos: c.id ? orderIds.indexOf(c.id) : -1, fallback: i }))
        .sort((a: any, b: any) => (a.pos === -1 ? 999 + a.fallback : a.pos) - (b.pos === -1 ? 999 + b.fallback : b.pos))
        .map(({ c }: any) => c);
      const res = await dashboards.update(selectedId, { ...(spec as object), name: selectedName || (spec as any).name, charts } as any);
      setOutput(`Saved layout order+hidden -> version ${(res as any).version ?? "?"}`);
      refresh();
    } catch (e: any) {
      setOutput(`Save layout error: ${e.message}`);
    }
  };

  // Parse 1 lan/render (tranh JSON.parse lap lai)
  const specSource: string | null | undefined = useMemo(() => {
    try {
      return JSON.parse(specText || "{}").source ?? "";
    } catch {
      return null;
    }
  }, [specText]);

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
        title={selectedName || "Dashboard"}
        desc="AI đề xuất 4-6 charts từ profile → lưu → xem real-data (mỗi chart 1 query DuckDB)."
        actions={<>
          <Input placeholder="Filter charts..." value={filter} onChange={(e) => setFilter(e.target.value)} style={{ width: 150 }} />
          <Button onClick={handleGenerate} disabled={generating}>{generating ? "Đang sinh..." : "Generate"}</Button>
          <Button variant="ghost" onClick={() => selectedId && loadData(selectedId)}>Refresh</Button>
          <Button variant="ghost" onClick={exportSpec}>Export</Button>
          <Button variant={editMode ? "primary" : "ghost"} onClick={() => setEditMode((e) => !e)}>Edit</Button>
        </>}
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

      {selectedId !== null && realCharts.length > 0 && (
        <Card>
          <h4>Layout Pro</h4>
          <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap", marginTop: 8 }}>
            <Button variant="ghost" size="sm" onClick={saveLayout}>Save layout (thứ tự + ẩn/hiện)</Button>
            <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: "var(--text-muted)" }}>Auto-refresh
              <select value={refreshSec} onChange={(e) => setRefreshSec(Number(e.target.value))}
                style={{ padding: 6, background: "var(--bg)", color: "var(--text)", border: "1px solid var(--border)", borderRadius: "var(--radius-input)", fontFamily: "var(--font-mono)", fontSize: 12 }}>
                <option value={0}>off</option>
                <option value={30}>30s</option>
                <option value={60}>1m</option>
                <option value={300}>5m</option>
              </select>
            </label>
            <span style={{ fontSize: 11, color: "var(--text-muted)" }}>Export từng chart: nút ⬇ trên góc chart (PNG/SVG/CSV).</span>
          </div>
        </Card>
      )}

      <div className="rise dash-grid">
        {realCharts.length > 0 ? realCharts.filter(matchFilter).map((c: any) => {
          const i = realCharts.indexOf(c);
          const key = `${i}-${c.id ?? c.type}`;
          const isHidden = !!hidden[key];
          if (isHidden && !editMode) return null;
          return (
          <Card key={key} style={{ padding: 0, overflow: "hidden", opacity: isHidden ? 0.45 : 1, gridColumn: `span ${spanFor(c.type)}` }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 14px", borderBottom: "1px solid var(--border)" }}>
              <span style={{ fontSize: 12, fontWeight: 600 }}>{c.title ?? c.type}</span>
              <div style={{ display: "flex", gap: 4, alignItems: "center" }}>
                <Badge variant="success">{c.type}</Badge>
                {editMode && (
                  <>
                <Button variant="ghost" size="sm" aria-label="Move chart up" onClick={() => move(i, -1)} disabled={i === 0}>↑</Button>
                <Button variant="ghost" size="sm" aria-label="Move chart down" onClick={() => move(i, 1)} disabled={i === realCharts.length - 1}>↓</Button>
                <Button variant="ghost" size="sm" aria-label={isHidden ? "Show chart" : "Hide chart"} onClick={() => setHidden((h) => ({ ...h, [key]: !h[key] }))}>{isHidden ? "show" : "hide"}</Button>
                  </>
                )}
              </div>
            </div>
            <div style={{ padding: 12 }}>
              <Chart type={c.type} height={c.type === "kpi" ? 120 : 160} options={toOptions(c)} toolbar />
            </div>
          </Card>
          );
        }) : ((["kpi", "bar", "hist", "box", "line", "scatter"] as const).filter((t) => matchFilter({ title: t, type: t })).map((t) => (
          <Card key={t} style={{ padding: 0, overflow: "hidden", opacity: 0.75, gridColumn: `span ${spanFor(t)}` }}>
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

      <Card>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
          <h4>Source data — kiểm chứng mart.*</h4>
          {specSource ? <Badge variant="neutral">{specSource}</Badge> : null}
        </div>
        {specSource === null
          ? <EmptyState title="Spec lỗi" hint="Spec JSON parse không được" />
          : specSource
            ? <DataTable key={specSource} table={specSource} />
            : <EmptyState title="Chưa có source" hint="Generate hoặc load dashboard để xem rows" />}
      </Card>

      <Card style={{ background: "#000" }}>
        <h4 style={{ marginBottom: 8 }}>Output</h4>
        <pre style={{ fontFamily: "var(--font-mono)", fontSize: 11, overflow: "auto", maxHeight: 200, margin: 0 }}>{output || "Generate → Save → click dashboard để xem real-data."}</pre>
      </Card>
    </div>
  );
}
