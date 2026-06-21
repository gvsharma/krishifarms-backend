"use client";

import { AppShell } from "@/components/shell/app-shell";
import { PageShell } from "@/components/shell/page-shell";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return <AppShell>{children}</AppShell>;
}
