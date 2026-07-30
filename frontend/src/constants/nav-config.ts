"use client";

import {
  AccountBalance,
  Agriculture,
  Analytics,
  Dashboard,
  Dataset,
  Handshake,
  HolidayVillage,
  People,
  Settings,
  Spa,
  WorkOutline,
} from "@mui/icons-material";
import type { SvgIconComponent } from "@mui/icons-material";
import { ROUTES } from "@/constants/routes";

/** Role codes aligned with backend RBAC. */
export type NavRole = "OWNER" | "MANAGER" | "SUPERVISOR" | "AGENT" | "DRIVER" | "WORKER" | "HAMALI" | "ACCOUNTANT";

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
    items: [
      { href: ROUTES.dashboard, label: "Dashboard", icon: Dashboard },
      {
        href: ROUTES.analytics,
        label: "Analytics",
        icon: Analytics,
        roles: ["OWNER", "MANAGER", "ACCOUNTANT"],
      },
    ],
  },
  {
    title: "Operations",
    items: [
      {
        href: ROUTES.farmers,
        label: "Farmers",
        icon: Agriculture,
        roles: ["OWNER", "MANAGER", "SUPERVISOR", "ACCOUNTANT"],
      },
      {
        href: ROUTES.villages,
        label: "Villages",
        icon: HolidayVillage,
        roles: ["OWNER", "MANAGER", "SUPERVISOR", "ACCOUNTANT", "AGENT", "DRIVER"],
      },
      {
        href: ROUTES.procurement,
        label: "Procurement",
        icon: Spa,
        roles: ["OWNER", "MANAGER", "SUPERVISOR"],
      },
      {
        href: ROUTES.hamali,
        label: "My work",
        icon: WorkOutline,
        roles: ["HAMALI"],
      },
      {
        href: ROUTES.settingsHamali,
        label: "Hamali work log",
        icon: WorkOutline,
        roles: ["OWNER", "MANAGER", "SUPERVISOR"],
      },
      {
        href: ROUTES.services,
        label: "Field services",
        icon: Handshake,
        roles: ["OWNER", "MANAGER", "SUPERVISOR", "AGENT", "DRIVER"],
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
        href: ROUTES.settingsUsers,
        label: "Users",
        icon: People,
        roles: ["OWNER", "MANAGER"],
      },
      {
        href: ROUTES.settingsMasterData,
        label: "Master data",
        icon: Dataset,
        roles: ["OWNER", "MANAGER"],
      },
      {
        href: ROUTES.settings,
        label: "Settings",
        icon: Settings,
        roles: ["OWNER", "MANAGER"],
      },
    ],
  },
];

export function filterNavByRole(sections: NavSection[], role: NavRole): NavSection[] {
  return sections
    .map((section) => ({
      ...section,
      items: section.items.filter((item) => !item.roles || item.roles.includes(role)),
    }))
    .filter((section) => section.items.length > 0);
}
