import { NavLink, Outlet } from "react-router-dom";

const nav = [
  { to: "/ingest", label: "Ingest" },
  { to: "/pipeline", label: "Pipeline" },
  { to: "/brief", label: "Brief" },
  { to: "/dashboard", label: "Dashboard" },
  { to: "/lab", label: "Lab" },
  { to: "/settings", label: "Settings" },
  { to: "/lineage", label: "Lineage" },
];

export default function DesktopShell() {
  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "var(--bg)" }}>
      <aside
        style={{
          width: 240,
          borderRight: "1px solid var(--border)",
          padding: 16,
          background: "rgba(255,255,255,0.02)",
          backdropFilter: "blur(12px)",
          position: "sticky",
          top: 0,
          height: "100vh",
        }}
      >
        <h3 style={{ fontFamily: "var(--font-sans)", fontWeight: 600, fontSize: 16, margin: "0 0 16px", letterSpacing: "-0.01em" }}>Workbench AI</h3>
        <nav style={{ display: "flex", flexDirection: "column", gap: 4 }}>
          {nav.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              style={({ isActive }) => ({
                color: isActive ? "var(--accent)" : "var(--text-muted)",
                background: isActive ? "rgba(139,92,246,0.12)" : "transparent",
                textDecoration: "none",
                padding: "8px 12px",
                borderRadius: "var(--radius-input)",
                fontSize: 13,
                fontWeight: isActive ? 600 : 400,
              })}
            >
              {n.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main style={{ flex: 1, padding: 24, maxWidth: 1200, margin: "0 auto", width: "100%" }}>
        <Outlet />
      </main>
    </div>
  );
}
