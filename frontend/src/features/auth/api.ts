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
