export class ApiError extends Error {
  public code: string;
  public detail: string;
  public traceId?: string;
  public body?: Record<string, unknown>;
  constructor(message: string, public status: number, body?: Record<string, unknown>) {
    super(message);
    this.name = "ApiError";
    this.body = body;
    this.code = (body?.code as string) || `E${status}`;
    this.detail = (body?.detail as string) || message;
    this.traceId = body?.trace_id as string | undefined;
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
    const body = (await res.json().catch(() => ({} as any))) as Record<string, unknown>;
    // Standardized {code, message, detail, trace_id} or legacy {detail}
    const msg = (body?.message as string) || (body?.detail as string) || `HTTP ${res.status}`;
    throw new ApiError(msg, res.status, body);
  }
  return res.json() as Promise<T>;
}

function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

export async function requestWithRetry<T>(path: string, init: RequestInit = {}, opts: { retries?: number; baseDelay?: number } = {}): Promise<T> {
  const retries = opts.retries ?? 3;
  const baseDelay = opts.baseDelay ?? 1000;
  let lastErr: unknown;
  for (let i = 0; i <= retries; i++) {
    try {
      return await request<T>(path, init);
    } catch (e) {
      lastErr = e;
      if (e instanceof ApiError && [408, 429, 500, 502, 503].includes(e.status) && i < retries) {
        await sleep(baseDelay * Math.pow(2, i));
        continue;
      }
      throw e;
    }
  }
  throw lastErr;
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
