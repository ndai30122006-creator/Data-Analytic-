import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { datasets } from "@app/shared/api/datasets";
import { pipelines } from "@app/shared/api/pipelines";
import { dashboards } from "@app/shared/api/dashboards";
import { Button } from "@app/shared/components/ui/Button";
import { Card } from "@app/shared/components/ui/Card";
import { Badge } from "@app/shared/components/ui/Badge";
import { Skeleton } from "@app/shared/components/ui/Skeleton";

const FLOW = [
  { label: "Ingest", desc: "csv → raw.*", to: "/ingest" },
  { label: "Pipeline", desc: "spec → mart.*", to: "/pipeline" },
  { label: "Brief", desc: "narrative", to: "/brief" },
  { label: "Dashboard", desc: "charts", to: "/dashboard" },
];

export default function Overview() {
  const nav = useNavigate();
  const [stats, setStats] = useState({ ds: 0, pipe: 0, runs: 0, dash: 0 });
  const [recentRuns, setRecentRuns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [d, p, r, b] = await Promise.all([
          datasets.list().catch(() => ({ datasets: [] }) as any),
          pipelines.list().catch(() => ({ pipelines: [] }) as any),
          pipelines.listRuns().catch(() => ({ runs: [] }) as any),
          dashboards.list().catch(() => ({ dashboards: [] }) as any),
        ]);
        setStats({
          ds: (d.datasets ?? []).length,
          pipe: (p.pipelines ?? []).length,
          runs: (r.runs ?? []).length,
          dash: (b.dashboards ?? []).length,
        });
        setRecentRuns((r.runs ?? []).slice(0, 5));
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const cards = [
    { label: "datasets", value: stats.ds, to: "/ingest" },
    { label: "pipelines", value: stats.pipe, to: "/pipeline" },
    { label: "runs", value: stats.runs, to: "/pipeline" },
    { label: "dashboards", value: stats.dash, to: "/dashboard" },
  ];

  return (
    <div className="rise" style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      {/* hero */}
      <Card className="hud" style={{ padding: 28, overflow: "hidden", position: "relative" }}>
        <div style={{ fontSize: 11, color: "var(--accent)" }}>$ workbench-ai --overview</div>
        <h2 style={{ fontSize: 30, marginTop: 8 }}>
          Dữ liệu thô <span className="grad-text">→ quyết định</span>
        </h2>
        <div style={{ fontSize: 13, color: "var(--text-muted)", marginTop: 8, maxWidth: 560 }}>
          Ingest file, AI sinh pipeline ETL, brief narrative tiếng Việt và dashboard charts — local-first với DuckDB + BYOK.
        </div>
        <div style={{ display: "flex", gap: 8, marginTop: 16, flexWrap: "wrap" }}>
          <Button onClick={() => nav("/ingest")}>Upload dataset</Button>
          <Button variant="ghost" onClick={() => nav("/pipeline")}>AI Generate Spec</Button>
          <Button variant="ghost" onClick={() => nav("/dashboard")}>Xem Dashboard</Button>
        </div>
      </Card>

      {/* stats */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px,1fr))", gap: 20 }}>
        {loading ? [0, 1, 2, 3].map((i) => <Skeleton key={i} height={86} />) : cards.map((c) => (
          <Card key={c.label} hover style={{ cursor: "pointer", textAlign: "center", padding: 20 }} >
            <div onClick={() => nav(c.to)}>
              <div style={{ fontSize: 34, fontWeight: 800, fontFamily: "var(--font-mono)", color: "var(--accent)", textShadow: "0 0 18px rgba(45,212,191,0.35)" }}>{c.value}</div>
              <div style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.1em", marginTop: 4 }}>{c.label}</div>
            </div>
          </Card>
        ))}
      </div>

      {/* flow */}
      <Card>
        <h4>Luồng làm việc</h4>
        <div style={{ display: "flex", alignItems: "stretch", gap: 8, marginTop: 12, flexWrap: "wrap" }}>
          {FLOW.map((f, i) => (
            <div key={f.label} style={{ display: "flex", alignItems: "center", gap: 8, flex: 1, minWidth: 140 }}>
              <div onClick={() => nav(f.to)} style={{ flex: 1, cursor: "pointer", border: "1px solid var(--border)", borderRadius: "var(--radius-input)", padding: "12px", background: "var(--bg)", transition: "border-color 0.2s" }}
                onMouseEnter={(e) => (e.currentTarget.style.borderColor = "var(--accent)")}
                onMouseLeave={(e) => (e.currentTarget.style.borderColor = "var(--border)")}>
                <div style={{ fontSize: 10, color: "var(--text-muted)" }}>STEP {i + 1}</div>
                <div style={{ fontWeight: 700, fontSize: 13 }}>{f.label}</div>
                <div style={{ fontSize: 11, color: "var(--text-muted)" }}>{f.desc}</div>
              </div>
              {i < FLOW.length - 1 && <span style={{ color: "var(--accent)", fontWeight: 700 }}>→</span>}
            </div>
          ))}
        </div>
      </Card>

      {/* recent runs */}
      <Card>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
          <h4>Runs gần đây</h4>
          <Button variant="ghost" size="sm" onClick={() => nav("/pipeline")}>Mở Pipeline</Button>
        </div>
        {loading ? <Skeleton height={30} /> : recentRuns.length === 0
          ? <div style={{ fontSize: 12, color: "var(--text-muted)" }}>Chưa có run — vào Pipeline tạo và chạy pipeline đầu tiên.</div>
          : recentRuns.map((r: any) => (
            <div key={r.run_id} style={{ display: "flex", gap: 8, alignItems: "center", padding: "8px 0", borderBottom: "1px solid var(--border)", fontSize: 12 }}>
              <span style={{ fontWeight: 700, fontFamily: "var(--font-mono)" }}>{r.run_id}</span>
              <Badge variant={r.status === "done" ? "success" : r.status === "failed" ? "danger" : "warn"}>{r.status}</Badge>
              <span style={{ color: "var(--text-muted)" }}>→ {r.pipeline_id}</span>
            </div>
          ))}
      </Card>
    </div>
  );
}
