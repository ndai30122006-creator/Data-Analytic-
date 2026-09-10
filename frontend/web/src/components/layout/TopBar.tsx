import { getStoredUser, logout } from "@app/shared/src/features/auth/store";

/** TopBar: brand + global search trigger + user/logout. */
export function TopBar({ onSearch, onLogout }: { onSearch: () => void; onLogout: () => void }) {
  const user = getStoredUser() ?? "?";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "8px 16px", borderBottom: "1px solid var(--border)", background: "var(--bg-card)", position: "sticky", top: 0, zIndex: 20 }}>
      <span className="grad-text" style={{ fontSize: 14, fontWeight: 800, letterSpacing: "-0.01em", filter: "drop-shadow(0 0 8px rgba(45,212,191,0.35))" }}>
        dataworkbench
      </span>
      <button onClick={onSearch} aria-label="Global search"
        style={{ flex: 1, maxWidth: 420, display: "flex", alignItems: "center", gap: 8, background: "var(--bg)", border: "1px solid var(--border)", borderRadius: "var(--radius-input)", color: "var(--text-muted)", fontSize: 12, padding: "7px 12px", cursor: "pointer", textAlign: "left" }}>
        <span>Search datasets, pipelines, dashboards...</span>
        <span style={{ marginLeft: "auto", border: "1px solid var(--border)", borderRadius: 4, padding: "0 6px", fontSize: 10 }}>Ctrl K</span>
      </button>
      <span style={{ flex: 1 }} />
      <span style={{ fontSize: 12, color: "var(--text-muted)" }}>{user}</span>
      <button
        onClick={() => { logout(); onLogout(); }}
        style={{ background: "transparent", border: "1px solid var(--border)", color: "var(--text-muted)", fontSize: 11, padding: "6px 12px", borderRadius: "var(--radius-pill)", cursor: "pointer", fontFamily: "var(--font-mono)" }}
      >
        Logout
      </button>
    </div>
  );
}
