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
  primary: { background: "var(--accent)", color: "#03170d", borderColor: "var(--accent)", boxShadow: "0 0 5px #00ff88, 0 0 10px rgba(0,255,136,0.25)" },
  ghost: { background: "#1c1c2e", color: "var(--text)", borderColor: "var(--border)" },
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
