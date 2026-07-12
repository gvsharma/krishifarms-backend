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
  const role = primaryRole(roles);

  return {
    ...query,
    user: query.data?.user,
    roles,
    role,
    canDelete: canDelete(roles),
    canManageUsers: canManageUsers(roles),
    canAccessAdmin: canAccessAdmin(roles),
  };
}

export function useNavRole(): NavRole {
  const { role } = useAuth();
  return (role ?? "OWNER") as NavRole;
}
