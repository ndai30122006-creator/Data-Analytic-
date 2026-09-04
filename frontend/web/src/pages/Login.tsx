import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@app/shared/src/features/auth/useAuth";

export default function Login() {
  const { login, register, loading } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState<"login" | "register">("login");
  const nav = useNavigate();

  const submit = async () => {
    if (mode === "login") {
      await login(username, password);
      nav("/ingest");
    } else {
      await register(username, password);
      setMode("login");
    }
  };

  return (
    <div style={{ maxWidth: 360, margin: "80px auto" }}>
      <h2>{mode === "login" ? "Login" : "Register"}</h2>
      <input placeholder="username" value={username} onChange={(e) => setUsername(e.target.value)} style={{ width: "100%", padding: 8, marginBottom: 8 }} />
      <input placeholder="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} style={{ width: "100%", padding: 8, marginBottom: 8 }} />
      <button onClick={submit} disabled={loading} style={{ width: "100%", padding: 10 }}>
        {loading ? "..." : mode === "login" ? "Login" : "Register"}
      </button>
      <button onClick={() => setMode(mode === "login" ? "register" : "login")} style={{ marginTop: 8, background: "none", border: "none", color: "#8B5CF6" }}>
        {mode === "login" ? "Need account? Register" : "Have account? Login"}
      </button>
    </div>
  );
}
