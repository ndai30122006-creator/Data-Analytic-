import { useState } from "react";
export default function Settings() {
  const [key, setKey] = useState("");
  return (
    <div>
      <h2>Settings — BYOK</h2>
      <input placeholder="API Key" type="password" value={key} onChange={(e) => setKey(e.target.value)} style={{ width: "100%", padding: 12, borderRadius: 12 }} />
      <button style={{ marginTop: 12, width: "100%", padding: 12, borderRadius: 999, background: "#8B5CF6", color: "white", border: "none" }}>Save Key</button>
    </div>
  );
}
