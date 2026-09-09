import { api } from "./client.js";
import type { DatasetListResponse, IngestResponse, ProfileResponse } from "../types/index.js";

export const datasets = {
  list: () => api.get<DatasetListResponse>("/datasets"),
  create: (dataset_name: string, rows?: number, cols?: number) => api.post<{ message: string }>("/datasets", { dataset_name, rows, cols }),
  ingestFile: (file: File) => api.upload<IngestResponse>("/datasets/ingest", file),
  getProfile: (id: number) => api.get<ProfileResponse>(`/datasets/${id}/profile`),
  rows: (id: number, p: { limit?: number; offset?: number; order_by?: string; order_dir?: string; q?: string } = {}) => {
    const qs = new URLSearchParams({ limit: String(p.limit ?? 20), offset: String(p.offset ?? 0) });
    if (p.order_by) { qs.set("order_by", p.order_by); qs.set("order_dir", p.order_dir ?? "asc"); }
    if (p.q) qs.set("q", p.q);
    return api.get<{ columns: string[]; rows: any[][]; total: number }>(`/datasets/${id}/rows?${qs}`);
  },
  tableRows: (table: string, p: { limit?: number; offset?: number; order_by?: string; order_dir?: string; q?: string } = {}) => {
    const qs = new URLSearchParams({ table, limit: String(p.limit ?? 20), offset: String(p.offset ?? 0) });
    if (p.order_by) { qs.set("order_by", p.order_by); qs.set("order_dir", p.order_dir ?? "asc"); }
    if (p.q) qs.set("q", p.q);
    return api.get<{ columns: string[]; rows: any[][]; total: number }>(`/tables/rows?${qs}`);
  },
  remove: (dataset_name: string) => api.del<{ message: string }>(`/datasets/${dataset_name}`),
};
