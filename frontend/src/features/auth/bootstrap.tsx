"use client";

import { useEffect } from "react";
import { bootstrapAuthToken } from "@/features/auth/api";

/** Ensures API client has a JWT before data queries (dev token or auto-login). */
export function AuthBootstrap({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    void bootstrapAuthToken();
  }, []);

  return <>{children}</>;
}
