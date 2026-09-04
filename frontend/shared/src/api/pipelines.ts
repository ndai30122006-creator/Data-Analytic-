import { api } from "./client.js";
import type { PipelineSpec, RunInfo, RunStarted } from "../types/index.js";

export const pipelines = {
  create: (spec: PipelineSpec) => api.post<{ pipeline_id: string }>("/pipelines", spec),
  list: () => api.get<{ pipelines: any[]; count: number }>("/pipelines"),
  get: (id: string) => api.get<any>(`/pipelines/${id}`),
  preview: (spec: PipelineSpec) => api.post<any>("/pipelines/preview", spec),
  run: (id: string) => api.post<RunStarted>(`/pipelines/run?pipeline_id=${id}`),
  listRuns: () => api.get<{ runs: RunInfo[]; count: number }>("/runs"),
  getRun: (id: string) => api.get<RunInfo>(`/runs/${id}`),
};
