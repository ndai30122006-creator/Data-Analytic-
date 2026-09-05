import React from "react";

type Variant = "success" | "warn" | "danger" | "neutral";

const colors: Record<Variant, string> = {
  success: "var(--success)",
  warn: "var(--warn)",
  danger: "var(--danger)",
  neutral: "var(--text-muted)",
};

export function Badge({ variant = "neutral", children, style }: { variant?: Variant; children: React.ReactNode; style?: React.CSSProperties }) {
  return (
    <span
      style={{
        display: "inline-block",
        padding: "2px 6px",
        borderRadius: 6,
        fontSize: 10,
        fontWeight: 600,
        background: variant === "neutral" ? "rgba(255,255,255,0.08)" : `${colors[variant]}20`,
        color: colors[variant],
        border: `1px solid ${colors[variant]}30`,
        ...style,
      }}
    >
      {children}
    </span>
  );
}
