import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { datasets } from "@app/shared/api/datasets";
import { pipelines } from "@app/shared/api/pipelines";
import { dashboards } from "@app/shared/api/dashboards";
import { brief } from "@app/shared/api/brief";
import { Button } from "@app/shared/components/ui/Button";
import { Card } from "@app/shared/components/ui/Card";
import { Badge } from "@app/shared/components/ui/Badge";
import { Skeleton } from "@app/shared/components/ui/Skeleton";

const FLOW = [
  { n: "01", label: "Ingest", desc: "upload csv/excel → raw.* + profile", to: "/ingest" },
  { n: "02", label: "Pipeline", desc: "AI spec → dry-run → mart.*", to: "/pipeline" },
  { n: "03", label: "Brief", desc: "narrative tiếng Việt, version", to: "/brief" },
  { n: "04", label: "Dashboard", desc: "4-6 charts real-data", to: "/dashboard" },
];

export default function Overview() {
  const nav = useNavigate();
  const [stats, setStats] = useState({ ds: 0, pipe: 0, runs: 0, dash: 0, brief: 0 });
  const [recentRuns, setRecentRuns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [visited, setVisited] = useState<string[]>(() => {
    try { return JSON.parse(localStorage.getItem("roadmap_visited") ?? "[]"); } catch { return []; }
  });

  useEffect(() => {
    (async () => {
      try {
        const [d, p, r, b] = await Promise.all([
          datasets.list().catch(() => ({ datasets: [] }) as any),
          pipelines.list().catch(() => ({ pipelines: [] }) as any),
          pipelines.listRuns().catch(() => ({ runs: [] }) as any),
          dashboards.list().catch(() => ({ dashboards: [] }) as any),
        ]);
        const dsList = d.datasets ?? [];
        let briefCount = 0;
        try {
          const first = dsList.find((x: any) => x.id);
          if (first) {
            const bl = await brief.list(first.id).catch(() => ({ briefs: [] }) as any);
            briefCount = (bl.briefs ?? []).length;
          }
        } catch { /* ignore */ }
        setStats({
          ds: dsList.length,
          pipe: (p.pipelines ?? []).length,
          runs: (r.runs ?? []).length,
          dash: (b.dashboards ?? []).length,
          brief: briefCount,
        });
        setRecentRuns((r.runs ?? []).slice(0, 5));
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // Roadmap: done = co data that HOAC da ghe tham; current = buoc dau tien chua xong
  const steps = useMemo(() => {
    const evidence = [stats.ds > 0, stats.pipe > 0, stats.brief > 0, stats.dash > 0];
    return FLOW.map((f, i) => ({
      ...f,
      done: evidence[i] || visited.includes(f.to),
      current: false,
    })).map((s, i, arr) => ({ ...s, current: !s.done && (i === 0 || arr[i - 1].done) }));
  }, [stats, visited]);

  const go = (to: string) => {
    setVisited((v) => {
      const next = v.includes(to) ? v : [...v, to];
      try { localStorage.setItem("roadmap_visited", JSON.stringify(next)); } catch { /* ignore */ }
      return next;
    });
    nav(to);
  };

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

      {/* roadmap */}
      <Card>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h4>Roadmap — bấm ô để chạy tới bước đó</h4>
          <Badge variant="neutral">{steps.filter((s) => s.done).length}/{steps.length} done</Badge>
        </div>
        <div style={{ position: "relative", display: "flex", alignItems: "stretch", gap: 0, marginTop: 16 }}>
          <div style={{ position: "absolute", top: 23, left: 40, right: 40, height: 2, background: "var(--border)" }} />
          <div style={{ position: "absolute", top: 23, left: 40, right: 40, height: 2, background: "linear-gradient(90deg, var(--accent), var(--accent-2))", opacity: 0.6, transformOrigin: "left", transform: `scaleX(${(steps.filter((s) => s.done).length) / steps.length})`, transition: "transform 0.6s var(--ease)" }} />
          <div className="traveler" />
          {steps.map((f) => (
            <div key={f.label} onClick={() => go(f.to)}
              style={{ position: "relative", flex: 1, minWidth: 0, cursor: "pointer", textAlign: "center", padding: "0 8px", opacity: !f.done && !f.current ? 0.65 : 1 }}>
              <div style={{
                width: 48, height: 48, margin: "0 auto", borderRadius: "50%",
                border: `2px solid ${f.done ? "var(--accent)" : f.current ? "var(--accent-2)" : "var(--border-strong)"}`,
                background: f.done ? "rgba(45,212,191,0.15)" : "var(--bg)",
                boxShadow: f.done ? "0 0 16px rgba(45,212,191,0.35)" : f.current ? "0 0 16px rgba(34,211,238,0.5)" : "none",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontWeight: 800, fontSize: 14, color: f.done ? "var(--accent)" : f.current ? "var(--accent-2)" : "var(--text-muted)",
                fontFamily: "var(--font-mono)",
                animation: f.current ? "soft-pulse 1.6s ease-in-out infinite" : "none",
              }}>{f.done ? "✓" : f.n}</div>
              <div style={{ fontWeight: 700, fontSize: 13, marginTop: 8 }}>{f.label}</div>
              <div style={{ fontSize: 11, color: f.current ? "var(--accent-2)" : "var(--text-muted)", marginTop: 2 }}>
                {f.done ? "done" : f.current ? "▶ next" : f.desc}
              </div>
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
