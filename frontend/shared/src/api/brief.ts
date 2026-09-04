import { api } from "./client.js";

export const brief = {
  create: (datasetId: number) => api.post<any>(`/brief/${datasetId}`),
  list: (datasetId: number) => api.get<any>(`/brief/${datasetId}`),
  get: (datasetId: number, version: number) => api.get<any>(`/brief/${datasetId}/${version}`),
};
