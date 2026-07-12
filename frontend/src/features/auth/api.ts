import {
  clearRefreshToken,
  clearSignedOutFlag,
  getRefreshToken,
  markSignedOut,
  setRefreshToken,
  wasExplicitlySignedOut,
} from "@/features/auth/session";
import type { AuthMe } from "@/features/auth/types";
import { clearAccessToken, fetchApi, getAccessToken, setAccessToken } from "@/lib/api/client";

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export async function loginWithPassword(email: string, password: string): Promise<string> {
  const data = await fetchApi<LoginResponse>("/auth/login", {
    method: "POST",
    body: { email, password },
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

export function updateMyProfile(payload: {
  preferred_locale?: string;
  full_name?: string;
}): Promise<{ id: string; preferred_locale: string; full_name: string }> {
  return fetchApi("/users/me", {
    method: "PATCH",
    body: payload,
    clientHeaders: true,
  });
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
