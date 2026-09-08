import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import CommandPalette from "../components/CommandPalette";
import StatusBar from "../components/StatusBar";
import { getStoredUser, logout } from "@app/shared/src/features/auth/store";

const nav = [
  { to: "/ingest", label: "Ingest" },
  { to: "/pipeline", label: "Pipeline" },
  { to: "/brief", label: "Brief" },
  { to: "/dashboard", label: "Dashboard" },
  { to: "/lab", label: "Lab" },
  { to: "/lineage", label: "Lineage" },
  { to: "/settings", label: "Settings" },
];

export default function DesktopShell() {
  const loc = useLocation();
  const navgo = useNavigate();
  const user = getStoredUser() ?? "?";

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh", background: "var(--bg)" }}>
      {/* title bar */}
      <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 16px", borderBottom: "1px solid var(--border)", background: "var(--bg-card)" }}>
        <span style={{ width: 10, height: 10, borderRadius: "50%", background: "var(--danger)" }} />
        <span style={{ width: 10, height: 10, borderRadius: "50%", background: "var(--warn)" }} />
        <span style={{ width: 10, height: 10, borderRadius: "50%", background: "var(--accent)" }} />
        <span style={{ marginLeft: 8, fontSize: 13, fontWeight: 700 }}>
          workbench<span style={{ color: "var(--accent)" }}>-ai</span>
        </span>
        <span style={{ fontSize: 11, color: "var(--text-muted)" }}>{user} · {loc.pathname}</span>
        <span style={{ flex: 1 }} />
        <span style={{ fontSize: 11, color: "var(--text-muted)", marginRight: 8 }}>ctrl+k</span>
        <button
          onClick={() => { logout(); navgo("/login"); }}
          style={{ background: "transparent", border: "1px solid var(--border)", color: "var(--text-muted)", fontSize: 11, padding: "5px 12px", borderRadius: "var(--radius-pill)", cursor: "pointer" }}
        >
          Logout
        </button>
      </div>

      {/* top navbar */}
      <nav style={{ display: "flex", gap: 4, padding: "8px 16px", borderBottom: "1px solid var(--border)", background: "rgba(255,255,255,0.015)", position: "sticky", top: 0, zIndex: 10, overflowX: "auto" }}>
        {nav.map((n) => (
          <NavLink
            key={n.to}
            to={n.to}
            style={({ isActive }) => ({
              color: isActive ? "#04211B" : "var(--text-muted)",
              background: isActive ? "var(--accent)" : "transparent",
              boxShadow: isActive ? "0 4px 14px rgba(45,212,191,0.3)" : "none",
              textDecoration: "none",
              padding: "7px 16px",
              borderRadius: "var(--radius-pill)",
              fontSize: 12,
              fontWeight: isActive ? 700 : 500,
              whiteSpace: "nowrap",
            })}
          >
            {n.label}
          </NavLink>
        ))}
      </nav>

      <main key={loc.pathname} className="page-enter" style={{ flex: 1, padding: 28, maxWidth: 1280, margin: "0 auto", width: "100%" }}>
        <Outlet />
      </main>

      <StatusBar />
      <CommandPalette />
    </div>
  );
}
