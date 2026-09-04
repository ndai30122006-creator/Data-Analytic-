import { api } from "./client.js";
import type { DashboardSpec } from "../types/index.js";

export const dashboards = {
  create: (spec: DashboardSpec & { name: string }) => api.post<{ dashboard_id: number }>("/dashboards", { name: spec.name, spec }),
  list: () => api.get<{ dashboards: any[] }>("/dashboards"),
  get: (id: number) => api.get<any>(`/dashboards/${id}`),
  update: (id: number, spec: any) => api.put<any>(`/dashboards/${id}`, { name: spec.name, spec }),
  data: (id: number) => api.post<any>(`/dashboards/${id}/data`),
  generate: (dataset_id: number) => api.post<{ spec: DashboardSpec }>(`/dashboards/generate?dataset_id=${dataset_id}`),
};
