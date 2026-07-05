import { getApiBaseUrl } from "./config";
import { getDeviceId } from "./device-id";

const TOKEN_KEY = "krishi-access-token";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public body?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setAccessToken(token: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(TOKEN_KEY, token);
}

export interface ApiEnvelope<T> {
  success: boolean;
  data: T;
  meta?: Record<string, unknown> | null;
}

export interface FetchApiOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
  /** Include X-Device-Id and X-Client-Type (default true for mutations). */
  clientHeaders?: boolean;
}

export async function fetchApi<T>(
  path: string,
  options: FetchApiOptions = {},
): Promise<T> {
  const { body, clientHeaders = options.method !== "GET", headers, ...rest } = options;
  const base = getApiBaseUrl().replace(/\/$/, "");
  const url = path.startsWith("http") ? path : `${base}${path.startsWith("/") ? path : `/${path}`}`;

  const token = getAccessToken();
  const reqHeaders = new Headers(headers);

  if (body !== undefined && !reqHeaders.has("Content-Type")) {
    reqHeaders.set("Content-Type", "application/json");
  }
  if (token) {
    reqHeaders.set("Authorization", `Bearer ${token}`);
  }
  if (clientHeaders) {
    reqHeaders.set("X-Device-Id", getDeviceId());
    reqHeaders.set("X-Client-Type", "web");
  }

  const response = await fetch(url, {
    ...rest,
    headers: reqHeaders,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  let payload: unknown;
  const contentType = response.headers.get("content-type");
  if (contentType?.includes("application/json")) {
    payload = await response.json();
  } else {
    payload = await response.text();
  }

  if (!response.ok) {
    const message =
      typeof payload === "object" &&
      payload !== null &&
      "detail" in payload &&
      typeof (payload as { detail: unknown }).detail === "string"
        ? (payload as { detail: string }).detail
        : `Request failed (${response.status})`;
    throw new ApiError(message, response.status, payload);
  }

  if (
    typeof payload === "object" &&
    payload !== null &&
    "success" in payload &&
    "data" in payload
  ) {
    return (payload as ApiEnvelope<T>).data;
  }

  return payload as T;
}
