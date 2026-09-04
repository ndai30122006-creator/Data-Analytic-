import { useState } from "react";
import { dashboards } from "@app/shared/src/api/dashboards";

export default function Dashboard() {
  const [spec, setSpec] = useState("");
  const generate = async () => {
    const res = await dashboards.generate(1);
    setSpec(JSON.stringify(res, null, 2));
  };
  return (
    <div>
      <h2>Dashboard — AI Generate</h2>
      <button onClick={generate} style={{ padding: "6px 12px" }}>
        Generate Dashboard
      </button>
      <pre style={{ marginTop: 12, background: "rgba(255,255,255,0.06)", padding: 12 }}>{spec || "No spec"}</pre>
    </div>
  );
}
