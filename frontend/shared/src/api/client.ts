export class ApiError extends Error {
  constructor(message: string, public status: number) {
    super(message);
    this.name = "ApiError";
  }
}

const BASE = (import.meta as any).env?.VITE_API_BASE ?? "http://localhost:8000";
let _token: string | null = null;

export function setToken(t: string | null) {
  _token = t;
  if (t) localStorage.setItem("app_token", t);
  else localStorage.removeItem("app_token");
}

export function getToken() {
  if (!_token) _token = localStorage.getItem("app_token");
  return _token;
}

export async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = { ...(init.headers as Record<string, string> | undefined) };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (init.body && !(init.body instanceof FormData)) headers["Content-Type"] = "application/json";
  const res = await fetch(`${BASE}${path}`, { ...init, headers });
  if (res.status === 401) window.dispatchEvent(new Event("app:unauthorized"));
  if (!res.ok) {
    const body = await res.json().catch(() => ({} as any));
    throw new ApiError(body?.detail ?? `HTTP ${res.status}`, res.status);
  }
  return res.json() as Promise<T>;
}

export const api = {
  get: <T>(p: string) => request<T>(p),
  post: <T>(p: string, body?: unknown) => request<T>(p, { method: "POST", body: body === undefined ? undefined : JSON.stringify(body) }),
  put: <T>(p: string, body: unknown) => request<T>(p, { method: "PUT", body: JSON.stringify(body) }),
  del: <T>(p: string) => request<T>(p, { method: "DELETE" }),
  upload: <T>(p: string, file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    return request<T>(p, { method: "POST", body: fd });
  },
};
