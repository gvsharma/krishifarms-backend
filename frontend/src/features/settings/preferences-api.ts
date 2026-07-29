import { fetchApi } from "@/lib/api/client";
import type { User } from "./api";

export function updateCurrentUser(payload: {
  full_name?: string;
  preferred_locale?: string;
}): Promise<User> {
  return fetchApi<User>("/users/me", { method: "PATCH", body: payload, clientHeaders: true });
}
