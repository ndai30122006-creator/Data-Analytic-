import { useEffect, useState } from "react";
import { auth } from "../../api/auth.js";
import { getStoredToken, getStoredUser, setToken, logout } from "./store.js";

export function useAuth() {
  const [user, setUser] = useState<string | null>(getStoredUser());
  const [token, setTok] = useState<string | null>(getStoredToken());
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (token) {
      auth.verify().catch(() => {
        logout();
        setUser(null);
        setTok(null);
      });
    }
    const onUnauth = () => {
      logout();
      setUser(null);
      setTok(null);
    };
    window.addEventListener("app:unauthorized", onUnauth);
    window.addEventListener("app:logout", onUnauth);
    return () => {
      window.removeEventListener("app:unauthorized", onUnauth);
      window.removeEventListener("app:logout", onUnauth);
    };
  }, [token]);

  const login = async (username: string, password: string) => {
    setLoading(true);
    try {
      const res = await auth.login(username, password);
      setToken(res.access_token, res.username);
      setUser(res.username);
      setTok(res.access_token);
      return res;
    } finally {
      setLoading(false);
    }
  };

  const register = async (username: string, password: string) => {
    setLoading(true);
    try {
      return await auth.register(username, password);
    } finally {
      setLoading(false);
    }
  };

  return { user, token, loading, login, register, logout: () => { logout(); setUser(null); setTok(null); } };
}
