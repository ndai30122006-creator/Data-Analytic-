import React from "react";

interface Props extends React.HTMLAttributes<HTMLDivElement> {
  hover?: boolean;
}

export function Card({ hover = false, style, children, ...rest }: Props) {
  return (
    <div
      className="wb-card"
      style={{
        background: "var(--bg-card)",
        border: "1px solid var(--border)",
        borderRadius: "var(--radius-card)",
        padding: 16,
        transition: "transform 0.22s var(--ease, ease), border-color 0.22s var(--ease, ease), box-shadow 0.22s var(--ease, ease)",
        ...(hover ? { cursor: "pointer" } : {}),
        ...style,
      }}
      {...rest}
    >
      {children}
    </div>
  );
}
