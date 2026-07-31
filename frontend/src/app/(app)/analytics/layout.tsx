"use client";

import { Alert } from "@mui/material";
import { useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";
import { PermissionGuard } from "@/components/auth/permission-guard";
import { ROUTES } from "@/constants/routes";
import { useAuth } from "@/hooks/use-auth";

/** Analytics Hub — OWNER/admin only (profit, revenue, expenses). */
export default function AnalyticsLayout({ children }: { children: ReactNode }) {
  const { role, isPending } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isPending && role && role !== "OWNER") {
      router.replace(ROUTES.dashboard);
    }
  }, [isPending, role, router]);

  return (
    <PermissionGuard
      permission="analytics:admin"
      fallback={
        <Alert severity="warning" sx={{ m: 3 }}>
          Analytics is restricted to admin (OWNER) only. Profit, revenue, and expense metrics are not
          available for your role.
        </Alert>
      }
    >
      {children}
    </PermissionGuard>
  );
}
