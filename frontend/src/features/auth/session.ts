const REFRESH_TOKEN_KEY = "krishi-refresh-token";
const SIGN_OUT_FLAG = "krishi-signed-out";

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  try {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setRefreshToken(token: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(REFRESH_TOKEN_KEY, token);
}

export function clearRefreshToken(): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  } catch {
    // Ignore storage errors
  }
}

export function wasExplicitlySignedOut(): boolean {
  if (typeof window === "undefined") return false;
  try {
    return sessionStorage.getItem(SIGN_OUT_FLAG) === "1";
  } catch {
    return false;
  }
}

export function markSignedOut(): void {
  if (typeof window === "undefined") return;
  try {
    sessionStorage.setItem(SIGN_OUT_FLAG, "1");
  } catch {
    // Ignore storage errors
  }
}

export function clearSignedOutFlag(): void {
  if (typeof window === "undefined") return;
  try {
    sessionStorage.removeItem(SIGN_OUT_FLAG);
  } catch {
    // Ignore storage errors
  }
}
