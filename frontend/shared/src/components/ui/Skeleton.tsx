import React from "react";

export function Skeleton({ height = 12, width = "100%", style }: { height?: number | string; width?: number | string; style?: React.CSSProperties }) {
  return <div className="shimmer" style={{ height, width, borderRadius: 8, ...style }} />;
}

export function EmptyState({ title, hint, action }: { title: string; hint?: string; action?: React.ReactNode }) {
  return (
    <div style={{ textAlign: "center", padding: 24, border: "1px dashed var(--border)", borderRadius: "var(--radius-card)", background: "rgba(45,212,191,0.04)" }}>
      <div style={{ fontWeight: 600, fontSize: 13 }}>{title}</div>
      {hint && <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 4 }}>{hint}</div>}
      {action && <div style={{ marginTop: 12 }}>{action}</div>}
    </div>
  );
}

export function Toast({ message, type = "info", onClose }: { message: string; type?: "info" | "success" | "error"; onClose?: () => void }) {
  const bg = type === "error" ? "rgba(248,113,113,0.1)" : type === "success" ? "rgba(52,211,153,0.1)" : "rgba(45,212,191,0.1)";
  const border = type === "error" ? "rgba(248,113,113,0.35)" : type === "success" ? "rgba(52,211,153,0.35)" : "rgba(45,212,191,0.3)";
  return (
    <div style={{ background: bg, border: `1px solid ${border}`, borderRadius: "var(--radius-input)", padding: "10px 12px", fontSize: 12, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
      <span>{message}</span>
      {onClose && <button onClick={onClose} style={{ background: "transparent", border: 0, color: "var(--text-muted)", cursor: "pointer", fontSize: 12 }}>✕</button>}
    </div>
  );
}
