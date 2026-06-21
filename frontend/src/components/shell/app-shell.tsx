"use client";

import { Sidebar } from "@/components/shell/sidebar";
import { Header } from "@/components/shell/header";
import { cn } from "@/lib/utils";
import { useUiStore } from "@/stores/ui-store";

interface AppShellProps {
  children: React.ReactNode;
  title?: string;
  breadcrumbs?: { label: string; href?: string }[];
}

export function AppShell({ children, title, breadcrumbs }: AppShellProps) {
  const collapsed = useUiStore((s) => s.sidebarCollapsed);

  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      <div
        className={cn(
          "flex min-h-screen flex-col transition-all duration-300 ease-premium",
          collapsed ? "pl-sidebar-collapsed" : "pl-sidebar",
        )}
      >
        <Header title={title} breadcrumbs={breadcrumbs} />
        <main className="flex-1">{children}</main>
      </div>
    </div>
  );
}
