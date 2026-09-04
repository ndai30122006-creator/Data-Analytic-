import { api } from "./client.js";
import type { EnvValidateResponse, HealthResponse } from "../types/index.js";

export const system = {
  health: () => api.get<HealthResponse>("/health"),
  envValidate: () => api.get<EnvValidateResponse>("/env/validate"),
};
