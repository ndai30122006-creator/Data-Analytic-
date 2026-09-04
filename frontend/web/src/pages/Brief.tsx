import { useState } from "react";
import { brief } from "@app/shared/src/api/brief";

export default function Brief() {
  const [datasetId, setDatasetId] = useState(1);
  const [content, setContent] = useState("");
  const create = async () => {
    const res = await brief.create(datasetId);
    setContent(JSON.stringify(res, null, 2));
  };
  return (
    <div>
      <h2>Brief — AI Summary</h2>
      <input type="number" value={datasetId} onChange={(e) => setDatasetId(Number(e.target.value))} style={{ padding: 6, marginRight: 8 }} />
      <button onClick={create} style={{ padding: "6px 12px" }}>
        Generate Brief
      </button>
      <pre style={{ marginTop: 12, background: "rgba(255,255,255,0.06)", padding: 12 }}>{content || "No brief yet"}</pre>
    </div>
  );
}
