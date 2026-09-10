import { api } from "./client.js";
import type { DatasetListResponse, IngestResponse, ProfileResponse } from "../types/index.js";

export interface RowsParams { limit?: number; offset?: number; order_by?: string; order_dir?: string; q?: string }
export interface RowsResponse { columns: string[]; rows: any[][]; total: number }

function buildRowsQs(p: RowsParams, extra: Record<string, string> = {}) {
  const qs = new URLSearchParams({ ...extra, limit: String(p.limit ?? 20), offset: String(p.offset ?? 0) });
  if (p.order_by) {
    qs.set("order_by", p.order_by);
    qs.set("order_dir", p.order_dir ?? "asc");
  }
  if (p.q) qs.set("q", p.q);
  return qs;
}

export const datasets = {
  list: () => api.get<DatasetListResponse>("/datasets"),
  create: (dataset_name: string, rows?: number, cols?: number) => api.post<{ message: string }>("/datasets", { dataset_name, rows, cols }),
  ingestFile: (file: File) => api.upload<IngestResponse>("/datasets/ingest", file),
  getProfile: (id: number) => api.get<ProfileResponse>(`/datasets/${id}/profile`),
  rows: (id: number, p: RowsParams = {}) =>
    api.get<RowsResponse>(`/datasets/${id}/rows?${buildRowsQs(p)}`),
  tableRows: (table: string, p: RowsParams = {}) =>
    api.get<RowsResponse>(`/tables/rows?${buildRowsQs(p, { table })}`),
  remove: (dataset_name: string) => api.del<{ message: string }>(`/datasets/${dataset_name}`),
};
