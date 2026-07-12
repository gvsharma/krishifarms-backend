"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchAuthMe } from "@/features/auth/api";
import {
  canAccessAdmin,
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
    retry: 1,
  });

  const roles = query.data?.roles ?? [];
  const permissions = query.data?.permissions ?? [];
  const role = primaryRole(roles);

  const hasPermission = (permission: string): boolean => {
    if (permissions.includes(permission)) return true;
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
    canAccessAdmin: canAccessAdmin(roles),
  };
}

export function useNavRole(): NavRole {
  const { role } = useAuth();
  return (role ?? "OWNER") as NavRole;
}
