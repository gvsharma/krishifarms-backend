"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchAuthMe } from "@/features/auth/api";
import { permissionMatches } from "@/features/auth/permission-aliases";
import {
  canAccessAdmin,
  canCreateUsers,
  canDelete,
  canManageUsers,
  primaryRole,
} from "@/features/auth/types";
import type { NavRole } from "@/constants/nav-config";

export function useAuth() {
  const query = useQuery({
    queryKey: ["auth", "me"],
    queryFn: fetchAuthMe,
    staleTime: 5 * 60_000,
    // 401s are handled by fetchApi (refresh or force logout) — don't spam retries.
    retry: (failureCount, error) => {
      if (error instanceof Error && "status" in error && (error as { status: number }).status === 401) {
        return false;
      }
      return failureCount < 1;
    },
  });

  const roles = query.data?.roles ?? [];
  const permissions = query.data?.permissions ?? [];
  const role = primaryRole(roles);

  const hasPermission = (permission: string): boolean => {
    if (permissionMatches(permissions, permission)) return true;
    // OWNER is treated as superuser for UI guards when catalog is sparse.
    if (roles.includes("OWNER")) return true;
    return false;
  };

  return {
    ...query,
    user: query.data?.user,
    roles,
    permissions,
    role,
    hasPermission,
    canDelete: canDelete(roles),
    canManageUsers: canManageUsers(roles),
    canCreateUsers: canCreateUsers(roles, permissions),
    canAccessAdmin: canAccessAdmin(roles),
  };
}

const NAV_ROLES = [
  "OWNER",
  "MANAGER",
  "SUPERVISOR",
  "AGENT",
  "DRIVER",
  "WORKER",
  "ACCOUNTANT",
] as const;

export function useNavRole(): NavRole {
  const { role } = useAuth();
  if (role && NAV_ROLES.includes(role as (typeof NAV_ROLES)[number])) {
    return role as NavRole;
  }
  return "WORKER";
}
