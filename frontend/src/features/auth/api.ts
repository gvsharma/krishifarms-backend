import type { AuthMe } from "@/features/auth/types";
import { fetchApi, setAccessToken } from "@/lib/api/client";

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export async function loginWithPassword(email: string, password: string): Promise<string> {
  const data = await fetchApi<LoginResponse>("/auth/login", {
    method: "POST",
    body: { email, password },
    clientHeaders: false,
  });
  setAccessToken(data.access_token);
  return data.access_token;
}

export function fetchAuthMe(): Promise<AuthMe> {
  return fetchApi<AuthMe>("/auth/me", { method: "GET", clientHeaders: false });
}

/** Dev-only: seed token from env or password login once per session. */
export async function bootstrapAuthToken(): Promise<void> {
  if (typeof window === "undefined") return;

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
