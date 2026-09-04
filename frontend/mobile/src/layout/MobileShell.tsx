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
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <main style={{ flex: 1, padding: 16, paddingBottom: 80 }}><Outlet /></main>
      <nav style={{ position: "fixed", bottom: 0, left: 0, right: 0, display: "flex", justifyContent: "space-around", padding: "12px 0", background: "rgba(10,10,26,0.95)", borderTop: "1px solid rgba(255,255,255,0.1)", backdropFilter: "blur(12px)" }}>
        {nav.map((n) => (
          <NavLink key={n.to} to={n.to} style={({ isActive }) => ({ color: isActive ? "#8B5CF6" : "rgba(255,255,255,0.6)", textDecoration: "none", fontSize: 12, padding: "8px 12px", minWidth: 44, textAlign: "center" as const })}>
            {n.label}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
