import { useMemo, useState } from "react";
import { Button } from "./ui/Button";
import { Badge } from "./ui/Badge";
import { Card } from "./ui/Card";
import { Textarea } from "./ui/Input";

export interface DagStep { id: string; op: string; params?: Record<string, any>; depends_on?: string[]; }

export const OPS = ["fill_missing", "drop_duplicates", "type_cast", "standardize_columns", "derive_column", "filter", "aggregate", "merge", "sql"];

const OP_HINT: Record<string, string> = {
  fill_missing: '{"column":"diem","method":"mean"}',
  drop_duplicates: '{}',
  type_cast: '{"column":"diem","dtype":"float"}',
  standardize_columns: '{}',
  derive_column: '{"name":"pass","expr":"diem>=5"}',
  filter: '{"query":"diem>=0"}',
  aggregate: '{"group_by":"lop","agg":{"diem":"mean"}}',
  merge: '{"how":"concat"}',
  sql: '{"query":"SELECT * FROM {{prev}}"}',
};

/** Validate DAG live: op la, dep la, cycle. */
export function validateSteps(steps: DagStep[]): string[] {
  const errs: string[] = [];
  const ids = new Set(steps.map((s) => s.id));
  const seen = new Set<string>();
  for (const s of steps) {
    if (!s.id.trim()) errs.push("Step thiếu id");
    if (seen.has(s.id)) errs.push(`Trùng id: ${s.id}`);
    seen.add(s.id);
    if (!OPS.includes(s.op)) errs.push(`${s.id}: op lạ '${s.op}'`);
    for (const d of s.depends_on ?? []) {
      if (!ids.has(d)) errs.push(`${s.id}: depends_on '${d}' không tồn tại`);
      if (d === s.id) errs.push(`${s.id}: tự phụ thuộc chính mình`);
    }
  }
  // cycle (Kahn)
  const indeg = new Map(steps.map((s) => [s.id, (s.depends_on ?? []).length]));
  const adj = new Map<string, string[]>(steps.map((s) => [s.id, []]));
  for (const s of steps) for (const d of s.depends_on ?? []) adj.get(d)?.push(s.id);
  const q = [...indeg].filter(([, v]) => v === 0).map(([k]) => k);
  let visited = 0;
  while (q.length) {
    const n = q.pop()!;
    visited++;
    for (const nb of adj.get(n) ?? []) {
      indeg.set(nb, indeg.get(nb)! - 1);
      if (indeg.get(nb) === 0) q.push(nb);
    }
  }
  if (visited !== steps.length && steps.length > 0) errs.push("Cycle trong DAG");
  return errs;
}

/** Editor DAG: kéo-thả sắp xếp + sửa op/params/depends_on + validate live. */
export function DagEditor({ steps, onChange }: { steps: DagStep[]; onChange: (s: DagStep[]) => void }) {
  const [dragId, setDragId] = useState<string | null>(null);
  const [paramsText, setParamsText] = useState<Record<string, string>>({});
  const errs = useMemo(() => validateSteps(steps), [steps]);

  const upd = (id: string, patch: Partial<DagStep>) =>
    onChange(steps.map((s) => (s.id === id ? { ...s, ...patch } : s)));

  const move = (fromId: string, toId: string) => {
    if (fromId === toId) return;
    const next = [...steps];
    const fi = next.findIndex((s) => s.id === fromId);
    const ti = next.findIndex((s) => s.id === toId);
    const [m] = next.splice(fi, 1);
    next.splice(ti, 0, m);
    onChange(next);
  };

  const add = () => {
    let i = steps.length + 1;
    while (steps.some((s) => s.id === `s${i}`)) i++;
    onChange([...steps, { id: `s${i}`, op: "drop_duplicates", params: {}, depends_on: steps.length ? [steps[steps.length - 1].id] : [] }]);
  };

  return (
    <div>
      {errs.length > 0 && (
        <div style={{ marginBottom: 10, padding: "8px 12px", border: "1px solid rgba(248,113,113,0.4)", borderRadius: "var(--radius-input)", background: "rgba(248,113,113,0.07)", fontSize: 12 }}>
          {errs.map((e, i) => <div key={i} style={{ color: "var(--danger)" }}>! {e}</div>)}
        </div>
      )}
      <div style={{ position: "relative", display: "flex", flexDirection: "column", gap: 4 }}>
        {steps.map((s, i) => (
          <div key={s.id}>
            <Card
              draggable
              onDragStart={() => setDragId(s.id)}
              onDragOver={(e) => e.preventDefault()}
              onDrop={() => { if (dragId) { move(dragId, s.id); setDragId(null); } }}
              style={{ padding: 12, opacity: dragId === s.id ? 0.5 : 1, borderColor: errs.some((e) => e.startsWith(s.id + ":")) ? "rgba(248,113,113,0.5)" : undefined }}
            >
              <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                <span style={{ cursor: "grab", color: "var(--text-muted)" }} title="Kéo để sắp xếp">⠿</span>
                <Badge variant="neutral">{i + 1}</Badge>
                <input value={s.id} onChange={(e) => upd(s.id, { id: e.target.value })}
                  style={{ width: 64, padding: 6, background: "var(--bg)", color: "var(--text)", border: "1px solid var(--border)", borderRadius: "var(--radius-input)", fontFamily: "var(--font-mono)", fontSize: 12 }} />
                <select value={s.op} onChange={(e) => upd(s.id, { op: e.target.value })}
                  style={{ padding: 6, background: "var(--bg)", color: "var(--accent)", border: "1px solid var(--border)", borderRadius: "var(--radius-input)", fontFamily: "var(--font-mono)", fontSize: 12 }}>
                  {OPS.map((o) => <option key={o} value={o}>{o}</option>)}
                </select>
                <Button variant="ghost" size="sm" onClick={() => onChange(steps.filter((x) => x.id !== s.id))}>✕</Button>
              </div>
              <div style={{ display: "flex", gap: 6, alignItems: "center", marginTop: 8, flexWrap: "wrap", fontSize: 11 }}>
                <span style={{ color: "var(--text-muted)" }}>depends_on:</span>
                {steps.filter((x) => x.id !== s.id).length === 0 && <span style={{ opacity: 0.5 }}>— (step đầu)</span>}
                {steps.filter((x) => x.id !== s.id).map((x) => {
                  const on = (s.depends_on ?? []).includes(x.id);
                  return (
                    <button key={x.id} onClick={() => upd(s.id, { depends_on: on ? (s.depends_on ?? []).filter((d) => d !== x.id) : [...(s.depends_on ?? []), x.id] })}
                      style={{ padding: "3px 8px", fontSize: 11, borderRadius: "var(--radius-pill)", cursor: "pointer", background: on ? "var(--accent)" : "transparent", color: on ? "#04211B" : "var(--text-muted)", border: "1px solid var(--border)" }}>
                      {x.id}
                    </button>
                  );
                })}
              </div>
              <Textarea
                rows={2} className="mono"
                placeholder={OP_HINT[s.op] ?? "{}"}
                value={paramsText[s.id] ?? JSON.stringify(s.params ?? {})}
                onChange={(e) => {
                  setParamsText((p) => ({ ...p, [s.id]: e.target.value }));
                  try { upd(s.id, { params: JSON.parse(e.target.value || "{}") }); } catch { /* doi go dung JSON */ }
                }}
                style={{ marginTop: 8, fontSize: 11 }}
              />
            </Card>
            {i < steps.length - 1 && <div style={{ textAlign: "center", color: "var(--accent)", fontSize: 12, lineHeight: 1.4 }}>▼</div>}
          </div>
        ))}
      </div>
      {steps.length === 0 && <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 8 }}>Chưa có step — bấm thêm.</div>}
      <Button variant="ghost" size="sm" onClick={add} style={{ marginTop: 8 }}>+ Thêm step</Button>
    </div>
  );
}
