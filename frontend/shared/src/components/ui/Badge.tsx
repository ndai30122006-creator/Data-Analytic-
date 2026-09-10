import React from "react";

type Variant = "success" | "warn" | "danger" | "neutral";

const colors: Record<Variant, string> = {
  success: "var(--success)",
  warn: "var(--warn)",
  danger: "var(--danger)",
  neutral: "var(--text-muted)",
};

const TINT: Record<Variant, string> = {
  success: "rgba(52,211,153,0.12)",
  warn: "rgba(251,191,36,0.12)",
  danger: "rgba(248,113,113,0.12)",
  neutral: "rgba(45,212,191,0.08)",
};
const TINT_BORDER: Record<Variant, string> = {
  success: "rgba(52,211,153,0.35)",
  warn: "rgba(251,191,36,0.35)",
  danger: "rgba(248,113,113,0.35)",
  neutral: "rgba(45,212,191,0.25)",
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
        background: TINT[variant],
        color: colors[variant],
        border: `1px solid ${TINT_BORDER[variant]}`,
        ...style,
      }}
    >
      {children}
    </span>
  );
}
