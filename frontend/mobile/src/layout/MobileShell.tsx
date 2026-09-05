import { NavLink, Outlet } from "react-router-dom";

const nav = [
  { to: "/brief", label: "Brief" },
  { to: "/dashboard", label: "Dash" },
  { to: "/lineage", label: "Lineage" },
  { to: "/lab", label: "Lab" },
  { to: "/settings", label: "Settings" },
];

export default function MobileShell() {
  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh", background: "var(--bg)" }}>
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
          background: "rgba(10,10,26,0.92)",
          borderTop: "1px solid var(--border)",
          backdropFilter: "blur(16px)",
        }}
      >
        {nav.map((n) => (
          <NavLink
            key={n.to}
            to={n.to}
            style={({ isActive }) => ({
              color: isActive ? "var(--accent)" : "var(--text-muted)",
              background: isActive ? "rgba(139,92,246,0.12)" : "transparent",
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
