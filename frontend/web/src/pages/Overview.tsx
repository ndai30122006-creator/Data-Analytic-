import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { datasets } from "@app/shared/api/datasets";
import { pipelines } from "@app/shared/api/pipelines";
import { dashboards } from "@app/shared/api/dashboards";
import { Button } from "@app/shared/components/ui/Button";
import { Card } from "@app/shared/components/ui/Card";
import { Badge } from "@app/shared/components/ui/Badge";
import { Skeleton } from "@app/shared/components/ui/Skeleton";

function Trunk({ delay = 0 }: { delay?: number }) {
  return (
    <div style={{ position: "relative", width: 2, height: 26, background: "linear-gradient(180deg, var(--accent), var(--accent-2))", opacity: 0.7 }}>
      <span className="flow-dot" style={{ left: -3, animation: "flow-y 1.6s linear infinite", animationDelay: `${delay}s` }} />
    </div>
  );
}

function TreeNode({ label, desc, to, go }: { label: string; desc: string; to: string; go: (t: string) => void }) {
  return (
    <div onClick={() => go(to)}
      style={{ cursor: "pointer", textAlign: "center", padding: "12px 28px", background: "var(--bg)", border: "1px solid var(--border-strong)", borderRadius: "var(--radius-card)", minWidth: 170, transition: "border-color 0.2s, box-shadow 0.25s, transform 0.2s" }}
      onMouseEnter={(e) => { e.currentTarget.style.borderColor = "var(--accent)"; e.currentTarget.style.boxShadow = "0 0 18px rgba(45,212,191,0.25)"; e.currentTarget.style.transform = "translateY(-2px)"; }}
      onMouseLeave={(e) => { e.currentTarget.style.borderColor = "var(--border-strong)"; e.currentTarget.style.boxShadow = "none"; e.currentTarget.style.transform = "none"; }}>
      <div style={{ fontWeight: 700, fontSize: 14 }}>{label}</div>
      <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>{desc}</div>
    </div>
  );
}

export default function Overview() {
  const nav = useNavigate();
  const [stats, setStats] = useState({ ds: 0, pipe: 0, runs: 0, dash: 0 });
  const [recentRuns, setRecentRuns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [outputErr, setOutputErr] = useState("");

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

  const go = (to: string) => nav(to);

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
        <div style={{ fontSize: 11, color: "var(--accent)" }}>$ dataworkbench --overview</div>
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

      {/* onboarding */}
      {!loading && stats.ds === 0 && (
        <Card style={{ borderColor: "var(--accent)", display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
          <div style={{ flex: 1, minWidth: 220 }}>
            <div style={{ fontWeight: 700, fontSize: 14 }}>Mới bắt đầu? Thử demo 1-click</div>
            <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 4 }}>
              Sinh 120 sinh viên mẫu (có missing/dup) → chạy đủ luồng Ingest → Pipeline → Brief → Dashboard.
            </div>
          </div>
          <Button onClick={async () => {
            setLoading(true);
            try {
              await datasets.demo();
              const [d, p, r, b] = await Promise.all([
                datasets.list().catch(() => ({ datasets: [] }) as any),
                pipelines.list().catch(() => ({ pipelines: [] }) as any),
                pipelines.listRuns().catch(() => ({ runs: [] }) as any),
                dashboards.list().catch(() => ({ dashboards: [] }) as any),
              ]);
              setStats({ ds: (d.datasets ?? []).length, pipe: (p.pipelines ?? []).length, runs: (r.runs ?? []).length, dash: (b.dashboards ?? []).length });
            } catch (e: any) {
              setRecentRuns([]);
              setOutputErr(e.message ?? "Demo failed");
            } finally {
              setLoading(false);
            }
          }}>Tải demo 1-click</Button>
        </Card>
      )}
      {outputErr && <div style={{ fontSize: 12, color: "var(--danger)" }}>{outputErr}</div>}

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

      {/* cay luồng du lieu */}
      <Card>
        <h4>Cây luồng dữ liệu — bấm ô để đi tới</h4>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", marginTop: 16 }}>
          <TreeNode label="Ingest" desc="upload csv/excel → raw.* + profile" to="/ingest" go={go} />
          <Trunk delay={0} />
          <TreeNode label="Pipeline" desc="AI spec → dry-run → mart.*" to="/pipeline" go={go} />
          <Trunk delay={0.8} />
          <div style={{ display: "flex", width: "100%", maxWidth: 560 }}>
            <div style={{ position: "relative", flex: 1, borderTop: "2px solid var(--border-strong)", borderRight: "1px solid var(--border-strong)", height: 22, marginRight: -1 }}>
              <span className="flow-dot" style={{ top: -5, animation: "flow-x-l 1.8s linear infinite" }} />
            </div>
            <div style={{ position: "relative", flex: 1, borderTop: "2px solid var(--border-strong)", borderLeft: "1px solid var(--border-strong)", height: 22, marginLeft: -1 }}>
              <span className="flow-dot" style={{ top: -5, animation: "flow-x-r 1.8s linear infinite" }} />
            </div>
          </div>
          <div style={{ display: "flex", gap: 32, flexWrap: "wrap", justifyContent: "center" }}>
            <TreeNode label="Brief" desc="narrative tiếng Việt" to="/brief" go={go} />
            <TreeNode label="Dashboard" desc="4-6 charts real-data" to="/dashboard" go={go} />
          </div>
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
