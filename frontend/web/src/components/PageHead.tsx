import type { ReactNode } from "react";

/** Chuẩn đầu trang: path + title + desc + actions phải. */
export default function PageHead({ path, title, desc, actions }: { path: string; title: string; desc?: string; actions?: ReactNode }) {
  return (
    <div style={{ position: "relative", display: "flex", alignItems: "flex-end", justifyContent: "space-between", gap: 16, flexWrap: "wrap", paddingBottom: 14, borderBottom: "1px solid var(--border)" }}>
      <div>
        <div style={{ fontSize: 11, color: "var(--accent)", marginBottom: 4 }}>$ ~/workbench/{path}</div>
        <h2 style={{ fontSize: 24 }}>{title}</h2>
        {desc && <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 6, maxWidth: 640 }}>{desc}</div>}
      </div>
      {actions && <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>{actions}</div>}
      <div className="grad-bar" style={{ position: "absolute", bottom: -1, left: 0, width: 220, maxWidth: "40%" }} />
    </div>
  );
}
