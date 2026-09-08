import { useEffect, useState } from "react";
import { datasets } from "@app/shared/api/datasets";
import { lineage, type LineageResponse } from "@app/shared/api/lineage";
import { Button } from "@app/shared/components/ui/Button";
import { Card } from "@app/shared/components/ui/Card";
import { Badge } from "@app/shared/components/ui/Badge";
import { EmptyState, Skeleton } from "@app/shared/components/ui/Skeleton";
import PageHead from "../components/PageHead";

const KIND_STYLE: Record<string, { bg: string; border: string }> = {
  dataset: { bg: "rgba(0,255,136,0.15)", border: "rgba(0,255,136,0.5)" },
  pipeline: { bg: "rgba(6,182,212,0.12)", border: "rgba(6,182,212,0.5)" },
  mart: { bg: "rgba(16,185,129,0.12)", border: "rgba(16,185,129,0.5)" },
  dashboard: { bg: "rgba(245,158,11,0.12)", border: "rgba(245,158,11,0.5)" },
  brief: { bg: "rgba(244,114,182,0.12)", border: "rgba(244,114,182,0.5)" },
};

export default function Lineage() {
  const [list, setList] = useState<any[]>([]);
  const [detail, setDetail] = useState<LineageResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    datasets.list().then((r) => setList(r.datasets ?? [])).catch(() => {});
  }, []);

  const view = async (id: number) => {
    setLoading(true);
    setError("");
    try {
      const res = await lineage.get(id);
      setDetail(res);
    } catch (e: any) {
      setError(e.message ?? "Load lineage failed");
      setDetail(null);
    } finally {
      setLoading(false);
    }
  };

  const byKind = (kind: string) => (detail?.nodes ?? []).filter((n) => n.kind === kind);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <PageHead
        path="lineage"
        title="Lineage"
        desc="Đồ thị dataset → brief/pipeline → mart → dashboard. Hover node để xem quan hệ."
      />
      <div style={{ display: "grid", gridTemplateColumns: "minmax(280px, 4fr) minmax(320px, 7fr)", gap: 20 }}>
        <Card>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
            <h4>Datasets</h4>
            <Badge variant="neutral">{list.length}</Badge>
          </div>
          {list.length === 0 ? <EmptyState title="Chưa có dataset" hint="Upload ở Ingest trước" /> : list.map((d: any) => (
            <div key={d.dataset_name} style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)", fontSize: 12 }}>
              <span>{d.dataset_name} <span style={{ color: "var(--text-muted)" }}>{d.rows}×{d.cols}</span></span>
              <Button variant="ghost" size="sm" onClick={() => d.id && view(d.id)}>View</Button>
            </div>
          ))}
        </Card>
        <Card>
          <h4>Graph trực quan {detail && <span style={{ color: "var(--text-muted)" }}>— {detail.dataset}</span>}</h4>
          {loading ? <><Skeleton height={40} style={{ marginBottom: 8 }} /><Skeleton height={40} /></>
            : error ? <div style={{ color: "#EF4444", fontSize: 12 }}>{error}</div>
            : !detail ? <EmptyState title="Chọn dataset để xem lineage" hint="Nodes: dataset → pipeline → mart → dashboard + brief" />
            : (
              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                {(["dataset", "pipeline", "mart", "dashboard", "brief"] as const).map((k) => byKind(k).length > 0 && (
                  <div key={k}>
                    <div style={{ fontSize: 10, textTransform: "uppercase", color: "var(--text-muted)", marginBottom: 4 }}>{k} ({byKind(k).length})</div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                      {byKind(k).map((n) => (
                        <div key={n.id} title={(detail.edges ?? []).filter((e) => e.from === n.id || e.to === n.id).map((e) => `${e.from} —${e.label ?? ""}→ ${e.to}`).join("\n")}
                          style={{ background: KIND_STYLE[k]?.bg, border: `1px solid ${KIND_STYLE[k]?.border}`, borderRadius: "var(--radius-input)", padding: "6px 10px", fontSize: 12 }}>
                          <div style={{ fontWeight: 600 }}>{n.label}</div>
                          {n.meta && <div style={{ fontSize: 10, color: "var(--text-muted)" }}>{n.meta}</div>}
                        </div>
                      ))}
                    </div>
                    {k !== "brief" && <div style={{ textAlign: "center", color: "var(--text-muted)", fontSize: 14 }}>↓</div>}
                  </div>
                ))}
                <div style={{ fontSize: 11, color: "var(--text-muted)" }}>
                  {detail.edges.length} edges · pipelines: {detail.pipelines_count} · dashboards: {detail.dashboards} · briefs: {detail.briefs} (hover node để xem quan hệ)
                </div>
              </div>
            )}
        </Card>
      </div>
      <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Nguồn: warehouse/lineage.py get_lineage — GET /lineage/{"{id}"} trả nodes/edges.</div>
    </div>
  );
}
