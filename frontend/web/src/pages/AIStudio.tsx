import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { pipelines } from "@app/shared/api/pipelines";
import { datasets } from "@app/shared/api/datasets";
import { Button } from "@app/shared/components/ui/Button";
import { Card } from "@app/shared/components/ui/Card";
import { Input } from "@app/shared/components/ui/Input";
import { Textarea } from "@app/shared/components/ui/Input";
import { PageHead } from "@app/shared/src/components/PageHead";
import { ProposalPanel } from "@app/shared/src/components/ProposalPanel";
import { parseApiError } from "@app/shared/src/hooks/useErrorHandler";

export default function AIStudio() {
  const nav = useNavigate();
  const [source, setSource] = useState("");
  const [target, setTarget] = useState("");
  const [nl, setNl] = useState("xóa dòng trùng, điền missing cột diem bằng median");
  const [proposal, setProposal] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [output, setOutput] = useState("");

  const generate = async () => {
    if (!source.trim() || !target.trim() || !nl.trim()) {
      setOutput("Nhập source, target và mô tả trước.");
      return;
    }
    setLoading(true);
    try {
      const res = await pipelines.generate(source.trim(), target.trim(), nl);
      setProposal(res);
      setOutput(`Proposal ${res.proposal_id} [${res.model_used}] — review panel rồi Approve.`);
    } catch (e: any) {
      setOutput(parseApiError(e).message);
    } finally {
      setLoading(false);
    }
  };

  const approve = async () => {
    if (!proposal?.proposal_id) return;
    try {
      const res = await pipelines.approveProposal(proposal.proposal_id);
      setProposal({ ...proposal, status: res.status });
      setOutput(`Approved — sang Pipeline để Create & Run.`);
    } catch (e: any) {
      setOutput(parseApiError(e).message);
    }
  };

  const reject = async () => {
    if (!proposal?.proposal_id) return;
    try {
      await pipelines.rejectProposal(proposal.proposal_id);
      setProposal(null);
      setOutput("Rejected.");
    } catch (e: any) {
      setOutput(parseApiError(e).message);
    }
  };

  const fillDemo = async () => {
    try {
      const ds = await datasets.list();
      const first = (ds.datasets ?? [])[0] as any;
      if (first?.id) {
        const prof = await datasets.getProfile(first.id).catch(() => null);
        const table = (prof as any)?.table ?? (prof as any)?.dataset_name;
        if (table) setSource(table.startsWith("raw.") || table.startsWith("mart.") ? table : `raw.${table}`);
        else if ((prof as any)?.profile) setSource(`raw.${first.dataset_name}`);
      }
    } catch { /* ignore */ }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <PageHead
        path="ai-studio"
        title="AI Studio"
        desc="AI-assisted engineering workspace — LLM đề xuất, engine validate, human approve."
        actions={<Button variant="ghost" onClick={() => nav("/pipeline")}>Mở Pipeline</Button>}
      />
      <div style={{ display: "grid", gridTemplateColumns: "minmax(280px, 4fr) minmax(340px, 7fr)", gap: 20 }}>
        <Card>
          <h4>AI Request</h4>
          <label style={{ display: "block", fontSize: 12, color: "var(--text-muted)", marginTop: 8 }}>Source (raw.*)
            <Input value={source} onChange={(e) => setSource(e.target.value)} placeholder="raw.demo" style={{ marginTop: 4 }} />
          </label>
          <label style={{ display: "block", fontSize: 12, color: "var(--text-muted)", marginTop: 8 }}>Target (mart.*)
            <Input value={target} onChange={(e) => setTarget(e.target.value)} placeholder="mart.demo" style={{ marginTop: 4 }} />
          </label>
          <label style={{ display: "block", fontSize: 12, color: "var(--text-muted)", marginTop: 8 }}>Mô tả tiếng Việt
            <Textarea value={nl} onChange={(e) => setNl(e.target.value)} rows={4} style={{ marginTop: 4 }} />
          </label>
          <div style={{ display: "flex", gap: 8, marginTop: 12, flexWrap: "wrap" }}>
            <Button onClick={generate} disabled={loading}>{loading ? "Đang sinh..." : "Generate"}</Button>
            <Button variant="ghost" onClick={fillDemo}>Lấy dataset đầu</Button>
          </div>
          {output && <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 10 }}>{output}</div>}
        </Card>
        <div>
          {proposal
            ? <ProposalPanel proposal={proposal} onApprove={approve} onReject={reject} />
            : <Card><div style={{ fontSize: 12, color: "var(--text-muted)" }}>Proposal sẽ hiện ở đây sau khi Generate — gồm steps, 4 lớp validation, cost, dry-run.</div></Card>}
        </div>
      </div>
    </div>
  );
}
