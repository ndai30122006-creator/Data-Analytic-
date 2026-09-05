import { useEffect, useState } from "react";
import { pipelines } from "@app/shared/src/api/pipelines";
import type { PipelineSpec } from "@app/shared/src/types/index";
import { Button } from "@app/shared/src/components/ui/Button";
import { Card } from "@app/shared/src/components/ui/Card";
import { Textarea } from "@app/shared/src/components/ui/Input";
import { Badge } from "@app/shared/src/components/ui/Badge";
import { useErrorHandler } from "@app/shared/src/hooks/useErrorHandler";

const defaultSpec: PipelineSpec = {
  name: "demo-pipeline",
  source: "raw.demo",
  target: "mart.demo",
  steps: [{ id: "s1", op: "drop_duplicates", params: {} }],
};

export default function Pipeline() {
  const [specText, setSpecText] = useState(JSON.stringify(defaultSpec, null, 2));
  const [pipelinesList, setPipelinesList] = useState<any[]>([]);
  const [runs, setRuns] = useState<any[]>([]);
  const [output, setOutput] = useState("");
  const [loading, setLoading] = useState(false);
  const [nl, setNl] = useState("xóa dòng trùng, điền missing cột diem bằng median");
  const { error: apiError, handleError, clearError } = useErrorHandler();

  const refresh = async () => {
    try {
      clearError();
      const [p, r] = await Promise.all([pipelines.list(), pipelines.listRuns()]);
      setPipelinesList(p.pipelines ?? []);
      setRuns(r.runs ?? []);
    } catch (e: any) {
      const info = handleError(e);
      setOutput(`List error [${info.code}]: ${info.message} ${info.traceId ? `(trace ${info.traceId})` : ""}`);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const parseSpec = (): PipelineSpec | null => {
    try {
      return JSON.parse(specText);
    } catch (e: any) {
      setOutput(`JSON parse error: ${e.message}`);
      return null;
    }
  };

  const handlePreview = async () => {
    const spec = parseSpec();
    if (!spec) return;
    setLoading(true);
    try {
      const res = await pipelines.preview(spec);
      setOutput(`Preview (dry-run 100 rows):\n${JSON.stringify(res, null, 2)}`);
    } catch (e: any) {
      setOutput(`Preview error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    const spec = parseSpec();
    if (!spec) return;
    setLoading(true);
    try {
      const res = await pipelines.create(spec);
      setOutput(`Created pipeline: ${JSON.stringify(res, null, 2)}`);
      refresh();
    } catch (e: any) {
      setOutput(`Create error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleRun = async (pipelineId: string) => {
    setLoading(true);
    try {
      const { run_id } = await pipelines.run(pipelineId);
      setOutput(`Run started: ${run_id} — polling...`);
      let attempts = 0;
      const poll = async () => {
        attempts++;
        const info: any = await pipelines.getRun(run_id);
        setOutput(`Run ${run_id} [${info.status}] (poll ${attempts}):\n${JSON.stringify(info, null, 2)}`);
        if (info.status === "queued" || info.status === "running") {
          const delay = Math.min(2000 * Math.pow(1.5, attempts - 1), 8000);
          setTimeout(poll, delay);
        } else {
          refresh();
        }
      };
      setTimeout(poll, 1500);
    } catch (e: any) {
      setOutput(`Run error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <h2>Pipeline — ETL/ELT (AI author → DAG)</h2>
      {apiError && (
        <Card style={{ background: "rgba(239,68,68,0.08)", borderColor: "rgba(239,68,68,0.3)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ fontSize: 12, color: "var(--danger)" }}>
            [{apiError.code}] {apiError.message} {apiError.traceId && <span style={{ opacity: 0.6 }}>trace:{apiError.traceId}</span>}
          </span>
          <Button variant="ghost" size="sm" onClick={clearError}>Dismiss</Button>
        </Card>
      )}

      <Card style={{ background: "rgba(139,92,246,0.08)", borderColor: "rgba(139,92,246,0.2)" }}>
        <label style={{ fontSize: 12, color: "var(--text-muted)" }}>Mô tả tiếng Việt (NL → spec, hiện manual edit):</label>
        <Textarea value={nl} onChange={(e) => setNl(e.target.value)} rows={2} style={{ marginTop: 6 }} placeholder="VD: điền missing diem bằng median, xóa trùng ma_sv" />
        <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>Gợi ý BYOK: sau này gọi LLM etl_author để sinh spec từ NL + profile.</div>
      </Card>

      <Card>
        <label style={{ fontWeight: 600, fontSize: 13 }}>PipelineSpec JSON</label>
        <Textarea value={specText} onChange={(e) => setSpecText(e.target.value)} rows={12} className="mono" style={{ marginTop: 8, fontSize: 12 }} />
        <div style={{ display: "flex", gap: 8, marginTop: 10 }}>
          <Button onClick={handlePreview} disabled={loading}>Dry-run Preview</Button>
          <Button onClick={handleCreate} disabled={loading}>Create Pipeline</Button>
          <Button variant="ghost" onClick={refresh} disabled={loading}>Refresh Lists</Button>
        </div>
      </Card>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <Card>
          <h4>Pipelines ({pipelinesList.length})</h4>
          {pipelinesList.length === 0 ? (
            <div style={{ opacity: 0.5, fontSize: 13, color: "var(--text-muted)" }}>Chưa có pipeline</div>
          ) : (
            pipelinesList.map((p) => (
              <div key={p.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
                <div>
                  <div style={{ fontWeight: 600, fontSize: 13 }}>{p.name} <span style={{ opacity: 0.5 }}>({p.id})</span></div>
                  <div style={{ fontSize: 11, color: "var(--text-muted)" }}>{p.source} → {p.target}</div>
                </div>
                <Button size="sm" onClick={() => handleRun(p.id)} style={{ background: "var(--success)" }}>Run</Button>
              </div>
            ))
          )}
        </Card>
        <Card>
          <h4>Runs ({runs.length})</h4>
          {runs.length === 0 ? (
            <div style={{ opacity: 0.5, fontSize: 13, color: "var(--text-muted)" }}>Chưa có run</div>
          ) : (
            runs.map((r: any) => (
              <div key={r.run_id} style={{ padding: "6px 0", borderBottom: "1px solid var(--border)", fontSize: 12, display: "flex", gap: 6, alignItems: "center" }}>
                <span style={{ fontWeight: 600 }}>{r.run_id}</span>
                <Badge variant={r.status === "done" ? "success" : r.status === "failed" ? "danger" : "warn"}>{r.status}</Badge>
                <span style={{ opacity: 0.5 }}>— {r.pipeline_id}</span>
              </div>
            ))
          )}
        </Card>
      </div>

      <Card style={{ background: "rgba(0,0,0,0.2)" }}>
        <pre style={{ fontFamily: "var(--font-mono)", fontSize: 12, overflow: "auto", maxHeight: 300, margin: 0, whiteSpace: "pre-wrap" }}>{output || "Output sẽ hiện ở đây (preview/run)"}</pre>
      </Card>

      <div style={{ fontSize: 11, color: "var(--text-muted)" }}>7 ops: fill_missing, drop_duplicates, type_cast, standardize_columns, derive_column, filter, aggregate + sql {'{{prev}}'} — executor warehouse_write_lock 30s.</div>
    </div>
  );
}
