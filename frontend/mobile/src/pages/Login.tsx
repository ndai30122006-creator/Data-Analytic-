import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@app/shared/src/features/auth/useAuth";

export default function Login() {
  const { login } = useAuth();
  const [u, setU] = useState("");
  const [p, setP] = useState("");
  const nav = useNavigate();
  return (
    <div style={{ padding: 24, maxWidth: 360, margin: "40px auto" }}>
      <h2>Login — Mobile</h2>
      <input placeholder="username" value={u} onChange={(e) => setU(e.target.value)} style={{ width: "100%", padding: 12, marginBottom: 12, borderRadius: 12 }} />
      <input placeholder="password" type="password" value={p} onChange={(e) => setP(e.target.value)} style={{ width: "100%", padding: 12, marginBottom: 12, borderRadius: 12 }} />
      <button onClick={async () => { await login(u, p); nav("/brief"); }} style={{ width: "100%", padding: 12, borderRadius: 999, background: "#8B5CF6", color: "white", border: "none" }}>
        Login
      </button>
    </div>
  );
}
