export interface AuthUser {
  id: string;
  name: string;
  mobile: string;
  email: string | null;
  village_id: string | null;
  preferred_locale: string;
}

export interface AuthMe {
  user: AuthUser;
  roles: string[];
  permissions: string[];
  accessibleModules: string[];
}

export type AppRole = "OWNER" | "MANAGER" | "SUPERVISOR" | "AGENT" | "DRIVER" | "WORKER" | "ACCOUNTANT";

export function primaryRole(roles: string[]): AppRole | null {
  const order: AppRole[] = ["OWNER", "MANAGER", "SUPERVISOR", "ACCOUNTANT", "AGENT", "DRIVER", "WORKER"];
  return order.find((r) => roles.includes(r)) ?? null;
}

export function canDelete(roles: string[]): boolean {
  return roles.includes("OWNER");
}

export function canManageUsers(roles: string[]): boolean {
  return roles.some((r) => r === "OWNER" || r === "MANAGER");
}

export function canAccessAdmin(roles: string[]): boolean {
  return canManageUsers(roles);
}
