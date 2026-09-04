import { setToken as setClientToken } from "../../api/client.js";

const KEY = "app_token";
const USER_KEY = "app_user";

export function setToken(token: string | null, username?: string) {
  setClientToken(token);
  if (token) {
    localStorage.setItem(KEY, token);
    if (username) localStorage.setItem(USER_KEY, username);
  } else {
    localStorage.removeItem(KEY);
    localStorage.removeItem(USER_KEY);
  }
}

export function getStoredToken() {
  return localStorage.getItem(KEY);
}

export function getStoredUser() {
  return localStorage.getItem(USER_KEY);
}

export function logout() {
  setToken(null);
  window.dispatchEvent(new Event("app:logout"));
}
