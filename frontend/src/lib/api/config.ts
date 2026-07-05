const API_V1_PREFIX = "/api/v1";

const isVercel = Boolean(process.env.VERCEL);
const localhostDefault = "http://localhost:8080/api/v1";

function isLocalApiBase(value: string | undefined): boolean {
  if (!value) return true;
  return value === localhostDefault || value.startsWith("http://localhost");
}

/** Single source of truth for API base URL (mirrors next.config.ts rewrites). */
export function getApiBaseUrl(): string {
  const raw = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  if (typeof window !== "undefined") {
    if (isVercel && isLocalApiBase(raw)) return API_V1_PREFIX;
    return raw || localhostDefault;
  }
  if (isVercel && isLocalApiBase(raw)) return API_V1_PREFIX;
  return raw || localhostDefault;
}
