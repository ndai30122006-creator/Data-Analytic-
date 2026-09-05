import { useEffect, useState } from "react";
import { pipelines } from "@app/shared/src/api/pipelines";
import type { PipelineSpec } from "@app/shared/src/types/index";

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

  const refresh = async () => {
    try {
      const [p, r] = await Promise.all([pipelines.list(), pipelines.listRuns()]);
      setPipelinesList(p.pipelines ?? []);
      setRuns(r.runs ?? []);
    } catch (e: any) {
      setOutput(`List error: ${e.message}`);
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

      <div style={{ background: "rgba(139,92,246,0.08)", border: "1px solid rgba(139,92,246,0.2)", padding: 12, borderRadius: 8 }}>
        <label style={{ fontSize: 12, opacity: 0.7 }}>Mô tả tiếng Việt (NL → spec, hiện manual edit):</label>
        <textarea value={nl} onChange={(e) => setNl(e.target.value)} rows={2} style={{ width: "100%", marginTop: 6, padding: 8, background: "rgba(0,0,0,0.3)", color: "white", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 6 }} placeholder="VD: điền missing diem bằng median, xóa trùng ma_sv" />
        <div style={{ fontSize: 11, opacity: 0.5, marginTop: 4 }}>Gợi ý BYOK: sau này gọi LLM etl_author để sinh spec từ NL + profile.</div>
      </div>

      <div>
        <label style={{ fontWeight: 600 }}>PipelineSpec JSON</label>
        <textarea value={specText} onChange={(e) => setSpecText(e.target.value)} rows={12} style={{ width: "100%", marginTop: 8, fontFamily: "monospace", fontSize: 12, padding: 12, background: "rgba(0,0,0,0.4)", color: "#E5E7EB", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8 }} />
        <div style={{ display: "flex", gap: 8, marginTop: 10 }}>
          <button onClick={handlePreview} disabled={loading} style={{ padding: "8px 14px", background: "#3B82F6", color: "white", border: 0, borderRadius: 6, cursor: "pointer" }}>Dry-run Preview</button>
          <button onClick={handleCreate} disabled={loading} style={{ padding: "8px 14px", background: "#8B5CF6", color: "white", border: 0, borderRadius: 6, cursor: "pointer" }}>Create Pipeline</button>
          <button onClick={refresh} disabled={loading} style={{ padding: "8px 14px", background: "rgba(255,255,255,0.08)", color: "white", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 6, cursor: "pointer" }}>Refresh Lists</button>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <div style={{ border: "1px solid rgba(255,255,255,0.08)", borderRadius: 8, padding: 12 }}>
          <h4 style={{ margin: "0 0 8px" }}>Pipelines ({pipelinesList.length})</h4>
          {pipelinesList.length === 0 ? <div style={{ opacity: 0.5, fontSize: 13 }}>Chưa có pipeline</div> : pipelinesList.map((p) => (
            <div key={p.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 0", borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
              <div><div style={{ fontWeight: 600, fontSize: 13 }}>{p.name} <span style={{ opacity: 0.5 }}>({p.id})</span></div><div style={{ fontSize: 11, opacity: 0.6 }}>{p.source} → {p.target}</div></div>
              <button onClick={() => handleRun(p.id)} style={{ padding: "6px 10px", background: "#10B981", color: "white", border: 0, borderRadius: 6, fontSize: 12, cursor: "pointer" }}>Run</button>
            </div>
          ))}
        </div>
        <div style={{ border: "1px solid rgba(255,255,255,0.08)", borderRadius: 8, padding: 12 }}>
          <h4 style={{ margin: "0 0 8px" }}>Runs ({runs.length})</h4>
          {runs.length === 0 ? <div style={{ opacity: 0.5, fontSize: 13 }}>Chưa có run</div> : runs.map((r: any) => (
            <div key={r.run_id} style={{ padding: "6px 0", borderBottom: "1px solid rgba(255,255,255,0.06)", fontSize: 12 }}>
              <span style={{ fontWeight: 600 }}>{r.run_id}</span> <span style={{ padding: "2px 6px", borderRadius: 4, background: r.status === "done" ? "#10B981" : r.status === "failed" ? "#EF4444" : "#F59E0B", fontSize: 10 }}>{r.status}</span> <span style={{ opacity: 0.5 }}>— {r.pipeline_id}</span>
            </div>
          ))}
        </div>
      </div>

      <pre style={{ background: "rgba(0,0,0,0.4)", padding: 12, borderRadius: 8, fontSize: 12, overflow: "auto", maxHeight: 300, border: "1px solid rgba(255,255,255,0.06)" }}>{output || "Output sẽ hiện ở đây (preview/run)"}</pre>

      <div style={{ fontSize: 11, opacity: 0.4 }}>7 ops: fill_missing, drop_duplicates, type_cast, standardize_columns, derive_column, filter, aggregate + sql {'{{prev}}'} — executor warehouse_write_lock 30s.</div>
    </div>
  );
}
