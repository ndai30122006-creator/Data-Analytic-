import { useCallback, useState } from "react";
import { ApiError } from "../api/client";
import { parseApiError, type ErrorInfo } from "./useErrorHandler";

export interface UseApiCallOptions {
  retries?: number; // default 3
  retryDelay?: number; // base ms, default 1000
  retryOn?: (status: number) => boolean; // default retry 408,429,500,502,503
}

const DEFAULT_RETRY_ON = (s: number) => [408, 429, 500, 502, 503].includes(s);

function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

export function useApiCall<T>(fn: (...args: any[]) => Promise<T>, opts: UseApiCallOptions = {}) {
  const { retries = 3, retryDelay = 1000, retryOn = DEFAULT_RETRY_ON } = opts;
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ErrorInfo | null>(null);
  const [data, setData] = useState<T | null>(null);
  const [attempt, setAttempt] = useState(0);

  const execute = useCallback(
    async (...args: any[]): Promise<T> => {
      setLoading(true);
      setError(null);
      let lastErr: unknown;
      for (let i = 0; i <= retries; i++) {
        setAttempt(i);
        try {
          const res = await fn(...args);
          setData(res as T);
          setLoading(false);
          return res;
        } catch (e) {
          lastErr = e;
          const isApi = e instanceof ApiError;
          const status = isApi ? (e as ApiError).status : 0;
          const shouldRetry = isApi && retryOn(status) && i < retries;
          if (shouldRetry) {
            const delay = retryDelay * Math.pow(2, i); // 1s ->2s ->4s
            await sleep(delay);
            continue;
          }
          const info = parseApiError(e);
          setError(info);
          setLoading(false);
          throw e;
        }
      }
      // Exhausted retries
      const info = parseApiError(lastErr);
      setError(info);
      setLoading(false);
      throw lastErr;
    },
    [fn, retries, retryDelay, retryOn],
  );

  const reset = useCallback(() => {
    setError(null);
    setData(null);
    setAttempt(0);
  }, []);

  return { loading, error, data, attempt, execute, reset };
}
