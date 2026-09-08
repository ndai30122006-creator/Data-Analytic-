import { api } from "./client.js";

export interface LineageNode { id: string; kind: string; label: string; meta?: string }
export interface LineageEdge { from: string; to: string; label?: string }
export interface LineageResponse {
  dataset: string;
  table: string;
  briefs: number;
  dashboards: number;
  pipelines_count: number;
  pipeline_list: { id: string; name: string; source: string; target: string }[];
  dashboard_list: { id: number; name: string }[];
  brief_versions: { version: number; model: string }[];
  nodes: LineageNode[];
  edges: LineageEdge[];
}

export const lineage = {
  get: (datasetId: number) => api.get<LineageResponse>(`/lineage/${datasetId}`),
};
