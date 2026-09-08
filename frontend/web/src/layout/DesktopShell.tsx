import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import CommandPalette from "../components/CommandPalette";
import StatusBar from "../components/StatusBar";
import { getStoredUser, logout } from "@app/shared/src/features/auth/store";

const nav = [
  { to: "/ingest", label: "ingest", cmd: "upload csv/excel" },
  { to: "/pipeline", label: "pipeline", cmd: "etl spec + run" },
  { to: "/brief", label: "brief", cmd: "ai narrative" },
  { to: "/dashboard", label: "dashboard", cmd: "charts" },
  { to: "/lab", label: "lab", cmd: "statistics" },
  { to: "/lineage", label: "lineage", cmd: "graph" },
  { to: "/settings", label: "settings", cmd: "byok key" },
];

export default function DesktopShell() {
  const loc = useLocation();
  const navgo = useNavigate();
  const user = getStoredUser() ?? "?";

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh", background: "var(--bg)" }}>
      {/* terminal title bar */}
      <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 14px", borderBottom: "1px solid var(--border-strong)", background: "var(--bg-card)", position: "sticky", top: 0, zIndex: 10 }}>
        <span style={{ width: 10, height: 10, borderRadius: "50%", background: "#F87171" }} />
        <span style={{ width: 10, height: 10, borderRadius: "50%", background: "#FACC15" }} />
        <span style={{ width: 10, height: 10, borderRadius: "50%", background: "var(--accent)" }} />
        <span style={{ marginLeft: 8, fontSize: 12 }}>
          <span style={{ color: "var(--accent)" }}>{user}@workbench</span>
          <span style={{ color: "var(--text-muted)" }}>:{loc.pathname} — ctrl+k</span>
        </span>
        <span style={{ flex: 1 }} />
        <button
          onClick={() => { logout(); navgo("/login"); }}
          style={{ background: "transparent", border: "1px solid var(--border)", color: "var(--text-muted)", fontFamily: "var(--font-mono)", fontSize: 11, padding: "4px 10px", cursor: "pointer" }}
        >
          exit
        </button>
      </div>

      <div style={{ display: "flex", flex: 1 }}>
        {/* ls-style sidebar */}
        <aside style={{ width: 220, borderRight: "1px solid var(--border)", padding: "12px 0", background: "var(--bg-card)", position: "sticky", top: 41, height: "calc(100vh - 41px)", overflow: "auto" }}>
          <div style={{ padding: "0 14px 8px", fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em" }}>$ ls ~/workbench</div>
          <nav style={{ display: "flex", flexDirection: "column" }}>
            {nav.map((n) => (
              <NavLink
                key={n.to}
                to={n.to}
                style={({ isActive }) => ({
                  color: isActive ? "var(--accent)" : "var(--text-muted)",
                  background: isActive ? "rgba(45,212,191,0.1)" : "transparent",
                  borderLeft: isActive ? "2px solid var(--accent)" : "2px solid transparent",
                  textDecoration: "none",
                  padding: "7px 14px",
                  fontSize: 12,
                })}
              >
                <span style={{ color: "var(--accent)", marginRight: 6 }}>›</span>
                ./{n.label}
                <div style={{ fontSize: 10, opacity: 0.6, marginLeft: 14 }}>{n.cmd}</div>
              </NavLink>
            ))}
          </nav>
          <div style={{ padding: "12px 14px", fontSize: 10, color: "var(--text-muted)" }}>tip: ctrl+k palette</div>
        </aside>
        <main style={{ flex: 1, padding: 24, maxWidth: 1200, margin: "0 auto", width: "100%" }}>
          <Outlet />
        </main>
      </div>

      <StatusBar />
      <CommandPalette />
    </div>
  );
}
