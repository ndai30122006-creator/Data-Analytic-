import React from "react";

export function Skeleton({ height = 12, width = "100%", style }: { height?: number | string; width?: number | string; style?: React.CSSProperties }) {
  return <div style={{ height, width, background: "rgba(255,255,255,0.06)", borderRadius: 6, animation: "pulse 1.5s infinite", ...style }} />;
}

export function EmptyState({ title, hint, action }: { title: string; hint?: string; action?: React.ReactNode }) {
  return (
    <div style={{ textAlign: "center", padding: 24, border: "1px dashed var(--border)", borderRadius: "var(--radius-card)", background: "rgba(255,255,255,0.02)" }}>
      <div style={{ fontWeight: 600, fontSize: 13 }}>{title}</div>
      {hint && <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 4 }}>{hint}</div>}
      {action && <div style={{ marginTop: 12 }}>{action}</div>}
    </div>
  );
}

export function Toast({ message, type = "info", onClose }: { message: string; type?: "info" | "success" | "error"; onClose?: () => void }) {
  const bg = type === "error" ? "rgba(239,68,68,0.12)" : type === "success" ? "rgba(16,185,129,0.12)" : "rgba(139,92,246,0.12)";
  const border = type === "error" ? "rgba(239,68,68,0.3)" : type === "success" ? "rgba(16,185,129,0.3)" : "rgba(139,92,246,0.3)";
  return (
    <div style={{ background: bg, border: `1px solid ${border}`, borderRadius: "var(--radius-input)", padding: "10px 12px", fontSize: 12, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
      <span>{message}</span>
      {onClose && <button onClick={onClose} style={{ background: "transparent", border: 0, color: "var(--text-muted)", cursor: "pointer", fontSize: 12 }}>✕</button>}
    </div>
  );
}
