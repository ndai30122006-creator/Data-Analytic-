import React from "react";

interface Props {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    // In prod, send to logging service
    // eslint-disable-next-line no-console
    console.error("ErrorBoundary caught:", error, info);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;
      return (
        <div style={{ padding: 24, textAlign: "center", maxWidth: 480, margin: "40px auto", border: "1px solid rgba(239,68,68,0.3)", borderRadius: 12, background: "rgba(239,68,68,0.06)" }}>
          <h3 style={{ color: "#EF4444", margin: "0 0 8px" }}>Đã xảy ra lỗi</h3>
          <p style={{ fontSize: 13, opacity: 0.7, margin: "0 0 12px" }}>{this.state.error?.message ?? "Ứng dụng gặp sự cố không mong muốn."}</p>
          <pre style={{ fontSize: 11, opacity: 0.5, overflow: "auto", background: "rgba(0,0,0,0.3)", padding: 8, borderRadius: 6, textAlign: "left" }}>{String(this.state.error?.stack ?? "").slice(0, 500)}</pre>
          <div style={{ marginTop: 12, display: "flex", gap: 8, justifyContent: "center" }}>
            <button onClick={this.handleReset} style={{ padding: "8px 14px", background: "#8B5CF6", color: "white", border: 0, borderRadius: 6, cursor: "pointer" }}>Thử lại</button>
            <button onClick={() => (window.location.href = "/")} style={{ padding: "8px 14px", background: "rgba(255,255,255,0.08)", color: "white", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 6, cursor: "pointer" }}>Về trang chủ</button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
