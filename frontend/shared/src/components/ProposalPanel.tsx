import { Button } from "./ui/Button";
import { Card } from "./ui/Card";

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

/** Panel proposal AI: validations 4 lop + cost + dry-run + approve/reject. */
export function ProposalPanel({ proposal, onApprove, onReject }: {
  proposal: any;
  onApprove?: () => void;
  onReject?: () => void;
}) {
  if (!proposal) return null;
  return (
    <Card style={{ borderColor: "var(--accent)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 8 }}>
        <h4>Proposal {proposal.proposal_id} · {proposal.model_used} · {proposal.status}</h4>
        <div style={{ display: "flex", gap: 8 }}>
          {proposal.status === "proposed" && (
            <><Button size="sm" onClick={onApprove}>Approve → cho execute</Button>
            <Button variant="ghost" size="sm" onClick={onReject}>Reject</Button></>
          )}
        </div>
      </div>
      {(proposal.spec?.steps ?? []).length > 0 && (
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 8 }}>
          {(proposal.spec.steps ?? []).map((s: any) => (
            <span key={s.id} style={{ fontSize: 11, fontFamily: "var(--font-mono)", border: "1px solid var(--border)", borderRadius: "var(--radius-input)", padding: "3px 8px" }}>
              {s.id}:{s.op}
            </span>
          ))}
        </div>
      )}
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
  );
}
