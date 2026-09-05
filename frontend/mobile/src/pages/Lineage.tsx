import { useEffect, useState } from "react";
import { datasets } from "@app/shared/src/api/datasets";

export default function Lineage() {
  const [list, setList] = useState<any[]>([]);
  const [detail, setDetail] = useState("");

  useEffect(() => {
    datasets.list().then((r) => setList(r.datasets ?? [])).catch(() => {});
  }, []);

  const view = async (name: string) => {
    setDetail(`Dataset ${name} → pipelines → dashboards\n(warehouse/lineage.py get_lineage — hiện skeleton, cần API lineage chi tiết)`);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <h2>Lineage — Dataset → Pipeline → Dashboard</h2>
      <div style={{ border: "1px solid rgba(255,255,255,0.08)", borderRadius: 8, padding: 12 }}>
        {list.length === 0 ? <div style={{ opacity: 0.5, fontSize: 13 }}>Chưa có dataset</div> : list.map((d: any) => (
          <div key={d.dataset_name} style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid rgba(255,255,255,0.06)", fontSize: 12 }}>
            <span>{d.dataset_name} <span style={{ opacity: 0.5 }}>{d.rows}×{d.cols}</span></span>
            <button onClick={() => view(d.dataset_name)} style={{ padding: "4px 10px", fontSize: 11, background: "rgba(255,255,255,0.08)", color: "white", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 6, cursor: "pointer" }}>View</button>
          </div>
        ))}
      </div>
      <pre style={{ background: "rgba(0,0,0,0.4)", padding: 12, borderRadius: 8, fontSize: 11, minHeight: 100, border: "1px solid rgba(255,255,255,0.06)" }}>{detail || "Chọn dataset để xem lineage (table/briefs/dashboards count)"}</pre>
      <div style={{ fontSize: 11, opacity: 0.4 }}>Demo data: scripts/generate_demo_data.py 300 SV missing/dup/outlier → lineage hiển thị.</div>
    </div>
  );
}
