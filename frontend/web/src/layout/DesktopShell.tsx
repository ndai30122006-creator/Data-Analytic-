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
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <aside style={{ width: 220, borderRight: "1px solid rgba(255,255,255,0.1)", padding: 16 }}>
        <h3>Workbench</h3>
        <nav style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {nav.map((n) => (
            <NavLink key={n.to} to={n.to} style={({ isActive }) => ({ color: isActive ? "#8B5CF6" : "rgba(255,255,255,0.7)", textDecoration: "none" })}>
              {n.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main style={{ flex: 1, padding: 24 }}>
        <Outlet />
      </main>
    </div>
  );
}
