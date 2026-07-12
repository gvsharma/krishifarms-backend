"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getAccessToken } from "@/lib/api/client";
import { ROUTES } from "@/constants/routes";
import { MuiAppShell } from "@/components/shell/mui-app-shell";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!getAccessToken()) {
      router.replace(ROUTES.login);
      return;
    }
    setReady(true);
  }, [router]);

  if (!ready) return null;

  return <MuiAppShell>{children}</MuiAppShell>;
}
