/** Tabs nhe — dung cho Dataset detail, Inspector sections. */
export function Tabs({ tabs, value, onChange }: {
  tabs: { id: string; label: string; badge?: string | number }[];
  value: string;
  onChange: (id: string) => void;
}) {
  return (
    <div role="tablist" style={{ display: "flex", gap: 4, borderBottom: "1px solid var(--border)", overflowX: "auto" }}>
      {tabs.map((t) => {
        const active = t.id === value;
        return (
          <button key={t.id} role="tab" aria-selected={active} onClick={() => onChange(t.id)}
            style={{
              background: "transparent", border: 0, cursor: "pointer",
              borderBottom: active ? "2px solid var(--accent)" : "2px solid transparent",
              color: active ? "var(--text)" : "var(--text-muted)",
              fontWeight: active ? 700 : 400,
              fontSize: 12, padding: "8px 12px", whiteSpace: "nowrap", fontFamily: "var(--font-sans)",
            }}>
            {t.label}
            {t.badge !== undefined && (
              <span style={{ marginLeft: 6, fontSize: 10, background: "rgba(45,212,191,0.12)", color: "var(--accent)", borderRadius: 8, padding: "0 6px" }}>
                {t.badge}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
