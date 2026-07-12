import type { APIRequestContext, APIResponse } from "@playwright/test";

const API_BASE = process.env.PLAYWRIGHT_API_URL ?? process.env.PLAYWRIGHT_BASE_URL ?? "";

type ApiEnvelope<T> = {
  success: boolean;
  data?: T;
  error?: { message?: string };
};

/** Authenticated API request using bearer token from env or storage. */
export async function apiGet<T>(
  request: APIRequestContext,
  path: string,
  token?: string,
): Promise<{ response: APIResponse; body: ApiEnvelope<T> }> {
  const headers: Record<string, string> = { Accept: "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await request.get(`${API_BASE}${path}`, { headers });
  const body = (await response.json()) as ApiEnvelope<T>;
  return { response, body };
}

export async function apiPost<T>(
  request: APIRequestContext,
  path: string,
  data: unknown,
  token?: string,
): Promise<{ response: APIResponse; body: ApiEnvelope<T> }> {
  const headers: Record<string, string> = {
    Accept: "application/json",
    "Content-Type": "application/json",
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await request.post(`${API_BASE}${path}`, { headers, data });
  const body = (await response.json()) as ApiEnvelope<T>;
  return { response, body };
}

/** Login via API and return access token (for hybrid API+UI tests). */
export async function loginViaApi(
  request: APIRequestContext,
  email: string,
  password: string,
): Promise<string> {
  const { response, body } = await apiPost<{ access_token: string }>(
    request,
    "/auth/login",
    { email, password },
  );
  if (!response.ok() || !body.data?.access_token) {
    throw new Error(`API login failed: ${body.error?.message ?? response.status()}`);
  }
  return body.data.access_token;
}
