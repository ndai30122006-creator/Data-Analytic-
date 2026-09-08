import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@app/shared/features/auth/useAuth";
import { Card } from "@app/shared/src/components/ui/Card";
import { Button } from "@app/shared/src/components/ui/Button";

export default function Login() {
  const { login, register, loading } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState<"login" | "register">("login");
  const [out, setOut] = useState<string[]>(["workbench-ai v1.3.0 — local-first data workbench", "type credentials to continue"]);
  const nav = useNavigate();

  const print = (s: string) => setOut((o) => [...o.slice(-8), s]);

  const submit = async () => {
    if (!username.trim() || !password) { print("! empty credentials"); return; }
    try {
      if (mode === "login") {
        print(`$ ssh ${username}@workbench ...`);
        await login(username, password);
        print("$ auth OK — entering shell");
        setTimeout(() => nav("/ingest"), 400);
      } else {
        await register(username, password);
        print("$ account created — now login");
        setMode("login");
      }
    } catch (e: any) {
      print(`! ${e.message ?? "auth failed"}`);
    }
  };

  const onKey = (e: React.KeyboardEvent) => { if (e.key === "Enter") submit(); };

  return (
    <div style={{ maxWidth: 480, margin: "8vh auto", padding: 16 }}>
      <Card>
        <div style={{ fontSize: 22, fontWeight: 700, letterSpacing: "-0.02em" }}>
          <span style={{ color: "var(--accent)" }}>workbench</span>
          <span style={{ color: "var(--text)" }}>-ai</span>
          <span style={{ fontSize: 11, color: "var(--text-muted)", fontWeight: 400, marginLeft: 8 }}>v1.3.0</span>
        </div>
        <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>local-first data workbench · duckdb + byok</div>
        <div style={{ marginTop: 12, fontSize: 12, minHeight: 60 }}>
          {out.map((l, i) => (
            <div key={i} style={{ color: l.startsWith("!") ? "var(--danger)" : l.startsWith("$") ? "var(--text)" : "var(--text-muted)" }}>{l}</div>
          ))}
        </div>
        <div style={{ marginTop: 12 }}>
          <label style={{ fontSize: 12 }}>
            <span style={{ color: "var(--accent)" }}>{mode === "login" ? "login:" : "new user:"} </span>
            <input value={username} onChange={(e) => setUsername(e.target.value)} onKeyDown={onKey} autoFocus placeholder="username"
              style={{ background: "transparent", border: 0, borderBottom: "1px solid var(--border)", outline: "none", color: "var(--text)", fontFamily: "var(--font-mono)", fontSize: 13, width: 200 }} />
          </label>
        </div>
        <div style={{ marginTop: 8 }}>
          <label style={{ fontSize: 12 }}>
            <span style={{ color: "var(--accent)" }}>password: </span>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} onKeyDown={onKey} placeholder="••••••••"
              style={{ background: "transparent", border: 0, borderBottom: "1px solid var(--border)", outline: "none", color: "var(--text)", fontFamily: "var(--font-mono)", fontSize: 13, width: 200 }} />
          </label>
        </div>
        <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
          <Button onClick={submit} disabled={loading}>{loading ? "..." : mode === "login" ? "./enter" : "./register"}</Button>
          <Button variant="ghost" onClick={() => setMode(mode === "login" ? "register" : "login")}>
            {mode === "login" ? "need account?" : "have account?"}
          </Button>
        </div>
      </Card>
      <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 8 }}>demo: dev / dev123 · keys stored BYOK in Settings</div>
    </div>
  );
}
