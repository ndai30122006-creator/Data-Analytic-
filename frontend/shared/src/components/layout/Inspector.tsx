import type { ReactNode } from "react";

/** Inspector slide-over ben phai — dung chung cho node/graph/row details (Phase 1 infra). */
export function Inspector({ open, title, subtitle, onClose, children, width = 360 }: {
  open: boolean;
  title: string;
  subtitle?: string;
  onClose: () => void;
  children: ReactNode;
  width?: number;
}) {
  return (
    <div aria-hidden={!open}
      style={{
        position: "fixed", top: 0, right: 0, bottom: 0, width: `min(${width}px, 92vw)`,
        background: "var(--bg-card)", borderLeft: "1px solid var(--border-strong)",
        boxShadow: "var(--shadow-pop)", zIndex: 60,
        transform: open ? "translateX(0)" : "translateX(105%)",
        transition: "transform 0.24s var(--ease)",
        display: "flex", flexDirection: "column",
        pointerEvents: open ? "auto" : "none",
      }}>
      <div style={{ display: "flex", alignItems: "flex-start", gap: 8, padding: "14px 16px", borderBottom: "1px solid var(--border)" }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontWeight: 700, fontSize: 13 }}>{title}</div>
          {subtitle && <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>{subtitle}</div>}
        </div>
        <button onClick={onClose} aria-label="Close inspector"
          style={{ background: "transparent", border: "1px solid var(--border)", color: "var(--text-muted)", borderRadius: "var(--radius-input)", cursor: "pointer", padding: "4px 10px", fontSize: 12 }}>
          ✕
        </button>
      </div>
      <div style={{ flex: 1, overflowY: "auto", padding: 16 }}>{children}</div>
    </div>
  );
}
