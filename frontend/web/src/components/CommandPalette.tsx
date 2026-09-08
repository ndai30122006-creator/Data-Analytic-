import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { logout } from "@app/shared/src/features/auth/store";

type Nav = (p: string) => void;
const COMMANDS: { name: string; hint: string; run: (nav: Nav) => void }[] = [
  { name: "ingest — upload csv/excel", run: (nav) => nav("/ingest"), hint: "upload" },
  { name: "pipeline — etl spec + run", run: (nav) => nav("/pipeline"), hint: "etl run" },
  { name: "brief — ai narrative", run: (nav) => nav("/brief"), hint: "report" },
  { name: "dashboard — charts", run: (nav) => nav("/dashboard"), hint: "chart" },
  { name: "lab — statistics", run: (nav) => nav("/lab"), hint: "stats test" },
  { name: "lineage — graph", run: (nav) => nav("/lineage"), hint: "graph" },
  { name: "settings — byok key", run: (nav) => nav("/settings"), hint: "key" },
  { name: "logout", run: (nav) => { logout(); nav("/login"); }, hint: "exit quit" },
];

export default function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");
  const [idx, setIdx] = useState(0);
  const nav = useNavigate();

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setQ("");
        setIdx(0);
        setOpen((o) => !o);
      }
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const list = useMemo(() => {
    const s = q.trim().toLowerCase();
    if (!s) return COMMANDS;
    return COMMANDS.filter((c) => (c.name + " " + c.hint).toLowerCase().includes(s));
  }, [q]);

  useEffect(() => setIdx(0), [q]);

  if (!open) return null;
  const go = (i: number) => {
    const c = list[i];
    if (!c) return;
    setOpen(false);
    c.run(nav);
  };

  return (
    <div
      onClick={() => setOpen(false)}
      style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.6)", zIndex: 50, display: "flex", justifyContent: "center", paddingTop: "15vh" }}
    >
      <div onClick={(e) => e.stopPropagation()} style={{ width: 520, maxWidth: "90vw", height: "fit-content", background: "var(--bg-card)", border: "1px solid var(--border-strong)" }}>
        <div style={{ display: "flex", alignItems: "center", borderBottom: "1px solid var(--border)" }}>
          <span style={{ padding: "10px 0 10px 12px", color: "var(--accent)" }}>$</span>
          <input
            autoFocus
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "ArrowDown") { e.preventDefault(); setIdx((i) => Math.min(i + 1, list.length - 1)); }
              if (e.key === "ArrowUp") { e.preventDefault(); setIdx((i) => Math.max(i - 1, 0)); }
              if (e.key === "Enter") go(idx);
            }}
            placeholder="type command... (esc to close)"
            style={{ flex: 1, background: "transparent", border: 0, outline: "none", color: "var(--text)", padding: 10, fontFamily: "var(--font-mono)", fontSize: 13 }}
          />
        </div>
        <div style={{ maxHeight: 280, overflow: "auto" }}>
          {list.length === 0 && <div style={{ padding: 12, fontSize: 12, color: "var(--text-muted)" }}>no match</div>}
          {list.map((c, i) => (
            <div
              key={c.name}
              onClick={() => go(i)}
              onMouseEnter={() => setIdx(i)}
              style={{ padding: "8px 12px", fontSize: 12, cursor: "pointer", background: i === idx ? "rgba(0,255,136,0.12)" : "transparent", color: i === idx ? "var(--accent)" : "var(--text)" }}
            >
              <span style={{ color: "var(--accent)", marginRight: 8 }}>›</span>{c.name}
            </div>
          ))}
        </div>
        <div style={{ padding: "6px 12px", fontSize: 10, color: "var(--text-muted)", borderTop: "1px solid var(--border)" }}>↑↓ navigate · ↵ run · ctrl+k toggle</div>
      </div>
    </div>
  );
}
