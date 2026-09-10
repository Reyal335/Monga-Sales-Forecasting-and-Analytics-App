const FALLBACK_API_URL = "http://localhost:8000";
const ACCESS_TOKEN_KEY = "monga_access_token";

export const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? FALLBACK_API_URL).replace(/\/$/, "");

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export function getAccessToken() {
  if (typeof window === "undefined") return null;
  return window.sessionStorage.getItem(ACCESS_TOKEN_KEY);
}

export function setAccessToken(accessToken: string) {
  window.sessionStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
}

export function clearAccessToken() {
  if (typeof window !== "undefined") window.sessionStorage.removeItem(ACCESS_TOKEN_KEY);
}

export async function authenticatedFetch(path: string, init: RequestInit = {}) {
  const headers = new Headers(init.headers);
  const accessToken = getAccessToken();

  if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);

  return fetch(`${API_URL}${path.startsWith("/") ? path : `/${path}`}`, {
    ...init,
    credentials: "include",
    headers,
  });
}
