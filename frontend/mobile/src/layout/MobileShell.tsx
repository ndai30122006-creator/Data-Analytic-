import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { logout } from "@app/shared/src/features/auth/store";

const nav = [
  { to: "/", label: "Home" },
  { to: "/ingest", label: "Ingest" },
  { to: "/brief", label: "Brief" },
  { to: "/dashboard", label: "Dash" },
  { to: "/pipeline", label: "Pipe" },
  { to: "/lab", label: "Lab" },
];

export default function MobileShell() {
  const navgo = useNavigate();
  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh", background: "var(--bg)" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "10px 16px", borderBottom: "1px solid var(--border)", background: "var(--bg-card)" }}>
        <span style={{ fontSize: 13, fontWeight: 800 }}>dataworkbench</span>
        <span style={{ flex: 1 }} />
        <NavLink to="/lineage" style={{ fontSize: 11, color: "var(--text-muted)", textDecoration: "none" }}>Lineage</NavLink>
        <NavLink to="/settings" style={{ fontSize: 11, color: "var(--text-muted)", textDecoration: "none" }}>Settings</NavLink>
        <button onClick={() => { logout(); navgo("/login"); }}
          style={{ background: "transparent", border: "1px solid var(--border)", color: "var(--text-muted)", fontSize: 11, padding: "5px 10px", borderRadius: "var(--radius-pill)", fontFamily: "var(--font-mono)" }}>
          Logout
        </button>
      </div>
      <main style={{ flex: 1, padding: 16, paddingBottom: 80 }}>
        <Outlet />
      </main>
      <nav
        style={{
          position: "fixed",
          bottom: 0,
          left: 0,
          right: 0,
          display: "flex",
          justifyContent: "space-around",
          padding: "10px 0 calc(10px + env(safe-area-inset-bottom))",
          background: "var(--bg)",
          borderTop: "1px solid var(--border)",
        }}
      >
        {nav.map((n) => (
          <NavLink
            key={n.to}
            to={n.to}
            style={({ isActive }) => ({
              color: isActive ? "var(--accent)" : "var(--text-muted)",
              background: isActive ? "rgba(45,212,191,0.12)" : "transparent",
              textDecoration: "none",
              fontSize: 11,
              fontWeight: isActive ? 600 : 400,
              padding: "8px 12px",
              minWidth: 44,
              minHeight: 44,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              borderRadius: "var(--radius-input)",
              textAlign: "center" as const,
            })}
          >
            {n.label}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
