import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { getStoredUser } from "@app/shared/src/features/auth/store";

export default function StatusBar() {
  const [api, setApi] = useState<"online" | "offline" | "...">("...");
  const [clock, setClock] = useState("");
  const loc = useLocation();

  useEffect(() => {
    let stop = false;
    const ping = async () => {
      try {
        const res = await fetch("http://localhost:8000/health");
        if (!stop) setApi(res.ok ? "online" : "offline");
      } catch {
        if (!stop) setApi("offline");
      }
    };
    ping();
    const id = setInterval(ping, 15000);
    const tick = () => setClock(new Date().toLocaleTimeString("vi-VN", { hour12: false }));
    tick();
    const cid = setInterval(tick, 1000);
    return () => { stop = true; clearInterval(id); clearInterval(cid); };
  }, []);

  const dot = api === "online" ? "var(--accent)" : api === "offline" ? "var(--danger)" : "var(--warn)";

  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 16, padding: "6px 14px",
      borderTop: "1px solid var(--border-strong)", background: "var(--bg-card)",
      fontSize: 11, color: "var(--text-muted)", position: "sticky", bottom: 0, zIndex: 5,
    }}>
      <span><span className="dot-live" style={{ display: "inline-block", width: 8, height: 8, borderRadius: "50%", background: dot, marginRight: 6, boxShadow: `0 0 8px ${dot}` }} />api:{api}</span>
      <span>user:{getStoredUser() ?? "?"}</span>
      <span style={{ flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>~{loc.pathname}</span>
      <span>v1.3.0</span>
      <span>{clock}</span>
    </div>
  );
}
