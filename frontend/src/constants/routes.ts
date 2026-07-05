import {
  AccountBalance,
  Agriculture,
  Dashboard,
  Handshake,
  Settings,
  Spa,
} from "@mui/icons-material";
import type { SvgIconComponent } from "@mui/icons-material";

export const SITE_NAME = "KrishiFarms";

export const ROUTES = {
  dashboard: "/dashboard",
  farmers: "/farmers",
  farms: "/farms",
  collections: "/collections",
  procurement: "/procurement",
  services: "/workers",
  payments: "/payments",
  expenses: "/expenses",
  vehicles: "/vehicles",
  workers: "/workers",
  reports: "/reports",
  settings: "/settings",
  settingsUsers: "/settings/users",
  settingsVillages: "/settings/villages",
  settingsMasterData: "/settings/master-data",
} as const;

export type AppRoute = (typeof ROUTES)[keyof typeof ROUTES];

/** Role codes aligned with backend RBAC (placeholder gating for W1). */
export type NavRole = "OWNER" | "MANAGER" | "AGENT" | "DRIVER" | "ACCOUNTANT";

export interface NavItem {
  href: string;
  label: string;
  icon: SvgIconComponent;
  /** Empty = visible to all authenticated roles. */
  roles?: NavRole[];
}

export interface NavSection {
  title: string;
  items: NavItem[];
}

/** Role-aware nav matching backend module groups (W1 placeholders). */
export const NAV_SECTIONS: NavSection[] = [
  {
    title: "Overview",
    items: [{ href: ROUTES.dashboard, label: "Dashboard", icon: Dashboard }],
  },
  {
    title: "Operations",
    items: [
      { href: ROUTES.farmers, label: "Farmers", icon: Agriculture },
      { href: ROUTES.procurement, label: "Procurement", icon: Spa },
      {
        href: ROUTES.services,
        label: "Services",
        icon: Handshake,
        roles: ["OWNER", "MANAGER", "AGENT"],
      },
    ],
  },
  {
    title: "Finance",
    items: [
      {
        href: ROUTES.payments,
        label: "Finance",
        icon: AccountBalance,
        roles: ["OWNER", "MANAGER", "ACCOUNTANT"],
      },
    ],
  },
  {
    title: "System",
    items: [
      {
        href: ROUTES.settings,
        label: "Settings",
        icon: Settings,
        roles: ["OWNER", "MANAGER"],
      },
    ],
  },
];

/** W1 placeholder — replace with JWT role from auth context in W2. */
export const PLACEHOLDER_USER_ROLE: NavRole = "OWNER";

export function filterNavByRole(sections: NavSection[], role: NavRole): NavSection[] {
  return sections
    .map((section) => ({
      ...section,
      items: section.items.filter((item) => !item.roles || item.roles.includes(role)),
    }))
    .filter((section) => section.items.length > 0);
}
