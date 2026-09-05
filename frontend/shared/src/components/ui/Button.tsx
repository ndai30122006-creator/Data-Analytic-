import React from "react";

type Variant = "primary" | "ghost" | "danger";
type Size = "sm" | "md";

interface Props extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
}

const base: React.CSSProperties = {
  borderRadius: "var(--radius-pill)",
  fontWeight: 500,
  cursor: "pointer",
  border: "1px solid transparent",
  fontFamily: "var(--font-sans)",
};

const variants: Record<Variant, React.CSSProperties> = {
  primary: { background: "var(--accent)", color: "white", borderColor: "var(--accent)" },
  ghost: { background: "rgba(255,255,255,0.06)", color: "var(--text)", borderColor: "var(--border)" },
  danger: { background: "var(--danger)", color: "white", borderColor: "var(--danger)" },
};

const sizes: Record<Size, React.CSSProperties> = {
  sm: { padding: "6px 12px", fontSize: 12 },
  md: { padding: "8px 14px", fontSize: 13 },
};

export function Button({ variant = "primary", size = "md", style, children, ...rest }: Props) {
  return (
    <button style={{ ...base, ...variants[variant], ...sizes[size], ...style }} {...rest}>
      {children}
    </button>
  );
}
