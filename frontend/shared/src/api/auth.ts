import { api } from "./client.js";
import type { LoginResponse } from "../types/index.js";

export const auth = {
  register: (username: string, password: string) => api.post<{ message: string }>("/auth/register", { username, password }),
  login: (username: string, password: string) => api.post<LoginResponse>("/auth/login", { username, password }),
  verify: () => api.get<{ username: string; valid: boolean }>("/auth/verify"),
  saveApiKey: (api_key: string) => api.post<{ message: string }>("/auth/api-key", { api_key }),
  deleteUser: () => api.del<{ message: string }>("/auth/user"),
};
