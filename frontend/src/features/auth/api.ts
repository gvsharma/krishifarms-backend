import {
  clearRefreshToken,
  clearSignedOutFlag,
  getRefreshToken,
  markSignedOut,
  setRefreshToken,
  wasExplicitlySignedOut,
} from "@/features/auth/session";
import type { AuthMe } from "@/features/auth/types";
import {
  clearAccessToken,
  fetchApi,
  getAccessToken,
  setAccessToken,
} from "@/lib/api/client";
import { getApiBaseUrl } from "@/lib/api/config";
import { getDeviceId } from "@/lib/api/device-id";
import { ROUTES } from "@/constants/routes";
import {
  exchangeRefreshToken,
  shouldSkipAuthRefresh,
} from "@/features/auth/session-recovery";

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

/** Detect email vs phone for password login (`POST /auth/login` accepts either). */
export function isEmailIdentifier(value: string): boolean {
  return value.includes("@");
}

export async function loginWithPassword(identifier: string, password: string): Promise<string> {
  const trimmed = identifier.trim();
  const body = isEmailIdentifier(trimmed)
    ? { email: trimmed.toLowerCase(), password }
    : { mobile: trimmed.replace(/\D/g, ""), password };

  const data = await fetchApi<LoginResponse>("/auth/login", {
    method: "POST",
    body,
    clientHeaders: false,
  });
  setAccessToken(data.access_token);
  setRefreshToken(data.refresh_token);
  clearSignedOutFlag();
  return data.access_token;
}

export function fetchAuthMe(): Promise<AuthMe> {
  return fetchApi<AuthMe>("/auth/me", { method: "GET", clientHeaders: false });
}

/** Best-effort server logout when a refresh token is available. */
export async function logoutFromServer(): Promise<void> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return;

  try {
    await fetchApi<{ message: string }>("/auth/logout", {
      method: "POST",
      body: { refresh_token: refreshToken },
      clientHeaders: true,
      skipAuthRefresh: true,
    });
  } catch {
    // Local sign-out still succeeds if the server call fails.
  }
}

/** Clear tokens, mark explicit sign-out, and optionally revoke refresh token server-side. */
export async function signOut(): Promise<void> {
  markSignedOut();
  await logoutFromServer();
  clearAccessToken();
  clearRefreshToken();
}

/**
 * Local session wipe + hard navigate to login (expired/invalid token).
 * Does not call the server (tokens may already be invalid).
 */
export function forceSessionExpiredLogout(redirectToLogin = true): void {
  markSignedOut();
  clearAccessToken();
  clearRefreshToken();
  if (!redirectToLogin || typeof window === "undefined") return;
  const path = window.location.pathname;
  if (path === ROUTES.login || path.startsWith(`${ROUTES.login}/`)) return;
  window.location.replace(ROUTES.login);
}

let refreshInFlight: Promise<boolean> | null = null;

/**
 * Exchange refresh token for a new access (+ refresh) pair.
 * Uses raw fetch to avoid recursive 401 handling in fetchApi.
 * Concurrent callers share one in-flight request.
 */
export async function refreshSession(): Promise<boolean> {
  if (typeof window === "undefined") return false;
  if (refreshInFlight) return refreshInFlight;

  refreshInFlight = (async () => {
    const refreshToken = getRefreshToken();
    if (!refreshToken) return false;

    const tokens = await exchangeRefreshToken({
      apiBase: getApiBaseUrl(),
      refreshToken,
      deviceId: getDeviceId(),
    });
    if (!tokens) return false;

    setAccessToken(tokens.access_token);
    setRefreshToken(tokens.refresh_token);
    clearSignedOutFlag();
    return true;
  })().finally(() => {
    refreshInFlight = null;
  });

  return refreshInFlight;
}

/**
 * Handle 401 from an authenticated API call: refresh once, else force logout.
 * Returns true if the caller should retry the original request.
 */
export async function recoverFromUnauthorized(path: string): Promise<boolean> {
  if (shouldSkipAuthRefresh(path)) return false;
  const refreshed = await refreshSession();
  if (refreshed) return true;
  forceSessionExpiredLogout(true);
  return false;
}

/** Dev-only: seed token from env or password login once per session. */
export async function bootstrapAuthToken(): Promise<void> {
  if (typeof window === "undefined") return;
  if (wasExplicitlySignedOut()) return;
  if (getAccessToken()) return;

  const devToken = process.env.NEXT_PUBLIC_DEV_ACCESS_TOKEN?.trim();
  if (devToken) {
    setAccessToken(devToken);
    return;
  }

  const devEmail = process.env.NEXT_PUBLIC_DEV_LOGIN_EMAIL?.trim();
  const devPassword = process.env.NEXT_PUBLIC_DEV_LOGIN_PASSWORD?.trim();
  if (devEmail && devPassword) {
    try {
      await loginWithPassword(devEmail, devPassword);
    } catch {
      // Leave unauthenticated; pages show API errors.
    }
  }
}
