import { api } from "./client.js";
import type { DatasetListResponse, IngestResponse, ProfileResponse } from "../types/index.js";

export const datasets = {
  list: () => api.get<DatasetListResponse>("/datasets"),
  create: (dataset_name: string, rows?: number, cols?: number) => api.post<{ message: string }>("/datasets", { dataset_name, rows, cols }),
  ingestFile: (file: File) => api.upload<IngestResponse>("/datasets/ingest", file),
  getProfile: (id: number) => api.get<ProfileResponse>(`/datasets/${id}/profile`),
  remove: (dataset_name: string) => api.del<{ message: string }>(`/datasets/${dataset_name}`),
};
