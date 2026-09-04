import { useState } from "react";
import { useSettings } from "@app/shared/src/features/settings/useSettings";

export default function Settings() {
  const { provider, saving, saveApiKey, PROVIDERS } = useSettings();
  const [key, setKey] = useState("");
  const [prov, setProv] = useState(provider);

  return (
    <div>
      <h2>Settings — BYOK</h2>
      <select value={prov} onChange={(e) => setProv(e.target.value as any)} style={{ padding: 8, marginBottom: 8 }}>
        {PROVIDERS.map((p) => (
          <option key={p} value={p}>
            {p}
          </option>
        ))}
      </select>
      <input placeholder="API Key" type="password" value={key} onChange={(e) => setKey(e.target.value)} style={{ width: "100%", padding: 8, marginBottom: 8 }} />
      <button onClick={() => saveApiKey(key, prov as any)} disabled={saving} style={{ padding: "8px 16px" }}>
        {saving ? "Saving..." : "Save Key"}
      </button>
    </div>
  );
}
