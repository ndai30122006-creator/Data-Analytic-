import { useEffect, useState } from "react";
import { pipelines } from "@app/shared/api/pipelines";
import type { PipelineSpec } from "@app/shared/types/index";
import { Button } from "@app/shared/components/ui/Button";
import { Card } from "@app/shared/components/ui/Card";
import { Textarea } from "@app/shared/components/ui/Input";
import { Badge } from "@app/shared/components/ui/Badge";
import { useErrorHandler } from "@app/shared/hooks/useErrorHandler";
import { PageHead } from "@app/shared/src/components/PageHead";
import { DagEditor } from "@app/shared/src/components/DagEditor";

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
  const [proposal, setProposal] = useState<any | null>(null);

function LayerRow({ title, ok, errs }: { title: string; ok?: boolean; errs?: string[] }) {
  return (
    <div style={{ display: "flex", gap: 8, alignItems: "baseline", fontSize: 12, marginTop: 6 }}>
      <span style={{ minWidth: 70, color: ok ? "var(--success)" : "var(--danger)", fontWeight: 700 }}>
        {ok ? "✓" : "✗"} {title}
      </span>
      <span style={{ color: "var(--text-muted)" }}>{(errs ?? []).join(" | ") || "ok"}</span>
    </div>
  );
}
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

  const [mode, setMode] = useState<"visual" | "json">("visual");

  const getSteps = (): import("@app/shared/src/components/DagEditor").DagStep[] => {
    try {
      const s = JSON.parse(specText || "{}");
      return Array.isArray(s.steps) ? s.steps : [];
    } catch { return []; }
  };
  const setSteps = (steps: import("@app/shared/src/components/DagEditor").DagStep[]) => {
    try {
      const s = JSON.parse(specText || "{}");
      setSpecText(JSON.stringify({ engine: "pandas", name: "demo-pipeline", source: "raw.demo", target: "mart.demo", ...s, steps }, null, 2));
    } catch {
      setSpecText(JSON.stringify({ name: "demo-pipeline", source: "raw.demo", target: "mart.demo", engine: "pandas", steps }, null, 2));
    }
  };

  const handleGenerate = async () => {
    setLoading(true);
    try {
      clearError();
      const cur = parseSpec();
      const source = cur?.source ?? "raw.demo";
      const target = cur?.target ?? "mart.demo";
      const res = await pipelines.generate(source, target, nl);
      setSpecText(JSON.stringify(res.spec, null, 2));
      setProposal(res);
      const v = res.validations ?? {};
      const ok = v.schema_ok && v.semantic_ok && v.safety_ok && v.dry_run_ok;
      setOutput(`Proposal ${res.proposal_id} [${res.model_used}] — validation ${ok ? "PASS" : "FAIL"} — xem panel, Approve roi moi Create.`);
    } catch (e: any) {
      setOutput(`Generate error: ${e.message}`);
    } finally {
      setLoading(false);
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
      // Approval gate: neu spec den tu proposal chua approved -> backend 403
      const body: any = { ...spec };
      if (proposal && proposal.status === "approved" && proposal.proposal_id) body.proposal_id = proposal.proposal_id;
      const res = await pipelines.create(body);
      setOutput(`Created pipeline: ${JSON.stringify(res, null, 2)}`);
      setProposal(null);
      refresh();
    } catch (e: any) {
      setOutput(`Create error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    if (!proposal?.proposal_id) return;
    try {
      const res = await pipelines.approveProposal(proposal.proposal_id);
      setProposal({ ...proposal, status: res.status });
      setOutput(`Proposal ${proposal.proposal_id} approved — gio Create de execute.`);
    } catch (e: any) {
      setOutput(`Approve error: ${e.message}`);
    }
  };

  const handleReject = async () => {
    if (!proposal?.proposal_id) return;
    try {
      await pipelines.rejectProposal(proposal.proposal_id);
      setProposal(null);
      setOutput(`Proposal ${proposal.proposal_id} rejected.`);
    } catch (e: any) {
      setOutput(`Reject error: ${e.message}`);
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
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <PageHead
        path="pipeline"
        title="Pipeline"
        desc="AI sinh spec từ tiếng Việt → dry-run 100 rows → run ra mart.*. Mỗi run ghi steps log."
        actions={<><Button variant="ghost" onClick={refresh} disabled={loading}>Refresh</Button></>}
      />
      {apiError && (
        <Card style={{ background: "rgba(255,51,102,0.07)", borderColor: "rgba(255,51,102,0.35)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ fontSize: 12, color: "var(--danger)" }}>
            [{apiError.code}] {apiError.message} {apiError.traceId && <span style={{ opacity: 0.6 }}>trace:{apiError.traceId}</span>}
          </span>
          <Button variant="ghost" size="sm" onClick={clearError}>Dismiss</Button>
        </Card>
      )}

      {proposal && (
        <Card style={{ borderColor: "var(--accent)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 8 }}>
            <h4>Proposal {proposal.proposal_id} · {proposal.model_used} · {proposal.status}</h4>
            <div style={{ display: "flex", gap: 8 }}>
              {proposal.status === "proposed" && (
                <><Button size="sm" onClick={handleApprove}>Approve → cho execute</Button>
                <Button variant="ghost" size="sm" onClick={handleReject}>Reject</Button></>
              )}
            </div>
          </div>
          <LayerRow title="schema" ok={proposal.validations?.schema_ok} errs={proposal.validations?.schema_errors} />
          <LayerRow title="semantic" ok={proposal.validations?.semantic_ok} errs={proposal.validations?.semantic_errors} />
          <LayerRow title="safety" ok={proposal.validations?.safety_ok} errs={proposal.validations?.safety_errors} />
          <LayerRow title="dry-run" ok={proposal.validations?.dry_run_ok} errs={proposal.validations?.dry_run_error ? [proposal.validations.dry_run_error] : []} />
          <div style={{ fontSize: 12, marginTop: 8, color: "var(--text-muted)" }}>
            cost: {proposal.cost?.source_rows ?? "?"} rows · {proposal.cost?.steps} steps → engine {proposal.cost?.recommended_engine} ({proposal.cost?.reason})
            {proposal.dry_run?.rows !== undefined && <span> · dry-run {proposal.dry_run.rows} rows</span>}
          </div>
          {(proposal.notes ?? []).length > 0 && <div style={{ fontSize: 11, color: "var(--warn)", marginTop: 4 }}>{proposal.notes.join(" ")}</div>}
          <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 6 }}>LLM proposes. Engine validates. Human approves. Executor executes.</div>
        </Card>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "minmax(280px, 4fr) minmax(320px, 6fr)", gap: 20 }}>
        <Card style={{ background: "rgba(45,212,191,0.04)", borderColor: "rgba(45,212,191,0.25)" }}>
          <h4>STEP 1 · Mô tả → proposal</h4>
          <Textarea value={nl} onChange={(e) => setNl(e.target.value)} rows={4} style={{ marginTop: 8 }} placeholder="VD: điền missing diem bằng median, xóa trùng ma_sv" />
          <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 6 }}>Cần BYOK key ở Settings, không thì dùng spec mặc định.</div>
          <div style={{ marginTop: 10 }}>
            <Button onClick={handleGenerate} disabled={loading || !nl.trim()}>AI Generate Spec</Button>
          </div>
        </Card>

        <Card>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 8 }}>
            <h4>STEP 2 · Spec → dry-run → create</h4>
            <div style={{ display: "flex", gap: 4, alignItems: "center" }}>
              <select value={parseSpec()?.engine ?? "pandas"} onChange={(e) => {
                try {
                  const s = JSON.parse(specText || "{}");
                  setSpecText(JSON.stringify({ ...s, engine: e.target.value }, null, 2));
                } catch { /* ignore */ }
              }} title="Engine: pandas (small) | duckdb (large, SQL push-down)"
                style={{ padding: 6, background: "var(--bg)", color: "var(--accent)", border: "1px solid var(--border)", borderRadius: "var(--radius-input)", fontFamily: "var(--font-mono)", fontSize: 12 }}>
                <option value="pandas">pandas engine</option>
                <option value="duckdb">duckdb engine</option>
              </select>
              <Button variant={mode === "visual" ? "primary" : "ghost"} size="sm" onClick={() => setMode("visual")}>Visual</Button>
              <Button variant={mode === "json" ? "primary" : "ghost"} size="sm" onClick={() => setMode("json")}>JSON</Button>
            </div>
          </div>
          {mode === "visual" ? (
            <div style={{ marginTop: 8 }}>
              <DagEditor steps={getSteps()} onChange={setSteps} />
            </div>
          ) : (
            <Textarea value={specText} onChange={(e) => setSpecText(e.target.value)} rows={8} className="mono" style={{ marginTop: 8, fontSize: 12 }} />
          )}
          <div style={{ display: "flex", gap: 8, marginTop: 10, flexWrap: "wrap" }}>
            <Button onClick={handlePreview} disabled={loading}>Dry-run Preview</Button>
            <Button onClick={handleCreate} disabled={loading}>Create Pipeline</Button>
          </div>
        </Card>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        <Card>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
            <h4>STEP 3 · Pipelines</h4>
            <Badge variant="neutral">{pipelinesList.length}</Badge>
          </div>
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
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
            <h4>Runs</h4>
            <Badge variant="neutral">{runs.length}</Badge>
          </div>
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

      <Card style={{ background: "#000" }}>
        <h4 style={{ marginBottom: 8 }}>Output</h4>
        <pre style={{ fontFamily: "var(--font-mono)", fontSize: 12, overflow: "auto", maxHeight: 300, margin: 0, whiteSpace: "pre-wrap" }}>{output || "Output sẽ hiện ở đây (preview/run)"}</pre>
      </Card>

      <div style={{ fontSize: 11, color: "var(--text-muted)" }}>7 ops: fill_missing, drop_duplicates, type_cast, standardize_columns, derive_column, filter, aggregate + sql {'{{prev}}'} — executor warehouse_write_lock 30s.</div>
    </div>
  );
}
