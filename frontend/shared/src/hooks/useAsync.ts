import { useCallback, useState } from "react";

export function useAsync<T>(fn: (...args: any[]) => Promise<T>) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [data, setData] = useState<T | null>(null);
  const execute = useCallback(async (...args: any[]) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fn(...args);
      setData(res as T);
      return res;
    } catch (e) {
      setError(e as Error);
      throw e;
    } finally {
      setLoading(false);
    }
  }, [fn]);
  return { loading, error, data, execute };
}
