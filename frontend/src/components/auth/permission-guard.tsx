"use client";

import type { ReactNode } from "react";
import { useAuth } from "@/hooks/use-auth";

export type PermissionGuardProps = {
  /** Single permission or any-of list (e.g. `procurements:confirm`). */
  permission: string | string[];
  children: ReactNode;
  /** Rendered when the user lacks permission. Default: nothing. */
  fallback?: ReactNode;
};

/**
 * Conditionally render children when `/auth/me` includes the required permission.
 * Prefer action-level guards over role-only checks for workflow buttons.
 */
export function PermissionGuard({
  permission,
  children,
  fallback = null,
}: PermissionGuardProps) {
  const { hasPermission } = useAuth();
  const allowed = Array.isArray(permission)
    ? permission.some((p) => hasPermission(p))
    : hasPermission(permission);
  return allowed ? <>{children}</> : <>{fallback}</>;
}
