import { useCallback, useEffect, useState } from "react";
import { datasets } from "../api/datasets";
import { Button } from "./ui/Button";
import { Input } from "./ui/Input";
import { EmptyState, Skeleton } from "./ui/Skeleton";

const PAGE_SIZE = 20;

/** Bang xem rows that: phan trang + sort click-header + search (dataset id hoac table). */
export function DataTable({ datasetId, table, title }: { datasetId?: number; table?: string; title?: string }) {
  const [cols, setCols] = useState<string[]>([]);
  const [rows, setRows] = useState<any[][]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [sort, setSort] = useState<{ col: string; dir: "asc" | "desc" } | null>(null);
  const [q, setQ] = useState("");
  const [qSent, setQSent] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    if (!datasetId && !table) return;
    setLoading(true);
    setError("");
    try {
      const res = datasetId
        ? await datasets.rows(datasetId, { limit: PAGE_SIZE, offset: page * PAGE_SIZE, order_by: sort?.col, order_dir: sort?.dir, q: qSent || undefined })
        : await datasets.tableRows(table!, { limit: PAGE_SIZE, offset: page * PAGE_SIZE, order_by: sort?.col, order_dir: sort?.dir, q: qSent || undefined });
      setCols(res.columns ?? []);
      setRows(res.rows ?? []);
      setTotal(res.total ?? 0);
    } catch (e: any) {
      setError(e.message ?? "Load failed");
    } finally {
      setLoading(false);
    }
  }, [datasetId, table, page, sort, qSent]);

  useEffect(() => { load(); }, [load]);
  useEffect(() => { setPage(0); }, [datasetId, table]);

  const pages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const toggleSort = (c: string) => {
    setPage(0);
    setSort((s) => (!s || s.col !== c ? { col: c, dir: "asc" } : s.dir === "asc" ? { col: c, dir: "desc" } : null));
  };

  if (!datasetId && !table) return <EmptyState title="Chưa chọn nguồn" hint="Chọn dataset/dashboard để xem rows" />;

  return (
    <div>
      <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 10, flexWrap: "wrap" }}>
        <Input placeholder="search..." value={q} onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") { setPage(0); setQSent(q); } }} style={{ width: 200 }} />
        <Button variant="ghost" size="sm" onClick={() => { setPage(0); setQSent(q); }}>Search</Button>
        {(qSent || sort) && <Button variant="ghost" size="sm" onClick={() => { setQ(""); setQSent(""); setSort(null); setPage(0); }}>Clear</Button>}
        <span style={{ marginLeft: "auto", fontSize: 11, color: "var(--text-muted)" }}>
          {title ?? ""} · {total} rows · p.{page + 1}/{pages}
        </span>
      </div>
      {loading ? <Skeleton height={120} /> : error ? <div style={{ color: "var(--danger)", fontSize: 12 }}>{error}</div> : rows.length === 0
        ? <EmptyState title="Không có rows" hint="Bảng trống hoặc search không khớp" />
        : (
          <div style={{ overflow: "auto", border: "1px solid var(--border)", borderRadius: "var(--radius-input)", maxHeight: 380 }}>
            <table style={{ borderCollapse: "collapse", width: "100%", fontSize: 11, fontFamily: "var(--font-mono)" }}>
              <thead style={{ position: "sticky", top: 0, background: "var(--bg-card)", zIndex: 1 }}>
                <tr>
                  <th style={{ padding: "8px 10px", color: "var(--text-muted)", borderBottom: "1px solid var(--border)", width: 44 }}>#</th>
                  {cols.map((c) => (
                    <th key={c} onClick={() => toggleSort(c)} title="Click để sort"
                      style={{ padding: "8px 10px", textAlign: "left", borderBottom: "1px solid var(--border)", cursor: "pointer", color: sort?.col === c ? "var(--accent)" : "var(--text-muted)", whiteSpace: "nowrap" }}>
                      {c}{sort?.col === c ? (sort.dir === "asc" ? " ▲" : " ▼") : ""}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((r, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid var(--border)" }}>
                    <td style={{ padding: "6px 10px", color: "var(--text-muted)" }}>{page * PAGE_SIZE + i + 1}</td>
                    {r.map((v: any, j: number) => (
                      <td key={j} style={{ padding: "6px 10px", whiteSpace: "nowrap", maxWidth: 220, overflow: "hidden", textOverflow: "ellipsis" }}>
                        {v === null || v === undefined ? <span style={{ opacity: 0.4 }}>null</span> : String(v)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      <div style={{ display: "flex", gap: 8, alignItems: "center", marginTop: 10 }}>
        <Button variant="ghost" size="sm" onClick={() => setPage((p) => Math.max(0, p - 1))} disabled={page === 0 || loading}>← Prev</Button>
        <Button variant="ghost" size="sm" onClick={() => setPage((p) => Math.min(pages - 1, p + 1))} disabled={page >= pages - 1 || loading}>Next →</Button>
        <Button variant="ghost" size="sm" onClick={load} disabled={loading}>Reload</Button>
      </div>
    </div>
  );
}
