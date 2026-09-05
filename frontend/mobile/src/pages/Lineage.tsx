import { useEffect, useState } from "react";
import { datasets } from "@app/shared/src/api/datasets";
import { Button } from "@app/shared/src/components/ui/Button";
import { Card } from "@app/shared/src/components/ui/Card";

export default function Lineage() {
  const [list, setList] = useState<any[]>([]);
  const [detail, setDetail] = useState("");

  useEffect(() => {
    datasets.list().then((r) => setList(r.datasets ?? [])).catch(() => {});
  }, []);

  const view = async (name: string) => {
    setDetail(`Dataset ${name} → pipelines → dashboards\n(warehouse/lineage.py get_lineage — GET /lineage/{id})`);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <h2>Lineage — Dataset → Pipeline → Dashboard</h2>
      <Card>
        {list.length === 0 ? <div style={{ opacity: 0.5, fontSize: 13, color: "var(--text-muted)" }}>Chưa có dataset</div> : list.map((d: any) => (
          <div key={d.dataset_name} style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)", fontSize: 12 }}>
            <span>{d.dataset_name} <span style={{ color: "var(--text-muted)" }}>{d.rows}×{d.cols}</span></span>
            <Button variant="ghost" size="sm" onClick={() => view(d.dataset_name)}>View</Button>
          </div>
        ))}
      </Card>
      <Card style={{ background: "rgba(0,0,0,0.2)" }}>
        <pre style={{ fontFamily: "var(--font-mono)", fontSize: 11, minHeight: 100, margin: 0 }}>{detail || "Chọn dataset để xem lineage (table/briefs/dashboards count)"}</pre>
      </Card>
      <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Demo data: scripts/generate_demo_data.py 300 SV missing/dup/outlier → lineage hiển thị.</div>
    </div>
  );
}
