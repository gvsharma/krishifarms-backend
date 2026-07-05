"use client";

import { MuiAppShell } from "@/components/shell/mui-app-shell";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return <MuiAppShell>{children}</MuiAppShell>;
}
