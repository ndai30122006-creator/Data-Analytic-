import { useEffect, useState } from "react";
import { pipelines } from "@app/shared/api/pipelines";
import { Button } from "@app/shared/components/ui/Button";
import { Card } from "@app/shared/components/ui/Card";
import { Badge } from "@app/shared/components/ui/Badge";
import { EmptyState, Skeleton } from "@app/shared/components/ui/Skeleton";
import { PageHeader } from "@app/shared/src/components/layout/PageHeader";
import { StatusDot } from "@app/shared/src/components/ui/StatusDot";
import { Inspector } from "@app/shared/src/components/layout/Inspector";

export default function Runs() {
  const [runs, setRuns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [detail, setDetail] = useState<any | null>(null);
  const [inspectorOpen, setInspectorOpen] = useState(false);

  const refresh = async () => {
    setLoading(true);
    try {
      const r = await pipelines.listRuns();
      setRuns(r.runs ?? []);
    } catch {
      setRuns([]);
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => { refresh(); }, []);

  const open = async (runId: string) => {
    try {
      const info = await pipelines.getRun(runId);
      setDetail(info);
      setInspectorOpen(true);
    } catch { /* ignore */ }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <PageHeader
        path="runs"
        title="Runs"
        desc="Lịch sử thực thi pipelines — bấm dòng để xem steps, timings, engine."
        actions={<Button variant="ghost" onClick={refresh}>Refresh</Button>}
      />
      <Card>
        {loading ? <Skeleton height={120} /> : runs.length === 0
          ? <EmptyState title="Chưa có run" hint="Vào Pipeline tạo và chạy pipeline đầu tiên" />
          : (
            <table style={{ borderCollapse: "collapse", width: "100%", fontSize: 12 }}>
              <thead>
                <tr style={{ textAlign: "left", color: "var(--text-muted)", fontSize: 11 }}>
                  <th style={{ padding: "8px" }}>run</th>
                  <th style={{ padding: "8px" }}>pipeline</th>
                  <th style={{ padding: "8px" }}>status</th>
                  <th style={{ padding: "8px" }}>created</th>
                </tr>
              </thead>
              <tbody>
                {runs.map((r: any) => (
                  <tr key={r.run_id} onClick={() => open(r.run_id)} style={{ borderTop: "1px solid var(--border)", cursor: "pointer" }}>
                    <td style={{ padding: "8px", fontFamily: "var(--font-mono)", fontWeight: 700 }}>{r.run_id}</td>
                    <td style={{ padding: "8px", color: "var(--text-muted)" }}>{r.pipeline_id}</td>
                    <td style={{ padding: "8px" }}>
                      <StatusDot status={r.status} />
                    </td>
                    <td style={{ padding: "8px", color: "var(--text-muted)", fontSize: 11 }}>{r.created_at ?? ""}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
      </Card>
      <Inspector open={inspectorOpen} title={`Run ${detail?.run_id ?? ""}`} subtitle={detail ? `${detail.pipeline_id} · ${detail.status}` : ""} onClose={() => setInspectorOpen(false)}>
        {!detail ? <div style={{ fontSize: 12, color: "var(--text-muted)" }}>...</div> : (
          <div style={{ display: "flex", flexDirection: "column", gap: 12, fontSize: 12 }}>
            <div>
              <div style={{ color: "var(--text-muted)", fontSize: 11 }}>ENGINE / DURATION / ROWS</div>
              <div style={{ marginTop: 4 }}>{detail.engine ?? "?"} · {detail.duration_s ?? "?"}s · {detail.rows_out ?? "?"} rows</div>
            </div>
            <div>
              <div style={{ color: "var(--text-muted)", fontSize: 11 }}>STEPS</div>
              {(detail.steps ?? []).length === 0 && <div style={{ marginTop: 4, opacity: 0.6 }}>no step logs</div>}
              {(detail.steps ?? []).map((s: any, i: number) => (
                <div key={i} style={{ display: "flex", gap: 8, padding: "6px 0", borderBottom: "1px solid var(--border)" }}>
                  <Badge variant={s.status === "done" ? "success" : s.status === "failed" ? "danger" : "warn"}>{s.status}</Badge>
                  <span style={{ fontFamily: "var(--font-mono)" }}>{s.step_id}</span>
                </div>
              ))}
            </div>
            {detail.result?.error && (
              <div>
                <div style={{ color: "var(--text-muted)", fontSize: 11 }}>ERROR</div>
                <pre style={{ whiteSpace: "pre-wrap", fontSize: 11, color: "var(--danger)" }}>{detail.result.error}</pre>
              </div>
            )}
          </div>
        )}
      </Inspector>
    </div>
  );
}
