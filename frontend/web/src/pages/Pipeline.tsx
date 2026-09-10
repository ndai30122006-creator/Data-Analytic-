import { useEffect, useRef, useState } from "react";
import { pipelines } from "@app/shared/api/pipelines";
import type { PipelineSpec } from "@app/shared/types/index";
import { Button } from "@app/shared/components/ui/Button";
import { Card } from "@app/shared/components/ui/Card";
import { Textarea } from "@app/shared/components/ui/Input";
import { Badge } from "@app/shared/components/ui/Badge";
import { useErrorHandler } from "@app/shared/hooks/useErrorHandler";
import { PageHead } from "@app/shared/src/components/PageHead";
import { DagEditor } from "@app/shared/src/components/DagEditor";
import { ProposalPanel } from "@app/shared/src/components/ProposalPanel";

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
  const [selectedStepId, setSelectedStepId] = useState<string | null>(null);
  const [lastRun, setLastRun] = useState<any | null>(null);
  const [consoleOpen, setConsoleOpen] = useState(true);

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

  const tryParse = (): PipelineSpec | null => {
    try {
      return JSON.parse(specText);
    } catch {
      return null;
    }
  };

  const parseSpec = (): PipelineSpec | null => {
    const s = tryParse();
    if (!s) setOutput("JSON parse error: spec khong phai JSON hop le.");
    return s;
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

  const [runningId, setRunningId] = useState<string | null>(null);
  const timers = useRef<ReturnType<typeof setTimeout>[]>([]);
  useEffect(() => () => { timers.current.forEach(clearTimeout); }, []);

  const later = (fn: () => void, ms: number) => {
    const t = setTimeout(fn, ms);
    timers.current.push(t);
  };

  const handleRun = async (pipelineId: string) => {
    setLoading(true);
    setRunningId(null);
    try {
      const { run_id } = await pipelines.run(pipelineId);
      setRunningId(run_id);
      setOutput(`Run started: ${run_id} — polling...`);
      let attempts = 0;
      const poll = async () => {
        attempts++;
        try {
          const info: any = await pipelines.getRun(run_id);
          setOutput(`Run ${run_id} [${info.status}] (poll ${attempts}):\n${JSON.stringify(info, null, 2)}`);
          if (info.status === "queued" || info.status === "running") {
            if (attempts >= 20) {
              setOutput(`Run ${run_id} van chua xong sau 20 lan poll — vao Runs de xem lai.`);
              setLoading(false);
              return;
            }
            const delay = Math.min(2000 * Math.pow(1.5, attempts - 1), 8000);
            later(poll, delay);
          } else {
            setLoading(false);
            setLastRun(info);
            refresh();
          }
        } catch (e: any) {
          setOutput(`Poll error: ${e.message}`);
          setLoading(false);
        }
      };
      later(poll, 1500);
    } catch (e: any) {
      setOutput(`Run error: ${e.message}`);
      setLoading(false);
    }
    // Khong setLoading(false) o finally — poll nen giu loading den khi xong/timeout
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <PageHead
        path="pipeline"
        title="Pipeline"
        desc="AI sinh spec từ tiếng Việt → dry-run 100 rows → run ra mart.*. Mỗi run ghi steps log."
        actions={<>
          <Button variant="ghost" onClick={handleGenerate} disabled={loading || !nl.trim()}>AI</Button>
          <Button variant="ghost" onClick={handlePreview} disabled={loading}>Dry-run</Button>
          <Button onClick={handleCreate} disabled={loading}>Create</Button>
          <Button variant="ghost" onClick={refresh} disabled={loading}>Refresh</Button>
        </>}
      />
      {apiError && (
        <Card style={{ background: "rgba(255,51,102,0.07)", borderColor: "rgba(255,51,102,0.35)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ fontSize: 12, color: "var(--danger)" }}>
            [{apiError.code}] {apiError.message} {apiError.traceId && <span style={{ opacity: 0.6 }}>trace:{apiError.traceId}</span>}
          </span>
          <Button variant="ghost" size="sm" onClick={clearError}>Dismiss</Button>
        </Card>
      )}

      {proposal && <ProposalPanel proposal={proposal} onApprove={handleApprove} onReject={handleReject} />}

      <div style={{ display: "grid", gridTemplateColumns: selectedStepId ? "minmax(240px, 3fr) minmax(320px, 6fr) minmax(260px, 3fr)" : "minmax(280px, 4fr) minmax(320px, 8fr)", gap: 20 }}>
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
              <select value={tryParse()?.engine ?? "pandas"} onChange={(e) => {
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
              <DagEditor steps={getSteps()} onChange={setSteps} selectedId={selectedStepId} onSelect={setSelectedStepId} />
            </div>
          ) : (
            <Textarea value={specText} onChange={(e) => setSpecText(e.target.value)} rows={8} className="mono" style={{ marginTop: 8, fontSize: 12 }} />
          )}
          <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 8 }}>Bấm node để xem Inspector → · Dry-run/Create ở toolbar trên.</div>
        </Card>
        {selectedStepId && (
          <Card style={{ borderColor: "var(--accent)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h4>Inspector · {selectedStepId}</h4>
              <Button variant="ghost" size="sm" onClick={() => setSelectedStepId(null)}>✕</Button>
            </div>
            {(() => {
              const s = getSteps().find((x) => x.id === selectedStepId);
              if (!s) return <div style={{ fontSize: 12, color: "var(--text-muted)" }}>Node không còn trong spec.</div>;
              const runStep = (lastRun?.steps ?? []).find((x: any) => x.step_id === s.id);
              const timing = lastRun?.result?.step_timings?.[s.id];
              return (
                <div style={{ fontSize: 12, display: "flex", flexDirection: "column", gap: 8, marginTop: 8 }}>
                  <div><span style={{ color: "var(--text-muted)" }}>operation </span><Badge variant="neutral">{s.op}</Badge></div>
                  <div><span style={{ color: "var(--text-muted)" }}>status </span>{runStep ? <Badge variant={runStep.status === "done" ? "success" : runStep.status === "failed" ? "danger" : "warn"}>{runStep.status}</Badge> : <span style={{ opacity: 0.6 }}>— (chưa chạy)</span>}</div>
                  <div><span style={{ color: "var(--text-muted)" }}>input </span><span style={{ fontFamily: "var(--font-mono)" }}>{(s.depends_on ?? []).length ? (s.depends_on ?? []).join(", ") : "source"}</span></div>
                  <div><span style={{ color: "var(--text-muted)" }}>duration </span>{timing !== undefined ? `${timing} ms` : "—"}</div>
                  <div><span style={{ color: "var(--text-muted)" }}>params</span><pre style={{ fontFamily: "var(--font-mono)", fontSize: 11, background: "#000", border: "1px solid var(--border)", borderRadius: "var(--radius-input)", padding: 8, overflow: "auto", margin: "4px 0 0" }}>{JSON.stringify(s.params ?? {}, null, 2)}</pre></div>
                  {runStep?.log && <div><span style={{ color: "var(--text-muted)" }}>log</span><pre style={{ fontSize: 11, whiteSpace: "pre-wrap", color: "var(--danger)" }}>{runStep.log}</pre></div>}
                </div>
              );
            })()}
          </Card>
        )}
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
            <h4>Runs {runningId && <span style={{ color: "var(--accent)" }}>· polling {runningId}…</span>}</h4>
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
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
          <h4>Run Console {lastRun && <span style={{ color: "var(--text-muted)" }}>· {lastRun.run_id} [{lastRun.status}]</span>}</h4>
          <Button variant="ghost" size="sm" onClick={() => setConsoleOpen((o) => !o)}>{consoleOpen ? "▾" : "▸"}</Button>
        </div>
        {consoleOpen && (
          lastRun ? (
            <div style={{ fontFamily: "var(--font-mono)", fontSize: 12 }}>
              {(lastRun.steps ?? []).length === 0 && <div style={{ opacity: 0.6 }}>run {lastRun.status} — chi tiết ở Runs.</div>}
              {(lastRun.steps ?? []).map((s: any, i: number) => (
                <div key={i} style={{ display: "flex", gap: 8, padding: "3px 0" }}>
                  <span style={{ color: s.status === "done" ? "var(--success)" : s.status === "failed" ? "var(--danger)" : "var(--warn)" }}>
                    {s.status === "done" ? "✓" : s.status === "failed" ? "✗" : "○"}
                  </span>
                  <span>{s.step_id}</span>
                  <span style={{ marginLeft: "auto", color: "var(--text-muted)" }}>{lastRun.result?.step_timings?.[s.step_id] !== undefined ? `${lastRun.result.step_timings[s.step_id]} ms` : ""}</span>
                </div>
              ))}
              {lastRun.result?.error && <div style={{ color: "var(--danger)", marginTop: 6, whiteSpace: "pre-wrap" }}>{lastRun.result.error}</div>}
            </div>
          ) : (
            <pre style={{ fontFamily: "var(--font-mono)", fontSize: 12, overflow: "auto", maxHeight: 200, margin: 0, whiteSpace: "pre-wrap" }}>{output || "Chạy pipeline để xem console."}</pre>
          )
        )}
      </Card>

      <div style={{ fontSize: 11, color: "var(--text-muted)" }}>8 ops: fill_missing, drop_duplicates, type_cast, standardize_columns, derive_column, filter, aggregate, merge + sql {'{{prev}}'} — engines pandas/duckdb.</div>
    </div>
  );
}
