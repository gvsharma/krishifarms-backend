/** Paths that must never trigger refresh-on-401 (avoids loops). */
export const AUTH_NO_REFRESH_PATHS = [
  "/auth/login",
  "/auth/refresh",
  "/auth/logout",
  "/auth/firebase-login",
] as const;

export function normalizeApiPath(path: string): string {
  let bare = path;
  try {
    if (path.startsWith("http://") || path.startsWith("https://")) {
      bare = new URL(path).pathname;
    }
  } catch {
    // fall through
  }
  if (!bare.startsWith("/")) bare = `/${bare}`;
  // Strip optional /api/v1 prefix used by absolute or proxied URLs.
  const stripped = bare.replace(/^\/api\/v1(?=\/|$)/, "") || "/";
  return stripped.startsWith("/") ? stripped : `/${stripped}`;
}

export function shouldSkipAuthRefresh(path: string): boolean {
  const normalized = normalizeApiPath(path);
  return AUTH_NO_REFRESH_PATHS.some(
    (skip) => normalized === skip || normalized.endsWith(skip),
  );
}

/** True when an API error should attempt session recovery (refresh or logout). */
export function isUnauthorizedStatus(status: number): boolean {
  return status === 401;
}

/**
 * Decide post-401 action after an optional refresh attempt.
 * - refreshed: caller should retry the original request once
 * - logout: clear session and send user to login
 */
export function decideUnauthorizedRecovery(refreshed: boolean): "retry" | "logout" {
  return refreshed ? "retry" : "logout";
}

export type TokenPair = {
  access_token: string;
  refresh_token: string;
  token_type?: string;
};

/** Parse refresh API JSON (envelope or flat). */
export function parseRefreshTokenPayload(payload: unknown): TokenPair | null {
  if (typeof payload !== "object" || payload === null) return null;
  const body = payload as {
    data?: Partial<TokenPair>;
    access_token?: string;
    refresh_token?: string;
    token_type?: string;
  };
  const nested = body.data;
  const access = nested?.access_token ?? body.access_token;
  const refresh = nested?.refresh_token ?? body.refresh_token;
  if (!access || !refresh) return null;
  return {
    access_token: access,
    refresh_token: refresh,
    token_type: nested?.token_type ?? body.token_type ?? "bearer",
  };
}

/**
 * POST /auth/refresh with injectable fetch — used by web client and unit tests.
 */
export async function exchangeRefreshToken(options: {
  apiBase: string;
  refreshToken: string;
  deviceId: string;
  fetchImpl?: typeof fetch;
}): Promise<TokenPair | null> {
  const fetchImpl = options.fetchImpl ?? fetch;
  const base = options.apiBase.replace(/\/$/, "");
  const url = `${base}/auth/refresh`;

  try {
    const response = await fetchImpl(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Device-Id": options.deviceId,
        "X-Client-Type": "web",
      },
      body: JSON.stringify({ refresh_token: options.refreshToken }),
    });
    if (!response.ok) return null;
    const payload: unknown = await response.json();
    return parseRefreshTokenPayload(payload);
  } catch {
    return null;
  }
}
