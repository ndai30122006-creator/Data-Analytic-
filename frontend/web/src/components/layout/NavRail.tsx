import { NavLink } from "react-router-dom";

export interface NavItem { to: string; label: string }
export interface NavGroup { title: string; items: NavItem[] }

export const NAV_GROUPS: NavGroup[] = [
  {
    title: "Workspace",
    items: [
      { to: "/", label: "Overview" },
      { to: "/ingest", label: "Data" },
      { to: "/pipeline", label: "Pipelines" },
      { to: "/dashboard", label: "Dashboards" },
    ],
  },
  {
    title: "Intelligence",
    items: [
      { to: "/ai-studio", label: "AI Studio" },
      { to: "/brief", label: "Brief" },
      { to: "/lab", label: "Statistics Lab" },
    ],
  },
  {
    title: "Governance",
    items: [
      { to: "/lineage", label: "Lineage" },
      { to: "/runs", label: "Runs" },
    ],
  },
  {
    title: "System",
    items: [{ to: "/settings", label: "Settings" }],
  },
];

/** Navigation rail: 64px collapsed / 220px expanded, group theo domain. */
export function NavRail({ collapsed, onToggle }: { collapsed: boolean; onToggle: () => void }) {
  const width = collapsed ? 64 : 220;
  return (
    <aside style={{ width, flexShrink: 0, borderRight: "1px solid var(--border)", background: "var(--bg-card)", display: "flex", flexDirection: "column", position: "sticky", top: 49, height: "calc(100vh - 49px)", transition: "width 0.22s var(--ease)", overflow: "hidden" }}>
      <div style={{ flex: 1, overflowY: "auto", padding: "8px 0" }}>
        {NAV_GROUPS.map((g) => (
          <div key={g.title} style={{ marginBottom: 4 }}>
            {!collapsed && (
              <div style={{ padding: "8px 16px 4px", fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.1em" }}>
                {g.title}
              </div>
            )}
            {g.items.map((n) => (
              <NavLink
                key={n.to}
                to={n.to}
                title={n.label}
                style={({ isActive }) => ({
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  color: isActive ? "var(--accent)" : "var(--text-muted)",
                  background: isActive ? "rgba(45,212,191,0.1)" : "transparent",
                  borderLeft: isActive ? "2px solid var(--accent)" : "2px solid transparent",
                  textDecoration: "none",
                  padding: collapsed ? "10px 0" : "8px 16px",
                  justifyContent: collapsed ? "center" : "flex-start",
                  fontSize: 12,
                  fontWeight: isActive ? 700 : 400,
                  whiteSpace: "nowrap",
                })}
              >
                {collapsed
                  ? <span style={{ width: 8, height: 8, borderRadius: "50%", background: "currentColor", opacity: 0.8 }} />
                  : <span>{n.label}</span>}
              </NavLink>
            ))}
          </div>
        ))}
      </div>
      <button onClick={onToggle} aria-label={collapsed ? "Expand navigation" : "Collapse navigation"}
        style={{ background: "transparent", border: 0, borderTop: "1px solid var(--border)", color: "var(--text-muted)", cursor: "pointer", padding: "10px", fontSize: 12, fontFamily: "var(--font-mono)" }}>
        {collapsed ? "»" : "« collapse"}
      </button>
    </aside>
  );
}
