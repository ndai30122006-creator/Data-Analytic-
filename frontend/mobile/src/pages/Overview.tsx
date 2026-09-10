import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { datasets } from "@app/shared/api/datasets";
import { pipelines } from "@app/shared/api/pipelines";
import { dashboards } from "@app/shared/api/dashboards";
import { Button } from "@app/shared/components/ui/Button";
import { Card } from "@app/shared/components/ui/Card";
import { PageHeader } from "@app/shared/src/components/layout/PageHeader";
import { StatusDot } from "@app/shared/src/components/ui/StatusDot";
import { Skeleton } from "@app/shared/components/ui/Skeleton";

function greeting() {
  const h = new Date().getHours();
  if (h < 11) return "Good morning";
  if (h < 14) return "Good midday";
  if (h < 18) return "Good afternoon";
  return "Good evening";
}

const FLOW = [
  { label: "Ingest", to: "/ingest" },
  { label: "Pipeline", to: "/pipeline" },
  { label: "Brief", to: "/brief" },
  { label: "Dashboard", to: "/dashboard" },
];

export default function Overview() {
  const nav = useNavigate();
  const [stats, setStats] = useState({ ds: 0, pipe: 0, runs: 0, failed: 0, dash: 0 });
  const [recentRuns, setRecentRuns] = useState<any[]>([]);
  const [recentDs, setRecentDs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [outputErr, setOutputErr] = useState("");

  const load = async () => {
    setLoading(true);
    try {
      const [d, p, r, b] = await Promise.all([
        datasets.list().catch(() => ({ datasets: [] }) as any),
        pipelines.list().catch(() => ({ pipelines: [] }) as any),
        pipelines.listRuns().catch(() => ({ runs: [] }) as any),
        dashboards.list().catch(() => ({ dashboards: [] }) as any),
      ]);
      const dsList = d.datasets ?? [];
      const runList = r.runs ?? [];
      setStats({
        ds: dsList.length,
        pipe: (p.pipelines ?? []).length,
        runs: runList.length,
        failed: runList.filter((x: any) => x.status === "failed").length,
        dash: (b.dashboards ?? []).length,
      });
      setRecentDs(dsList.slice(0, 6));
      setRecentRuns(runList.slice(0, 6));
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => { load(); }, []);

  const demo = async () => {
    setLoading(true);
    try {
      await datasets.demo();
      await load();
    } catch (e: any) {
      setOutputErr(e.message ?? "Demo failed");
    } finally {
      setLoading(false);
    }
  };

  const metrics = [
    { label: "datasets", value: stats.ds, to: "/ingest" },
    { label: "pipelines", value: stats.pipe, to: "/pipeline" },
    { label: "runs", value: stats.runs, to: "/runs" },
    { label: "failures", value: stats.failed, to: "/runs", alert: stats.failed > 0 },
  ];

  return (
    <div className="rise" style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <PageHeader
        path=""
        title={`${greeting()} — Control Center`}
        desc="Dữ liệu thô → quyết định. Local-first với DuckDB + BYOK."
        actions={<><Button onClick={() => nav("/ingest")}>+ New dataset</Button><Button variant="ghost" onClick={() => nav("/pipeline")}>AI Generate</Button></>}
      />

      {!loading && stats.ds === 0 && (
        <Card style={{ borderColor: "var(--accent)", display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
          <div style={{ flex: 1, minWidth: 220 }}>
            <div style={{ fontWeight: 700, fontSize: 14 }}>Mới bắt đầu? Thử demo 1-click</div>
            <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 4 }}>Sinh 120 sinh viên mẫu → chạy đủ luồng Ingest → Pipeline → Brief → Dashboard.</div>
          </div>
          <Button onClick={demo}>Tải demo 1-click</Button>
        </Card>
      )}
      {outputErr && <div style={{ fontSize: 12, color: "var(--danger)" }}>{outputErr}</div>}

      {/* key metrics */}
      <div>
        <h4 style={{ marginBottom: 8 }}>Key metrics</h4>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px,1fr))", gap: 0, border: "1px solid var(--border)", borderRadius: "var(--radius-card)", overflow: "hidden" }}>
          {loading ? [0, 1, 2, 3].map((i) => <Skeleton key={i} height={76} />) : metrics.map((c, i) => (
            <div key={c.label} onClick={() => nav(c.to)}
              style={{ cursor: "pointer", padding: "14px 18px", background: "var(--bg-card)", borderLeft: i > 0 ? "1px solid var(--border)" : "none" }}>
              <div style={{ fontSize: 28, fontWeight: 800, fontFamily: "var(--font-mono)", color: c.alert ? "var(--danger)" : "var(--accent)" }}>{c.value}</div>
              <div style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.1em", marginTop: 2 }}>{c.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* activity + runs */}
      <div style={{ display: "grid", gridTemplateColumns: "minmax(300px, 7fr) minmax(280px, 5fr)", gap: 20 }}>
        <div>
          <h4 style={{ marginBottom: 8 }}>Pipeline activity</h4>
          {loading ? <Skeleton height={120} /> : recentRuns.length === 0
            ? <div style={{ fontSize: 12, color: "var(--text-muted)", padding: "12px 0" }}>Chưa có run — vào Pipeline tạo và chạy pipeline đầu tiên.</div>
            : recentRuns.map((r: any) => (
              <div key={r.run_id} onClick={() => nav("/runs")} style={{ display: "flex", gap: 10, alignItems: "center", padding: "9px 0", borderBottom: "1px solid var(--border)", fontSize: 12, cursor: "pointer" }}>
                <StatusDot status={r.status} />
                <span style={{ fontWeight: 700, fontFamily: "var(--font-mono)" }}>{r.run_id}</span>
                <span style={{ color: "var(--text-muted)" }}>→ {r.pipeline_id}</span>
              </div>
            ))}
        </div>
        <div>
          <h4 style={{ marginBottom: 8 }}>Datasets</h4>
          {loading ? <Skeleton height={120} /> : recentDs.length === 0
            ? <div style={{ fontSize: 12, color: "var(--text-muted)", padding: "12px 0" }}>Chưa có dataset.</div>
            : recentDs.map((d: any) => (
              <div key={d.id ?? d.dataset_name} onClick={() => nav("/ingest")} style={{ display: "flex", justifyContent: "space-between", padding: "9px 0", borderBottom: "1px solid var(--border)", fontSize: 12, cursor: "pointer" }}>
                <span style={{ fontWeight: 600 }}>{d.dataset_name}</span>
                <span style={{ color: "var(--text-muted)" }}>{d.rows}×{d.cols}</span>
              </div>
            ))}
        </div>
      </div>

      {/* flow strip */}
      <div>
        <h4 style={{ marginBottom: 8 }}>Workflow</h4>
        <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
          {FLOW.map((f, i) => (
            <div key={f.label} style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <button onClick={() => nav(f.to)}
                style={{ background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: "var(--radius-pill)", color: "var(--text)", fontSize: 12, padding: "7px 16px", cursor: "pointer" }}>
                <span style={{ color: "var(--text-muted)", marginRight: 6 }}>0{i + 1}</span>{f.label}
              </button>
              {i < FLOW.length - 1 && <span style={{ color: "var(--accent)" }}>→</span>}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
