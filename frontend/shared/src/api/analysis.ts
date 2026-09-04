import { api } from "./client.js";
import type { AnalysisRequest, AnalysisResponse } from "../types/index.js";

export const analysis = {
  run: (req: AnalysisRequest) => api.post<AnalysisResponse>("/analysis/run", req),
};
