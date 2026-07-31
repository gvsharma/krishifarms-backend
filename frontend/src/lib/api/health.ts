import { getApiBaseUrl } from "./config";

const HEALTH_TIMEOUT_MS = 8_000;

/** Public GET /health — no auth. Returns false on network/timeout/non-OK. */
export async function fetchApiHealth(): Promise<boolean> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), HEALTH_TIMEOUT_MS);
  try {
    const res = await fetch(`${getApiBaseUrl()}/health`, {
      method: "GET",
      signal: controller.signal,
      cache: "no-store",
    });
    if (!res.ok) return false;
    const payload = (await res.json()) as { success?: boolean };
    return payload.success === true;
  } catch {
    return false;
  } finally {
    clearTimeout(timeout);
  }
}
