const MAP: Record<string, { color: string; pulse?: boolean }> = {
  done: { color: "var(--success)" },
  success: { color: "var(--success)" },
  pass: { color: "var(--success)" },
  running: { color: "var(--accent)", pulse: true },
  queued: { color: "var(--warn)", pulse: true },
  failed: { color: "var(--danger)" },
  error: { color: "var(--danger)" },
  warn: { color: "var(--warn)" },
};

/** Cham trang thai + nhan — thay the hien status roi rac bang mau don thuan. */
export function StatusDot({ status, label }: { status: string; label?: string }) {
  const m = MAP[status] ?? { color: "var(--text-muted)" };
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 12 }}>
      <span className={m.pulse ? "dot-live" : undefined}
        style={{ width: 8, height: 8, borderRadius: "50%", background: m.color, boxShadow: `0 0 8px ${m.color}` }} />
      <span>{label ?? status}</span>
    </span>
  );
}
