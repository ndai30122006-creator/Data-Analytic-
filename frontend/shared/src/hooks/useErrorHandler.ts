import { useCallback, useState } from "react";
import { ApiError } from "../api/client";

export interface ErrorInfo {
  message: string;
  code?: string;
  detail?: string;
  traceId?: string;
  status?: number;
}

const STATUS_MESSAGES: Record<number, string> = {
  400: "Yêu cầu không hợp lệ — kiểm tra lại dữ liệu nhập.",
  401: "Phiên đăng nhập hết hạn — vui lòng đăng nhập lại.",
  402: "Thanh toán yêu cầu.",
  403: "Bạn không có quyền thực hiện thao tác này.",
  404: "Không tìm thấy dữ liệu yêu cầu.",
  408: "Yêu cầu hết thời gian — thử lại.",
  409: "Xung đột dữ liệu — có thể đã tồn tại.",
  422: "Dữ liệu không hợp lệ — kiểm tra lại.",
  429: "Quá nhiều yêu cầu — chậm lại và thử lại sau.",
  500: "Lỗi máy chủ — thử lại sau ít phút.",
  502: "Dịch vụ tạm thời không khả dụng.",
  503: "Dịch vụ bận — thử lại sau.",
};

export function parseApiError(e: unknown): ErrorInfo {
  if (e instanceof ApiError) {
    // Try to parse standardized body if available
    const raw = (e as any).body as Record<string, unknown> | undefined;
    if (raw && typeof raw === "object") {
      return {
        message: (raw.message as string) || STATUS_MESSAGES[e.status] || e.message,
        code: (raw.code as string) || `E${e.status}`,
        detail: (raw.detail as string) || e.message,
        traceId: raw.trace_id as string | undefined,
        status: e.status,
      };
    }
    return {
      message: STATUS_MESSAGES[e.status] || e.message,
      code: `E${e.status}`,
      detail: e.message,
      status: e.status,
    };
  }
  if (e instanceof Error) {
    return { message: e.message, detail: e.message };
  }
  return { message: String(e), detail: String(e) };
}

export function useErrorHandler() {
  const [error, setError] = useState<ErrorInfo | null>(null);

  const handleError = useCallback((e: unknown) => {
    const info = parseApiError(e);
    setError(info);
    // 401 auto logout handled via ApiError dispatch elsewhere
    return info;
  }, []);

  const clearError = useCallback(() => setError(null), []);

  return { error, handleError, clearError, parseApiError };
}
