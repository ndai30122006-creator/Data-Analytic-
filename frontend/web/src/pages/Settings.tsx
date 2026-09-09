import { useState } from "react";
import { useSettings } from "@app/shared/features/settings/useSettings";
import { Button } from "@app/shared/components/ui/Button";
import { Card } from "@app/shared/components/ui/Card";
import { Input } from "@app/shared/components/ui/Input";
import { Toast } from "@app/shared/components/ui/Skeleton";
import { PageHead } from "@app/shared/src/components/PageHead";

export default function Settings() {
  const { provider, saving, saveApiKey, PROVIDERS } = useSettings();
  const [key, setKey] = useState("");
  const [prov, setProv] = useState(provider);
  const [msg, setMsg] = useState("");

  const save = async () => {
    try {
      await saveApiKey(key, prov as any);
      setMsg("Key saved — Brief/Dashboard/Pipeline-generate sẽ dùng LLM, fail thì fallback rule-based.");
      setKey("");
    } catch (e: any) {
      setMsg(`Error: ${e.message}`);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <PageHead path="settings" title="Settings" desc="Bring Your Own Key — key mã hóa Fernet at-rest, chỉ dùng cho LLM, không bao giờ gửi raw data." />
      <Card style={{ maxWidth: 560 }}>
        <h4>01 · Provider</h4>
        <select value={prov} onChange={(e) => setProv(e.target.value as any)}
          style={{ width: "100%", marginTop: 8, padding: 10, background: "var(--bg)", color: "var(--text)", border: "1px solid var(--border)", borderRadius: "var(--radius-input)", fontFamily: "var(--font-mono)", fontSize: 13 }}>
          {PROVIDERS.map((p) => <option key={p} value={p}>{p}</option>)}
        </select>
        <h4 style={{ marginTop: 16 }}>02 · API key</h4>
        <Input placeholder="sk-... / gemini key" type="password" value={key} onChange={(e) => setKey(e.target.value)} style={{ marginTop: 8 }} />
        <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
          <Button onClick={save} disabled={saving || !key.trim()}>{saving ? "Saving..." : "Save Key"}</Button>
        </div>
        {msg && <div style={{ marginTop: 12 }}><Toast message={msg} type={msg.startsWith("Error") ? "error" : "success"} onClose={() => setMsg("")} /></div>}
      </Card>
      <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Test: mở Brief → Generate, xem dòng model: openai:gpt-4o-mini thay vì rule-based.</div>
    </div>
  );
}
