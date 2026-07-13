"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { CircularProgress, Box } from "@mui/material";
import { fetchAuthMe, forceSessionExpiredLogout } from "@/features/auth/api";
import { ApiError, getAccessToken } from "@/lib/api/client";
import { ROUTES } from "@/constants/routes";
import { MuiAppShell } from "@/components/shell/mui-app-shell";

/**
 * App shell requires a valid access token. Missing token → login.
 * Present-but-invalid token is recovered (refresh) or cleared via fetchApi 401 handling
 * when /auth/me runs; if refresh fails we land on login.
 */
export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function gate() {
      if (!getAccessToken()) {
        router.replace(ROUTES.login);
        return;
      }

      try {
        // Proactively validate / refresh session before rendering protected UI.
        await fetchAuthMe();
        if (!cancelled) setReady(true);
      } catch (err) {
        if (cancelled) return;
        // fetchApi already tried refresh on 401; if tokens remain, force clear.
        if (err instanceof ApiError && err.status === 401) {
          forceSessionExpiredLogout(true);
          return;
        }
        if (!getAccessToken()) {
          router.replace(ROUTES.login);
          return;
        }
        // Transient network blip: allow shell; pages show their own errors.
        setReady(true);
      }
    }

    void gate();
    return () => {
      cancelled = true;
    };
  }, [router]);

  if (!ready) {
    return (
      <Box sx={{ minHeight: "100vh", display: "grid", placeItems: "center" }}>
        <CircularProgress size={28} aria-label="Checking session" />
      </Box>
    );
  }

  return <MuiAppShell>{children}</MuiAppShell>;
}
