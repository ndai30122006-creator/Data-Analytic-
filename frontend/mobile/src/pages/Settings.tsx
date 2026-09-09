import { useState } from "react";
import { useSettings } from "@app/shared/features/settings/useSettings";
import { Button } from "@app/shared/src/components/ui/Button";
import { Card } from "@app/shared/src/components/ui/Card";
import { Input } from "@app/shared/src/components/ui/Input";
import { Toast } from "@app/shared/src/components/ui/Skeleton";
import { PageHead } from "@app/shared/src/components/PageHead";

export default function Settings() {
  const { provider, saving, saveApiKey, PROVIDERS } = useSettings();
  const [key, setKey] = useState("");
  const [prov, setProv] = useState(provider);
  const [msg, setMsg] = useState("");

  const save = async () => {
    try {
      await saveApiKey(key, prov as any);
      setMsg("Key saved.");
      setKey("");
    } catch (e: any) {
      setMsg(`Error: ${e.message}`);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <PageHead path="settings" title="Settings" desc="BYOK key — mã hóa at-rest." />
      <Card>
        <select value={prov} onChange={(e) => setProv(e.target.value as any)}
          style={{ width: "100%", padding: 10, background: "var(--bg)", color: "var(--text)", border: "1px solid var(--border)", borderRadius: "var(--radius-input)", fontFamily: "var(--font-mono)", fontSize: 13 }}>
          {PROVIDERS.map((p) => <option key={p} value={p}>{p}</option>)}
        </select>
        <Input placeholder="API Key" type="password" value={key} onChange={(e) => setKey(e.target.value)} style={{ marginTop: 8 }} />
        <Button onClick={save} disabled={saving || !key.trim()} style={{ marginTop: 12, width: "100%" }}>{saving ? "Saving..." : "Save Key"}</Button>
        {msg && <div style={{ marginTop: 12 }}><Toast message={msg} type={msg.startsWith("Error") ? "error" : "success"} onClose={() => setMsg("")} /></div>}
      </Card>
    </div>
  );
}
