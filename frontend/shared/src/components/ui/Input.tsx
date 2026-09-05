import React from "react";

export function Input(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      style={{
        width: "100%",
        padding: "8px 10px",
        background: "rgba(0,0,0,0.3)",
        color: "var(--text)",
        border: "1px solid var(--border)",
        borderRadius: "var(--radius-input)",
        fontFamily: "var(--font-sans)",
        fontSize: 13,
        outline: "none",
        ...(props.style || {}),
      }}
      onFocus={(e) => {
        e.currentTarget.style.borderColor = "var(--border-strong)";
        props.onFocus?.(e);
      }}
      onBlur={(e) => {
        e.currentTarget.style.borderColor = "var(--border)";
        props.onBlur?.(e);
      }}
    />
  );
}

export function Textarea(props: React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      {...props}
      style={{
        width: "100%",
        padding: 12,
        background: "rgba(0,0,0,0.4)",
        color: "var(--text)",
        border: "1px solid var(--border)",
        borderRadius: "var(--radius-input)",
        fontFamily: "var(--font-mono)",
        fontSize: 12,
        outline: "none",
        ...(props.style || {}),
      }}
    />
  );
}
