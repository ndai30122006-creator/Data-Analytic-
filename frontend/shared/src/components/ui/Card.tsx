import React from "react";

interface Props extends React.HTMLAttributes<HTMLDivElement> {
  hover?: boolean;
}

export function Card({ hover = false, style, children, ...rest }: Props) {
  return (
    <div
      style={{
        background: "var(--bg-card)",
        border: "1px solid var(--border)",
        borderRadius: "var(--radius-card)",
        padding: 16,
        backdropFilter: "blur(12px)",
        ...(hover ? { cursor: "pointer" } : {}),
        ...style,
      }}
      {...rest}
    >
      {children}
    </div>
  );
}
