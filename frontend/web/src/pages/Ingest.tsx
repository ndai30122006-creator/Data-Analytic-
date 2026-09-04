import { useState } from "react";
import { datasets } from "@app/shared/src/api/datasets";

export default function Ingest() {
  const [file, setFile] = useState<File | null>(null);
  const [msg, setMsg] = useState("");

  const upload = async () => {
    if (!file) return;
    try {
      const res = await datasets.ingestFile(file);
      setMsg(`Ingested: ${JSON.stringify(res)}`);
    } catch (e: any) {
      setMsg(`Error: ${e.message}`);
    }
  };

  return (
    <div>
      <h2>Ingest — Datasets</h2>
      <input type="file" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
      <button onClick={upload} style={{ marginLeft: 8, padding: "6px 12px" }}>
        Upload & Ingest
      </button>
      <div style={{ marginTop: 12 }}>{msg}</div>
    </div>
  );
}
