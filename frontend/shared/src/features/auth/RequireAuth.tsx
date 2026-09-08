import { useEffect, useState, type ReactNode } from "react";
import { getStoredToken, logout } from "./store.js";

/** Chan route can auth (khong phu thuoc react-router): chua login / 401 -> ve /login. */
export function RequireAuth({ children }: { children: ReactNode }) {
  const [ok, setOk] = useState(() => !!getStoredToken());

  useEffect(() => {
    if (!getStoredToken()) {
      window.location.replace("/login");
      return;
    }
    const onUnauth = () => {
      logout();
      setOk(false);
      window.location.replace("/login");
    };
    window.addEventListener("app:unauthorized", onUnauth);
    return () => window.removeEventListener("app:unauthorized", onUnauth);
  }, []);

  if (!ok || !getStoredToken()) return <div style={{ padding: 24, fontSize: 13, opacity: 0.6 }}>Redirecting to login...</div>;
  return <>{children}</>;
}
