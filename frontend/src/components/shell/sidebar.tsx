"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  ChevronLeft,
  ChevronRight,
  CreditCard,
  LayoutDashboard,
  Leaf,
  Receipt,
  Settings,
  Sprout,
  Tractor,
  Truck,
  Users,
  Wallet,
  Wheat,
  type LucideIcon,
} from "lucide-react";
import { ROUTES, SITE_NAME } from "@/constants/routes";
import { cn } from "@/lib/utils";
import { useUiStore } from "@/stores/ui-store";
import { Button } from "@/components/ui/button";

interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

const NAV_SECTIONS: NavSection[] = [
  {
    title: "Overview",
    items: [{ href: ROUTES.dashboard, label: "Dashboard", icon: LayoutDashboard }],
  },
  {
    title: "Operations",
    items: [
      { href: ROUTES.farmers, label: "Farmers", icon: Users },
      { href: ROUTES.farms, label: "Farms", icon: Sprout },
      { href: ROUTES.collections, label: "Collections", icon: Wallet },
      { href: ROUTES.procurement, label: "Procurement", icon: Wheat },
      { href: ROUTES.vehicles, label: "Vehicles", icon: Truck },
      { href: ROUTES.workers, label: "Workers", icon: Tractor },
    ],
  },
  {
    title: "Finance",
    items: [
      { href: ROUTES.payments, label: "Payments", icon: CreditCard },
      { href: ROUTES.expenses, label: "Expenses", icon: Receipt },
    ],
  },
  {
    title: "Insights",
    items: [{ href: ROUTES.reports, label: "Reports", icon: BarChart3 }],
  },
  {
    title: "System",
    items: [{ href: ROUTES.settings, label: "Settings", icon: Settings }],
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const collapsed = useUiStore((s) => s.sidebarCollapsed);
  const toggleSidebar = useUiStore((s) => s.toggleSidebar);

  return (
    <aside
      className={cn(
        "fixed inset-y-0 left-0 z-30 flex flex-col border-r border-sidebar-border bg-sidebar shadow-sidebar transition-all duration-300 ease-premium",
        collapsed ? "w-sidebar-collapsed" : "w-sidebar",
      )}
    >
      <div
        className={cn(
          "flex h-header items-center border-b border-sidebar-border px-4",
          collapsed ? "justify-center" : "gap-3",
        )}
      >
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-primary text-primary-foreground">
          <Leaf className="h-5 w-5" strokeWidth={2} />
        </div>
        {!collapsed && (
          <div className="min-w-0">
            <p className="truncate font-display text-base font-semibold tracking-tight text-foreground">
              {SITE_NAME}
            </p>
            <p className="truncate text-[11px] text-muted-foreground">Bhairkhanpally</p>
          </div>
        )}
      </div>

      <nav className="flex-1 overflow-y-auto px-3 py-4">
        {NAV_SECTIONS.map((section) => (
          <div key={section.title} className="mb-5 last:mb-0">
            {!collapsed && (
              <p className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                {section.title}
              </p>
            )}
            <ul className="space-y-1">
              {section.items.map((item) => {
                const active =
                  pathname === item.href || pathname.startsWith(`${item.href}/`);
                const Icon = item.icon;
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      title={collapsed ? item.label : undefined}
                      className={cn(
                        "group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200 ease-premium",
                        active
                          ? "nav-item-active"
                          : "text-muted-foreground hover:bg-sidebar-accent hover:text-foreground",
                        collapsed && "justify-center px-2",
                      )}
                    >
                      <Icon
                        className={cn("h-5 w-5 shrink-0", active && "text-primary-foreground")}
                        strokeWidth={active ? 2 : 1.75}
                      />
                      {!collapsed && <span className="truncate">{item.label}</span>}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      <div className="border-t border-sidebar-border p-3">
        <Button
          type="button"
          variant="ghost"
          size={collapsed ? "icon" : "md"}
          onClick={toggleSidebar}
          className={cn("w-full", collapsed && "mx-auto")}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <>
              <ChevronLeft className="h-4 w-4" />
              <span>Collapse</span>
            </>
          )}
        </Button>
      </div>
    </aside>
  );
}
